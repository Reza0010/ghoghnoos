import '../repositories/scan_repository.dart';

class ScanUseCase {
  final ScanRepository _repository;

  ScanUseCase(this._repository);

  Stream<ScanProgressEntity> execute(String subnet) {
    return _repository.scanSubnet(subnet);
  }
}
