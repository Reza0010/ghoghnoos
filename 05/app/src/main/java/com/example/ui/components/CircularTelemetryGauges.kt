package com.example.ui.components

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Air
import androidx.compose.material.icons.filled.FlashOn
import androidx.compose.material.icons.filled.ReportProblem
import androidx.compose.material.icons.filled.ShowChart
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material.icons.filled.Thermostat
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.CyberAmber
import com.example.ui.theme.CyberCyan
import com.example.ui.theme.CyberEmerald
import com.example.ui.theme.CyberPurple
import com.example.ui.theme.CyberRed
import com.example.ui.theme.DarkSurfaceVariant
import com.example.ui.theme.TextMuted
import com.example.ui.theme.TextPrimary
import java.util.Locale
import kotlin.math.cos
import kotlin.math.sin

// ==================== Constants ====================

private const val START_ANGLE = 140f
private const val MAX_SWEEP_ANGLE = 260f
private const val ANIMATION_DURATION_MS = 800

// ==================== Sparkline Mini-Chart ====================

/**
 * 📈 Sparkline Mini-Chart
 * نمودار نوسان آنی و لحظه‌ای با گرادینت نئونی و نقطه متحرک پایانی
 */
@Composable
fun SparklineMiniChart(
    points: List<Float>,
    lineColor: Color,
    glowColor: Color = lineColor,
    modifier: Modifier = Modifier,
    height: Dp = 22.dp,
    showGradientFill: Boolean = true
) {
    if (points.isEmpty()) return

    val minVal = points.minOrNull() ?: 0f
    val maxVal = points.maxOrNull() ?: 1f
    val range = if (maxVal - minVal < 0.001f) 1f else (maxVal - minVal)

    val infiniteTransition = rememberInfiniteTransition(label = "sparklinePulse")
    val pulseAlpha by infiniteTransition.animateFloat(
        initialValue = 0.35f,
        targetValue = 0.95f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "sparklinePulse"
    )

    Canvas(
        modifier = modifier
            .fillMaxWidth()
            .height(height)
    ) {
        val w = size.width
        val h = size.height
        val stepX = if (points.size > 1) w / (points.size - 1) else w

        val path = Path()
        val fillPath = Path()

        points.forEachIndexed { i, pt ->
            val x = i * stepX
            val normY = (pt - minVal) / range
            // Invert Y axis with top/bottom padding
            val y = (h - 3.dp.toPx()) - (normY * (h - 6.dp.toPx())) - 2.dp.toPx()

            if (i == 0) {
                path.moveTo(x, y)
                fillPath.moveTo(x, h)
                fillPath.lineTo(x, y)
            } else {
                val prevX = (i - 1) * stepX
                val prevPt = points[i - 1]
                val prevNormY = (prevPt - minVal) / range
                val prevY = (h - 3.dp.toPx()) - (prevNormY * (h - 6.dp.toPx())) - 2.dp.toPx()

                val controlX1 = prevX + stepX * 0.5f
                val controlY1 = prevY
                val controlX2 = prevX + stepX * 0.5f
                val controlY2 = y

                path.cubicTo(controlX1, controlY1, controlX2, controlY2, x, y)
                fillPath.cubicTo(controlX1, controlY1, controlX2, controlY2, x, y)
            }

            if (i == points.lastIndex) {
                fillPath.lineTo(x, h)
                fillPath.close()

                // Live Glowing Head Point
                drawCircle(
                    color = glowColor.copy(alpha = pulseAlpha * 0.8f),
                    radius = 4.dp.toPx(),
                    center = Offset(x, y)
                )
                drawCircle(
                    color = Color.White,
                    radius = 2.dp.toPx(),
                    center = Offset(x, y)
                )
            }
        }

        if (showGradientFill) {
            drawPath(
                path = fillPath,
                brush = Brush.verticalGradient(
                    colors = listOf(
                        lineColor.copy(alpha = 0.40f),
                        lineColor.copy(alpha = 0.08f),
                        Color.Transparent
                    )
                )
            )
        }

        drawPath(
            path = path,
            color = lineColor,
            style = Stroke(width = 2.dp.toPx(), cap = StrokeCap.Round)
        )
    }
}

/**
 * تولید خودکار یا حفظ نوسانات آنی هماهنگ برای Sparkline
 */
@Composable
fun rememberSparklineHistory(currentVal: Float, sampleCount: Int = 10, seedOffset: Int = 0): List<Float> {
    return remember(currentVal, seedOffset) {
        if (currentVal <= 0f) {
            List(sampleCount) { 0f }
        } else {
            val list = mutableListOf<Float>()
            var v = currentVal * 0.95f
            val stepVariation = currentVal * 0.022f
            repeat(sampleCount - 1) { idx ->
                val delta = (sin((idx + seedOffset) * 0.9) * stepVariation).toFloat()
                v = (v + delta).coerceIn(currentVal * 0.82f, currentVal * 1.18f)
                list.add(v)
            }
            list.add(currentVal) // آخرین نقطه مقدار دقیق لحظه‌ای
            list
        }
    }
}

// ==================== Shared Radial Arc Gauge Drawing ====================

/**
 * ⭕ رسم پیشرفته گیج دایره‌ای آرک به همراه:
 * ۱. خطوط درجه‌بندی شعاعی (Radial Ticks)
 * ۲. هاله درخشان نئونی (Neon Glow Arc)
 * ۳. گرادینت نئونی فعال (Active Neon Sweep Gradient)
 * ۴. نشانگر درخشان رأس انیمیشنی (Pulsing Tip Indicator)
 */
private fun DrawScope.drawGaugeArc(
    progress: Float,
    gaugeSize: Dp,
    strokeWidthPx: Float,
    trackColor: Color,
    activeBrush: Brush,
    glowColor: Color? = null,
    pulseAlpha: Float = 0.3f,
    showTicks: Boolean = true,
    targetProgress: Float? = null
) {
    val sizePx = gaugeSize.toPx()
    val radius = (sizePx - strokeWidthPx * 2.4f) / 2f
    val center = Offset(sizePx / 2f, sizePx / 2f)
    val topLeft = Offset((sizePx - radius * 2f) / 2f, (sizePx - radius * 2f) / 2f)
    val arcSize = Size(radius * 2f, radius * 2f)

    val activeSweep = progress * MAX_SWEEP_ANGLE

    // ۱. Radial Ticks Graduation Lines
    if (showTicks) {
        val tickCount = 21
        val tickInnerRadius = radius + strokeWidthPx * 0.7f
        val tickOuterLengthMajor = strokeWidthPx * 0.45f
        val tickOuterLengthMinor = strokeWidthPx * 0.25f

        for (i in 0 until tickCount) {
            val tickAngle = START_ANGLE + (i.toFloat() / (tickCount - 1)) * MAX_SWEEP_ANGLE
            val isMajor = i % 5 == 0
            val tickLen = if (isMajor) tickOuterLengthMajor else tickOuterLengthMinor
            val angleRad = Math.toRadians(tickAngle.toDouble())

            val startX = center.x + tickInnerRadius * cos(angleRad).toFloat()
            val startY = center.y + tickInnerRadius * sin(angleRad).toFloat()
            val endX = center.x + (tickInnerRadius + tickLen) * cos(angleRad).toFloat()
            val endY = center.y + (tickInnerRadius + tickLen) * sin(angleRad).toFloat()

            val isPassed = tickAngle <= (START_ANGLE + activeSweep)
            val tickColor = if (isPassed && glowColor != null) {
                glowColor.copy(alpha = if (isMajor) 0.85f else 0.5f)
            } else {
                trackColor.copy(alpha = if (isMajor) 0.5f else 0.25f)
            }

            drawLine(
                color = tickColor,
                start = Offset(startX, startY),
                end = Offset(endX, endY),
                strokeWidth = if (isMajor) 2.dp.toPx() else 1.dp.toPx(),
                cap = StrokeCap.Round
            )
        }
    }

    // ۲. Background Base Track Arc
    drawArc(
        color = trackColor,
        startAngle = START_ANGLE,
        sweepAngle = MAX_SWEEP_ANGLE,
        useCenter = false,
        topLeft = topLeft,
        size = arcSize,
        style = Stroke(width = strokeWidthPx, cap = StrokeCap.Round)
    )

    // ۳. Target Indicator Notch Marker
    if (targetProgress != null && targetProgress in 0f..1f) {
        val targetSweep = targetProgress * MAX_SWEEP_ANGLE
        val targetAngleRad = Math.toRadians((START_ANGLE + targetSweep).toDouble())
        val innerR = radius - strokeWidthPx * 0.75f
        val outerR = radius + strokeWidthPx * 0.75f
        val startX = center.x + innerR * cos(targetAngleRad).toFloat()
        val startY = center.y + innerR * sin(targetAngleRad).toFloat()
        val endX = center.x + outerR * cos(targetAngleRad).toFloat()
        val endY = center.y + outerR * sin(targetAngleRad).toFloat()

        drawLine(
            color = Color.White,
            start = Offset(startX, startY),
            end = Offset(endX, endY),
            strokeWidth = 2.5.dp.toPx(),
            cap = StrokeCap.Round
        )
    }

    // ۴. Active Progress Arc with Neon Sweep Gradient
    if (activeSweep > 0f) {
        // Pulsing Glow Aura Halo behind arc
        if (glowColor != null) {
            drawArc(
                color = glowColor.copy(alpha = pulseAlpha * 0.55f),
                startAngle = START_ANGLE,
                sweepAngle = activeSweep,
                useCenter = false,
                topLeft = Offset(topLeft.x - strokeWidthPx * 0.3f, topLeft.y - strokeWidthPx * 0.3f),
                size = Size(arcSize.width + strokeWidthPx * 0.6f, arcSize.height + strokeWidthPx * 0.6f),
                style = Stroke(width = strokeWidthPx * 1.5f, cap = StrokeCap.Round)
            )
        }

        // Core Active Arc
        drawArc(
            brush = activeBrush,
            startAngle = START_ANGLE,
            sweepAngle = activeSweep,
            useCenter = false,
            topLeft = topLeft,
            size = arcSize,
            style = Stroke(width = strokeWidthPx, cap = StrokeCap.Round)
        )

        // ۵. Live Glowing Tip Indicator Dot with Pulse Aura
        val endAngleRad = Math.toRadians((START_ANGLE + activeSweep).toDouble())
        val tipX = center.x + radius * cos(endAngleRad).toFloat()
        val tipY = center.y + radius * sin(endAngleRad).toFloat()
        val tipPos = Offset(tipX, tipY)

        val tipColor = glowColor ?: CyberCyan
        // Outer pulsing aura
        drawCircle(
            color = tipColor.copy(alpha = pulseAlpha * 0.85f),
            radius = strokeWidthPx * 0.95f,
            center = tipPos
        )
        // Middle neon ring
        drawCircle(
            color = tipColor,
            radius = strokeWidthPx * 0.6f,
            center = tipPos
        )
        // Center white hot spot
        drawCircle(
            color = Color.White,
            radius = strokeWidthPx * 0.35f,
            center = tipPos
        )
    }
}

// ==================== Temperature Radial Arc Gauge ====================

/**
 * 🌡️ گیج دایره‌ای آرک دما با نوسان آنی Sparkline و حالت هشدارهای دیداری متمایز
 */
@Composable
fun CircularTemperatureGauge(
    temperatureC: Double,
    maxTempC: Double = 100.0,
    history: List<Float>? = null,
    modifier: Modifier = Modifier,
    gaugeSize: Dp = 140.dp,
    size: Dp = gaugeSize
) {
    val actualSize = if (size != 140.dp) size else gaugeSize
    val tempClamped = temperatureC.coerceIn(0.0, maxTempC).toFloat()
    val progress = (tempClamped / maxTempC.toFloat()).coerceIn(0f, 1f)
    val animatedProgress by animateFloatAsState(
        targetValue = progress,
        animationSpec = tween(durationMillis = ANIMATION_DURATION_MS, easing = FastOutSlowInEasing),
        label = "tempProgress"
    )

    // Alert & Danger Thresholds
    val isCriticalAlert = temperatureC >= 84.0
    val isWarningAlert = temperatureC >= 75.0 && !isCriticalAlert

    // Animated Pulse & Hazard Flashing
    val infiniteTransition = rememberInfiniteTransition(label = "tempPulse")
    val pulseAlpha by infiniteTransition.animateFloat(
        initialValue = if (isCriticalAlert) 0.4f else 0.25f,
        targetValue = if (isCriticalAlert) 0.95f else 0.65f,
        animationSpec = infiniteRepeatable(
            animation = tween(if (isCriticalAlert) 450 else 1200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulseAlpha"
    )

    val gaugeColor = remember(temperatureC) {
        when {
            temperatureC <= 0 -> TextMuted
            temperatureC < 75.0 -> CyberEmerald
            temperatureC < 84.0 -> CyberAmber
            else -> CyberRed
        }
    }

    val statusText = remember(temperatureC) {
        when {
            temperatureC <= 0 -> "نامشخص"
            temperatureC < 75.0 -> "نرمال"
            temperatureC < 84.0 -> "⚠️ هشدار دما"
            else -> "🚨 حرارت بالا!"
        }
    }

    val tempDisplayText = remember(temperatureC) {
        if (temperatureC > 0) String.format(Locale.US, "%.1f°C", temperatureC) else "--"
    }

    val defaultHistory = rememberSparklineHistory(currentVal = temperatureC.toFloat(), seedOffset = 1)
    val activeHistory = history ?: defaultHistory

    Box(
        contentAlignment = Alignment.Center,
        modifier = modifier
            .size(actualSize)
            .padding(2.dp)
            .then(
                if (isCriticalAlert) {
                    Modifier.border(
                        width = 1.5.dp,
                        brush = Brush.sweepGradient(listOf(CyberRed, Color.White, CyberRed)),
                        shape = RoundedCornerShape(16.dp)
                    )
                } else Modifier
            )
            .semantics {
                contentDescription = "دمای ماینر: $tempDisplayText، وضعیت: $statusText"
            }
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val strokeWidth = (actualSize.toPx() * 0.075f).coerceIn(8.dp.toPx(), 12.dp.toPx())
            val targetProg = (75.0 / maxTempC).coerceIn(0.0, 1.0).toFloat()
            drawGaugeArc(
                progress = animatedProgress,
                gaugeSize = actualSize,
                strokeWidthPx = strokeWidth,
                trackColor = DarkSurfaceVariant,
                activeBrush = Brush.sweepGradient(
                    colors = if (isCriticalAlert) {
                        listOf(CyberRed, CyberAmber, CyberRed)
                    } else {
                        listOf(CyberEmerald, CyberAmber, CyberRed)
                    }
                ),
                glowColor = if (temperatureC > 0) gaugeColor else null,
                pulseAlpha = if (temperatureC > 0) pulseAlpha else 0f,
                targetProgress = targetProg
            )
        }

        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
            modifier = Modifier.padding(horizontal = 10.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = if (isCriticalAlert) Icons.Default.Warning else Icons.Default.Thermostat,
                    contentDescription = null,
                    tint = gaugeColor,
                    modifier = Modifier.size(if (isCriticalAlert) 18.dp else 16.dp)
                )
                if (isCriticalAlert) {
                    Spacer(modifier = Modifier.width(2.dp))
                    Text(
                        text = "ALERT",
                        style = MaterialTheme.typography.labelSmall.copy(fontSize = 9.sp),
                        color = CyberRed,
                        fontWeight = FontWeight.Black
                    )
                }
            }

            Text(
                text = tempDisplayText,
                style = MaterialTheme.typography.titleLarge.copy(
                    fontWeight = FontWeight.Bold,
                    fontSize = if (actualSize < 130.dp) 16.sp else 19.sp
                ),
                fontFamily = FontFamily.Monospace,
                color = if (isCriticalAlert) CyberRed else TextPrimary,
                textAlign = TextAlign.Center
            )

            // Distinct Visual Alert Badge
            Surface(
                shape = RoundedCornerShape(8.dp),
                color = gaugeColor.copy(alpha = if (isCriticalAlert) 0.25f else 0.15f),
                border = androidx.compose.foundation.BorderStroke(
                    0.8.dp, gaugeColor.copy(alpha = if (isCriticalAlert) pulseAlpha else 0.4f)
                )
            ) {
                Text(
                    text = statusText,
                    style = MaterialTheme.typography.labelSmall.copy(fontSize = 8.5.sp),
                    color = gaugeColor,
                    fontWeight = FontWeight.Bold,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(horizontal = 5.dp, vertical = 1.5.dp)
                )
            }

            // 📈 Sparkline Mini-Chart (نوسان آنی زیر گیج)
            if (temperatureC > 0) {
                Spacer(modifier = Modifier.height(2.dp))
                SparklineMiniChart(
                    points = activeHistory,
                    lineColor = gaugeColor,
                    glowColor = if (isCriticalAlert) CyberRed else gaugeColor,
                    height = 16.dp,
                    modifier = Modifier
                        .fillMaxWidth(0.70f)
                        .clip(RoundedCornerShape(4.dp))
                )
            }
        }
    }
}

// ==================== Hashrate Radial Arc Gauge ====================

/**
 * ⚡ گیج دایره‌ای آرک هش‌ریت با گرادینت نئونی، Sparkline نوسان آنی و حالت هشدارهای متمایز
 */
@Composable
fun CircularHashrateGauge(
    hashrateThs: Double,
    targetHashrateThs: Double = 110.0,
    history: List<Float>? = null,
    modifier: Modifier = Modifier,
    gaugeSize: Dp = 140.dp,
    size: Dp = gaugeSize
) {
    val actualSize = if (size != 140.dp) size else gaugeSize
    val progress = if (targetHashrateThs > 0) {
        (hashrateThs / targetHashrateThs).coerceIn(0.0, 1.0).toFloat()
    } else 0f

    val animatedProgress by animateFloatAsState(
        targetValue = progress,
        animationSpec = tween(durationMillis = ANIMATION_DURATION_MS, easing = FastOutSlowInEasing),
        label = "hashrateProgress"
    )

    val isOffline = hashrateThs <= 0
    val isLowHashrate = !isOffline && (hashrateThs < targetHashrateThs * 0.7)

    // Infinite transition for micro-animation pulse
    val infiniteTransition = rememberInfiniteTransition(label = "hashratePulse")
    val pulseAlpha by infiniteTransition.animateFloat(
        initialValue = if (isOffline) 0.5f else 0.3f,
        targetValue = if (isOffline) 0.95f else 0.75f,
        animationSpec = infiniteRepeatable(
            animation = tween(if (isOffline) 500 else 1500, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulseAlpha"
    )

    val gaugeColor = remember(hashrateThs, isOffline, isLowHashrate) {
        when {
            isOffline -> CyberRed
            isLowHashrate -> CyberAmber
            else -> CyberCyan
        }
    }

    val statusText = remember(isOffline, isLowHashrate) {
        when {
            isOffline -> "🚨 قطع هش"
            isLowHashrate -> "⚠️ افت توان"
            else -> "پایدار"
        }
    }

    val hashrateDisplayText = remember(hashrateThs) {
        if (hashrateThs > 0) String.format(Locale.US, "%.1f", hashrateThs) else "0.0"
    }

    val defaultHistory = rememberSparklineHistory(currentVal = hashrateThs.toFloat(), seedOffset = 2)
    val activeHistory = history ?: defaultHistory

    Box(
        contentAlignment = Alignment.Center,
        modifier = modifier
            .size(actualSize)
            .padding(2.dp)
            .then(
                if (isOffline) {
                    Modifier.border(
                        width = 1.2.dp,
                        color = CyberRed.copy(alpha = pulseAlpha),
                        shape = RoundedCornerShape(16.dp)
                    )
                } else Modifier
            )
            .semantics {
                contentDescription = "هش‌ریت ماینر: $hashrateDisplayText تراهش بر ثانیه، وضعیت: $statusText"
            }
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val strokeWidth = (actualSize.toPx() * 0.075f).coerceIn(8.dp.toPx(), 12.dp.toPx())
            val targetProg = 0.85f
            drawGaugeArc(
                progress = animatedProgress,
                gaugeSize = actualSize,
                strokeWidthPx = strokeWidth,
                trackColor = DarkSurfaceVariant,
                activeBrush = Brush.sweepGradient(
                    colors = if (isOffline) {
                        listOf(CyberRed, CyberAmber, CyberRed)
                    } else {
                        listOf(CyberCyan, CyberEmerald, CyberCyan)
                    }
                ),
                glowColor = gaugeColor,
                pulseAlpha = pulseAlpha,
                targetProgress = targetProg
            )
        }

        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
            modifier = Modifier.padding(horizontal = 10.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = if (isOffline) Icons.Default.ReportProblem else Icons.Default.Speed,
                    contentDescription = null,
                    tint = gaugeColor,
                    modifier = Modifier.size(16.dp)
                )
                if (isOffline) {
                    Spacer(modifier = Modifier.width(2.dp))
                    Text(
                        text = "OFFLINE",
                        style = MaterialTheme.typography.labelSmall.copy(fontSize = 8.5.sp),
                        color = CyberRed,
                        fontWeight = FontWeight.Bold
                    )
                }
            }

            Text(
                text = hashrateDisplayText,
                style = MaterialTheme.typography.titleLarge.copy(
                    fontWeight = FontWeight.Bold,
                    fontSize = if (actualSize < 130.dp) 16.sp else 19.sp
                ),
                fontFamily = FontFamily.Monospace,
                color = if (isOffline) CyberRed else TextPrimary,
                textAlign = TextAlign.Center
            )

            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "TH/s",
                    style = MaterialTheme.typography.labelSmall.copy(fontSize = 9.sp),
                    color = CyberCyan,
                    fontWeight = FontWeight.Bold,
                    textAlign = TextAlign.Center
                )
                Spacer(modifier = Modifier.width(4.dp))
                Surface(
                    shape = RoundedCornerShape(6.dp),
                    color = gaugeColor.copy(alpha = 0.15f),
                    border = androidx.compose.foundation.BorderStroke(0.5.dp, gaugeColor.copy(alpha = 0.4f))
                ) {
                    Text(
                        text = statusText,
                        style = MaterialTheme.typography.labelSmall.copy(fontSize = 8.sp),
                        color = gaugeColor,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 4.dp, vertical = 1.dp)
                    )
                }
            }

            // 📈 Sparkline Mini-Chart (نوسان آنی لحظه‌ای)
            if (hashrateThs > 0) {
                Spacer(modifier = Modifier.height(2.dp))
                SparklineMiniChart(
                    points = activeHistory,
                    lineColor = gaugeColor,
                    glowColor = gaugeColor,
                    height = 16.dp,
                    modifier = Modifier
                        .fillMaxWidth(0.70f)
                        .clip(RoundedCornerShape(4.dp))
                )
            }
        }
    }
}

// ==================== Fan & Power Radial Arc Gauge ====================

/**
 * 🌀 گیج دایره‌ای آرک فن و برق با گرادینت نئونی، آیکون چرخان و Sparkline نوسان آنی
 */
@Composable
fun CircularFanPowerGauge(
    fanRpm: Int,
    powerWatts: Int,
    maxFanRpm: Int = 7000,
    history: List<Float>? = null,
    modifier: Modifier = Modifier,
    gaugeSize: Dp = 140.dp,
    size: Dp = gaugeSize
) {
    val actualSize = if (size != 140.dp) size else gaugeSize
    val rpmProgress = if (maxFanRpm > 0) {
        (fanRpm.toFloat() / maxFanRpm).coerceIn(0f, 1f)
    } else 0f

    val animatedRpm by animateFloatAsState(
        targetValue = rpmProgress,
        animationSpec = tween(durationMillis = ANIMATION_DURATION_MS, easing = FastOutSlowInEasing),
        label = "rpmProgress"
    )

    val isFanWarning = (fanRpm > 0 && fanRpm < 2000) || fanRpm > 6500

    // Animated Fan Rotation
    val infiniteTransition = rememberInfiniteTransition(label = "fanSpin")
    val fanRotation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(if (fanRpm > 4000) 700 else 1600, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "fanRotation"
    )
    val pulseAlpha by infiniteTransition.animateFloat(
        initialValue = 0.25f,
        targetValue = 0.65f,
        animationSpec = infiniteRepeatable(
            animation = tween(1400, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "fanPulse"
    )

    val fanDisplayText = remember(fanRpm) {
        if (fanRpm > 0) String.format(Locale.US, "%d RPM", fanRpm) else "--"
    }

    val powerDisplayText = remember(powerWatts) {
        if (powerWatts > 0) String.format(Locale.US, "%d W", powerWatts) else "--"
    }

    val defaultHistory = rememberSparklineHistory(currentVal = fanRpm.toFloat(), seedOffset = 3)
    val activeHistory = history ?: defaultHistory

    val gaugeColor = if (isFanWarning) CyberAmber else CyberPurple

    Box(
        contentAlignment = Alignment.Center,
        modifier = modifier
            .size(actualSize)
            .padding(2.dp)
            .semantics {
                contentDescription = "سرعت فن: $fanDisplayText، توان مصرفی: $powerDisplayText"
            }
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val strokeWidth = (actualSize.toPx() * 0.075f).coerceIn(8.dp.toPx(), 12.dp.toPx())
            drawGaugeArc(
                progress = animatedRpm,
                gaugeSize = actualSize,
                strokeWidthPx = strokeWidth,
                trackColor = DarkSurfaceVariant,
                activeBrush = Brush.sweepGradient(
                    colors = if (isFanWarning) {
                        listOf(CyberAmber, CyberRed, CyberAmber)
                    } else {
                        listOf(CyberPurple, CyberCyan, CyberPurple)
                    }
                ),
                glowColor = if (fanRpm > 0) gaugeColor else null,
                pulseAlpha = if (fanRpm > 0) pulseAlpha else 0f
            )
        }

        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
            modifier = Modifier.padding(horizontal = 8.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Default.Air,
                    contentDescription = null,
                    tint = gaugeColor,
                    modifier = Modifier
                        .size(15.dp)
                        .rotate(if (fanRpm > 0) fanRotation else 0f)
                )
                Spacer(modifier = Modifier.width(3.dp))
                Text(
                    text = fanDisplayText,
                    style = MaterialTheme.typography.titleSmall.copy(
                        fontWeight = FontWeight.Bold,
                        fontSize = if (actualSize < 130.dp) 11.5.sp else 13.sp
                    ),
                    fontFamily = FontFamily.Monospace,
                    color = TextPrimary,
                    textAlign = TextAlign.Center
                )
            }

            Spacer(modifier = Modifier.height(2.dp))

            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Default.FlashOn,
                    contentDescription = null,
                    tint = CyberAmber,
                    modifier = Modifier.size(14.dp)
                )
                Spacer(modifier = Modifier.width(3.dp))
                Text(
                    text = powerDisplayText,
                    style = MaterialTheme.typography.titleSmall.copy(
                        fontWeight = FontWeight.Bold,
                        fontSize = if (actualSize < 130.dp) 11.5.sp else 13.sp
                    ),
                    fontFamily = FontFamily.Monospace,
                    color = CyberAmber,
                    textAlign = TextAlign.Center
                )
            }

            // 📈 Sparkline Mini-Chart (نوسان آنی دور فن)
            if (fanRpm > 0) {
                Spacer(modifier = Modifier.height(3.dp))
                SparklineMiniChart(
                    points = activeHistory,
                    lineColor = gaugeColor,
                    glowColor = CyberPurple,
                    height = 15.dp,
                    modifier = Modifier
                        .fillMaxWidth(0.68f)
                        .clip(RoundedCornerShape(4.dp))
                )
            }
        }
    }
}

// ==================== Advanced Dual-Arc Hashrate Gauge ====================

/**
 * ⚡ گیج دو-محوره پیشرفته (Advanced Dual-Arc / Dual-Track Gauge)
 * نمایش همزمان:
 * ۱. کمان بیرونی (Outer Arc): هش‌ریت زنده و لحظه‌ای با درخشش نئونی فیروزه‌ای
 * ۲. کمان داخلی (Inner Arc): میانگین یا هدف هش‌ریت با رنگ بنفش/نارنجی نئونی
 * ۳. نشانگر روند نوسان (Trend Delta Badge) با درصد تغییرات (مثلاً ▲ +۴.۲٪ یا ▼ -۲.۱٪)
 */
@Composable
fun CircularDualArcHashrateGauge(
    liveHashrateThs: Double,
    avgHashrateThs: Double,
    maxHashrateThs: Double = 120.0,
    history: List<Float>? = null,
    modifier: Modifier = Modifier,
    gaugeSize: Dp = 140.dp,
    size: Dp = gaugeSize
) {
    val actualSize = if (size != 140.dp) size else gaugeSize

    val liveProgress = if (maxHashrateThs > 0) (liveHashrateThs / maxHashrateThs).coerceIn(0.0, 1.0).toFloat() else 0f
    val avgProgress = if (maxHashrateThs > 0) (avgHashrateThs / maxHashrateThs).coerceIn(0.0, 1.0).toFloat() else 0f

    val animatedLiveProgress by animateFloatAsState(
        targetValue = liveProgress,
        animationSpec = tween(durationMillis = ANIMATION_DURATION_MS, easing = FastOutSlowInEasing),
        label = "liveProgress"
    )

    val animatedAvgProgress by animateFloatAsState(
        targetValue = avgProgress,
        animationSpec = tween(durationMillis = ANIMATION_DURATION_MS, easing = FastOutSlowInEasing),
        label = "avgProgress"
    )

    // Delta Percentage calculation (Live vs Average/Target)
    val deltaPct = remember(liveHashrateThs, avgHashrateThs) {
        if (avgHashrateThs > 0 && liveHashrateThs > 0) {
            ((liveHashrateThs - avgHashrateThs) / avgHashrateThs) * 100.0
        } else 0.0
    }

    val isPositiveTrend = deltaPct >= 0
    val trendColor = when {
        liveHashrateThs <= 0 -> CyberRed
        isPositiveTrend -> CyberEmerald
        deltaPct > -5.0 -> CyberAmber
        else -> CyberRed
    }

    val trendText = remember(deltaPct, liveHashrateThs) {
        if (liveHashrateThs <= 0) "🚨 قطع"
        else if (isPositiveTrend) String.format(Locale.US, "▲ +%.1f%%", deltaPct)
        else String.format(Locale.US, "▼ %.1f%%", deltaPct)
    }

    val liveDisplayText = remember(liveHashrateThs) {
        if (liveHashrateThs > 0) String.format(Locale.US, "%.1f", liveHashrateThs) else "0.0"
    }

    val infiniteTransition = rememberInfiniteTransition(label = "dualArcPulse")
    val pulseAlpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.8f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulseAlpha"
    )

    val defaultHistory = rememberSparklineHistory(currentVal = liveHashrateThs.toFloat(), seedOffset = 2)
    val activeHistory = history ?: defaultHistory

    Box(
        contentAlignment = Alignment.Center,
        modifier = modifier
            .size(actualSize)
            .padding(2.dp)
            .semantics {
                contentDescription = "گیج دو محوره هش‌ریت: زنده $liveDisplayText TH/s، میانگین $avgHashrateThs TH/s، تغییرات: $trendText"
            }
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val strokeWidthOuter = (actualSize.toPx() * 0.065f).coerceIn(6.dp.toPx(), 9.dp.toPx())
            val strokeWidthInner = (actualSize.toPx() * 0.05f).coerceIn(4.dp.toPx(), 7.dp.toPx())

            val sizePx = actualSize.toPx()
            val center = Offset(sizePx / 2f, sizePx / 2f)

            // 1. Radial Ticks Graduation Background
            val tickCount = 21
            val radiusOuter = (sizePx - strokeWidthOuter * 2.2f) / 2f
            for (i in 0 until tickCount) {
                val tickAngle = START_ANGLE + (i.toFloat() / (tickCount - 1)) * MAX_SWEEP_ANGLE
                val isMajor = i % 5 == 0
                val angleRad = Math.toRadians(tickAngle.toDouble())
                val startX = center.x + (radiusOuter + strokeWidthOuter * 0.6f) * cos(angleRad).toFloat()
                val startY = center.y + (radiusOuter + strokeWidthOuter * 0.6f) * sin(angleRad).toFloat()
                val endX = center.x + (radiusOuter + strokeWidthOuter * (if (isMajor) 1.1f else 0.8f)) * cos(angleRad).toFloat()
                val endY = center.y + (radiusOuter + strokeWidthOuter * (if (isMajor) 1.1f else 0.8f)) * sin(angleRad).toFloat()

                drawLine(
                    color = DarkSurfaceVariant.copy(alpha = if (isMajor) 0.6f else 0.3f),
                    start = Offset(startX, startY),
                    end = Offset(endX, endY),
                    strokeWidth = if (isMajor) 1.8.dp.toPx() else 1.dp.toPx(),
                    cap = StrokeCap.Round
                )
            }

            // 2. Outer Track Arc (Live Hashrate)
            val topLeftOuter = Offset((sizePx - radiusOuter * 2f) / 2f, (sizePx - radiusOuter * 2f) / 2f)
            val arcSizeOuter = Size(radiusOuter * 2f, radiusOuter * 2f)
            val liveSweep = animatedLiveProgress * MAX_SWEEP_ANGLE

            // Outer Base Track
            drawArc(
                color = DarkSurfaceVariant,
                startAngle = START_ANGLE,
                sweepAngle = MAX_SWEEP_ANGLE,
                useCenter = false,
                topLeft = topLeftOuter,
                size = arcSizeOuter,
                style = Stroke(width = strokeWidthOuter, cap = StrokeCap.Round)
            )

            // Outer Active Live Arc
            if (liveSweep > 0f) {
                drawArc(
                    color = CyberCyan.copy(alpha = pulseAlpha * 0.4f),
                    startAngle = START_ANGLE,
                    sweepAngle = liveSweep,
                    useCenter = false,
                    topLeft = Offset(topLeftOuter.x - strokeWidthOuter * 0.2f, topLeftOuter.y - strokeWidthOuter * 0.2f),
                    size = Size(arcSizeOuter.width + strokeWidthOuter * 0.4f, arcSizeOuter.height + strokeWidthOuter * 0.4f),
                    style = Stroke(width = strokeWidthOuter * 1.3f, cap = StrokeCap.Round)
                )

                drawArc(
                    brush = Brush.sweepGradient(listOf(CyberCyan, CyberEmerald, CyberCyan)),
                    startAngle = START_ANGLE,
                    sweepAngle = liveSweep,
                    useCenter = false,
                    topLeft = topLeftOuter,
                    size = arcSizeOuter,
                    style = Stroke(width = strokeWidthOuter, cap = StrokeCap.Round)
                )

                val tipAngleRad = Math.toRadians((START_ANGLE + liveSweep).toDouble())
                val tipX = center.x + radiusOuter * cos(tipAngleRad).toFloat()
                val tipY = center.y + radiusOuter * sin(tipAngleRad).toFloat()
                drawCircle(color = CyberCyan, radius = strokeWidthOuter * 0.7f, center = Offset(tipX, tipY))
                drawCircle(color = Color.White, radius = strokeWidthOuter * 0.35f, center = Offset(tipX, tipY))
            }

            // 3. Inner Track Arc (Average / Target Hashrate)
            val radiusInner = radiusOuter - strokeWidthOuter * 1.35f
            val topLeftInner = Offset((sizePx - radiusInner * 2f) / 2f, (sizePx - radiusInner * 2f) / 2f)
            val arcSizeInner = Size(radiusInner * 2f, radiusInner * 2f)
            val avgSweep = animatedAvgProgress * MAX_SWEEP_ANGLE

            // Inner Base Track
            drawArc(
                color = DarkSurfaceVariant.copy(alpha = 0.5f),
                startAngle = START_ANGLE,
                sweepAngle = MAX_SWEEP_ANGLE,
                useCenter = false,
                topLeft = topLeftInner,
                size = arcSizeInner,
                style = Stroke(width = strokeWidthInner, cap = StrokeCap.Round)
            )

            // Inner Active Avg Arc
            if (avgSweep > 0f) {
                drawArc(
                    brush = Brush.sweepGradient(listOf(CyberPurple, CyberAmber, CyberPurple)),
                    startAngle = START_ANGLE,
                    sweepAngle = avgSweep,
                    useCenter = false,
                    topLeft = topLeftInner,
                    size = arcSizeInner,
                    style = Stroke(width = strokeWidthInner, cap = StrokeCap.Round)
                )

                val innerTipAngleRad = Math.toRadians((START_ANGLE + avgSweep).toDouble())
                val innerTipX = center.x + radiusInner * cos(innerTipAngleRad).toFloat()
                val innerTipY = center.y + radiusInner * sin(innerTipAngleRad).toFloat()
                drawCircle(color = CyberPurple, radius = strokeWidthInner * 0.7f, center = Offset(innerTipX, innerTipY))
                drawCircle(color = Color.White, radius = strokeWidthInner * 0.3f, center = Offset(innerTipX, innerTipY))
            }
        }

        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
            modifier = Modifier.padding(horizontal = 8.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Default.Speed,
                    contentDescription = null,
                    tint = CyberCyan,
                    modifier = Modifier.size(14.dp)
                )
                Spacer(modifier = Modifier.width(2.dp))
                // Live Value Display
                Text(
                    text = liveDisplayText,
                    style = MaterialTheme.typography.titleLarge.copy(
                        fontWeight = FontWeight.Bold,
                        fontSize = if (actualSize < 130.dp) 15.sp else 18.sp
                    ),
                    fontFamily = FontFamily.Monospace,
                    color = TextPrimary,
                    textAlign = TextAlign.Center
                )
                Spacer(modifier = Modifier.width(2.dp))
                Text(
                    text = "TH/s",
                    style = MaterialTheme.typography.labelSmall.copy(fontSize = 8.5.sp),
                    color = CyberCyan,
                    fontWeight = FontWeight.Bold
                )
            }

            // Delta Trend Badge (▲ +4.2%)
            Surface(
                shape = RoundedCornerShape(6.dp),
                color = trendColor.copy(alpha = 0.18f),
                border = androidx.compose.foundation.BorderStroke(0.6.dp, trendColor.copy(alpha = 0.5f))
            ) {
                Text(
                    text = trendText,
                    style = MaterialTheme.typography.labelSmall.copy(fontSize = 8.5.sp),
                    color = trendColor,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(horizontal = 5.dp, vertical = 1.dp)
                )
            }

            // Sparkline Mini-Chart
            if (liveHashrateThs > 0) {
                Spacer(modifier = Modifier.height(2.dp))
                SparklineMiniChart(
                    points = activeHistory,
                    lineColor = CyberCyan,
                    glowColor = CyberCyan,
                    height = 14.dp,
                    modifier = Modifier
                        .fillMaxWidth(0.65f)
                        .clip(RoundedCornerShape(4.dp))
                )
            }
        }
    }
}
