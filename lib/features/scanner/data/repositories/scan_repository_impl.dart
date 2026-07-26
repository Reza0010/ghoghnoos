import '../../domain/repositories/scan_repository.dart';
import '../datasources/network_scan_datasource.dart';

class ScanRepositoryImpl implements ScanRepository {
  final NetworkScanDataSource _dataSource;

  ScanRepositoryImpl(this._dataSource);

  @override
  Stream<ScanProgressEntity> scanSubnet(String subnet) {
    return _dataSource.scanSubnet(subnet).map((model) {
      return ScanProgressEntity(
        progress: model.progress,
        currentIp: model.currentIp,
        miners: model.miners,
      );
    });
  }
}
