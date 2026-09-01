import '../../../../core/network/miner_socket_client.dart';
import '../models/miner_metrics_model.dart';
import '../../domain/entities/miner_metrics_entity.dart';

abstract class MinerDetailRepository {
  Future<MinerMetricsEntity> getMinerMetrics({
    required String ip,
    required int port,
    required String type,
    required String model,
  });

  Future<bool> rebootMiner({
    required String ip,
    required int port,
    required String type,
  });
}

class MinerDetailRepositoryImpl implements MinerDetailRepository {
  final MinerSocketClient _socketClient;

  MinerDetailRepositoryImpl(this._socketClient);

  @override
  Future<MinerMetricsEntity> getMinerMetrics({
    required String ip,
    required int port,
    required String type,
    required String model,
  }) async {
    if (type == 'Whatsminer') {
      final response = await _socketClient.sendCommand(
        ip: ip,
        port: port,
        command: 'get_status',
      );
      return MinerMetricsModel.fromWhatsminerResponse(
        ip: ip,
        model: model,
        response: response,
      );
    } else {
      // Antminer / CGMiner
      final summaryResponse = await _socketClient.sendCommand(
        ip: ip,
        port: port,
        command: 'summary',
      );
      final statsResponse = await _socketClient.sendCommand(
        ip: ip,
        port: port,
        command: 'stats',
      );
      return MinerMetricsModel.fromCgminerResponse(
        ip: ip,
        model: model,
        summary: summaryResponse,
        stats: statsResponse,
      );
    }
  }

  @override
  Future<bool> rebootMiner({
    required String ip,
    required int port,
    required String type,
  }) async {
    try {
      final command = type == 'Whatsminer' ? 'reboot' : 'restart';
      final response = await _socketClient.sendCommand(
        ip: ip,
        port: port,
        command: command,
      );
      return response['status'] == 'OK' || response['STATUS']?[0]?['STATUS'] == 'S';
    } catch (_) {
      return false;
    }
  }
}
