import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/scan_provider.dart';
import '../../../miner_detail/presentation/pages/miner_detail_page.dart';

class ScanPage extends ConsumerStatefulWidget {
  const ScanPage({super.key});

  @override
  ConsumerState<ScanPage> createState() => _ScanPageState();
}

class _ScanPageState extends ConsumerState<ScanPage> {
  final TextEditingController _subnetController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final state = ref.read(scanProvider);
      _subnetController.text = state.subnet;
    });
  }

  @override
  void dispose() {
    _subnetController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(scanProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('اسکنر شبکه ماینرها'),
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
              // Subnet Input Section
              Card(
                margin: const EdgeInsets.all(16),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _subnetController,
                          decoration: InputDecoration(
                            labelText: 'محدوده آی‌پی (زیرشبکه)',
                            hintText: '192.168.1',
                            prefixIcon: const Icon(Icons.network_ping, color: Color(0xFF0D47A1)),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          keyboardType: TextInputType.number,
                          onChanged: (value) {
                            ref.read(scanProvider.notifier).setSubnet(value);
                          },
                          enabled: !state.isScanning,
                        ),
                      ),
                      const SizedBox(width: 12),
                      ElevatedButton(
                        onPressed: state.isScanning
                            ? () => ref.read(scanProvider.notifier).stopScan()
                            : () => ref.read(scanProvider.notifier).startScan(),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: state.isScanning ? Colors.red : const Color(0xFF0D47A1),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: Row(
                          children: [
                            Icon(state.isScanning ? Icons.stop : Icons.search),
                            const SizedBox(width: 4),
                            Text(state.isScanning ? 'توقف' : 'شروع اسکن'),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              // Progress Card
              if (state.isScanning || state.progress > 0.0)
                Card(
                  margin: const EdgeInsets.symmetric(horizontal: 16),
                  color: isDark ? const Color(0xFF1E1E1E) : Colors.white,
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              state.isScanning ? 'درحال جستجوی تجهیزات اسیک...' : 'اسکن شبکه به پایان رسید',
                              style: const TextStyle(fontWeight: FontWeight.bold),
                            ),
                            Text(
                              '${(state.progress * 100).toInt()}%',
                              style: const TextStyle(
                                color: Color(0xFFFFD700),
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        LinearProgressIndicator(
                          value: state.progress,
                          backgroundColor: Colors.grey[300],
                          color: const Color(0xFF0D47A1),
                          minHeight: 8,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        if (state.isScanning) ...[
                          const SizedBox(height: 8),
                          Text(
                            'آی‌پی درحال اسکن: ${state.currentIp}',
                            style: Theme.of(context).textTheme.labelLarge,
                          ),
                        ]
                      ],
                    ),
                  ),
                ),

              // Discovered Count Badge
              Padding(
                padding: const EdgeInsets.only(left: 16, right: 16, top: 16, bottom: 8),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'دستگاه‌های یافت شده',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: const Color(0xFF0D47A1).withOpacity(0.15),
                        border: Border.all(color: const Color(0xFF0D47A1), width: 1.5),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        '${state.miners.length} دستگاه',
                        style: const TextStyle(
                          color: Color(0xFF0D47A1),
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              // Miners List
              Expanded(
                child: state.miners.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.dns_outlined,
                              size: 80,
                              color: Colors.grey[400],
                            ),
                            const SizedBox(height: 16),
                            const Text(
                              'هیچ ماینری اسکن نشده یا یافت نگردید.',
                              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                            ),
                            const SizedBox(height: 8),
                            const Text(
                              'دکمه "شروع اسکن" را بفشارید تا جستجو آغاز شود.',
                              style: TextStyle(color: Colors.grey),
                            ),
                          ],
                        ),
                      )
                    : ListView.builder(
                        itemCount: state.miners.length,
                        padding: const EdgeInsets.symmetric(horizontal: 8),
                        itemBuilder: (context, index) {
                          final miner = state.miners[index];
                          return Card(
                            key: ValueKey(miner.ip),
                            elevation: 3,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: ListTile(
                              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                              leading: CircleAvatar(
                                radius: 26,
                                backgroundColor: miner.type == 'Whatsminer'
                                    ? const Color(0xFFFFD700).withOpacity(0.2)
                                    : const Color(0xFF0D47A1).withOpacity(0.2),
                                child: Icon(
                                  miner.type == 'Whatsminer' ? Icons.developer_board : Icons.memory,
                                  color: miner.type == 'Whatsminer'
                                      ? const Color(0xFFFFD700)
                                      : const Color(0xFF0D47A1),
                                ),
                              ),
                              title: Row(
                                children: [
                                  Text(
                                    miner.model,
                                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                                  ),
                                  const SizedBox(width: 8),
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: Colors.grey.withOpacity(0.2),
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                    child: Text(
                                      miner.type,
                                      style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
                                    ),
                                  ),
                                ],
                              ),
                              subtitle: Padding(
                                padding: const EdgeInsets.only(top: 6),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      'آی‌پی: ${miner.ip}',
                                      style: const TextStyle(
                                        fontFamily: 'monospace',
                                        fontSize: 13,
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Row(
                                      children: [
                                        Container(
                                          width: 10,
                                          height: 10,
                                          decoration: BoxDecoration(
                                            color: miner.statusColor,
                                            shape: BoxShape.circle,
                                          ),
                                        ),
                                        const SizedBox(width: 6),
                                        Text(
                                          miner.statusFa,
                                          style: TextStyle(
                                            color: miner.statusColor,
                                            fontWeight: FontWeight.w600,
                                            fontSize: 12,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                              trailing: const Icon(Icons.chevron_left, color: Color(0xFF0D47A1)),
                              onTap: () {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) => MinerDetailPage(
                                      ip: miner.ip,
                                      model: miner.model,
                                      type: miner.type,
                                      port: miner.port,
                                    ),
                                  ),
                                );
                              },
                            ),
                          );
                        },
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
