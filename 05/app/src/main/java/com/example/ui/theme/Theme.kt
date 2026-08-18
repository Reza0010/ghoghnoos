package com.example.ui.theme

import android.os.Build
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Shapes
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.dp

// ==================== Color Scheme ====================

private val DedicatedDarkColorScheme = darkColorScheme(
    // Primary
    primary = CyberCyan,
    onPrimary = Color.Black,
    primaryContainer = CyanContainer,
    onPrimaryContainer = CyberCyan,

    // Secondary
    secondary = CyberEmerald,
    onSecondary = Color.Black,
    secondaryContainer = EmeraldContainer,
    onSecondaryContainer = CyberEmerald,

    // Tertiary
    tertiary = CyberAmber,
    onTertiary = Color.Black,
    tertiaryContainer = PurpleContainer,
    onTertiaryContainer = Color(0xFFE9D5FF),

    // Error
    error = CyberRed,
    onError = Color.White,
    errorContainer = Color(0xFF7F1D1D),
    onErrorContainer = Color(0xFFFECACA),

    // Background
    background = DarkBackground,
    onBackground = TextPrimary,

    // Surface
    surface = DarkSurface,
    onSurface = TextPrimary,
    surfaceVariant = DarkSurfaceVariant,
    onSurfaceVariant = TextSecondary,

    // Surface Containers (Material 3)
    surfaceContainerLowest = DarkBackground,
    surfaceContainerLow = DarkSurface,
    surfaceContainer = DarkSurfaceVariant,
    surfaceContainerHigh = Color(0xFF1E293B),
    surfaceContainerHighest = Color(0xFF253044),

    // Outline
    outline = DarkCardBorder,
    outlineVariant = Color(0xFF1E293B),

    // Inverse
    inverseSurface = Color(0xFFE2E8F0),
    inverseOnSurface = Color(0xFF0F172A),
    inversePrimary = Color(0xFF0891B2),

    // Scrim
    scrim = Color(0xFF000000),

    // Surface Tint
    surfaceTint = CyberCyan
)

// ==================== Shapes ====================

private val AppShapes = Shapes(
    extraSmall = RoundedCornerShape(4.dp),
    small = RoundedCornerShape(8.dp),
    medium = RoundedCornerShape(12.dp),
    large = RoundedCornerShape(16.dp),
    extraLarge = RoundedCornerShape(20.dp)
)

// ==================== Theme Composable ====================

@Composable
fun WhatsMinerScannerTheme(
    useDynamicColor: Boolean = false,
    content: @Composable () -> Unit
) {
    val colorScheme = if (useDynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        val context = LocalContext.current
        dynamicDarkColorScheme(context)
    } else {
        DedicatedDarkColorScheme
    }

    CompositionLocalProvider(
        LocalLayoutDirection provides LayoutDirection.Rtl
    ) {
        MaterialTheme(
            colorScheme = colorScheme,
            typography = Typography,
            shapes = AppShapes,
            content = content
        )
    }
}
