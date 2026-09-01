import 'package:flutter/material.dart';
import '../../domain/entities/miner_scan_entity.dart';
import '../../../../core/network/subnet_scanner.dart';

class MinerScanModel extends MinerScanEntity {
  const MinerScanModel({
    required super.ip,
    required super.model,
    required super.type,
    required super.port,
    required super.statusFa,
    required super.statusColor,
  });

  factory MinerScanModel.fromDiscoveredMiner(DiscoveredMiner miner) {
    Color color;
    switch (miner.status) {
      case 'فعال':
        color = Colors.green;
        break;
      case 'دمای بالا':
        color = Colors.orange;
        break;
      case 'خطای هش‌برد':
        color = Colors.red;
        break;
      default:
        color = Colors.grey;
    }

    return MinerScanModel(
      ip: miner.ip,
      model: miner.model,
      type: miner.type,
      port: miner.port,
      statusFa: miner.status,
      statusColor: color,
    );
  }

  factory MinerScanModel.fromJson(Map<String, dynamic> json) {
    return MinerScanModel(
      ip: json['ip'] ?? '',
      model: json['model'] ?? '',
      type: json['type'] ?? '',
      port: json['port'] ?? 4028,
      statusFa: json['statusFa'] ?? 'نامشخص',
      statusColor: Colors.grey,
    );
  }
}
