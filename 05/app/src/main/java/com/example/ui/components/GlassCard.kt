package com.example.ui.components

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.example.ui.theme.CyberCyan
import com.example.ui.theme.CyberEmerald
import com.example.ui.theme.GlassGradientEnd
import com.example.ui.theme.GlassGradientStart
import com.example.ui.theme.NeonGradientEnd
import com.example.ui.theme.NeonGradientStart

/**
 * کارت شیشه‌ای با افکت شفافیت و حاشیه نئون
 */
@OptIn(ExperimentalFoundationApi::class)
@Composable
fun GlassmorphicCard(
    modifier: Modifier = Modifier,
    shape: Shape = RoundedCornerShape(16.dp),
    glowColor: Color = CyberCyan,
    borderColor: Color = glowColor.copy(alpha = 0.4f),
    borderWidth: Dp = 1.dp,
    contentDescription: String? = null,
    onClick: (() -> Unit)? = null,
    onLongClick: (() -> Unit)? = null,
    content: @Composable BoxScope.() -> Unit
) {
    Card(
        shape = shape,
        colors = CardDefaults.cardColors(containerColor = Color.Transparent),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp),
        modifier = modifier
            .then(
                if (onClick != null || onLongClick != null) {
                    Modifier
                        .semantics {
                            role = Role.Button
                            contentDescription?.let { this.contentDescription = it }
                        }
                        .combinedClickable(
                            onClick = onClick ?: {},
                            onLongClick = onLongClick
                        )
                } else Modifier
            )
            .clip(shape)
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        GlassGradientStart.copy(alpha = 0.85f),
                        GlassGradientEnd.copy(alpha = 0.95f)
                    )
                ),
                shape = shape
            )
            .border(
                width = borderWidth,
                brush = Brush.linearGradient(
                    colors = listOf(
                        borderColor,
                        borderColor.copy(alpha = 0.15f),
                        glowColor.copy(alpha = 0.3f)
                    )
                ),
                shape = shape
            )
    ) {
        Box(modifier = Modifier) {
            content()
        }
    }
}

/**
 * کارت با افکت نئون و انیمیشن Glow
 */
@Composable
fun NeonGlowCard(
    modifier: Modifier = Modifier,
    shape: Shape = RoundedCornerShape(16.dp),
    primaryGlow: Color = CyberCyan,
    secondaryGlow: Color = CyberEmerald,
    animateGlow: Boolean = true,
    borderWidth: Dp = 1.5.dp,
    contentDescription: String? = null,
    onClick: (() -> Unit)? = null,
    content: @Composable BoxScope.() -> Unit
) {
    val alphaAnim: Float = if (animateGlow) {
        val infiniteTransition = rememberInfiniteTransition(label = "neonGlow")
        val animatedValue by infiniteTransition.animateFloat(
            initialValue = 0.3f,
            targetValue = 0.8f,
            animationSpec = infiniteRepeatable(
                animation = tween(1800, easing = FastOutSlowInEasing),
                repeatMode = RepeatMode.Reverse
            ),
            label = "borderAlpha"
        )
        animatedValue
    } else {
        remember { 0.5f }
    }

    Card(
        shape = shape,
        colors = CardDefaults.cardColors(containerColor = Color.Transparent),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp),
        modifier = modifier
            .then(
                if (onClick != null) {
                    Modifier
                        .semantics {
                            role = Role.Button
                            contentDescription?.let { this.contentDescription = it }
                        }
                        .clickable(onClick = onClick)
                } else Modifier
            )
            .clip(shape)
            .background(
                brush = Brush.linearGradient(
                    colors = listOf(
                        NeonGradientStart.copy(alpha = 0.92f),
                        NeonGradientEnd.copy(alpha = 0.98f)
                    )
                ),
                shape = shape
            )
            .border(
                width = borderWidth,
                brush = Brush.sweepGradient(
                    colors = listOf(
                        primaryGlow.copy(alpha = alphaAnim),
                        secondaryGlow.copy(alpha = alphaAnim * 0.7f),
                        primaryGlow.copy(alpha = alphaAnim)
                    )
                ),
                shape = shape
            )
    ) {
        Box(modifier = Modifier) {
            content()
        }
    }
}
