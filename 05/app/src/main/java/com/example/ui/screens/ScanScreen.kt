package com.example.ui.screens

import androidx.activity.compose.BackHandler
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoMode
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Memory
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Router
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material.icons.filled.Wifi
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.components.GlassmorphicCard
import com.example.ui.theme.CyberAmber
import com.example.ui.theme.CyberCyan
import com.example.ui.theme.CyberEmerald
import com.example.ui.theme.CyberRed
import com.example.ui.theme.DarkCardBorder
import com.example.ui.theme.DarkSurface
import com.example.ui.theme.DarkSurfaceVariant
import com.example.ui.theme.TextMuted
import com.example.ui.theme.TextPrimary
import com.example.ui.theme.TextSecondary
import com.example.ui.viewmodels.ScanViewModel

@Composable
fun ScanScreen(
    viewModel: ScanViewModel,
    onNavigateToDeviceList: () -> Unit
) {
    val scanState by viewModel.scanState.collectAsState()
    val targetSubnetInput by viewModel.targetSubnetInput.collectAsState()
    val detectedInfo by viewModel.detectedSubnetInfo.collectAsState()
    
    val minerCount by viewModel.minerCount.collectAsState(initial = 0)

    val progress = remember(scanState.scannedCount, scanState.totalHosts) {
        if (scanState.totalHosts > 0) {
            scanState.scannedCount.toFloat() / scanState.totalHosts.toFloat()
        } else 0f
    }

    BackHandler(enabled = scanState.isScanning) {
        viewModel.stopScan()
    }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .windowInsetsPadding(WindowInsets.statusBars)
            .padding(horizontal = 16.dp)
            .testTag("scan_screen")
            .semantics { contentDescription = "صفحه اسکن شبکه" },
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // ==================== Header ====================
        item(key = "header") {
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "اسکنر شبکه",
                style = MaterialTheme.typography.titleLarge.copy(
                    fontWeight = FontWeight.Bold
                ),
                color = MaterialTheme.colorScheme.onBackground
            )
            Text(
                text = "جستجو و شناسایی همزمان پورت‌ها و API دستگاه‌های واتس‌ماینر",
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary
            )
        }

        // ==================== Radar Visualizer ====================
        item(key = "radar") {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkSurface),
                shape = RoundedCornerShape(20.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(1.dp, DarkCardBorder, RoundedCornerShape(20.dp))
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    PulsingCircularScanVisualizer(
                        isScanning = scanState.isScanning,
                        progress = progress,
                        foundCount = scanState.foundCount,
                        scannedCount = scanState.scannedCount,
                        totalHosts = scanState.totalHosts,
                        currentIp = scanState.currentScanningIp,
                        subnetCidr = scanState.subnetCidr
                    )
                }
            }
        }

        // ==================== Error State ====================
        if (scanState.errorMessage != null) {
            item(key = "error") {
                ScanErrorCard(
                    message = scanState.errorMessage!!,
                    onRetry = { viewModel.startScan() }
                )
            }
        }

        // ==================== Auto-Detected Wi-Fi Info ====================
        item(key = "wifi_info") {
            AutoDetectedWifiCard(
                detectedInfo = detectedInfo,
                onRefresh = { viewModel.refreshAutoDetectedSubnet() }
            )
        }

        // ==================== Subnet Config ====================
        item(key = "subnet_config") {
            SubnetConfigCard(
                targetSubnetInput = targetSubnetInput,
                onSubnetInputChange = { viewModel.onSubnetInputChange(it) },
                isScanning = scanState.isScanning,
                onStartScan = { viewModel.startScan() },
                onStopScan = { viewModel.stopScan() },
                onNavigateToDeviceList = onNavigateToDeviceList,
                minerCount = minerCount,
                onResetAuto = { viewModel.refreshAutoDetectedSubnet() }
            )
        }

        // ==================== Live Stats ====================
        item(key = "stats") {
            LiveStatsRow(
                foundCount = scanState.foundCount,
                isScanning = scanState.isScanning
            )
        }

        item(key = "bottom_spacer") {
            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}

// ==================== Sub-Components ====================

@Composable
private fun ScanErrorCard(
    message: String,
    onRetry: () -> Unit
) {
    GlassmorphicCard(
        glowColor = CyberRed,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = Icons.Default.Info,
                contentDescription = null,
                tint = CyberRed,
                modifier = Modifier.size(32.dp)
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "خطا در اسکن شبکه",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = CyberRed
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = message,
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary
            )
            Spacer(modifier = Modifier.height(12.dp))
            Button(
                onClick = onRetry,
                colors = ButtonDefaults.buttonColors(containerColor = CyberRed)
            ) {
                Text("تلاش مجدد", color = Color.White)
            }
        }
    }
}

@Composable
private fun AutoDetectedWifiCard(
    detectedInfo: com.example.data.network.SubnetInfo,
    onRefresh: () -> Unit
) {
    GlassmorphicCard(
        glowColor = CyberCyan,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Wifi,
                        contentDescription = null,
                        tint = CyberCyan,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "شناسایی اتوماتیک آی‌پی مودم",
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.Bold
                        ),
                        color = MaterialTheme.colorScheme.onBackground
                    )
                }
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = CyberEmerald.copy(alpha = 0.15f),
                    border = BorderStroke(0.5.dp, CyberEmerald.copy(alpha = 0.4f))
                ) {
                    Text(
                        text = "⚡ اسکن خودکار",
                        style = MaterialTheme.typography.labelSmall,
                        color = CyberEmerald,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    )
                }
            }

            Surface(
                shape = RoundedCornerShape(12.dp),
                color = DarkSurface,
                border = BorderStroke(0.5.dp, DarkCardBorder),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(12.dp),
                    verticalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    WifiInfoRow(
                        label = "آی‌پی دستگاه شما در شبکه مودم:",
                        value = detectedInfo.localIp,
                        valueColor = CyberCyan
                    )
                    WifiInfoRow(
                        label = "محدوده آی‌پی مودم (اتوماتیک):",
                        value = detectedInfo.subnetCidr,
                        valueColor = CyberEmerald
                    )
                    WifiInfoRow(
                        label = "تعداد هاست‌های مودم:",
                        value = "${detectedInfo.totalHosts} دستگاه (از 1 تا ${detectedInfo.totalHosts})",
                        valueColor = TextSecondary
                    )
                }
            }
        }
    }
}

@Composable
private fun WifiInfoRow(
    label: String,
    value: String,
    valueColor: Color
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = TextSecondary
        )
        Text(
            text = value,
            style = MaterialTheme.typography.titleSmall,
            fontFamily = FontFamily.Monospace,
            color = valueColor,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
private fun SubnetConfigCard(
    targetSubnetInput: String,
    onSubnetInputChange: (String) -> Unit,
    isScanning: Boolean,
    onStartScan: () -> Unit,
    onStopScan: () -> Unit,
    onNavigateToDeviceList: () -> Unit,
    minerCount: Int,
    onResetAuto: () -> Unit
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = DarkSurface),
        shape = RoundedCornerShape(16.dp),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, DarkCardBorder, RoundedCornerShape(16.dp))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "تنظیم اتوماتیک محدوده اسکن شبکه مودم",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextMuted,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 0.5.sp
                )
                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = CyberCyan.copy(alpha = 0.15f),
                    border = BorderStroke(0.5.dp, CyberCyan.copy(alpha = 0.4f)),
                    modifier = Modifier.clickable(onClick = onResetAuto)
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.AutoMode,
                            contentDescription = null,
                            tint = CyberCyan,
                            modifier = Modifier.size(12.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "شناسایی مجدد مودم",
                            style = MaterialTheme.typography.labelSmall,
                            color = CyberCyan,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            OutlinedTextField(
                value = targetSubnetInput,
                onValueChange = onSubnetInputChange,
                label = { Text("محدوده زیرشبکه (شناسایی اتوماتیک مودم)") },
                placeholder = { Text("192.168.1.0/24") },
                singleLine = true,
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = CyberCyan,
                    unfocusedBorderColor = DarkCardBorder,
                    focusedLabelColor = CyberCyan,
                    cursorColor = CyberCyan
                ),
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("subnet_input_field")
            )

            Spacer(modifier = Modifier.height(16.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                if (isScanning) {
                    Button(
                        onClick = onStopScan,
                        colors = ButtonDefaults.buttonColors(
                            containerColor = CyberRed,
                            contentColor = Color.White
                        ),
                        shape = RoundedCornerShape(10.dp),
                        modifier = Modifier
                            .weight(1f)
                            .testTag("stop_scan_button")
                    ) {
                        Icon(imageVector = Icons.Default.Stop, contentDescription = null)
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("توقف اسکن", fontWeight = FontWeight.Bold)
                    }
                } else {
                    Button(
                        onClick = onStartScan,
                        colors = ButtonDefaults.buttonColors(
                            containerColor = CyberCyan,
                            contentColor = Color.Black
                        ),
                        shape = RoundedCornerShape(10.dp),
                        modifier = Modifier
                            .weight(1f)
                            .testTag("start_scan_button")
                    ) {
                        Icon(imageVector = Icons.Default.PlayArrow, contentDescription = null)
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("شروع اسکن", fontWeight = FontWeight.Bold)
                    }
                }

                OutlinedButton(
                    onClick = onNavigateToDeviceList,
                    shape = RoundedCornerShape(10.dp),
                    modifier = Modifier
                        .weight(1f)
                        .testTag("view_results_button")
                ) {
                    Text("نتایج ($minerCount)", fontWeight = FontWeight.Bold, color = CyberCyan)
                }
            }
        }
    }
}

@Composable
private fun LiveStatsRow(
    foundCount: Int,
    isScanning: Boolean
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        StatCard(
            icon = Icons.Default.CheckCircle,
            iconTint = CyberEmerald,
            title = "شناسایی شده",
            value = "$foundCount ماینر",
            modifier = Modifier.weight(1f)
        )
        StatCard(
            icon = Icons.Default.Router,
            iconTint = CyberAmber,
            title = "پورت API",
            value = "پورت ۴۰۲۸ / TCP",
            modifier = Modifier.weight(1f)
        )
    }
}

@Composable
private fun StatCard(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    iconTint: Color,
    title: String,
    value: String,
    modifier: Modifier = Modifier
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = DarkSurface),
        shape = RoundedCornerShape(12.dp),
        modifier = modifier
            .border(1.dp, DarkCardBorder, RoundedCornerShape(12.dp))
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = iconTint,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = title,
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary
                )
            }
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                text = value,
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = iconTint
            )
        }
    }
}

// ==================== Radar Visualizer ====================

@Composable
fun PulsingCircularScanVisualizer(
    isScanning: Boolean,
    progress: Float,
    foundCount: Int,
    scannedCount: Int,
    totalHosts: Int,
    currentIp: String,
    subnetCidr: String
) {
    val animatedProgress by animateFloatAsState(
        targetValue = progress.coerceIn(0f, 1f),
        animationSpec = tween(durationMillis = 300, easing = LinearEasing),
        label = "progressAnimation"
    )

    val rotation: Float
    val pulseScale1: Float
    val pulseAlpha1: Float
    val pulseScale2: Float
    val pulseAlpha2: Float

    if (isScanning) {
        val infiniteTransition = rememberInfiniteTransition(label = "pulseTransition")
        
        rotation = infiniteTransition.animateFloat(
            initialValue = 0f,
            targetValue = 360f,
            animationSpec = infiniteRepeatable(
                animation = tween(2200, easing = LinearEasing),
                repeatMode = RepeatMode.Restart
            ),
            label = "radarRotation"
        ).value

        pulseScale1 = infiniteTransition.animateFloat(
            initialValue = 1f,
            targetValue = 1.45f,
            animationSpec = infiniteRepeatable(
                animation = tween(1800, easing = LinearEasing),
                repeatMode = RepeatMode.Restart
            ),
            label = "pulseScale1"
        ).value

        pulseAlpha1 = infiniteTransition.animateFloat(
            initialValue = 0.5f,
            targetValue = 0f,
            animationSpec = infiniteRepeatable(
                animation = tween(1800, easing = LinearEasing),
                repeatMode = RepeatMode.Restart
            ),
            label = "pulseAlpha1"
        ).value

        pulseScale2 = infiniteTransition.animateFloat(
            initialValue = 1f,
            targetValue = 1.45f,
            animationSpec = infiniteRepeatable(
                animation = tween(1800, delayMillis = 600, easing = LinearEasing),
                repeatMode = RepeatMode.Restart
            ),
            label = "pulseScale2"
        ).value

        pulseAlpha2 = infiniteTransition.animateFloat(
            initialValue = 0.5f,
            targetValue = 0f,
            animationSpec = infiniteRepeatable(
                animation = tween(1800, delayMillis = 600, easing = LinearEasing),
                repeatMode = RepeatMode.Restart
            ),
            label = "pulseAlpha2"
        ).value
    } else {
        rotation = 0f
        pulseScale1 = 1f
        pulseAlpha1 = 0f
        pulseScale2 = 1f
        pulseAlpha2 = 0f
    }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Box(
            contentAlignment = Alignment.Center,
            modifier = Modifier
                .size(230.dp)
                .padding(12.dp)
                .semantics {
                    contentDescription = "پیشرفت اسکن: ${(animatedProgress * 100).toInt()} درصد"
                }
        ) {
            if (isScanning) {
                Box(
                    modifier = Modifier
                        .size(200.dp)
                        .scale(pulseScale1)
                        .background(Color.Transparent, CircleShape)
                        .border(
                            width = 2.dp,
                            color = CyberCyan.copy(alpha = pulseAlpha1),
                            shape = CircleShape
                        )
                )
                Box(
                    modifier = Modifier
                        .size(200.dp)
                        .scale(pulseScale2)
                        .background(Color.Transparent, CircleShape)
                        .border(
                            width = 1.5.dp,
                            color = CyberEmerald.copy(alpha = pulseAlpha2),
                            shape = CircleShape
                        )
                )
            }

            Canvas(modifier = Modifier.fillMaxSize()) {
                val strokeWidth = 14.dp.toPx()
                val diameter = size.minDimension - strokeWidth
                val topPadding = (size.height - diameter) / 2
                val leftPadding = (size.width - diameter) / 2
                val arcSize = Size(diameter, diameter)

                // Track Ring
                drawArc(
                    color = DarkSurfaceVariant,
                    startAngle = 0f,
                    sweepAngle = 360f,
                    useCenter = false,
                    topLeft = Offset(leftPadding, topPadding),
                    size = arcSize,
                    style = Stroke(width = strokeWidth, cap = StrokeCap.Round)
                )

                // Progress Sweep Arc
                val sweepAngle = animatedProgress * 360f
                if (sweepAngle > 0f) {
                    drawArc(
                        brush = Brush.sweepGradient(
                            listOf(CyberCyan, CyberEmerald, CyberCyan)
                        ),
                        startAngle = -90f,
                        sweepAngle = sweepAngle,
                        useCenter = false,
                        topLeft = Offset(leftPadding, topPadding),
                        size = arcSize,
                        style = Stroke(width = strokeWidth, cap = StrokeCap.Round)
                    )
                }

                // Rotating Radar Beam
                if (isScanning) {
                    rotate(rotation, pivot = center) {
                        drawLine(
                            brush = Brush.radialGradient(
                                colors = listOf(CyberCyan, Color.Transparent),
                                center = center,
                                radius = diameter / 2
                            ),
                            start = center,
                            end = Offset(
                                center.x,
                                center.y - (diameter / 2) + (strokeWidth / 2)
                            ),
                            strokeWidth = 3.dp.toPx(),
                            cap = StrokeCap.Round
                        )
                    }
                }
            }

            // Center Content
            RadarCenterContent(
                isScanning = isScanning,
                animatedProgress = animatedProgress,
                foundCount = foundCount
            )
        }

        Spacer(modifier = Modifier.height(12.dp))

        // Bottom Info Bar
        ScanInfoBar(
            isScanning = isScanning,
            currentIp = currentIp,
            subnetCidr = subnetCidr,
            scannedCount = scannedCount,
            totalHosts = totalHosts
        )
    }
}

@Composable
private fun RadarCenterContent(
    isScanning: Boolean,
    animatedProgress: Float,
    foundCount: Int
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
        modifier = Modifier.padding(20.dp)
    ) {
        Text(
            text = "${(animatedProgress * 100).toInt()}%",
            style = MaterialTheme.typography.displayLarge.copy(
                fontWeight = FontWeight.Bold,
                fontSize = 36.sp
            ),
            color = if (isScanning) CyberCyan else TextPrimary
        )
        Spacer(modifier = Modifier.height(4.dp))
        Surface(
            shape = RoundedCornerShape(16.dp),
            color = if (foundCount > 0) CyberEmerald.copy(alpha = 0.2f)
            else DarkSurfaceVariant,
            border = BorderStroke(
                1.dp,
                if (foundCount > 0) CyberEmerald else DarkCardBorder
            )
        ) {
            Row(
                modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Default.Memory,
                    contentDescription = null,
                    tint = if (foundCount > 0) CyberEmerald else TextMuted,
                    modifier = Modifier.size(14.dp)
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text(
                    text = if (foundCount > 0) "$foundCount ماینر یافت شد"
                    else "بدون ماینر",
                    style = MaterialTheme.typography.labelMedium.copy(
                        fontWeight = FontWeight.Bold
                    ),
                    color = if (foundCount > 0) CyberEmerald else TextMuted
                )
            }
        }
        Spacer(modifier = Modifier.height(6.dp))
        Text(
            text = if (isScanning) "در حال اسکن شبکه..." else "اسکنر آماده",
            style = MaterialTheme.typography.bodySmall,
            color = if (isScanning) CyberCyan else TextSecondary,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
private fun ScanInfoBar(
    isScanning: Boolean,
    currentIp: String,
    subnetCidr: String,
    scannedCount: Int,
    totalHosts: Int
) {
    Surface(
        shape = RoundedCornerShape(12.dp),
        color = DarkSurfaceVariant,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 16.dp, vertical = 10.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Column {
                Text(
                    text = if (isScanning) "آی‌پی فعال در حال بررسی:"
                    else "محدوده زیرشبکه:",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextMuted
                )
                Text(
                    text = if (isScanning) currentIp.ifBlank { "..." } else subnetCidr,
                    style = MaterialTheme.typography.titleSmall,
                    fontFamily = FontFamily.Monospace,
                    color = if (isScanning) CyberCyan else TextPrimary,
                    fontWeight = FontWeight.Bold
                )
            }
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = "پیشرفت کل:",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextMuted
                )
                Text(
                    text = "$scannedCount از $totalHosts",
                    style = MaterialTheme.typography.titleSmall,
                    fontFamily = FontFamily.Monospace,
                    color = TextSecondary,
                    fontWeight = FontWeight.SemiBold
                )
            }
        }
    }
}

