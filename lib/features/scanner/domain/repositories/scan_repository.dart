import '../entities/miner_scan_entity.dart';

abstract class ScanRepository {
  Stream<ScanProgressEntity> scanSubnet(String subnet);
}

class ScanProgressEntity {
  final double progress;
  final String currentIp;
  final List<MinerScanEntity> miners;

  ScanProgressEntity({
    required this.progress,
    required this.currentIp,
    required this.miners,
  });
}
