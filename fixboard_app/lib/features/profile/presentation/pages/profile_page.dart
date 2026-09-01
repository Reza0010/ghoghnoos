import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../auth/presentation/providers/auth_providers.dart';

class ProfilePage extends ConsumerWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authStateProvider);
    final user = authState.value;

    return Scaffold(
      appBar: AppBar(title: const Text('حساب کاربری')),
      body: user == null
          ? _buildLoginPrompt(context)
          : _buildProfileInfo(context, ref, user),
    );
  }

  Widget _buildLoginPrompt(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.account_circle_outlined, size: 100, color: Colors.grey),
          const SizedBox(height: 16),
          const Text('شما وارد نشده‌اید'),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () {
              // Navigate to Login
            },
            child: const Text('ورود / ثبت نام'),
          ),
        ],
      ),
    );
  }

  Widget _buildProfileInfo(BuildContext context, WidgetRef ref, dynamic user) {
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        children: [
          const CircleAvatar(
            radius: 50,
            backgroundColor: Colors.blue,
            child: Icon(Icons.person, size: 60, color: Colors.white),
          ),
          const SizedBox(height: 16),
          Text(user.email ?? 'بدون ایمیل', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 32),
          const Divider(),
          ListTile(
            title: const Text('خریدهای من', textDirection: TextDirection.rtl),
            leading: const Icon(Icons.shopping_bag_outlined),
            onTap: () {},
          ),
          ListTile(
            title: const Text('آخرین مطالعه', textDirection: TextDirection.rtl),
            leading: const Icon(Icons.history),
            onTap: () {},
          ),
          ListTile(
            title: const Text('تنظیمات', textDirection: TextDirection.rtl),
            leading: const Icon(Icons.settings_outlined),
            onTap: () {},
          ),
          const Spacer(),
          TextButton.icon(
            onPressed: () => ref.read(authRepositoryProvider).signOut(),
            icon: const Icon(Icons.logout, color: Colors.red),
            label: const Text('خروج از حساب', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }
}
