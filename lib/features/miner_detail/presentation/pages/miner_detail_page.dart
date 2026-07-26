import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/miner_metrics_entity.dart';
import '../providers/miner_detail_provider.dart';
import '../../../ai_assistant/presentation/pages/ai_diagnostics_page.dart';

class MinerDetailPage extends ConsumerWidget {
  final String ip;
  final String model;
  final String type;
  final int port;

  const MinerDetailPage({
    super.key,
    required this.ip,
    required this.model,
    required this.type,
    required this.port,
  });

  String _formatUptime(int totalSeconds) {
    if (totalSeconds == 0) return 'نامشخص';
    final int days = totalSeconds ~/ (24 * 3600);
    final int hours = (totalSeconds % (24 * 3600)) ~/ 3600;
    final int minutes = (totalSeconds % 3600) ~/ 60;
    return '$days روز و $hours ساعت و $minutes دقیقه';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final params = MinerParams(ip: ip, port: port, type: type, model: model);
    final state = ref.watch(minerDetailProvider(params));
    final notifier = ref.read(minerDetailProvider(params).notifier);

    // Toast feedback for rebooting
    ref.listen<MinerDetailState>(minerDetailProvider(params), (previous, next) {
      if (previous?.isRebooting == true && next.isRebooting == false) {
        if (next.rebootSuccess == true) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('فرمان راه‌اندازی مجدد با موفقیت ارسال شد.'),
              backgroundColor: Colors.green,
            ),
          );
        } else if (next.rebootSuccess == false) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('خطا در ارسال فرمان راه‌اندازی مجدد.'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    });

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: Text(model),
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            onPressed: () {
              notifier.stopPolling();
              Navigator.pop(context);
            },
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: () => notifier.fetchMetrics(),
            )
          ],
        ),
        body: state.isLoading
            ? const Center(
                child: CircularProgressIndicator(
                  color: Color(0xFF0D47A1),
                ),
              )
            : state.errorMessage != null
                ? Center(
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.error_outline, size: 64, color: Colors.red),
                          const SizedBox(height: 16),
                          Text(
                            state.errorMessage!,
                            textAlign: TextAlign.center,
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                          ),
                          const SizedBox(height: 24),
                          ElevatedButton(
                            onPressed: () => notifier.fetchMetrics(),
                            child: const Text('تلاش مجدد'),
                          ),
                        ],
                      ),
                    ),
                  )
                : SingleChildScrollView(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // General Info Card
                        _buildGeneralInfoCard(context, state.metrics!),
                        const SizedBox(height: 16),

                        // Hashrate Section (Side-by-Side)
                        Row(
                          children: [
                            Expanded(
                              child: _buildHashrateCard(
                                context,
                                'تراهش لحظه‌ای (5s)',
                                state.metrics!.hashrateTh5s,
                                const Color(0xFF0D47A1),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: _buildHashrateCard(
                                context,
                                'تراهش میانگین (Av)',
                                state.metrics!.hashrateThAv,
                                const Color(0xFFFFD700),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),

                        // Fans & Temperature Section
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Expanded(child: _buildFansSection(context, state.metrics!.fanSpeeds)),
                            const SizedBox(width: 12),
                            Expanded(child: _buildTempsSection(context, state.metrics!.boardTemps)),
                          ],
                        ),
                        const SizedBox(height: 16),

                        // Interactive Hashboard Chip Grid Status
                        _buildHashboardChipStatusGrid(context, state.metrics!.boardChipStats),
                        const SizedBox(height: 20),

                        // Action Buttons
                        Row(
                          children: [
                            Expanded(
                              child: ElevatedButton.icon(
                                onPressed: state.isRebooting ? null : () => notifier.reboot(),
                                icon: state.isRebooting
                                    ? const SizedBox(
                                        width: 20,
                                        height: 20,
                                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                      )
                                    : const Icon(Icons.power_settings_new),
                                label: Text(state.isRebooting ? 'درحال ریبوت...' : 'راه‌اندازی مجدد'),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.red[700],
                                  foregroundColor: Colors.white,
                                  padding: const EdgeInsets.symmetric(vertical: 14),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: ElevatedButton.icon(
                                onPressed: () {
                                  // Pass simulated miner log directly to AI Diagnostics Screen
                                  final String sampleLog = _generateSimulatedMinerLog(state.metrics!);
                                  Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder: (context) => AiDiagnosticsPage(preloadedLog: sampleLog),
                                    ),
                                  );
                                },
                                icon: const Icon(Icons.analytics),
                                label: const Text('عیب‌یابی با هوش مصنوعی'),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: const Color(0xFF0D47A1),
                                  foregroundColor: Colors.white,
                                  padding: const EdgeInsets.symmetric(vertical: 14),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
      ),
    );
  }

  Widget _buildGeneralInfoCard(BuildContext context, MinerMetricsEntity metrics) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      metrics.model,
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'آی‌پی آدرس: ${metrics.ip}',
                      style: const TextStyle(fontFamily: 'monospace', color: Colors.grey),
                    ),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                  decoration: BoxDecoration(
                    color: metrics.statusMessage.contains('خطا') || metrics.statusMessage.contains('بحرانی')
                        ? Colors.red.withOpacity(0.15)
                        : Colors.green.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: metrics.statusMessage.contains('خطا') || metrics.statusMessage.contains('بحرانی')
                          ? Colors.red
                          : Colors.green,
                      width: 1.5,
                    ),
                  ),
                  child: Text(
                    metrics.statusMessage,
                    style: TextStyle(
                      color: metrics.statusMessage.contains('خطا') || metrics.statusMessage.contains('بحرانی')
                          ? Colors.red
                          : Colors.green,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            const Divider(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildInfoMiniTile('زمان کارکرد', _formatUptime(metrics.elapsedSeconds)),
                _buildInfoMiniTile('توان مصرفی', '${metrics.powerConsumptionWatts} وات'),
                _buildInfoMiniTile('ولتاژ کاری', '${metrics.voltageMv} میلی‌ولت'),
              ],
            )
          ],
        ),
      ),
    );
  }

  Widget _buildInfoMiniTile(String title, String value) {
    return Column(
      children: [
        Text(title, style: const TextStyle(color: Colors.grey, fontSize: 12)),
        const SizedBox(height: 6),
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
      ],
    );
  }

  Widget _buildHashrateCard(BuildContext context, String title, double hashrate, Color color) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text(
              title,
              style: const TextStyle(fontSize: 12, color: Colors.grey, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  width: 80,
                  height: 80,
                  child: CircularProgressIndicator(
                    value: hashrate / 120.0, // scale based on max hashrate
                    strokeWidth: 8,
                    backgroundColor: Colors.grey[800],
                    color: color,
                  ),
                ),
                Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      hashrate.toStringAsFixed(1),
                      style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 18),
                    ),
                    const Text('TH/s', style: TextStyle(fontSize: 10, color: Colors.grey)),
                  ],
                )
              ],
            )
          ],
        ),
      ),
    );
  }

  Widget _buildFansSection(BuildContext context, List<int> fanSpeeds) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.air, color: Color(0xFF0D47A1), size: 18),
                SizedBox(width: 6),
                Text('سرعت فن‌ها', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
              ],
            ),
            const SizedBox(height: 12),
            if (fanSpeeds.isEmpty)
              const Text('بدون داده فن')
            else
              ...fanSpeeds.asMap().entries.map((entry) {
                final idx = entry.key;
                final speed = entry.value;
                Color statusColor = Colors.green;
                if (speed < 2000) {
                  statusColor = Colors.red;
                } else if (speed < 4000) {
                  statusColor = Colors.orange;
                }
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 6),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('فن ${idx + 1}', style: const TextStyle(fontSize: 12)),
                          Text('$speed RPM', style: TextStyle(fontSize: 12, color: statusColor, fontWeight: FontWeight.bold)),
                        ],
                      ),
                      const SizedBox(height: 4),
                      LinearProgressIndicator(
                        value: speed / 8000.0,
                        backgroundColor: Colors.grey[800],
                        color: statusColor,
                        minHeight: 4,
                      )
                    ],
                  ),
                );
              }),
          ],
        ),
      ),
    );
  }

  Widget _buildTempsSection(BuildContext context, List<double> temps) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.thermostat, color: Color(0xFFFFD700), size: 18),
                SizedBox(width: 6),
                Text('دمای هش‌بردها', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
              ],
            ),
            const SizedBox(height: 12),
            if (temps.isEmpty)
              const Text('بدون داده دما')
            else
              ...temps.asMap().entries.map((entry) {
                final idx = entry.key;
                final temp = entry.value;
                Color statusColor = Colors.green;
                if (temp > 85) {
                  statusColor = Colors.red;
                } else if (temp > 75) {
                  statusColor = Colors.orange;
                }
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 6),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('برد ${idx + 1}', style: const TextStyle(fontSize: 12)),
                          Text('${temp.toStringAsFixed(1)} °C', style: TextStyle(fontSize: 12, color: statusColor, fontWeight: FontWeight.bold)),
                        ],
                      ),
                      const SizedBox(height: 4),
                      LinearProgressIndicator(
                        value: temp / 110.0,
                        backgroundColor: Colors.grey[800],
                        color: statusColor,
                        minHeight: 4,
                      )
                    ],
                  ),
                );
              }),
          ],
        ),
      ),
    );
  }

  Widget _buildHashboardChipStatusGrid(BuildContext context, List<String> chipStats) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.grid_view, color: Color(0xFF0D47A1), size: 18),
                SizedBox(width: 6),
                Text(
                  'وضعیت تراشه‌های هش‌بردها (ماتریس تراشه)',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                ),
              ],
            ),
            const SizedBox(height: 14),
            ...chipStats.asMap().entries.map((entry) {
              final idx = entry.key;
              final String statusStr = entry.value;
              final List<String> chips = statusStr.split('');

              final int okCount = chips.where((c) => c == 'O').length;
              final int totalCount = chips.length;

              return Padding(
                padding: const EdgeInsets.only(bottom: 14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'هش‌برد ${idx + 1}',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                        ),
                        Text(
                          '$okCount از $totalCount سالم',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: okCount == totalCount ? Colors.green : Colors.orange,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Wrap(
                      spacing: 3,
                      runSpacing: 3,
                      children: chips.map((c) {
                        final isOk = c == 'O';
                        return Container(
                          width: 10,
                          height: 10,
                          decoration: BoxDecoration(
                            color: isOk ? Colors.green : Colors.red,
                            borderRadius: BorderRadius.circular(2),
                          ),
                        );
                      }).toList(),
                    ),
                  ],
                ),
              );
            }),
          ],
        ),
      ),
    );
  }

  String _generateSimulatedMinerLog(MinerMetricsEntity metrics) {
    final buffer = StringBuffer();
    buffer.writeln('=== [${DateTime.now().toIso8601String()}] ASIC BOOT SEQUENCE ===');
    buffer.writeln('INFO: Starting BT-Miner client daemon for model: ${metrics.model}');
    buffer.writeln('INFO: Listening on port ${port}');
    buffer.writeln('INFO: Socket successfully bound to local IP: ${metrics.ip}');

    if (metrics.type == 'Whatsminer') {
      buffer.writeln('INFO: Initializing boards via smart Whatsminer controller.');
      buffer.writeln('INFO: Found 3 Hashboards on Whatsminer architecture.');
      buffer.writeln('INFO: Board 1 temps inlet=35, outlet=68, chip_avg=${metrics.boardTemps.isNotEmpty ? metrics.boardTemps[0] : 74}');
      buffer.writeln('INFO: Board 2 temps inlet=36, outlet=70, chip_avg=${metrics.boardTemps.length > 1 ? metrics.boardTemps[1] : 76}');

      if (metrics.boardTemps.length > 2 && metrics.boardTemps[2] > 85) {
        buffer.writeln('WARNING: Board 3 chip temperature is too high: ${metrics.boardTemps[2]}C');
        buffer.writeln('CRITICAL: over temperature shutdown triggered on Board 3');
      } else {
        buffer.writeln('INFO: Board 3 temps inlet=35, outlet=72, chip_avg=${metrics.boardTemps.length > 2 ? metrics.boardTemps[2] : 72}');
      }

      if (metrics.errorCode != null && metrics.errorCode != 0) {
        buffer.writeln('ERROR: WHATS_MINER_FAIL_CODE_${metrics.errorCode}: Hashboard 3 read error.');
        buffer.writeln('CRITICAL: some chip is broken on chain 3, missing 4 chips address check');
      } else {
        buffer.writeln('INFO: All chips passed SHA-256 self diagnostic checks successfully.');
      }
    } else {
      // Antminer
      buffer.writeln('INFO: CGMiner init successful for platform: S19');
      buffer.writeln('INFO: Setting S19 frequency preset: 675MHz');
      buffer.writeln('INFO: Detected fans Intake=5820 RPM, Exhaust=5910 RPM');

      final String chain2Status = metrics.boardChipStats.length > 2 ? metrics.boardChipStats[2] : '';
      if (chain2Status.contains('X')) {
        buffer.writeln('ERROR: Chain[2] contains broken chips. Check matrix: $chain2Status');
        buffer.writeln('ERROR: ASIC check failed on Board 3');
        buffer.writeln('WARNING: Hashboard 3 is deteriorating, average voltage drop detected.');
      } else {
        buffer.writeln('INFO: Chain[0] Status: OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO');
        buffer.writeln('INFO: Chain[1] Status: OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO');
        buffer.writeln('INFO: Chain[2] Status: OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO');
      }
    }

    buffer.writeln('INFO: Current Average Hashrate: ${metrics.hashrateThAv.toStringAsFixed(2)} TH/s');
    buffer.writeln('INFO: Current Live 5s Hashrate: ${metrics.hashrateTh5s.toStringAsFixed(2)} TH/s');
    buffer.writeln('INFO: Power draw: ${metrics.powerConsumptionWatts} Watts @ 220V');
    buffer.writeln('=== ASIC DIAGNOSTIC FINISHED ===');

    return buffer.toString();
  }
}
