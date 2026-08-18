package com.example.ui.screens

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
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
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.FlashOn
import androidx.compose.material.icons.filled.GridView
import androidx.compose.material.icons.filled.Memory
import androidx.compose.material.icons.filled.NetworkCheck
import androidx.compose.material.icons.filled.Radar
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material.icons.filled.Thermostat
import androidx.compose.material.icons.filled.ViewList
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material.icons.filled.Wifi
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.local.MinerEntity
import com.example.ui.components.CircularDualArcHashrateGauge
import com.example.ui.components.CircularHashrateGauge
import com.example.ui.components.CircularTemperatureGauge
import com.example.ui.components.GlassmorphicCard
import com.example.ui.components.LiveDualAxisChart
import com.example.ui.components.NeonGlowCard
import com.example.ui.components.SparklineGraph
import com.example.ui.theme.CyberAmber
import com.example.ui.theme.CyberCyan
import com.example.ui.theme.CyberEmerald
import com.example.ui.theme.CyberRed
import com.example.ui.theme.DarkCardBorder
import com.example.ui.theme.DarkSurface
import com.example.ui.theme.DarkSurfaceVariant
import com.example.ui.theme.TextMuted
import com.example.ui.theme.TextSecondary
import com.example.ui.viewmodels.HomeDashboardState
import com.example.ui.viewmodels.HomeViewModel

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun HomeScreen(
    viewModel: HomeViewModel,
    onNavigateToScan: () -> Unit,
    onNavigateToDeviceList: () -> Unit,
    onNavigateToDeviceDetails: (String) -> Unit
) {
    val state by viewModel.dashboardState.collectAsState()
    var isGridView by remember { mutableStateOf(false) }
    var minerToDelete by remember { mutableStateOf<MinerEntity?>(null) }
    var isPeakGaugeMode by remember { mutableStateOf(false) }

    if (minerToDelete != null) {
        AlertDialog(
            onDismissRequest = { minerToDelete = null },
            title = {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Delete,
                        contentDescription = null,
                        tint = CyberRed,
                        modifier = Modifier.size(22.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "حذف ماینر از لیست",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = CyberRed
                    )
                }
            },
            text = {
                Text(
                    text = "آیا از حذف ماینر با آی‌پی ${minerToDelete?.ipAddress} (${minerToDelete?.alias?.ifBlank { minerToDelete?.model }}) مطمئن هستید؟",
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondary
                )
            },
            confirmButton = {
                Button(
                    onClick = {
                        minerToDelete?.let { viewModel.deleteMiner(it.ipAddress) }
                        minerToDelete = null
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = CyberRed, contentColor = Color.White),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text("حذف ماینر", fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                OutlinedButton(
                    onClick = { minerToDelete = null },
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text("انصراف")
                }
            },
            containerColor = DarkSurface,
            shape = RoundedCornerShape(16.dp)
        )
    }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .windowInsetsPadding(WindowInsets.statusBars)
            .padding(horizontal = 14.dp)
            .testTag("home_screen"),
        verticalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        // ==================== Compact Header ====================
        item(key = "header") {
            Spacer(modifier = Modifier.height(2.dp))
            DashboardHeader(
                state = state,
                onRefresh = { viewModel.refreshAll() },
                onSelectInterval = { viewModel.setRefreshInterval(it) }
            )
        }

        // ==================== Compact Gauges & Telemetry ====================
        item(key = "gauges_header") {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                SectionLabel("پایش زنده و telemetry")

                // Quick Mode Switch Chips
                Surface(
                    shape = RoundedCornerShape(10.dp),
                    color = DarkSurfaceVariant,
                    border = androidx.compose.foundation.BorderStroke(1.dp, DarkCardBorder)
                ) {
                    Row(modifier = Modifier.padding(2.dp)) {
                        Surface(
                            shape = RoundedCornerShape(8.dp),
                            color = if (!isPeakGaugeMode) CyberCyan.copy(alpha = 0.25f) else Color.Transparent,
                            border = if (!isPeakGaugeMode) androidx.compose.foundation.BorderStroke(1.dp, CyberCyan) else null,
                            modifier = Modifier
                                .clip(RoundedCornerShape(8.dp))
                                .clickable { isPeakGaugeMode = false }
                        ) {
                            Text(
                                text = "وضعیت کل",
                                style = MaterialTheme.typography.labelSmall.copy(fontSize = 9.sp),
                                color = if (!isPeakGaugeMode) CyberCyan else TextMuted,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(horizontal = 7.dp, vertical = 3.dp)
                            )
                        }

                        Spacer(modifier = Modifier.width(2.dp))

                        Surface(
                            shape = RoundedCornerShape(8.dp),
                            color = if (isPeakGaugeMode) CyberAmber.copy(alpha = 0.25f) else Color.Transparent,
                            border = if (isPeakGaugeMode) androidx.compose.foundation.BorderStroke(1.dp, CyberAmber) else null,
                            modifier = Modifier
                                .clip(RoundedCornerShape(8.dp))
                                .clickable { isPeakGaugeMode = true }
                        ) {
                            Text(
                                text = "🚨 مشکل‌دار",
                                style = MaterialTheme.typography.labelSmall.copy(fontSize = 9.sp),
                                color = if (isPeakGaugeMode) CyberAmber else TextMuted,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(horizontal = 7.dp, vertical = 3.dp)
                            )
                        }
                    }
                }
            }
        }

        item(key = "gauges_row") {
            val maxTempMiner = remember(state.miners) { state.miners.maxByOrNull { it.temperatureC } }
            val minHashMiner = remember(state.miners) { state.miners.filter { it.isOnline }.minByOrNull { it.hashrateThs } }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                if (!isPeakGaugeMode) {
                    // Farm Total & Average Mode (Dual-Arc Track)
                    val targetTotalHash = (state.activeCount * 110.0).coerceAtLeast(110.0)
                    GaugeCard(
                        title = "قدرت کل (گیج ۲ محوره)",
                        subtitle = "${state.activeCount} از ${state.totalCount} دستگاه روشن",
                        targetText = "هدف: ${String.format(java.util.Locale.US, "%.0f", targetTotalHash)} TH/s",
                        glowColor = CyberCyan,
                        modifier = Modifier.weight(1f)
                    ) {
                        CircularDualArcHashrateGauge(
                            liveHashrateThs = if (state.smoothedHashrateThs > 0) state.smoothedHashrateThs else state.totalHashrateThs,
                            avgHashrateThs = targetTotalHash,
                            maxHashrateThs = targetTotalHash * 1.15,
                            gaugeSize = 92.dp
                        )
                    }

                    GaugeCard(
                        title = "دمای کارکرد و برق",
                        subtitle = if (state.totalPowerWatts > 0) "مصرف: ${state.totalPowerWatts}W" else "میانگین دما",
                        targetText = "حد مجاز: ۷۵.۰°C",
                        glowColor = if (state.smoothedAvgTempC > 80) CyberRed else CyberAmber,
                        modifier = Modifier.weight(1f)
                    ) {
                        CircularTemperatureGauge(
                            temperatureC = if (state.smoothedAvgTempC > 0) state.smoothedAvgTempC else state.avgTempC,
                            maxTempC = 100.0,
                            gaugeSize = 92.dp
                        )
                    }
                } else {
                    // Critical Peak Mode
                    val lowestHash = minHashMiner?.hashrateThs ?: 0.0
                    val highestTemp = maxTempMiner?.temperatureC ?: 0.0

                    GaugeCard(
                        title = "ضعیف‌ترین دستگاه",
                        subtitle = minHashMiner?.ipAddress ?: "دستگاهی فعال نیست",
                        targetText = "حد استاندارد: ۷۰ TH",
                        glowColor = if (lowestHash < 70 && lowestHash > 0) CyberRed else CyberAmber,
                        modifier = Modifier.weight(1f)
                    ) {
                        CircularHashrateGauge(
                            hashrateThs = lowestHash,
                            targetHashrateThs = 110.0,
                            gaugeSize = 92.dp
                        )
                    }

                    GaugeCard(
                        title = "داغ‌ترین دستگاه",
                        subtitle = maxTempMiner?.ipAddress ?: "دستگاهی فعال نیست",
                        targetText = "حداکثر دما: ۸۵.۰°C",
                        glowColor = if (highestTemp > 82) CyberRed else CyberAmber,
                        modifier = Modifier.weight(1f)
                    ) {
                        CircularTemperatureGauge(
                            temperatureC = highestTemp,
                            maxTempC = 100.0,
                            gaugeSize = 92.dp
                        )
                    }
                }
            }
        }

        // ==================== Hashboard Imbalance Index ====================
        item(key = "hashboard_imbalance") {
            HashboardImbalanceCard(
                miners = state.miners,
                onNavigateToDeviceDetails = onNavigateToDeviceDetails
            )
        }

        // ==================== Quick Scan CTA ====================
        item(key = "scan_cta") {
            QuickScanCard(
                minerCount = state.totalCount,
                onNavigateToScan = onNavigateToScan,
                onNavigateToDeviceList = onNavigateToDeviceList
            )
        }

        // ==================== Recent Miners ====================
        item(key = "recent_header") {
            RecentMinersHeader(
                hasMiners = state.miners.isNotEmpty(),
                totalCount = state.totalCount,
                isGridView = isGridView,
                onToggleViewMode = { isGridView = !isGridView },
                onViewAll = onNavigateToDeviceList
            )
        }

        if (state.miners.isEmpty()) {
            item(key = "empty_state") {
                EmptyMinersCard()
            }
        } else if (isGridView) {
            val displayMiners = state.miners.take(4)
            val rows = displayMiners.chunked(2)
            items(
                items = rows,
                key = { row -> "home_miner_row_${row.first().ipAddress}" }
            ) { rowMiners ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    rowMiners.forEach { miner ->
                        GridHomeMinerCard(
                            miner = miner,
                            onClick = { onNavigateToDeviceDetails(miner.ipAddress) },
                            onLongClick = { minerToDelete = miner },
                            modifier = Modifier.weight(1f)
                        )
                    }
                    if (rowMiners.size == 1) {
                        Spacer(modifier = Modifier.weight(1f))
                    }
                }
            }
        } else {
            items(
                items = state.miners.take(4),
                key = { miner -> "home_miner_${miner.ipAddress}" }
            ) { miner ->
                HomeMinerCard(
                    miner = miner,
                    onClick = { onNavigateToDeviceDetails(miner.ipAddress) },
                    onLongClick = { minerToDelete = miner }
                )
            }
        }

        item(key = "bottom_spacer") {
            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}

// ==================== Sub-Components ====================

@Composable
private fun SectionLabel(text: String) {
    Text(
        text = text,
        style = MaterialTheme.typography.labelSmall,
        color = TextMuted,
        fontWeight = FontWeight.Bold,
        letterSpacing = 0.5.sp
    )
}

@Composable
private fun GaugeCard(
    title: String,
    glowColor: Color,
    modifier: Modifier = Modifier,
    subtitle: String? = null,
    targetText: String? = null,
    content: @Composable () -> Unit
) {
    val infiniteTransition = rememberInfiniteTransition(label = "gaugePulse")
    val pulseGlowAlpha by infiniteTransition.animateFloat(
        initialValue = 0.35f,
        targetValue = 0.85f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulseGlowAlpha"
    )

    GlassmorphicCard(
        glowColor = glowColor.copy(alpha = pulseGlowAlpha),
        modifier = modifier
    ) {
        Column(
            modifier = Modifier.padding(vertical = 8.dp, horizontal = 6.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.labelMedium.copy(fontSize = 11.sp),
                color = TextSecondary,
                fontWeight = FontWeight.Bold,
                textAlign = androidx.compose.ui.text.style.TextAlign.Center
            )
            if (subtitle != null) {
                Text(
                    text = subtitle,
                    style = MaterialTheme.typography.labelSmall.copy(fontSize = 9.5.sp),
                    color = TextMuted,
                    textAlign = androidx.compose.ui.text.style.TextAlign.Center
                )
            }
            Spacer(modifier = Modifier.height(2.dp))
            content()
            if (targetText != null) {
                Spacer(modifier = Modifier.height(2.dp))
                Surface(
                    shape = RoundedCornerShape(6.dp),
                    color = glowColor.copy(alpha = 0.12f),
                    border = androidx.compose.foundation.BorderStroke(0.6.dp, glowColor.copy(alpha = 0.35f))
                ) {
                    Text(
                        text = targetText,
                        style = MaterialTheme.typography.labelSmall.copy(fontSize = 8.5.sp),
                        color = glowColor,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 1.5.dp)
                    )
                }
            }
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun DashboardHeader(
    state: HomeDashboardState,
    onRefresh: () -> Unit,
    onSelectInterval: (Int) -> Unit
) {
    val infiniteTransition = rememberInfiniteTransition(label = "pulseTransition")
    val pulseScale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1.6f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "pulseScale"
    )
    val pulseAlpha by infiniteTransition.animateFloat(
        initialValue = 0.8f,
        targetValue = 0f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "pulseAlpha"
    )

    val healthScore = remember(state.activeCount, state.totalCount, state.avgTempC) {
        if (state.totalCount == 0) 100 else {
            val activeRatio = state.activeCount.toDouble() / state.totalCount.toDouble()
            val tempFactor = if (state.avgTempC <= 75.0) 1.0
            else maxOf(0.4, 1.0 - (state.avgTempC - 75.0) * 0.03)
            (activeRatio * tempFactor * 100).toInt().coerceIn(0, 100)
        }
    }

    val (healthColor, healthLabel) = remember(healthScore) {
        when {
            healthScore >= 90 -> CyberEmerald to "عالی"
            healthScore >= 70 -> CyberAmber to "متوسط"
            else -> CyberRed to "بحرانی"
        }
    }

    GlassmorphicCard(
        glowColor = healthColor,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(10.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            // Row 1: Title, Health Score Badge, Subnet & Refresh
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        contentAlignment = Alignment.Center,
                        modifier = Modifier.size(16.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(14.dp)
                                .scale(pulseScale)
                                .background(healthColor.copy(alpha = pulseAlpha), CircleShape)
                        )
                        Box(
                            modifier = Modifier
                                .size(8.dp)
                                .background(healthColor, CircleShape)
                        )
                    }
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "داشبورد واتس‌ماینر",
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.Bold,
                            fontSize = 15.sp
                        ),
                        color = MaterialTheme.colorScheme.onBackground
                    )
                }

                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    // Health pill
                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = healthColor.copy(alpha = 0.15f),
                        border = androidx.compose.foundation.BorderStroke(0.5.dp, healthColor.copy(alpha = 0.4f))
                    ) {
                        Text(
                            text = "سلامت $healthScore٪ ($healthLabel)",
                            style = MaterialTheme.typography.labelSmall.copy(fontSize = 9.5.sp),
                            color = healthColor,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }

                    // Subnet pill
                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = CyberCyan.copy(alpha = 0.15f),
                        border = androidx.compose.foundation.BorderStroke(0.5.dp, CyberCyan.copy(alpha = 0.4f))
                    ) {
                        Text(
                            text = state.subnetInfo.subnetCidr,
                            style = MaterialTheme.typography.labelSmall.copy(fontSize = 9.5.sp),
                            color = CyberCyan,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }

                    IconButton(
                        onClick = onRefresh,
                        modifier = Modifier
                            .size(28.dp)
                            .background(DarkSurfaceVariant, CircleShape)
                            .border(1.dp, CyberCyan.copy(alpha = 0.4f), CircleShape)
                            .testTag("refresh_dashboard_button")
                    ) {
                        Icon(
                            imageVector = Icons.Default.Refresh,
                            contentDescription = "به‌روزرسانی داده‌ها",
                            tint = CyberCyan,
                            modifier = Modifier.size(16.dp)
                        )
                    }
                }
            }

            // Row 2: Refresh Speed Controls & Live Progress Bar
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                RefreshIntervalSelector(
                    currentInterval = state.refreshIntervalSec,
                    onSelectInterval = onSelectInterval
                )

                if (state.refreshIntervalSec > 0) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = "بروزرسانی زنده",
                            style = MaterialTheme.typography.labelSmall.copy(fontSize = 9.sp),
                            color = TextMuted
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        TelemetryDataStreamAnimation()
                    }
                }
            }

            // ⚡ Live Refresh Countdown Progress Bar
            if (state.refreshIntervalSec > 0) {
                var progress by remember { mutableFloatStateOf(1f) }

                LaunchedEffect(state.lastUpdatedMillis, state.refreshIntervalSec) {
                    val intervalMs = state.refreshIntervalSec * 1000L
                    val startTime = System.currentTimeMillis()
                    while (true) {
                        val elapsed = System.currentTimeMillis() - startTime
                        val remainingRatio = (1f - elapsed.toFloat() / intervalMs.toFloat()).coerceIn(0f, 1f)
                        progress = remainingRatio
                        if (remainingRatio <= 0f) break
                        kotlinx.coroutines.delay(100L)
                    }
                }

                LinearProgressIndicator(
                    progress = { progress },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(2.5.dp)
                        .clip(RoundedCornerShape(2.dp)),
                    color = CyberCyan,
                    trackColor = DarkSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun TelemetryDataStreamAnimation() {
    val infiniteTransition = rememberInfiniteTransition(label = "dataStream")
    val dotOffset by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 3f,
        animationSpec = infiniteRepeatable(
            animation = tween(900, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "dotOffset"
    )

    Row(
        horizontalArrangement = Arrangement.spacedBy(2.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        for (i in 0..2) {
            val isHigh = (dotOffset.toInt() % 3) == i
            Box(
                modifier = Modifier
                    .size(if (isHigh) 5.dp else 3.5.dp)
                    .background(
                        color = if (isHigh) CyberCyan else CyberCyan.copy(alpha = 0.3f),
                        shape = CircleShape
                    )
            )
        }
    }
}

@Composable
private fun RefreshIntervalSelector(
    currentInterval: Int,
    onSelectInterval: (Int) -> Unit
) {
    val presetIntervals = listOf(
        5 to "۵ث",
        10 to "۱۰ث",
        30 to "۳۰ث",
        60 to "۶۰ث",
        0 to "دستی"
    )

    Row(
        horizontalArrangement = Arrangement.spacedBy(4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = "دوره:",
            style = MaterialTheme.typography.labelSmall.copy(fontSize = 9.5.sp),
            color = TextMuted,
            fontWeight = FontWeight.Bold
        )

        presetIntervals.forEach { (sec, label) ->
            val isSelected = currentInterval == sec
            Surface(
                shape = RoundedCornerShape(8.dp),
                color = if (isSelected) CyberCyan.copy(alpha = 0.25f) else DarkSurface,
                border = androidx.compose.foundation.BorderStroke(
                    width = if (isSelected) 1.dp else 0.5.dp,
                    color = if (isSelected) CyberCyan else DarkCardBorder
                ),
                modifier = Modifier
                    .clickable { onSelectInterval(sec) }
                    .testTag("home_interval_chip_$sec")
            ) {
                Text(
                    text = label,
                    style = MaterialTheme.typography.labelMedium.copy(
                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                        fontSize = 10.sp
                    ),
                    color = if (isSelected) CyberCyan else TextSecondary,
                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                )
            }
        }
    }
}

@Composable
private fun QuickScanCard(
    minerCount: Int,
    onNavigateToScan: () -> Unit,
    onNavigateToDeviceList: () -> Unit
) {
    NeonGlowCard(
        primaryGlow = CyberCyan,
        secondaryGlow = CyberEmerald,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .padding(horizontal = 12.dp, vertical = 8.dp)
                .fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.weight(1f)
            ) {
                Icon(
                    imageVector = Icons.Default.Radar,
                    contentDescription = "اسکن رادار",
                    tint = CyberCyan,
                    modifier = Modifier.size(22.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Column {
                    Text(
                        text = "جستجوی خودکار در شبکه",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onBackground
                    )
                    Text(
                        text = "شناسایی ماینرها | $minerCount دستگاه کشف شده",
                        style = MaterialTheme.typography.labelSmall.copy(fontSize = 10.sp),
                        color = TextSecondary
                    )
                }
            }

            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                Button(
                    onClick = onNavigateToScan,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = CyberCyan,
                        contentColor = Color.Black
                    ),
                    shape = RoundedCornerShape(8.dp),
                    contentPadding = androidx.compose.foundation.layout.PaddingValues(horizontal = 10.dp, vertical = 4.dp),
                    modifier = Modifier.testTag("start_scan_cta_button")
                ) {
                    Text("اسکن شبکه", fontWeight = FontWeight.Bold, fontSize = 11.sp)
                }

                OutlinedButton(
                    onClick = onNavigateToDeviceList,
                    shape = RoundedCornerShape(8.dp),
                    contentPadding = androidx.compose.foundation.layout.PaddingValues(horizontal = 10.dp, vertical = 4.dp),
                    modifier = Modifier.testTag("view_devices_cta_button")
                ) {
                    Text("لیست ($minerCount)", color = CyberCyan, fontSize = 11.sp)
                }
            }
        }
    }
}

@Composable
private fun RecentMinersHeader(
    hasMiners: Boolean,
    totalCount: Int,
    isGridView: Boolean,
    onToggleViewMode: () -> Unit,
    onViewAll: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier = Modifier
                    .size(6.dp)
                    .background(CyberCyan, CircleShape)
            )
            Spacer(modifier = Modifier.width(6.dp))
            Text(
                text = "ماینرهای شناسایی‌شده اخیر",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onBackground,
                fontWeight = FontWeight.Bold,
                letterSpacing = 0.5.sp
            )
        }
        if (hasMiners) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                // View Mode Toggle Button (Grid vs List)
                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = DarkSurfaceVariant,
                    border = androidx.compose.foundation.BorderStroke(
                        0.5.dp, DarkCardBorder
                    ),
                    modifier = Modifier
                        .clickable(onClick = onToggleViewMode)
                        .testTag("toggle_view_mode_button")
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = if (isGridView) Icons.Default.ViewList else Icons.Default.GridView,
                            contentDescription = "تغییر حالت نمایش",
                            tint = CyberCyan,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = if (isGridView) "لیست" else "شبکه",
                            style = MaterialTheme.typography.labelSmall,
                            color = CyberCyan,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }

                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = CyberCyan.copy(alpha = 0.12f),
                    border = androidx.compose.foundation.BorderStroke(
                        0.5.dp, CyberCyan.copy(alpha = 0.3f)
                    ),
                    modifier = Modifier.clickable(onClick = onViewAll)
                ) {
                    Text(
                        text = "مشاهده همه ($totalCount)",
                        style = MaterialTheme.typography.labelSmall,
                        color = CyberCyan,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    )
                }
            }
        }
    }
}

@Composable
private fun EmptyMinersCard() {
    GlassmorphicCard(
        glowColor = DarkCardBorder,
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = Icons.Default.NetworkCheck,
                contentDescription = "خالی",
                tint = TextMuted,
                modifier = Modifier.size(40.dp)
            )
            Spacer(modifier = Modifier.height(12.dp))
            Text(
                text = "هنوز هیچ دستگاه واتس‌ماینری کشف نشده است",
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium,
                color = TextSecondary
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "به وای‌فای متصل شده و اسکن شبکه را شروع کنید.",
                style = MaterialTheme.typography.bodySmall,
                color = TextMuted
            )
        }
    }
}

@Composable
fun MetricCard(
    title: String,
    value: String,
    subtitle: String,
    icon: ImageVector,
    accentColor: Color,
    modifier: Modifier = Modifier
) {
    GlassmorphicCard(
        glowColor = accentColor,
        modifier = modifier
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary
                )
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .background(accentColor.copy(alpha = 0.15f), CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = icon,
                        contentDescription = title,
                        tint = accentColor,
                        modifier = Modifier.size(18.dp)
                    )
                }
            }
            Spacer(modifier = Modifier.height(10.dp))
            Text(
                text = value,
                style = MaterialTheme.typography.titleLarge.copy(
                    fontWeight = FontWeight.Bold
                ),
                color = MaterialTheme.colorScheme.onBackground
            )
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = subtitle,
                style = MaterialTheme.typography.labelSmall,
                color = TextMuted
            )
        }
    }
}

@Composable
fun HomeMinerCard(
    miner: MinerEntity,
    onClick: () -> Unit,
    onLongClick: (() -> Unit)? = null
) {
    // Real current hashrate flat-line representation (no simulated seed fluctuations)
    val realSparklineData = remember(miner.hashrateThs) {
        List(10) { miner.hashrateThs }
    }

    GlassmorphicCard(
        glowColor = if (miner.isOnline) CyberEmerald else CyberRed,
        onClick = onClick,
        onLongClick = onLongClick,
        modifier = Modifier
            .fillMaxWidth()
            .testTag("home_miner_card_${miner.ipAddress}")
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(10.dp)
                        .background(
                            if (miner.isOnline) CyberEmerald else CyberRed,
                            CircleShape
                        )
                )
                Spacer(modifier = Modifier.width(12.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        val displayName = miner.alias.ifBlank { miner.ipAddress }
                        Text(
                            text = displayName.trim(),
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                            color = if (miner.alias.isNotBlank()) CyberCyan
                            else MaterialTheme.colorScheme.onBackground
                        )
                        if (miner.alias.isNotBlank()) {
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = "(${miner.ipAddress})",
                                style = MaterialTheme.typography.bodySmall,
                                color = TextMuted
                            )
                        }
                    }
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = "مدل: ${miner.model.trim()} | هش‌ریت: ${miner.hashrateFormatted.trim()}",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary
                    )
                }

                // Sparkline Graph
                Box(
                    modifier = Modifier
                        .width(70.dp)
                        .padding(horizontal = 4.dp)
                ) {
                    SparklineGraph(
                        dataPoints = realSparklineData,
                        lineColor = if (miner.isOnline) CyberCyan else TextMuted,
                        height = 28.dp
                    )
                }

                Spacer(modifier = Modifier.width(4.dp))

                Icon(
                    imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                    contentDescription = "جزئیات",
                    tint = TextMuted
                )
            }
        }
    }
}

@Composable
fun GridHomeMinerCard(
    miner: MinerEntity,
    onClick: () -> Unit,
    onLongClick: (() -> Unit)? = null,
    modifier: Modifier = Modifier
) {
    // Real current hashrate flat-line representation (no simulated seed fluctuations)
    val realSparklineData = remember(miner.hashrateThs) {
        List(8) { miner.hashrateThs }
    }

    GlassmorphicCard(
        glowColor = if (miner.isOnline) CyberEmerald else CyberRed,
        onClick = onClick,
        onLongClick = onLongClick,
        modifier = modifier.testTag("grid_miner_card_${miner.ipAddress}")
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .background(
                                if (miner.isOnline) CyberEmerald else CyberRed,
                                CircleShape
                            )
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = if (miner.isOnline) "آنلاین" else "آفلاین",
                        style = MaterialTheme.typography.labelSmall,
                        color = if (miner.isOnline) CyberEmerald else CyberRed,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                    contentDescription = "جزئیات",
                    tint = TextMuted,
                    modifier = Modifier.size(16.dp)
                )
            }

            val displayName = miner.alias.ifBlank { miner.ipAddress }
            Text(
                text = displayName.trim(),
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold,
                color = if (miner.alias.isNotBlank()) CyberCyan else MaterialTheme.colorScheme.onBackground,
                maxLines = 1
            )

            if (miner.alias.isNotBlank()) {
                Text(
                    text = miner.ipAddress,
                    style = MaterialTheme.typography.labelSmall,
                    color = TextMuted,
                    fontSize = 10.sp
                )
            }

            // Sparkline Graph
            SparklineGraph(
                dataPoints = realSparklineData,
                lineColor = if (miner.isOnline) CyberCyan else TextMuted,
                height = 24.dp
            )

            Surface(
                color = DarkSurfaceVariant,
                shape = RoundedCornerShape(6.dp)
            ) {
                Text(
                    text = miner.model.trim().ifBlank { "WhatsMiner" },
                    style = MaterialTheme.typography.labelSmall,
                    color = TextSecondary,
                    fontSize = 10.sp,
                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                )
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = miner.hashrateFormatted.trim(),
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Bold,
                        fontSize = 13.sp
                    ),
                    color = CyberCyan
                )

                if (miner.effectiveTemperatureC > 0) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.Thermostat,
                            contentDescription = null,
                            tint = if (miner.effectiveTemperatureC > 80) CyberRed else CyberAmber,
                            modifier = Modifier.size(14.dp)
                        )
                        Text(
                            text = "${miner.effectiveTemperatureC.toInt()}°C",
                            style = MaterialTheme.typography.labelSmall,
                            color = if (miner.effectiveTemperatureC > 80) CyberRed else CyberAmber,
                            fontWeight = FontWeight.Bold,
                            fontSize = 11.sp
                        )
                    }
                }
            }
        }
    }
}

// ==================== Hashboard Imbalance & Health Card ====================

@Composable
private fun HashboardImbalanceCard(
    miners: List<MinerEntity>,
    onNavigateToDeviceDetails: (String) -> Unit
) {
    val activeMiners = remember(miners) { miners.filter { it.isOnline } }
    if (activeMiners.isEmpty()) return

    // Farm-wide board balance analysis
    val totalBoardsExpected = activeMiners.size * 3
    var totalHealthyBoards = 0
    val imbalancedMiners = remember(miners) {
        val list = mutableListOf<Triple<String, String, String>>()
        activeMiners.forEach { miner ->
            val boards = miner.hashboardList
            if (boards.isNotEmpty()) {
                val h1 = boards.getOrNull(0)?.isHealthy == true
                val h2 = boards.getOrNull(1)?.isHealthy == true
                val h3 = boards.getOrNull(2)?.isHealthy == true

                val healthyCount = (if (h1) 1 else 0) + (if (h2) 1 else 0) + (if (h3) 1 else 0)
                totalHealthyBoards += healthyCount

                if (healthyCount < 3) {
                    val issue = "افت توان: $healthyCount از ۳ برد فعال است"
                    list.add(Triple(miner.ipAddress, miner.alias.ifBlank { miner.model }, issue))
                } else {
                    val maxHash = boards.maxOfOrNull { it.hashrateThs } ?: 0.0
                    val minHash = boards.minOfOrNull { it.hashrateThs } ?: 0.0
                    if (maxHash > 0 && minHash > 0 && (maxHash - minHash) / maxHash > 0.35) {
                        val issue = "عدم تقارن بین بردها (${String.format(java.util.Locale.US, "%.1f", minHash)} vs ${String.format(java.util.Locale.US, "%.1f", maxHash)} TH/s)"
                        list.add(Triple(miner.ipAddress, miner.alias.ifBlank { miner.model }, issue))
                    }
                }
            } else {
                if (miner.hashrateThs > 0) {
                    totalHealthyBoards += 3
                }
            }
        }
        list
    }

    var b1Healthy = 0
    var b2Healthy = 0
    var b3Healthy = 0
    activeMiners.forEach { miner ->
        val boards = miner.hashboardList
        if (boards.isNotEmpty()) {
            if (boards.getOrNull(0)?.isHealthy == true) b1Healthy++
            if (boards.getOrNull(1)?.isHealthy == true) b2Healthy++
            if (boards.getOrNull(2)?.isHealthy == true) b3Healthy++
        } else if (miner.hashrateThs > 0) {
            b1Healthy++
            b2Healthy++
            b3Healthy++
        }
    }

    val balancePct = if (totalBoardsExpected > 0) {
        (totalHealthyBoards.toDouble() / totalBoardsExpected * 100.0).coerceIn(0.0, 100.0)
    } else 100.0

    val isBalanced = imbalancedMiners.isEmpty() && balancePct >= 95.0
    val badgeColor = when {
        isBalanced -> CyberEmerald
        balancePct >= 80.0 -> CyberAmber
        else -> CyberRed
    }

    GlassmorphicCard(
        glowColor = badgeColor,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(10.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            // Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Memory,
                        contentDescription = "هش‌بردها",
                        tint = badgeColor,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "شاخص عدم تقارن هش‌بردها",
                        style = MaterialTheme.typography.titleSmall.copy(fontSize = 12.sp, fontWeight = FontWeight.Bold),
                        color = MaterialTheme.colorScheme.onBackground
                    )
                }

                Surface(
                    shape = RoundedCornerShape(10.dp),
                    color = badgeColor.copy(alpha = 0.15f),
                    border = androidx.compose.foundation.BorderStroke(0.5.dp, badgeColor.copy(alpha = 0.4f))
                ) {
                    Text(
                        text = if (isBalanced) "۹۸.۵٪ متوازن (پایدار)" else "${String.format(java.util.Locale.US, "%.1f", balancePct)}٪ تعادل",
                        style = MaterialTheme.typography.labelSmall.copy(fontSize = 9.sp, fontWeight = FontWeight.Bold),
                        color = badgeColor,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
            }

            // 3-Board Distribution Horizontal Bars
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                val b1Pct = if (activeMiners.isNotEmpty()) (b1Healthy.toFloat() / activeMiners.size).coerceIn(0f, 1f) else 1f
                val b2Pct = if (activeMiners.isNotEmpty()) (b2Healthy.toFloat() / activeMiners.size).coerceIn(0f, 1f) else 1f
                val b3Pct = if (activeMiners.isNotEmpty()) (b3Healthy.toFloat() / activeMiners.size).coerceIn(0f, 1f) else 1f

                BoardStatusTrack(label = "برد SM1", progress = b1Pct, activeCount = b1Healthy, totalCount = activeMiners.size, modifier = Modifier.weight(1f))
                BoardStatusTrack(label = "برد SM2", progress = b2Pct, activeCount = b2Healthy, totalCount = activeMiners.size, modifier = Modifier.weight(1f))
                BoardStatusTrack(label = "برد SM3", progress = b3Pct, activeCount = b3Healthy, totalCount = activeMiners.size, modifier = Modifier.weight(1f))
            }

            // Alert Chip or Status Info
            if (imbalancedMiners.isNotEmpty()) {
                val (ip, name, issue) = imbalancedMiners.first()
                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = CyberAmber.copy(alpha = 0.12f),
                    border = androidx.compose.foundation.BorderStroke(0.5.dp, CyberAmber.copy(alpha = 0.35f)),
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onNavigateToDeviceDetails(ip) }
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.weight(1f)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Warning,
                                contentDescription = null,
                                tint = CyberAmber,
                                modifier = Modifier.size(13.dp)
                            )
                            Spacer(modifier = Modifier.width(5.dp))
                            Text(
                                text = "🚨 $ip ($name): $issue",
                                style = MaterialTheme.typography.labelSmall.copy(fontSize = 9.sp),
                                color = CyberAmber,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis
                            )
                        }
                        Text(
                            text = "بررسی >",
                            style = MaterialTheme.typography.labelSmall.copy(fontSize = 8.5.sp, fontWeight = FontWeight.Bold),
                            color = CyberCyan
                        )
                    }
                }
            } else {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.padding(horizontal = 2.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.CheckCircle,
                        contentDescription = null,
                        tint = CyberEmerald,
                        modifier = Modifier.size(12.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "تمامی بردهای ۳گانه در دستگاه‌های روشن متوازن و با راندمان کامل فعال هستند.",
                        style = MaterialTheme.typography.labelSmall.copy(fontSize = 8.5.sp),
                        color = TextMuted
                    )
                }
            }
        }
    }
}

@Composable
private fun BoardStatusTrack(
    label: String,
    progress: Float,
    activeCount: Int,
    totalCount: Int,
    modifier: Modifier = Modifier
) {
    val barColor = when {
        progress >= 0.95f -> CyberCyan
        progress >= 0.75f -> CyberAmber
        else -> CyberRed
    }

    Column(modifier = modifier) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(text = label, style = MaterialTheme.typography.labelSmall.copy(fontSize = 8.5.sp), color = TextMuted)
            Text(text = "$activeCount/$totalCount", style = MaterialTheme.typography.labelSmall.copy(fontSize = 8.5.sp, fontWeight = FontWeight.Bold), color = barColor)
        }
        Spacer(modifier = Modifier.height(2.dp))
        LinearProgressIndicator(
            progress = { progress },
            modifier = Modifier
                .fillMaxWidth()
                .height(3.dp)
                .clip(RoundedCornerShape(2.dp)),
            color = barColor,
            trackColor = DarkSurfaceVariant
        )
    }
}
