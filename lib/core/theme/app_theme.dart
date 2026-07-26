import 'package:flutter/material.dart';

class AppTheme {
  // Brand colors
  static const Color primaryBlue = Color(0xFF0D47A1);
  static const Color accentGold = Color(0xFFFFD700);

  static const Color darkBackground = Color(0xFF121212);
  static const Color darkSurface = Color(0xFF1E1E1E);
  static const Color darkCard = Color(0xFF252525);

  static const Color lightBackground = Color(0xFFF5F7FA);
  static const Color lightSurface = Color(0xFFFFFFFF);
  static const Color lightCard = Color(0xFFEDF1F6);

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      primaryColor: primaryBlue,
      scaffoldBackgroundColor: darkBackground,
      colorScheme: const ColorScheme.dark(
        primary: primaryBlue,
        secondary: accentGold,
        surface: darkSurface,
        onPrimary: Colors.white,
        onSecondary: Colors.black,
        error: Color(0xFFCF6679),
      ),
      cardTheme: const CardThemeData(
        color: darkCard,
        elevation: 2,
        margin: EdgeInsets.symmetric(vertical: 6, horizontal: 8),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: darkSurface,
        elevation: 0,
        centerTitle: true,
        iconTheme: IconThemeData(color: Colors.white),
        titleTextStyle: TextStyle(
          fontFamily: 'Vazirmatn',
          fontSize: 18,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
      textTheme: TextTheme(
        headlineLarge: const TextStyle(fontFamily: 'Vazirmatn', fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white),
        headlineMedium: const TextStyle(fontFamily: 'Vazirmatn', fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
        titleLarge: const TextStyle(fontFamily: 'Vazirmatn', fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
        bodyLarge: TextStyle(fontFamily: 'Vazirmatn', fontSize: 16, color: Colors.white.withOpacity(0.9)),
        bodyMedium: const TextStyle(fontFamily: 'Vazirmatn', fontSize: 14, color: Colors.white70),
        labelLarge: const TextStyle(fontFamily: 'Vazirmatn', fontSize: 12, color: Colors.white60),
      ),
    );
  }

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      primaryColor: primaryBlue,
      scaffoldBackgroundColor: lightBackground,
      colorScheme: const ColorScheme.light(
        primary: primaryBlue,
        secondary: accentGold,
        surface: lightSurface,
        onPrimary: Colors.white,
        onSecondary: Colors.black,
        error: Color(0xFFB00020),
      ),
      cardTheme: const CardThemeData(
        color: lightCard,
        elevation: 1,
        margin: EdgeInsets.symmetric(vertical: 6, horizontal: 8),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: primaryBlue,
        elevation: 0,
        centerTitle: true,
        iconTheme: IconThemeData(color: Colors.white),
        titleTextStyle: TextStyle(
          fontFamily: 'Vazirmatn',
          fontSize: 18,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
      textTheme: TextTheme(
        headlineLarge: TextStyle(fontFamily: 'Vazirmatn', fontSize: 24, fontWeight: FontWeight.bold, color: Colors.black.withOpacity(0.8)),
        headlineMedium: TextStyle(fontFamily: 'Vazirmatn', fontSize: 20, fontWeight: FontWeight.bold, color: Colors.black.withOpacity(0.8)),
        titleLarge: TextStyle(fontFamily: 'Vazirmatn', fontSize: 18, fontWeight: FontWeight.bold, color: Colors.black.withOpacity(0.8)),
        bodyLarge: const TextStyle(fontFamily: 'Vazirmatn', fontSize: 16, color: Colors.black87),
        bodyMedium: const TextStyle(fontFamily: 'Vazirmatn', fontSize: 14, color: Colors.black54),
        labelLarge: const TextStyle(fontFamily: 'Vazirmatn', fontSize: 12, color: Colors.black45),
      ),
    );
  }
}
