import '../../../../core/network/subnet_scanner.dart';
import '../models/miner_scan_model.dart';

abstract class NetworkScanDataSource {
  Stream<ScanProgressModel> scanSubnet(String subnet);
}

class ScanProgressModel {
  final double progress;
  final String currentIp;
  final List<MinerScanModel> miners;

  ScanProgressModel({
    required this.progress,
    required this.currentIp,
    required this.miners,
  });
}

class NetworkScanDataSourceImpl implements NetworkScanDataSource {
  final SubnetScanner _scanner;

  NetworkScanDataSourceImpl(this._scanner);

  @override
  Stream<ScanProgressModel> scanSubnet(String subnet) {
    return _scanner.scanSubnet(subnet).map((progress) {
      final List<MinerScanModel> models = progress.miners
          .map((m) => MinerScanModel.fromDiscoveredMiner(m))
          .toList();
      return ScanProgressModel(
        progress: progress.progress,
        currentIp: progress.currentIp,
        miners: models,
      );
    });
  }
}
