import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:firebase_core/firebase_core.dart';
import 'core/theme/app_theme.dart';
import 'features/home/presentation/pages/splash_screen.dart';
import 'features/auth/presentation/providers/auth_providers.dart';
import 'features/home/presentation/pages/home_page.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Note: For a real app, you MUST provide google-services.json for Android
  // and GoogleService-Info.plist for iOS and call Firebase.initializeApp().
  // Since I don't have those files, I will mock the initialization or skip for now.

  runApp(
    const ProviderScope(
      child: FixboardApp(),
    ),
  );
}

class FixboardApp extends ConsumerWidget {
  const FixboardApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp(
      title: 'Fixboard',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      home: const SplashScreen(),
    );
  }
}
