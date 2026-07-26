import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/network/subnet_scanner.dart';
import '../../data/datasources/network_scan_datasource.dart';
import '../../data/repositories/scan_repository_impl.dart';
import '../../domain/entities/miner_scan_entity.dart';
import '../../domain/usecases/scan_usecase.dart';

class ScanState {
  final bool isScanning;
  final double progress;
  final String currentIp;
  final List<MinerScanEntity> miners;
  final String subnet;

  ScanState({
    required this.isScanning,
    required this.progress,
    required this.currentIp,
    required this.miners,
    required this.subnet,
  });

  factory ScanState.initial() {
    return ScanState(
      isScanning: false,
      progress: 0.0,
      currentIp: '',
      miners: [],
      subnet: '192.168.1',
    );
  }

  ScanState copyWith({
    bool? isScanning,
    double? progress,
    String? currentIp,
    List<MinerScanEntity>? miners,
    String? subnet,
  }) {
    return ScanState(
      isScanning: isScanning ?? this.isScanning,
      progress: progress ?? this.progress,
      currentIp: currentIp ?? this.currentIp,
      miners: miners ?? this.miners,
      subnet: subnet ?? this.subnet,
    );
  }
}

class ScanNotifier extends StateNotifier<ScanState> {
  final ScanUseCase _scanUseCase;
  StreamSubscription? _subscription;

  ScanNotifier(this._scanUseCase) : super(ScanState.initial());

  void setSubnet(String value) {
    state = state.copyWith(subnet: value);
  }

  void startScan() {
    _subscription?.cancel();

    state = state.copyWith(
      isScanning: true,
      progress: 0.0,
      currentIp: '',
      miners: [],
    );

    _subscription = _scanUseCase.execute(state.subnet).listen(
      (scanProgress) {
        state = state.copyWith(
          progress: scanProgress.progress,
          currentIp: scanProgress.currentIp,
          miners: scanProgress.miners,
        );
      },
      onError: (err) {
        state = state.copyWith(isScanning: false);
      },
      onDone: () {
        state = state.copyWith(isScanning: false);
      },
    );
  }

  void stopScan() {
    _subscription?.cancel();
    state = state.copyWith(isScanning: false);
  }

  @override
  void dispose() {
    _subscription?.cancel();
    super.dispose();
  }
}

// Global providers for Clean Architecture dependency injection
final subnetScannerProvider = Provider((ref) => SubnetScanner());

final networkScanDataSourceProvider = Provider((ref) {
  final scanner = ref.watch(subnetScannerProvider);
  return NetworkScanDataSourceImpl(scanner);
});

final scanRepositoryProvider = Provider((ref) {
  final dataSource = ref.watch(networkScanDataSourceProvider);
  return ScanRepositoryImpl(dataSource);
});

final scanUseCaseProvider = Provider((ref) {
  final repository = ref.watch(scanRepositoryProvider);
  return ScanUseCase(repository);
});

final scanProvider = StateNotifierProvider<ScanNotifier, ScanState>((ref) {
  final useCase = ref.watch(scanUseCaseProvider);
  return ScanNotifier(useCase);
});
