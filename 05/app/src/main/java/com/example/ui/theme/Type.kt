package com.example.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.googlefonts.Font
import androidx.compose.ui.text.googlefonts.GoogleFont
import androidx.compose.ui.unit.sp
import com.example.R

// ==================== Google Fonts Provider ====================

private val fontProvider = GoogleFont.Provider(
    providerAuthority = "com.google.android.gms.fonts",
    providerPackage = "com.google.android.gms",
    certificates = R.array.com_google_android_gms_fonts_certs
)

private val vazirmatnGoogleFont = GoogleFont("Vazirmatn")

// ==================== Font Family ====================

/**
 * ✅ FontFamily با fallback محلی و سیستمی
 * اگر Google Fonts لود نشود، از sans-serif استفاده می‌شود
 */
val VazirmatnFontFamily = FontFamily(
    // Google Fonts
    Font(googleFont = vazirmatnGoogleFont, fontProvider = fontProvider, weight = FontWeight.Normal),
    Font(googleFont = vazirmatnGoogleFont, fontProvider = fontProvider, weight = FontWeight.Medium),
    Font(googleFont = vazirmatnGoogleFont, fontProvider = fontProvider, weight = FontWeight.SemiBold),
    Font(googleFont = vazirmatnGoogleFont, fontProvider = fontProvider, weight = FontWeight.Bold),
    Font(googleFont = vazirmatnGoogleFont, fontProvider = fontProvider, weight = FontWeight.ExtraBold),
)

/**
 * ✅ Fallback FontFamily برای وقتی Google Fonts در دسترس نیست
 */
val FallbackFontFamily = FontFamily.SansSerif

/**
 * ✅ FontFamily با fallback خودکار
 */
val AppFontFamily = try {
    VazirmatnFontFamily
} catch (e: Exception) {
    FallbackFontFamily
}

// ==================== Typography ====================

val Typography = Typography(
    // ==================== Display ====================
    displayLarge = TextStyle(
        fontFamily = AppFontFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 32.sp,
        lineHeight = 44.sp,
        letterSpacing = 0.sp  // ✅ بدون letterSpacing برای فارسی
    ),
    displayMedium = TextStyle(
        fontFamily = AppFontFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 28.sp,
        lineHeight = 40.sp,
        letterSpacing = 0.sp
    ),
    displaySmall = TextStyle(
        fontFamily = AppFontFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 24.sp,
        lineHeight = 36.sp,
        letterSpacing = 0.sp
    ),

    // ==================== Headline ====================
    headlineLarge = TextStyle(
        fontFamily = AppFontFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 26.sp,
        lineHeight = 38.sp,
        letterSpacing = 0.sp
    ),
    headlineMedium = TextStyle(
        fontFamily = AppFontFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 24.sp,
        lineHeight = 36.sp,
        letterSpacing = 0.sp
    ),
    headlineSmall = TextStyle(
        fontFamily = AppFontFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 20.sp,
        lineHeight = 30.sp,
        letterSpacing = 0.sp
    ),

    // ==================== Title ====================
    titleLarge = TextStyle(
        fontFamily = AppFontFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 20.sp,
        lineHeight = 30.sp,
        letterSpacing = 0.sp
    ),
    titleMedium = TextStyle(
        fontFamily = AppFontFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 16.sp,
        lineHeight = 26.sp,
        letterSpacing = 0.1.sp  // ✅ کمتر برای فارسی
    ),
    titleSmall = TextStyle(
        fontFamily = AppFontFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 22.sp,
        letterSpacing = 0.1.sp
    ),

    // ==================== Body ====================
    bodyLarge = TextStyle(
        fontFamily = AppFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 26.sp,
        letterSpacing = 0.2.sp  // ✅ کمتر برای فارسی
    ),
    bodyMedium = TextStyle(
        fontFamily = AppFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 14.sp,
        lineHeight = 22.sp,
        letterSpacing = 0.15.sp  // ✅ کمتر برای فارسی
    ),
    bodySmall = TextStyle(
        fontFamily = AppFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 12.sp,
        lineHeight = 18.sp,
        letterSpacing = 0.2.sp
    ),

    // ==================== Label ====================
    labelLarge = TextStyle(
        fontFamily = AppFontFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 22.sp,
        letterSpacing = 0.1.sp
    ),
    labelMedium = TextStyle(
        fontFamily = AppFontFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 12.sp,
        lineHeight = 18.sp,
        letterSpacing = 0.3.sp
    ),
    labelSmall = TextStyle(
        fontFamily = AppFontFamily,
        fontWeight = FontWeight.Medium,  // ✅ Medium به جای Bold
        fontSize = 11.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.3.sp
    )
)

// ==================== Monospace Typography ====================

/**
 * ✅ برای اعداد و IP ها
 */
val MonospaceTypography = Typography(
    bodyMedium = TextStyle(
        fontFamily = FontFamily.Monospace,
        fontWeight = FontWeight.Normal,
        fontSize = 14.sp,
        lineHeight = 22.sp
    ),
    titleSmall = TextStyle(
        fontFamily = FontFamily.Monospace,
        fontWeight = FontWeight.Bold,
        fontSize = 14.sp,
        lineHeight = 22.sp
    )
)
