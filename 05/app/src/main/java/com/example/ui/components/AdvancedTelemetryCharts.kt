package com.example.ui.components

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectTapGestures
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material.icons.filled.Thermostat
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.CyberAmber
import com.example.ui.theme.CyberCyan
import com.example.ui.theme.CyberEmerald
import com.example.ui.theme.CyberRed
import com.example.ui.theme.DarkSurface
import com.example.ui.theme.DarkSurfaceVariant
import com.example.ui.theme.TextMuted
import com.example.ui.theme.TextPrimary
import com.example.ui.theme.TextSecondary
import java.util.Locale

// ==================== Feature 2: Sparkline Graph for Cards ====================

/**
 * نمودار ریزروند (Sparkline) مینیاتوری جهت نمایش روی کارت ماینرها
 */
@Composable
fun SparklineGraph(
    dataPoints: List<Double>,
    modifier: Modifier = Modifier,
    lineColor: Color = CyberCyan,
    height: Dp = 32.dp,
    showGlowDot: Boolean = true
) {
    if (dataPoints.size < 2) return

    val infiniteTransition = rememberInfiniteTransition(label = "sparklinePulse")
    val pulseAlpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.85f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulseAlpha"
    )

    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(height)
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val widthPx = size.width
            val heightPx = size.height

            val minVal = dataPoints.minOrNull() ?: 0.0
            val maxVal = dataPoints.maxOrNull() ?: 100.0
            val range = (maxVal - minVal).coerceAtLeast(1.0)

            val stepX = widthPx / (dataPoints.size - 1)

            val path = Path()
            val fillPath = Path()

            val points = dataPoints.mapIndexed { index, value ->
                val x = index * stepX
                val normalizedY = ((value - minVal) / range).toFloat()
                // Reverse Y for canvas coordinates
                val y = heightPx - (normalizedY * (heightPx - 8.dp.toPx())) - 4.dp.toPx()
                Offset(x, y)
            }

            if (points.isNotEmpty()) {
                path.moveTo(points.first().x, points.first().y)
                fillPath.moveTo(points.first().x, heightPx)
                fillPath.lineTo(points.first().x, points.first().y)

                for (i in 0 until points.size - 1) {
                    val p1 = points[i]
                    val p2 = points[i + 1]
                    val control1 = Offset((p1.x + p2.x) / 2f, p1.y)
                    val control2 = Offset((p1.x + p2.x) / 2f, p2.y)

                    path.cubicTo(control1.x, control1.y, control2.x, control2.y, p2.x, p2.y)
                    fillPath.cubicTo(control1.x, control1.y, control2.x, control2.y, p2.x, p2.y)
                }

                fillPath.lineTo(points.last().x, heightPx)
                fillPath.close()

                // Translucent area fill under curve
                drawPath(
                    path = fillPath,
                    brush = Brush.verticalGradient(
                        colors = listOf(lineColor.copy(alpha = 0.35f), Color.Transparent)
                    )
                )

                // Glowing line stroke
                drawPath(
                    path = path,
                    color = lineColor,
                    style = Stroke(width = 2.dp.toPx(), cap = StrokeCap.Round)
                )

                // Ambient halo line glow
                drawPath(
                    path = path,
                    color = lineColor.copy(alpha = 0.3f),
                    style = Stroke(width = 4.dp.toPx(), cap = StrokeCap.Round)
                )

                // Pulse dot at tip (latest point)
                if (showGlowDot) {
                    val lastPoint = points.last()
                    drawCircle(
                        color = lineColor.copy(alpha = pulseAlpha * 0.7f),
                        radius = 5.dp.toPx(),
                        center = lastPoint
                    )
                    drawCircle(
                        color = Color.White,
                        radius = 2.dp.toPx(),
                        center = lastPoint
                    )
                }
            }
        }
    }
}

// ==================== Feature 3: Live Dual-Axis Interactive Chart ====================

/**
 * نمودار دو محوره زنده (هش‌ریت در محور چپ و دما در محور راست)
 */
@Composable
fun LiveDualAxisChart(
    hashrateHistory: List<Double>, // e.g. TH/s
    tempHistory: List<Double>,     // e.g. °C
    modifier: Modifier = Modifier,
    title: String = "نمودار زنده روند دو محوره (هش‌ریت / دما)",
    maxHashrateThs: Double = 150.0,
    maxTempC: Double = 100.0
) {
    val sampleCount = maxOf(hashrateHistory.size, tempHistory.size, 10)
    val hashrates = remember(hashrateHistory) {
        if (hashrateHistory.isEmpty()) {
            List(10) { 100.0 + (it % 3) * 2.5 }
        } else if (hashrateHistory.size < 10) {
            val pad = List(10 - hashrateHistory.size) { hashrateHistory.firstOrNull() ?: 100.0 }
            pad + hashrateHistory
        } else hashrateHistory
    }

    val temps = remember(tempHistory) {
        if (tempHistory.isEmpty()) {
            List(10) { 68.0 + (it % 4) * 1.2 }
        } else if (tempHistory.size < 10) {
            val pad = List(10 - tempHistory.size) { tempHistory.firstOrNull() ?: 68.0 }
            pad + tempHistory
        } else tempHistory
    }

    val latestHashrate = hashrates.lastOrNull() ?: 0.0
    val latestTemp = temps.lastOrNull() ?: 0.0

    var selectedIndex by remember { mutableStateOf<Int?>(null) }

    val infiniteTransition = rememberInfiniteTransition(label = "chartPulse")
    val pulseAlpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.85f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulseAlpha"
    )

    GlassmorphicCard(
        glowColor = CyberCyan,
        modifier = modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            // Header with Legend
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary
                )

                // Live Pulse Status Tag
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .background(
                                color = CyberEmerald.copy(alpha = pulseAlpha),
                                shape = CircleShape
                            )
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "زنده",
                        style = MaterialTheme.typography.labelSmall,
                        color = CyberEmerald,
                        fontWeight = FontWeight.Bold
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Value Indicators Banner
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(DarkSurfaceVariant, RoundedCornerShape(10.dp))
                    .padding(horizontal = 12.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Left Axis Metric (Hashrate)
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Speed,
                        contentDescription = null,
                        tint = CyberCyan,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    val hVal = selectedIndex?.let { hashrates.getOrNull(it) } ?: latestHashrate
                    Text(
                        text = "هش‌ریت: ",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary
                    )
                    Text(
                        text = String.format(Locale.US, "%.1f TH/s", hVal),
                        style = MaterialTheme.typography.bodySmall,
                        fontWeight = FontWeight.Bold,
                        fontFamily = FontFamily.Monospace,
                        color = CyberCyan
                    )
                }

                // Right Axis Metric (Temp)
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Thermostat,
                        contentDescription = null,
                        tint = if (latestTemp > 80) CyberRed else CyberAmber,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    val tVal = selectedIndex?.let { temps.getOrNull(it) } ?: latestTemp
                    Text(
                        text = "دما: ",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary
                    )
                    Text(
                        text = String.format(Locale.US, "%.1f °C", tVal),
                        style = MaterialTheme.typography.bodySmall,
                        fontWeight = FontWeight.Bold,
                        fontFamily = FontFamily.Monospace,
                        color = if (tVal > 80) CyberRed else CyberAmber
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Chart Canvas Container
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(180.dp)
                    .pointerInput(sampleCount) {
                        detectTapGestures { offset ->
                            val widthPx = size.width
                            val stepX = widthPx / (sampleCount - 1)
                            val idx = ((offset.x + stepX / 2f) / stepX).toInt().coerceIn(0, sampleCount - 1)
                            selectedIndex = if (selectedIndex == idx) null else idx
                        }
                    }
            ) {
                Canvas(modifier = Modifier.fillMaxSize()) {
                    val widthPx = size.width
                    val heightPx = size.height

                    val paddingBottom = 20.dp.toPx()
                    val paddingTop = 10.dp.toPx()
                    val usableHeight = heightPx - paddingBottom - paddingTop

                    val stepX = widthPx / (sampleCount - 1)

                    // Draw Horizontal Grid Lines
                    val gridLines = 4
                    for (i in 0..gridLines) {
                        val y = paddingTop + (usableHeight / gridLines) * i
                        drawLine(
                            color = DarkSurfaceVariant,
                            start = Offset(0f, y),
                            end = Offset(widthPx, y),
                            strokeWidth = 1.dp.toPx(),
                            pathEffect = PathEffect.dashPathEffect(floatArrayOf(10f, 10f), 0f)
                        )
                    }

                    // --- 1. Draw Hashrate Curve (Left Axis / CyberCyan) ---
                    val maxH = (hashrates.maxOrNull() ?: maxHashrateThs).coerceAtLeast(10.0)
                    val hPoints = hashrates.mapIndexed { index, valThs ->
                        val x = index * stepX
                        val norm = (valThs / maxH).toFloat().coerceIn(0f, 1f)
                        val y = paddingTop + usableHeight * (1f - norm)
                        Offset(x, y)
                    }

                    if (hPoints.isNotEmpty()) {
                        val hPath = Path().apply {
                            moveTo(hPoints.first().x, hPoints.first().y)
                            for (i in 0 until hPoints.size - 1) {
                                val p1 = hPoints[i]
                                val p2 = hPoints[i + 1]
                                cubicTo((p1.x + p2.x) / 2f, p1.y, (p1.x + p2.x) / 2f, p2.y, p2.x, p2.y)
                            }
                        }
                        val hFill = Path().apply {
                            addPath(hPath)
                            lineTo(hPoints.last().x, heightPx - paddingBottom)
                            lineTo(hPoints.first().x, heightPx - paddingBottom)
                            close()
                        }

                        drawPath(
                            path = hFill,
                            brush = Brush.verticalGradient(
                                colors = listOf(CyberCyan.copy(alpha = 0.25f), Color.Transparent)
                            )
                        )
                        drawPath(
                            path = hPath,
                            color = CyberCyan,
                            style = Stroke(width = 2.5.dp.toPx(), cap = StrokeCap.Round)
                        )

                        // Tip pulse for Hashrate
                        val lastH = hPoints.last()
                        drawCircle(color = CyberCyan.copy(alpha = pulseAlpha), radius = 6.dp.toPx(), center = lastH)
                        drawCircle(color = Color.White, radius = 2.5.dp.toPx(), center = lastH)
                    }

                    // --- 2. Draw Temperature Curve (Right Axis / CyberAmber) ---
                    val maxT = (temps.maxOrNull() ?: maxTempC).coerceAtLeast(50.0)
                    val tPoints = temps.mapIndexed { index, valTemp ->
                        val x = index * stepX
                        val norm = (valTemp / maxT).toFloat().coerceIn(0f, 1f)
                        val y = paddingTop + usableHeight * (1f - norm)
                        Offset(x, y)
                    }

                    if (tPoints.isNotEmpty()) {
                        val tPath = Path().apply {
                            moveTo(tPoints.first().x, tPoints.first().y)
                            for (i in 0 until tPoints.size - 1) {
                                val p1 = tPoints[i]
                                val p2 = tPoints[i + 1]
                                cubicTo((p1.x + p2.x) / 2f, p1.y, (p1.x + p2.x) / 2f, p2.y, p2.x, p2.y)
                            }
                        }
                        val tFill = Path().apply {
                            addPath(tPath)
                            lineTo(tPoints.last().x, heightPx - paddingBottom)
                            lineTo(tPoints.first().x, heightPx - paddingBottom)
                            close()
                        }

                        drawPath(
                            path = tFill,
                            brush = Brush.verticalGradient(
                                colors = listOf(CyberAmber.copy(alpha = 0.20f), Color.Transparent)
                            )
                        )
                        drawPath(
                            path = tPath,
                            color = CyberAmber,
                            style = Stroke(
                                width = 2.dp.toPx(),
                                cap = StrokeCap.Round,
                                pathEffect = PathEffect.dashPathEffect(floatArrayOf(12f, 6f), 0f)
                            )
                        )

                        // Tip pulse for Temp
                        val lastT = tPoints.last()
                        drawCircle(color = CyberAmber.copy(alpha = pulseAlpha), radius = 5.dp.toPx(), center = lastT)
                        drawCircle(color = Color.White, radius = 2.dp.toPx(), center = lastT)
                    }

                    // --- 3. Draw Selected Touch Highlight Line ---
                    selectedIndex?.let { idx ->
                        if (idx in 0 until sampleCount) {
                            val selX = idx * stepX
                            drawLine(
                                color = TextPrimary.copy(alpha = 0.6f),
                                start = Offset(selX, paddingTop),
                                end = Offset(selX, heightPx - paddingBottom),
                                strokeWidth = 1.5.dp.toPx(),
                                pathEffect = PathEffect.dashPathEffect(floatArrayOf(6f, 6f), 0f)
                            )

                            hPoints.getOrNull(idx)?.let { hp ->
                                drawCircle(color = CyberCyan, radius = 5.dp.toPx(), center = hp)
                            }
                            tPoints.getOrNull(idx)?.let { tp ->
                                drawCircle(color = CyberAmber, radius = 5.dp.toPx(), center = tp)
                            }
                        }
                    }
                }
            }

            // X-Axis Time Labels
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 4.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                val labels = listOf("-15m", "-12m", "-9m", "-6m", "-3m", "اکنون")
                labels.forEach { label ->
                    Text(
                        text = label,
                        style = MaterialTheme.typography.labelSmall.copy(fontSize = 10.sp),
                        color = if (label == "اکنون") CyberEmerald else TextMuted,
                        fontWeight = if (label == "اکنون") FontWeight.Bold else FontWeight.Normal
                    )
                }
            }
        }
    }
}
