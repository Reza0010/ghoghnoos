import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../booklet/presentation/providers/booklet_providers.dart';

class AdminDashboard extends ConsumerWidget {
  const AdminDashboard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('پنل مدیریت Fixboard')),
      body: GridView.count(
        padding: const EdgeInsets.all(16),
        crossAxisCount: 2,
        children: [
          _buildAdminCard(context, 'افزودن فصل', Icons.add_circle_outline, () {}),
          _buildAdminCard(context, 'مدیریت کاربران', Icons.people_outline, () {}),
          _buildAdminCard(context, 'گزارش فروش', Icons.bar_chart, () {}),
          _buildAdminCard(context, 'تنظیمات اپ', Icons.app_settings_alt, () {}),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {},
        label: const Text('فصل جدید'),
        icon: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildAdminCard(BuildContext context, String title, IconData icon, VoidCallback onTap) {
    return Card(
      child: InkWell(
        onTap: onTap,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 48, color: Colors.blue),
            const SizedBox(height: 12),
            Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
}
