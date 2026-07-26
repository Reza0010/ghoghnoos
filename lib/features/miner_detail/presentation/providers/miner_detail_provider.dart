import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/network/miner_socket_client.dart';
import '../../domain/entities/miner_metrics_entity.dart';
import '../../data/drivers/miner_drivers.dart';

class MinerDetailState {
  final bool isLoading;
  final MinerMetricsEntity? metrics;
  final String? errorMessage;
  final bool isRebooting;
  final bool? rebootSuccess;

  MinerDetailState({
    required this.isLoading,
    this.metrics,
    this.errorMessage,
    required this.isRebooting,
    this.rebootSuccess,
  });

  factory MinerDetailState.initial() {
    return MinerDetailState(
      isLoading: true,
      isRebooting: false,
    );
  }

  MinerDetailState copyWith({
    bool? isLoading,
    MinerMetricsEntity? metrics,
    String? errorMessage,
    bool? isRebooting,
    bool? rebootSuccess,
  }) {
    return MinerDetailState(
      isLoading: isLoading ?? this.isLoading,
      metrics: metrics ?? this.metrics,
      errorMessage: errorMessage, // can be set to null
      isRebooting: isRebooting ?? this.isRebooting,
      rebootSuccess: rebootSuccess ?? this.rebootSuccess,
    );
  }
}

class MinerDetailNotifier extends StateNotifier<MinerDetailState> {
  final MinerDetailRepository _repository;
  final String ip;
  final int port;
  final String type;
  final String model;
  Timer? _pollingTimer;

  MinerDetailNotifier({
    required MinerDetailRepository repository,
    required this.ip,
    required this.port,
    required this.type,
    required this.model,
  })  : _repository = repository,
        super(MinerDetailState.initial()) {
    fetchMetrics();
    startPolling();
  }

  Future<void> fetchMetrics() async {
    try {
      final data = await _repository.getMinerMetrics(
        ip: ip,
        port: port,
        type: type,
        model: model,
      );
      state = state.copyWith(
        isLoading: false,
        metrics: data,
        errorMessage: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در ارتباط با سوکت دستگاه ماینر: $e',
      );
    }
  }

  void startPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = Timer.periodic(const Duration(seconds: 5), (_) {
      fetchMetrics();
    });
  }

  void stopPolling() {
    _pollingTimer?.cancel();
  }

  Future<void> reboot() async {
    state = state.copyWith(isRebooting: true, rebootSuccess: null);
    try {
      final success = await _repository.rebootMiner(
        ip: ip,
        port: port,
        type: type,
      );
      state = state.copyWith(isRebooting: false, rebootSuccess: success);
    } catch (_) {
      state = state.copyWith(isRebooting: false, rebootSuccess: false);
    }
  }

  @override
  void dispose() {
    _pollingTimer?.cancel();
    super.dispose();
  }
}

// Global Providers for Dependency Injection
final minerSocketClientProvider = Provider((ref) => MinerSocketClient());

final minerDetailRepositoryProvider = Provider((ref) {
  final socketClient = ref.watch(minerSocketClientProvider);
  return MinerDetailRepositoryImpl(socketClient);
});

// Family Parameter
class MinerParams {
  final String ip;
  final int port;
  final String type;
  final String model;

  MinerParams({
    required this.ip,
    required this.port,
    required this.type,
    required this.model,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is MinerParams &&
          runtimeType == other.runtimeType &&
          ip == other.ip &&
          port == other.port &&
          type == other.type &&
          model == other.model;

  @override
  int get hashCode => ip.hashCode ^ port.hashCode ^ type.hashCode ^ model.hashCode;
}

final minerDetailProvider = StateNotifierProvider.family<MinerDetailNotifier, MinerDetailState, MinerParams>((ref, params) {
  final repository = ref.watch(minerDetailRepositoryProvider);
  return MinerDetailNotifier(
    repository: repository,
    ip: params.ip,
    port: params.port,
    type: params.type,
    model: params.model,
  );
});
