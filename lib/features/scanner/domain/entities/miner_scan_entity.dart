import 'package:flutter/material.dart';

class MinerScanEntity {
  final String ip;
  final String model;
  final String type; // 'Antminer' or 'Whatsminer'
  final int port;
  final String statusFa;
  final Color statusColor;

  const MinerScanEntity({
    required this.ip,
    required this.model,
    required this.type,
    required this.port,
    required this.statusFa,
    required this.statusColor,
  });
}
