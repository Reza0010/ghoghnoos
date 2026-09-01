import '../../domain/entities/miner_metrics_entity.dart';

class MinerMetricsModel extends MinerMetricsEntity {
  const MinerMetricsModel({
    required super.ip,
    required super.model,
    required super.type,
    required super.elapsedSeconds,
    required super.hashrateThAv,
    required super.hashrateTh5s,
    required super.powerConsumptionWatts,
    required super.voltageMv,
    required super.fanSpeeds,
    required super.boardTemps,
    required super.boardChipStats,
    super.errorCode,
    required super.statusMessage,
  });

  factory MinerMetricsModel.fromCgminerResponse({
    required String ip,
    required String model,
    required Map<String, dynamic> summary,
    required Map<String, dynamic> stats,
  }) {
    // Parse CGMiner Summary
    final summaryData = summary['SUMMARY']?[0] ?? {};
    final elapsed = summaryData['Elapsed'] ?? 0;
    final hsAv = (summaryData['MHS av'] ?? 0.0) / 1000000.0; // MHS to THS
    final hs5s = (summaryData['MHS 5s'] ?? 0.0) / 1000000.0;

    // Parse CGMiner Stats
    final statsData = stats['STATS']?[0] ?? {};
    final power = statsData['Power'] ?? 3250;
    final voltage = statsData['Voltage'] ?? 1250;

    // Fan speeds
    final List<int> fans = [];
    final int fanNum = statsData['Fan Num'] ?? 4;
    for (int i = 0; i < fanNum; i++) {
      final fanSpeed = statsData['Fan[$i]'];
      if (fanSpeed != null) {
        fans.add(fanSpeed as int);
      }
    }

    // Board temperatures
    final List<double> temps = [];
    final int tempNum = statsData['Temp Num'] ?? 3;
    for (int i = 0; i < tempNum; i++) {
      final temp = statsData['Temp[$i]'];
      if (temp != null) {
        temps.add((temp as num).toDouble());
      }
    }

    // Board chip status
    final List<String> chips = [];
    for (int i = 0; i < 3; i++) {
      final chainData = statsData['Chain[$i]'] ?? {};
      final String chainStatus = chainData['Status'] ?? 'OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO';
      chips.add(chainStatus);
    }

    // Check if there is any failed chip ('X')
    bool hasBrokenChip = chips.any((s) => s.contains('X'));
    String msg = 'سالم و فعال';
    if (hasBrokenChip) {
      msg = 'خطای سخت‌افزاری تراشه (رگبار X)';
    } else if (temps.any((t) => t > 80)) {
      msg = 'دمای بحرانی برد';
    }

    return MinerMetricsModel(
      ip: ip,
      model: model,
      type: 'Antminer',
      elapsedSeconds: elapsed,
      hashrateThAv: hsAv,
      hashrateTh5s: hs5s,
      powerConsumptionWatts: power,
      voltageMv: voltage,
      fanSpeeds: fans,
      boardTemps: temps,
      boardChipStats: chips,
      statusMessage: msg,
    );
  }

  factory MinerMetricsModel.fromWhatsminerResponse({
    required String ip,
    required String model,
    required Map<String, dynamic> response,
  }) {
    final result = response['result'] ?? {};
    final elapsed = result['elapsed'] ?? 0;
    final hsAv = (result['hs'] ?? 0.0) / 1000.0; // Whatsminer reports in GHs usually
    final hs5s = (result['hs_5s'] ?? 0.0) / 1000.0;
    final power = result['power'] ?? 3150;
    final voltage = result['voltage'] ?? 1240;

    // Fan speeds
    final List<int> fans = List<int>.from(result['fans'] ?? [6000, 5900]);

    // Temperatures
    final List<double> temps = [];
    final boards = result['temps'] ?? [];
    for (var b in boards) {
      final chipAvg = b['chip_avg'] ?? 70;
      temps.add((chipAvg as num).toDouble());
    }

    // Chip stats mapping
    // Whatsminer has "chips_ok" and "chips_total" counts
    final List<String> chips = [];
    final List<dynamic> okList = result['chips_ok'] ?? [112, 112, 112];
    final List<dynamic> totalList = result['chips_total'] ?? [112, 112, 112];

    for (int i = 0; i < okList.length; i++) {
      final int ok = okList[i];
      final int total = totalList[i];
      final int failed = total - ok;

      final String okStr = 'O' * ok;
      final String failStr = 'X' * failed;
      chips.add(okStr + failStr);
    }

    final int? errorCode = result['error_code'];
    String msg = 'سالم و فعال';
    if (errorCode != null && errorCode != 0) {
      msg = 'کد خطا: $errorCode (تحلیل لاگ الزامی)';
    } else if (temps.any((t) => t > 85)) {
      msg = 'دمای بحرانی هش‌برد';
    }

    return MinerMetricsModel(
      ip: ip,
      model: model,
      type: 'Whatsminer',
      elapsedSeconds: elapsed,
      hashrateThAv: hsAv,
      hashrateTh5s: hs5s,
      powerConsumptionWatts: power,
      voltageMv: voltage,
      fanSpeeds: fans,
      boardTemps: temps,
      boardChipStats: chips,
      errorCode: errorCode,
      statusMessage: msg,
    );
  }
}
