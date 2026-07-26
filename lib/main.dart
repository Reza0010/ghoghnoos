import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/theme/app_theme.dart';
import 'features/scanner/presentation/pages/scan_page.dart';
import 'features/ai_assistant/presentation/pages/ai_diagnostics_page.dart';
import 'features/repair_kb/presentation/pages/repair_kb_page.dart';

void main() {
  runApp(
    const ProviderScope(
      child: MinerRepairApp(),
    ),
  );
}

// Global Provider for Theme Mode Selection (Dark vs Light)
final themeModeProvider = StateProvider<ThemeMode>((ref) => ThemeMode.dark);

class MinerRepairApp extends ConsumerWidget {
  const MinerRepairApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeModeProvider);

    return MaterialApp(
      title: 'ماینر یار | عیب‌یاب هوشمند اسیک',
      debugShowCheckedModeBanner: false,

      // Theme settings
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: themeMode,

      // RTL & Persian configuration
      locale: const Locale('fa', 'IR'),
      supportedLocales: const [
        Locale('fa', 'IR'),
      ],
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],

      home: const MainNavigationScaffold(),
    );
  }
}

class MainNavigationScaffold extends StatefulWidget {
  const MainNavigationScaffold({super.key});

  @override
  State<MainNavigationScaffold> createState() => _MainNavigationScaffoldState();
}

class _MainNavigationScaffoldState extends State<MainNavigationScaffold> {
  int _currentIndex = 0;

  final List<Widget> _pages = const [
    ScanPage(),
    AiDiagnosticsPage(),
    RepairKbPage(),
  ];

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Scaffold(
      // Drawer for Theme Controls and general instructions
      drawer: _buildDrawer(context),
      body: _pages[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        selectedItemColor: const Color(0xFFFFD700), // Brand accent Gold
        unselectedItemColor: isDark ? Colors.white60 : Colors.black45,
        backgroundColor: isDark ? const Color(0xFF1E1E1E) : Colors.white,
        type: BottomNavigationBarType.fixed,
        selectedLabelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
        unselectedLabelStyle: const TextStyle(fontSize: 11),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dns),
            activeIcon: Icon(Icons.dns, color: Color(0xFFFFD700)),
            label: 'اسکنر شبکه',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.psychology),
            activeIcon: Icon(Icons.psychology, color: Color(0xFFFFD700)),
            label: 'عیب‌یابی AI',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.menu_book),
            activeIcon: Icon(Icons.menu_book, color: Color(0xFFFFD700)),
            label: 'دانشنامه خطا',
          ),
        ],
      ),
    );
  }

  Widget _buildDrawer(BuildContext context) {
    return Consumer(
      builder: (context, ref, child) {
        final themeMode = ref.watch(themeModeProvider);
        final isDark = themeMode == ThemeMode.dark;

        return Directionality(
          textDirection: TextDirection.rtl,
          child: Drawer(
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                DrawerHeader(
                  decoration: const BoxDecoration(
                    color: Color(0xFF0D47A1), // Brand primary blue
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Icon(
                              Icons.developer_board,
                              color: Color(0xFF0D47A1),
                              size: 32,
                            ),
                          ),
                          const SizedBox(width: 12),
                          const Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'ماینر یار',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                'نسخه ۱.۰.۰',
                                style: TextStyle(
                                  color: Colors.white70,
                                  fontSize: 11,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'دستیار تخصصی عیب‌یابی و تعمیرات اسیک',
                        style: TextStyle(color: Colors.white.withOpacity(0.9), fontSize: 11.5),
                      ),
                    ],
                  ),
                ),
                ListTile(
                  leading: const Icon(Icons.palette),
                  title: const Text('حالت تاریک (Dark Mode)'),
                  trailing: Switch(
                    value: isDark,
                    activeTrackColor: const Color(0xFFFFD700),
                    onChanged: (value) {
                      ref.read(themeModeProvider.notifier).state =
                          value ? ThemeMode.dark : ThemeMode.light;
                    },
                  ),
                ),
                const Divider(),
                const Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'درباره نرم‌افزار:',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                      ),
                      SizedBox(height: 8),
                      Text(
                        'این نرم‌افزار به صورت کاملاً بومی و اختصاصی برای عیب‌یابی عمیق کارت‌های پردازش تراهش (Hashboard) دستگاه‌های انت‌ماینر و واتس‌ماینر توسعه یافته است.',
                        style: TextStyle(fontSize: 12, height: 1.6, color: Colors.grey),
                      ),
                      SizedBox(height: 8),
                      Text(
                        'با استفاده از پروتکل‌های مانیتورینگ CGMiner و WhatsMiner API، اطلاعات دقیقی در سطوح تراشه اسیک استخراج و تحلیل می‌گردد.',
                        style: TextStyle(fontSize: 12, height: 1.6, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
