class MinerMetricsEntity {
  final String ip;
  final String model;
  final String type;
  final int elapsedSeconds;
  final double hashrateThAv;
  final double hashrateTh5s;
  final int powerConsumptionWatts;
  final int voltageMv;
  final List<int> fanSpeeds;
  final List<double> boardTemps;
  final List<String> boardChipStats; // list of "OOOXOOOO..."
  final int? errorCode;
  final String statusMessage;

  const MinerMetricsEntity({
    required this.ip,
    required this.model,
    required this.type,
    required this.elapsedSeconds,
    required this.hashrateThAv,
    required this.hashrateTh5s,
    required this.powerConsumptionWatts,
    required this.voltageMv,
    required this.fanSpeeds,
    required this.boardTemps,
    required this.boardChipStats,
    this.errorCode,
    required this.statusMessage,
  });
}
