import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/ai_assistant_provider.dart';

class AiDiagnosticsPage extends ConsumerStatefulWidget {
  final String? preloadedLog;

  const AiDiagnosticsPage({super.key, this.preloadedLog});

  @override
  ConsumerState<AiDiagnosticsPage> createState() => _AiDiagnosticsPageState();
}

class _AiDiagnosticsPageState extends ConsumerState<AiDiagnosticsPage> {
  final TextEditingController _logController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (widget.preloadedLog != null) {
        _logController.text = widget.preloadedLog!;
        ref.read(aiAssistantProvider.notifier).setLog(widget.preloadedLog!);
        ref.read(aiAssistantProvider.notifier).runDiagnostics();
      } else {
        final currentLog = ref.read(aiAssistantProvider).rawLog;
        _logController.text = currentLog;
      }
    });
  }

  @override
  void dispose() {
    _logController.dispose();
    super.dispose();
  }

  void _loadSampleLog(String logType) {
    String logText = '';
    switch (logType) {
      case 'hashboard_error':
        logText = '=== ANTMINER S19 PRO LOG ===\n'
            'INFO: CGMiner client starting\n'
            'INFO: Chain[0] frequency=675, chips=120, status=OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO\n'
            'INFO: Chain[1] frequency=675, chips=120, status=OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO\n'
            'ERROR: Chain[2] contains broken chips. Check matrix: OOOOXOOOOOOOOOXXXXXOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO\n'
            'CRITICAL: Board not found or hashboard dead on slot 3\n'
            'CRITICAL: Find 0 chain or pic init failed';
        break;
      case 'over_temp':
        logText = '=== WHATSMINER M30S LOG ===\n'
            'INFO: btminer init... found 3 boards\n'
            'INFO: board[1] temp chip_avg=72C\n'
            'INFO: board[2] temp chip_avg=75C\n'
            'WARNING: Board 3 chip temperature is too high: 96.5C\n'
            'CRITICAL: over temperature shutdown triggered on Board 3\n'
            'ERROR: Temp sensor limit exceeded! critical temp alarm!';
        break;
      case 'pool_lost':
        logText = '=== GENERAL ASIC SYSTEM LOG ===\n'
            'INFO: Booting system daemon...\n'
            'WARNING: Socket connect failed to stratum.f2pool.com:3333\n'
            'ERROR: Fail to connect to pool or Stratum connection lost\n'
            'INFO: Retrying pool connection in 10 seconds...';
        break;
    }

    _logController.text = logText;
    ref.read(aiAssistantProvider.notifier).setLog(logText);
    ref.read(aiAssistantProvider.notifier).runDiagnostics();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(aiAssistantProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('پایگاه عیب‌یابی و هوش مصنوعی'),
          elevation: 2,
        ),
        body: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: isDark
                  ? [const Color(0xFF121212), const Color(0xFF1E1E1E)]
                  : [const Color(0xFFF5F7FA), const Color(0xFFE4E9F0)],
            ),
          ),
          child: Column(
            children: [
              // Log Input Section
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // Instructions Card
                      Card(
                        margin: const EdgeInsets.only(bottom: 16),
                        child: Padding(
                          padding: const EdgeInsets.all(12),
                          child: Row(
                            children: [
                              const CircleAvatar(
                                backgroundColor: Color(0xFF0D47A1),
                                child: Icon(Icons.psychology, color: Colors.white),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Text(
                                  'برای عیب‌یابی، کدهای خطا یا لاگ رویدادهای ماینر را در کادر زیر قرار دهید تا سیستم هوش مصنوعی آن را فورا عیب‌یابی و تحلیل کند.',
                                  style: Theme.of(context).textTheme.bodyMedium,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),

                      // Input Box Card
                      Card(
                        elevation: 3,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              TextField(
                                controller: _logController,
                                maxLines: 7,
                                decoration: const InputDecoration(
                                  border: OutlineInputBorder(),
                                  labelText: 'سیاهه رویدادها (ASIC Logs / Errors)',
                                  hintText: 'مثال:\nCRITICAL: board not found slot 2...\nERROR: Fan lost...',
                                  alignLabelWithHint: true,
                                ),
                                style: const TextStyle(fontFamily: 'monospace', fontSize: 13),
                                onChanged: (value) {
                                  ref.read(aiAssistantProvider.notifier).setLog(value);
                                },
                                enabled: !state.isAnalyzing,
                              ),
                              const SizedBox(height: 12),
                              ElevatedButton.icon(
                                onPressed: state.isAnalyzing
                                    ? null
                                    : () => ref.read(aiAssistantProvider.notifier).runDiagnostics(),
                                icon: const Icon(Icons.flash_on),
                                label: const Text('آنالیز و عیب‌یابی هوشمند لاگ'),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: const Color(0xFF0D47A1),
                                  foregroundColor: Colors.white,
                                  padding: const EdgeInsets.symmetric(vertical: 14),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Quick Test Scenarios
                      Text(
                        'لاگ‌های نمونه برای تست سریع عیب‌یاب',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton(
                              onPressed: state.isAnalyzing ? null : () => _loadSampleLog('hashboard_error'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFFFFD700).withOpacity(0.15),
                                foregroundColor: isDark ? Colors.white : Colors.black87,
                                side: const BorderSide(color: Color(0xFFFFD700)),
                                padding: const EdgeInsets.symmetric(vertical: 10),
                              ),
                              child: const Text('خطای هش‌برد', style: TextStyle(fontSize: 12)),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: ElevatedButton(
                              onPressed: state.isAnalyzing ? null : () => _loadSampleLog('over_temp'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFFFFD700).withOpacity(0.15),
                                foregroundColor: isDark ? Colors.white : Colors.black87,
                                side: const BorderSide(color: Color(0xFFFFD700)),
                                padding: const EdgeInsets.symmetric(vertical: 10),
                              ),
                              child: const Text('دمای بحرانی', style: TextStyle(fontSize: 12)),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: ElevatedButton(
                              onPressed: state.isAnalyzing ? null : () => _loadSampleLog('pool_lost'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFFFFD700).withOpacity(0.15),
                                foregroundColor: isDark ? Colors.white : Colors.black87,
                                side: const BorderSide(color: Color(0xFFFFD700)),
                                padding: const EdgeInsets.symmetric(vertical: 10),
                              ),
                              child: const Text('قطعی استخر', style: TextStyle(fontSize: 12)),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 24),

                      // Animated Pipeline Overlay
                      if (state.isAnalyzing) _buildAnimatedPipeline(context, state.analysisStep),

                      // Diagnostics Results
                      if (state.report != null && !state.isAnalyzing) ...[
                        _buildDiagnosticResultSection(context, state.report!),
                      ],

                      if (state.errorMessage != null && !state.isAnalyzing) ...[
                        const SizedBox(height: 16),
                        Text(
                          state.errorMessage!,
                          style: const TextStyle(color: Colors.red, fontWeight: FontWeight.bold),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAnimatedPipeline(BuildContext context, String stepText) {
    return Card(
      color: const Color(0xFF0D47A1).withOpacity(0.1),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: Color(0xFF0D47A1), width: 1.5),
      ),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            const CircularProgressIndicator(
              color: Color(0xFF0D47A1),
            ),
            const SizedBox(height: 16),
            const Text(
              'موتور هوش مصنوعی در حال اجرای فرآیند عیب‌یابی...',
              style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF0D47A1)),
            ),
            const SizedBox(height: 8),
            Text(
              stepText,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 13, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDiagnosticResultSection(BuildContext context, Map<String, dynamic> report) {
    final String manufacturer = report['manufacturer'] ?? 'نامشخص';
    final String status = report['status'] ?? 'سالم';
    final List<dynamic> issues = report['issues'] ?? [];
    final String advice = report['advice'] ?? '';

    Color statusColor = Colors.green;
    if (status.contains('بحرانی')) {
      statusColor = Colors.red;
    } else if (status.contains('هشدار')) {
      statusColor = Colors.orange;
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'گزارش و نتیجه عیب‌یابی هوشمند',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 12),

        // Overall Status Header
        Card(
          elevation: 4,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('برند دستگاه شناسایی‌شده:', style: TextStyle(color: Colors.grey, fontSize: 12)),
                    const SizedBox(height: 4),
                    Text(manufacturer, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                  decoration: BoxDecoration(
                    color: statusColor.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: statusColor, width: 1.5),
                  ),
                  child: Text(
                    status,
                    style: TextStyle(color: statusColor, fontWeight: FontWeight.bold, fontSize: 13),
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),

        // Discovered Issues Cards
        ...issues.map((issue) {
          final String title = issue['title'] ?? 'خطا';
          final String desc = issue['description'] ?? '';
          final String severity = issue['severity'] ?? 'warning';
          final List<dynamic> steps = issue['steps'] ?? [];

          Color sevColor = Colors.orange;
          if (severity == 'critical') {
            sevColor = Colors.red;
          } else if (severity == 'info') {
            sevColor = Colors.blue;
          }

          return Card(
            margin: const EdgeInsets.only(bottom: 14),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            elevation: 2,
            child: ExpansionTile(
              initiallyExpanded: true,
              leading: Icon(Icons.report_problem, color: sevColor),
              title: Text(
                title,
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
              ),
              subtitle: Text(
                sevColor == Colors.red ? 'اولویت: بحرانی (سخت‌افزاری)' : 'اولویت: هشدار عمومی',
                style: TextStyle(color: sevColor, fontSize: 11, fontWeight: FontWeight.w600),
              ),
              children: [
                Padding(
                  padding: const EdgeInsets.only(left: 16, right: 16, bottom: 16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Divider(),
                      Text(desc, style: const TextStyle(fontSize: 13, height: 1.6)),
                      const SizedBox(height: 12),
                      const Text(
                        'مراحل عیب‌یابی و رفع خطا (توصیه کارشناس):',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF0D47A1)),
                      ),
                      const SizedBox(height: 8),
                      ...steps.asMap().entries.map((stepEntry) {
                        final sIdx = stepEntry.key;
                        final String sText = stepEntry.value;
                        return Padding(
                          padding: const EdgeInsets.symmetric(vertical: 4),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              CircleAvatar(
                                radius: 10,
                                backgroundColor: const Color(0xFF0D47A1).withOpacity(0.15),
                                child: Text(
                                  '${sIdx + 1}',
                                  style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF0D47A1)),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  sText,
                                  style: const TextStyle(fontSize: 12.5, height: 1.5),
                                ),
                              ),
                            ],
                          ),
                        );
                      }),
                    ],
                  ),
                ),
              ],
            ),
          );
        }),

        // Expert Advice Panel
        Card(
          color: const Color(0xFFFFD700).withOpacity(0.1),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: const BorderSide(color: Color(0xFFFFD700), width: 1.5),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.lightbulb, color: Color(0xFFFFD700)),
                    SizedBox(width: 8),
                    Text('توصیه عمومی هوش مصنوعی', style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFFFFD700))),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  advice,
                  style: const TextStyle(fontSize: 13, height: 1.6),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
