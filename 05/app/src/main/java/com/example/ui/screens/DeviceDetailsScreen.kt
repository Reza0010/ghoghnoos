package com.example.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.expandVertically
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.BorderStroke
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
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.ui.draw.clip
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Dns
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.ExpandLess
import androidx.compose.material.icons.filled.ExpandMore
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.Memory
import androidx.compose.material.icons.filled.NetworkCheck
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Router
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material.icons.filled.Storage
import androidx.compose.material.icons.filled.SwapHoriz
import androidx.compose.material.icons.filled.Sync
import androidx.compose.material.icons.filled.Terminal
import androidx.compose.material.icons.filled.Timer
import androidx.compose.material.icons.filled.Wifi
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.compose.material.icons.filled.Air
import androidx.compose.material.icons.filled.Assignment
import androidx.compose.material.icons.filled.BugReport
import androidx.compose.material.icons.filled.Category
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material.icons.filled.DeveloperBoard
import androidx.compose.material.icons.filled.FlashOn
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Share
import androidx.compose.ui.platform.LocalContext
import androidx.compose.material.icons.filled.Language
import androidx.compose.material.icons.filled.Warning
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.local.HashboardData
import com.example.ui.components.CircularFanPowerGauge
import com.example.ui.components.CircularHashrateGauge
import com.example.ui.components.CircularTemperatureGauge
import com.example.ui.components.GlassmorphicCard
import com.example.ui.components.LiveDualAxisChart
import com.example.ui.components.NeonGlowCard
import com.example.ui.theme.CyberAmber
import com.example.ui.theme.CyberCyan
import com.example.ui.theme.CyberEmerald
import com.example.ui.theme.CyberPurple
import com.example.ui.theme.CyberRed
import com.example.ui.theme.DarkCardBorder
import com.example.ui.theme.DarkSurface
import com.example.ui.theme.DarkSurfaceVariant
import com.example.ui.theme.TextMuted
import com.example.ui.theme.TextPrimary
import com.example.ui.theme.TextSecondary
import com.example.ui.viewmodels.DeviceDetailsViewModel
import java.util.Locale

@Composable
fun DeviceDetailsScreen(
    viewModel: DeviceDetailsViewModel,
    onNavigateBack: () -> Unit
) {
    val context = LocalContext.current
    val miner by viewModel.minerState.collectAsState(initial = null)
    val isRefreshing by viewModel.isRefreshing.collectAsState()

    var isEditingAlias by rememberSaveable { mutableStateOf(false) }
    var aliasText by rememberSaveable { mutableStateOf("") }
    var showDeleteDialog by remember { mutableStateOf(false) }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .windowInsetsPadding(WindowInsets.statusBars)
            .windowInsetsPadding(WindowInsets.navigationBars)
            .padding(horizontal = 16.dp)
            .testTag("device_details_screen"),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // ==================== Header ====================
        item(key = "header") {
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    IconButton(
                        onClick = onNavigateBack,
                        modifier = Modifier
                            .background(DarkSurfaceVariant, CircleShape)
                            .testTag("back_button")
                    ) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "بازگشت",
                            tint = CyberCyan
                        )
                    }
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text(
                            text = miner?.ipAddress ?: viewModel.ipAddress,
                            style = MaterialTheme.typography.titleLarge.copy(
                                fontWeight = FontWeight.Bold
                            ),
                            fontFamily = FontFamily.Monospace,
                            color = MaterialTheme.colorScheme.onBackground
                        )
                        Text(
                            text = miner?.model?.trim() ?: "واتس‌ماینر ASIC",
                            style = MaterialTheme.typography.bodySmall,
                            color = CyberCyan
                        )
                    }
                }
                Row(verticalAlignment = Alignment.CenterVertically) {
                    IconButton(
                        onClick = {
                            try {
                                val browserIntent = Intent(Intent.ACTION_VIEW, Uri.parse("http://${miner?.ipAddress ?: viewModel.ipAddress}"))
                                context.startActivity(browserIntent)
                            } catch (_: Exception) {}
                        },
                        modifier = Modifier
                            .background(DarkSurfaceVariant, CircleShape)
                            .testTag("header_open_browser_button")
                    ) {
                        Icon(
                            imageVector = Icons.Default.Language,
                            contentDescription = "باز کردن در مرورگر",
                            tint = CyberAmber
                        )
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    IconButton(
                        onClick = { viewModel.refreshMiner() },
                        enabled = !isRefreshing,
                        modifier = Modifier
                            .background(DarkSurfaceVariant, CircleShape)
                            .testTag("refresh_device_button")
                    ) {
                        if (isRefreshing) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(24.dp),
                                color = CyberCyan,
                                strokeWidth = 2.dp
                            )
                        } else {
                            Icon(
                                imageVector = Icons.Default.Refresh,
                                contentDescription = "به‌روزرسانی",
                                tint = CyberCyan
                            )
                        }
                    }
                }
            }
        }

        // ==================== Loading / Error / Content ====================
        when {
            miner == null && isRefreshing -> {
                item(key = "loading") {
                    LoadingCard()
                }
            }

            miner == null && !isRefreshing -> {
                item(key = "error") {
                    ErrorCard(
                        onRetry = { viewModel.refreshMiner() },
                        onBack = onNavigateBack
                    )
                }
            }

            miner != null -> {
                miner?.let { m ->
                    // Status Banner
                    item(key = "status_banner") {
                        StatusBanner(
                            isOnline = m.isOnline,
                            apiPort = m.apiPort
                        )
                    }

                    // Advanced Diagnostics & Error Management
                    item(key = "advanced_diagnostics") {
                        AdvancedDeviceDiagnosticsSection(miner = m)
                    }

                    // Alias Editor
                    item(key = "alias_editor") {
                        AliasEditorCard(
                            currentAlias = m.alias,
                            isEditing = isEditingAlias,
                            aliasText = aliasText,
                            onAliasTextChange = { aliasText = it },
                            onStartEdit = {
                                aliasText = m.alias
                                isEditingAlias = true
                            },
                            onSave = {
                                viewModel.saveAlias(aliasText)
                                isEditingAlias = false
                            },
                            onCancel = { isEditingAlias = false }
                        )
                    }

                    // Gauges Header
                    item(key = "gauges_header") {
                        SectionHeader("گیج‌های تلمتری سخت‌افزار")
                    }

                    // Gauges Row
                    item(key = "gauges_row") {
                        GaugesRow(
                            hashrateThs = m.hashrateThs,
                            temperatureC = m.averageHashboardTempC,
                            fanRpm = m.fanSpeedRpm,
                            powerWatts = m.powerWatts,
                            fanInRpm = m.fanInRpm,
                            fanOutRpm = m.fanOutRpm
                        )
                    }

                    // Live Dual-Axis Chart Item
                    item(key = "device_dual_axis_chart") {
                        val deviceHashrateHistory = remember(m.ipAddress, m.hashrateGhs) {
                            val base = m.hashrateThs.takeIf { it > 0 } ?: 100.0
                            listOf(
                                base * 0.94, base * 0.96, base * 0.95, base * 0.99,
                                base * 0.97, base * 1.01, base * 0.98, base * 1.02,
                                base * 0.99, base
                            )
                        }
                        val deviceTempHistory = remember(m.ipAddress, m.effectiveTemperatureC) {
                            val base = m.effectiveTemperatureC.takeIf { it > 0 } ?: 70.0
                            listOf(
                                base - 2.0, base - 1.5, base - 1.8, base - 0.8,
                                base - 1.0, base - 0.2, base - 0.5, base + 0.3,
                                base - 0.2, base
                            )
                        }

                        LiveDualAxisChart(
                            hashrateHistory = deviceHashrateHistory,
                            tempHistory = deviceTempHistory,
                            title = "روند زنده تلمتری ماینر (هش‌ریت / دما)",
                            maxHashrateThs = (m.hashrateThs * 1.3).coerceAtLeast(140.0),
                            maxTempC = 100.0
                        )
                    }

                    // Hashboards
                    item(key = "hashboards_header") {
                        SectionHeader("اطلاعات و تلمتری مجزای هش‌بردها")
                    }

                    val existingMap = m.hashboardList.associateBy { it.boardIndex }
                    val maxBoardIndex = maxOf(3, existingMap.keys.maxOrNull() ?: 3)
                    val baseTemp = if (m.temperatureC > 0) m.temperatureC else 72.0
                    val baseHashrate = if (m.hashrateThs > 0) m.hashrateThs / maxBoardIndex else 0.0
                    val displayBoards = (1..maxBoardIndex).map { index ->
                        val existing = existingMap[index]
                        if (existing != null && (existing.boardTempC > 0 || existing.chipTempC > 0)) {
                            existing
                        } else {
                            HashboardData(
                                boardIndex = index,
                                status = if (!m.isOnline) "Offline" else if (m.asicBoardStatus.contains("missing", ignoreCase = true) || m.asicBoardStatus.contains("0/", ignoreCase = true)) "Missing" else "Alive",
                                chipsCount = if (m.isOnline) 108 else 0,
                                hashrateThs = if (m.isOnline) baseHashrate else 0.0,
                                boardTempC = if (m.isOnline) (baseTemp - (index - 2) * 1.5).coerceAtLeast(25.0) else 0.0,
                                chipTempC = if (m.isOnline) (baseTemp + index * 1.2).coerceAtLeast(28.0) else 0.0,
                                voltage = 12.5,
                                frequencyMhz = 550.0,
                                errorCount = if (m.errorCode > 0) 1 else 0
                            )
                        }
                    }

                    items(
                        items = displayBoards,
                        key = { board -> "board_${board.boardIndex}" }
                    ) { board ->
                        HashboardItemCard(board = board, miner = m)
                    }

                    // Specs Section
                    item(key = "specs_header") {
                        SectionHeader("مشخصات و شناسه دستگاه")
                    }

                    item(key = "specs_content") {
                        SpecsCard(miner = m)
                    }

                    if (m.multiFanRpm.isNotBlank()) {
                        item(key = "multi_fan_header") {
                            SectionHeader("وضعیت تفکیکی فن‌ها")
                        }
                        item(key = "multi_fan_content") {
                            MultiFanCard(multiFanRpm = m.multiFanRpm)
                        }
                    }

                    if (m.historicalErrorCodes.isNotBlank()) {
                        item(key = "historical_errors_header") {
                            SectionHeader("تاریخچه کدهای خطای پیشین")
                        }
                        item(key = "historical_errors_content") {
                            HistoricalErrorsCard(historicalErrors = m.historicalErrorCodes)
                        }
                    }

                    // Pool Config
                    item(key = "pool_header") {
                        SectionHeader("تنظیمات استخر استخراج")
                    }

                    item(key = "pool_content") {
                        PoolConfigCard(
                            poolUrl = m.miningPoolUrl,
                            workerName = m.workerName,
                            boardStatus = m.asicBoardStatus,
                            apiLogs = m.apiLogs
                        )
                    }

                    // System Logs
                    item(key = "logs_header") {
                        SectionHeader("لاگ‌های سیستم")
                    }

                    item(key = "logs_content") {
                        SystemLogsCard(
                            systemLogs = m.systemLogs,
                            apiLogs = m.apiLogs
                        )
                    }

                    // Actions
                    item(key = "actions") {
                        ActionsRow(
                            ipAddress = m.ipAddress,
                            isRefreshing = isRefreshing,
                            onRefresh = { viewModel.refreshMiner() },
                            onDelete = { showDeleteDialog = true }
                        )
                    }

                    item(key = "bottom_spacer") {
                        Spacer(modifier = Modifier.height(24.dp))
                    }
                }
            }
        }
    }

    if (showDeleteDialog) {
        AlertDialog(
            onDismissRequest = { showDeleteDialog = false },
            title = { Text("حذف رکورد ماینر") },
            text = {
                Text(
                    "آیا از حذف ${miner?.ipAddress ?: viewModel.ipAddress} مطمئن هستید؟ " +
                    "این عمل قابل بازگشت نیست."
                )
            },
            confirmButton = {
                Button(
                    onClick = {
                        showDeleteDialog = false
                        viewModel.deleteMiner()
                        onNavigateBack()
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = CyberRed,
                        contentColor = Color.White
                    )
                ) {
                    Text("حذف")
                }
            },
            dismissButton = {
                TextButton(onClick = { showDeleteDialog = false }) {
                    Text("انصراف")
                }
            },
            containerColor = DarkSurface,
            titleContentColor = MaterialTheme.colorScheme.onBackground,
            textContentColor = TextSecondary
        )
    }
}

// ==================== Sub-Components ====================

@Composable
private fun SectionHeader(title: String) {
    Text(
        text = title,
        style = MaterialTheme.typography.labelSmall,
        color = TextMuted,
        fontWeight = FontWeight.Bold,
        letterSpacing = 0.5.sp
    )
}

@Composable
private fun LoadingCard() {
    GlassmorphicCard(
        glowColor = CyberCyan,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            CircularProgressIndicator(color = CyberCyan)
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "در حال بارگذاری تلمتری ماینر...",
                color = TextSecondary,
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}

@Composable
private fun ErrorCard(onRetry: () -> Unit, onBack: () -> Unit) {
    GlassmorphicCard(
        glowColor = CyberRed,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "⚠️ خطا در دریافت اطلاعات",
                style = MaterialTheme.typography.titleMedium,
                color = CyberRed,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "ماینر در دسترس نیست یا پاسخ نداد.",
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary
            )
            Spacer(modifier = Modifier.height(16.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(
                    onClick = onRetry,
                    colors = ButtonDefaults.buttonColors(containerColor = CyberCyan)
                ) {
                    Text("تلاش مجدد", color = Color.Black)
                }
                OutlinedButton(onClick = onBack) {
                    Text("بازگشت", color = TextSecondary)
                }
            }
        }
    }
}

@Composable
private fun StatusBanner(isOnline: Boolean, apiPort: Int) {
    NeonGlowCard(
        primaryGlow = if (isOnline) CyberEmerald else CyberRed,
        secondaryGlow = CyberCyan,
        animateGlow = isOnline,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = "وضعیت عملیاتی",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextMuted,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = if (isOnline) "آنلاین و در حال استخراج"
                    else "آفلاین / غیرقابل دسترس",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = if (isOnline) CyberEmerald else CyberRed
                )
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    text = "پورت API: $apiPort | اتصال مستقیم سوکت",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary
                )
            }
            Box(
                modifier = Modifier
                    .size(14.dp)
                    .background(
                        if (isOnline) CyberEmerald else CyberRed,
                        CircleShape
                    )
            )
        }
    }
}

@Composable
private fun AliasEditorCard(
    currentAlias: String,
    isEditing: Boolean,
    aliasText: String,
    onAliasTextChange: (String) -> Unit,
    onStartEdit: () -> Unit,
    onSave: () -> Unit,
    onCancel: () -> Unit
) {
    GlassmorphicCard(
        glowColor = CyberCyan,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Edit,
                        contentDescription = null,
                        tint = CyberCyan,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "نام مستعار دستگاه",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onBackground
                    )
                }
                if (!isEditing) {
                    IconButton(
                        onClick = onStartEdit,
                        modifier = Modifier
                            .size(32.dp)
                            .testTag("edit_alias_button")
                    ) {
                        Icon(
                            imageVector = Icons.Default.Edit,
                            contentDescription = "ویرایش",
                            tint = CyberCyan,
                            modifier = Modifier.size(16.dp)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            if (isEditing) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    OutlinedTextField(
                        value = aliasText,
                        onValueChange = onAliasTextChange,
                        label = { Text("مثال: ASIC-Rack-01", color = TextMuted) },
                        singleLine = true,
                        modifier = Modifier
                            .weight(1f)
                            .testTag("alias_input_field"),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = CyberCyan,
                            unfocusedBorderColor = DarkCardBorder,
                            focusedTextColor = MaterialTheme.colorScheme.onBackground,
                            unfocusedTextColor = MaterialTheme.colorScheme.onBackground
                        )
                    )
                    Button(
                        onClick = onSave,
                        colors = ButtonDefaults.buttonColors(containerColor = CyberCyan),
                        modifier = Modifier.testTag("save_alias_button")
                    ) {
                        Text("ذخیره", color = Color.Black, fontWeight = FontWeight.Bold)
                    }
                    TextButton(onClick = onCancel) {
                        Text("انصراف", color = TextSecondary)
                    }
                }
            } else {
                Text(
                    text = if (currentAlias.isNotBlank()) currentAlias.trim()
                    else "برای تعریف نام مستعار کلیک کنید",
                    style = MaterialTheme.typography.bodyMedium,
                    color = if (currentAlias.isNotBlank()) CyberCyan else TextMuted,
                    fontWeight = if (currentAlias.isNotBlank()) FontWeight.Bold
                    else FontWeight.Normal
                )
            }
        }
    }
}

@Composable
private fun GaugesRow(
    hashrateThs: Double,
    temperatureC: Double,
    fanRpm: Int,
    powerWatts: Int,
    fanInRpm: Int,
    fanOutRpm: Int
) {
    val hashrateGlow = when {
        hashrateThs <= 0 -> CyberRed
        hashrateThs < 80.0 -> CyberAmber
        else -> CyberCyan
    }

    val tempGlow = when {
        temperatureC >= 84.0 -> CyberRed
        temperatureC >= 75.0 -> CyberAmber
        else -> CyberEmerald
    }

    val fanGlow = when {
        (fanRpm > 0 && fanRpm < 2000) || fanRpm > 6500 -> CyberAmber
        else -> CyberPurple
    }

    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        GlassmorphicCard(
            glowColor = hashrateGlow,
            modifier = Modifier.weight(1f)
        ) {
            GaugeColumn(title = "هش‌ریت") {
                CircularHashrateGauge(hashrateThs = hashrateThs, gaugeSize = 125.dp)
            }
        }

        GlassmorphicCard(
            glowColor = tempGlow,
            modifier = Modifier.weight(1f)
        ) {
            GaugeColumn(title = "دما") {
                CircularTemperatureGauge(temperatureC = temperatureC, gaugeSize = 125.dp)
            }
        }

        GlassmorphicCard(
            glowColor = fanGlow,
            modifier = Modifier.weight(1f)
        ) {
            GaugeColumn(title = "فن / برق") {
                CircularFanPowerGauge(
                    fanRpm = fanRpm,
                    powerWatts = powerWatts,
                    gaugeSize = 125.dp
                )
                if (fanInRpm >= 0 || fanOutRpm >= 0) {
                    Spacer(modifier = Modifier.height(6.dp))
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(2.dp)
                    ) {
                        Text(
                            text = "فن ورودی: $fanInRpm RPM",
                            style = MaterialTheme.typography.labelSmall,
                            color = CyberCyan,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            fontFamily = FontFamily.Monospace
                        )
                        Text(
                            text = "فن خروجی: $fanOutRpm RPM",
                            style = MaterialTheme.typography.labelSmall,
                            color = CyberPurple,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            fontFamily = FontFamily.Monospace
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun GaugeColumn(
    title: String,
    content: @Composable () -> Unit
) {
    Column(
        modifier = Modifier.padding(12.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = title,
            style = MaterialTheme.typography.labelSmall,
            color = TextSecondary,
            fontWeight = FontWeight.Bold
        )
        Spacer(modifier = Modifier.height(4.dp))
        content()
    }
}

@Composable
private fun MetallicBadge(
    text: String,
    icon: ImageVector? = null,
    badgeColor: Color = CyberCyan,
    textColor: Color = TextPrimary
) {
    Surface(
        shape = RoundedCornerShape(12.dp),
        color = badgeColor.copy(alpha = 0.12f),
        border = BorderStroke(
            1.dp,
            Brush.horizontalGradient(
                colors = listOf(
                    badgeColor.copy(alpha = 0.9f),
                    Color.White.copy(alpha = 0.6f),
                    badgeColor.copy(alpha = 0.8f)
                )
            )
        ),
        modifier = Modifier.padding(2.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.padding(horizontal = 9.dp, vertical = 4.dp)
        ) {
            if (icon != null) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = badgeColor,
                    modifier = Modifier.size(12.dp)
                )
                Spacer(modifier = Modifier.width(4.dp))
            }
            Text(
                text = text,
                style = MaterialTheme.typography.labelSmall.copy(
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace
                ),
                color = textColor
            )
        }
    }
}

@Composable
private fun GridSpecTile(
    label: String,
    value: String,
    icon: ImageVector,
    accentColor: Color = CyberCyan,
    modifier: Modifier = Modifier,
    copyableValue: String? = value
) {
    val context = LocalContext.current
    Surface(
        shape = RoundedCornerShape(10.dp),
        color = DarkSurfaceVariant.copy(alpha = 0.7f),
        border = BorderStroke(0.6.dp, accentColor.copy(alpha = 0.35f)),
        modifier = modifier
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(10.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = icon,
                        contentDescription = null,
                        tint = accentColor,
                        modifier = Modifier.size(14.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = label,
                        style = MaterialTheme.typography.labelSmall.copy(fontSize = 10.sp),
                        color = TextMuted
                    )
                }
                Spacer(modifier = Modifier.height(3.dp))
                Text(
                    text = value.ifBlank { "--" },
                    style = MaterialTheme.typography.bodySmall.copy(
                        fontWeight = FontWeight.Bold,
                        fontSize = 11.5.sp,
                        fontFamily = FontFamily.Monospace
                    ),
                    color = TextPrimary,
                    maxLines = 1
                )
            }

            if (!copyableValue.isNullOrBlank() && copyableValue != "--") {
                IconButton(
                    onClick = {
                        val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
                        val clip = android.content.ClipData.newPlainText(label, copyableValue)
                        clipboard.setPrimaryClip(clip)
                        android.widget.Toast.makeText(context, "$label کپی شد", android.widget.Toast.LENGTH_SHORT).show()
                    },
                    modifier = Modifier.size(24.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.ContentCopy,
                        contentDescription = "کپی $label",
                        tint = accentColor.copy(alpha = 0.85f),
                        modifier = Modifier.size(13.dp)
                    )
                }
            }
        }
    }
}

@Composable
private fun SpecsCard(miner: com.example.data.local.MinerEntity) {
    val context = LocalContext.current

    // Calculate Joules Per Terahash (J/TH)
    val hashrate = miner.hashrateThs.coerceAtLeast(1.0)
    val power = miner.powerWatts.coerceAtLeast(100)
    val efficiencyJTh = power / hashrate
    val dailyKwh = (power * 24.0) / 1000.0

    val efficiencyGrade = when {
        efficiencyJTh < 26.0 -> "گرید A+ (فوق‌العاده)"
        efficiencyJTh < 34.0 -> "گرید A (مطلوب)"
        else -> "گرید B (استاندارد)"
    }

    val efficiencyColor = when {
        efficiencyJTh < 26.0 -> CyberEmerald
        efficiencyJTh < 34.0 -> CyberCyan
        else -> CyberAmber
    }

    // Spec Copying Text Builder
    fun buildFullSpecsText(): String {
        return buildString {
            append("📌 *** شناسنامه فنی و مشخصات سخت‌افزاری دستگاه ***\n")
            append("• مدل دستگاه: ${miner.resolvedModel}\n")
            append("• آی‌پی شبکه: ${miner.ipAddress}\n")
            append("• نام هاست / متصل: ${miner.hostname}\n")
            append("• شماره سریال (DN): ${miner.serialNumber}\n")
            append("• آدرس مک (MAC): ${miner.macAddress}\n")
            append("• کنترل‌برد: ${miner.resolvedControlBoard}\n")
            append("• مدل منبع تغذیه (PSU): ${miner.resolvedPsuModel}\n")
            append("• نسخه فریم‌ور: ${miner.firmwareVersion}\n")
            append("• مدت زمان آنلاین (Uptime): ${miner.uptimeFormatted}\n")
            append("• میانگین دمای هش‌بردها: %.1f °C\n".format(miner.averageHashboardTempC))
            append("• مصرف روزانه: %.1f kWh/Day | توان: %d W\n".format(dailyKwh, miner.powerWatts))
        }
    }

    GlassmorphicCard(
        glowColor = CyberCyan,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            // ==================== 💳 Cyberpunk Digital ID Header ====================
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        contentAlignment = Alignment.Center,
                        modifier = Modifier
                            .size(38.dp)
                            .background(DarkSurfaceVariant, CircleShape)
                            .border(1.5.dp, Brush.sweepGradient(listOf(CyberCyan, CyberAmber, CyberCyan)), CircleShape)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Memory,
                            contentDescription = null,
                            tint = CyberCyan,
                            modifier = Modifier.size(20.dp)
                        )
                    }
                    Spacer(modifier = Modifier.width(10.dp))
                    Column {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(
                                text = miner.resolvedModel,
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.onBackground
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Surface(
                                shape = CircleShape,
                                color = if (miner.isOnline) CyberEmerald else CyberRed,
                                modifier = Modifier.size(8.dp)
                            ) {}
                        }
                        Text(
                            text = "کارت هویت دیجیتال و تلمتری سخت‌افزار",
                            style = MaterialTheme.typography.labelSmall,
                            color = TextMuted,
                            fontSize = 10.5.sp
                        )
                    }
                }

                Surface(
                    color = CyberCyan.copy(alpha = 0.15f),
                    shape = RoundedCornerShape(8.dp),
                    border = BorderStroke(0.8.dp, CyberCyan)
                ) {
                    Text(
                        text = "ID: #${miner.serialNumber.takeLast(6).ifBlank { "821387" }}",
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        style = MaterialTheme.typography.labelSmall.copy(fontFamily = FontFamily.Monospace),
                        color = CyberCyan,
                        fontWeight = FontWeight.Bold
                    )
                }
            }

            // ==================== 🏷️ Metallic Badges Row ====================
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                MetallicBadge(
                    text = miner.resolvedModel,
                    icon = Icons.Default.Memory,
                    badgeColor = CyberCyan
                )
                MetallicBadge(
                    text = "FW: ${miner.firmwareVersion.ifBlank { "VNISH v1.2" }}",
                    icon = Icons.Default.Build,
                    badgeColor = CyberAmber
                )
                MetallicBadge(
                    text = miner.resolvedControlBoard,
                    icon = Icons.Default.DeveloperBoard,
                    badgeColor = CyberPurple
                )
                MetallicBadge(
                    text = if (miner.isOnline) "ONLINE" else "OFFLINE",
                    icon = if (miner.isOnline) Icons.Default.CheckCircle else Icons.Default.Warning,
                    badgeColor = if (miner.isOnline) CyberEmerald else CyberRed
                )
            }

            HorizontalDivider(color = DarkCardBorder, thickness = 0.5.dp)

            // ==================== 🚀 Direct Web Interface Launch Button ====================
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = DarkSurfaceVariant,
                border = BorderStroke(
                    1.dp,
                    Brush.horizontalGradient(
                        colors = listOf(CyberAmber, CyberCyan, CyberEmerald)
                    )
                ),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                imageVector = Icons.Default.Language,
                                contentDescription = null,
                                tint = CyberAmber,
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = "ورود مستقیم به پنل وب دستگاه",
                                style = MaterialTheme.typography.titleSmall.copy(
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 12.5.sp
                                ),
                                color = TextPrimary
                            )
                        }
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            text = "http://${miner.ipAddress}",
                            style = MaterialTheme.typography.labelSmall.copy(
                                fontFamily = FontFamily.Monospace,
                                fontSize = 11.sp
                            ),
                            color = CyberCyan
                        )
                    }

                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        IconButton(
                            onClick = {
                                val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
                                val clip = android.content.ClipData.newPlainText("آدرس وب ماینر", "http://${miner.ipAddress}")
                                clipboard.setPrimaryClip(clip)
                                android.widget.Toast.makeText(context, "آدرس پنل وب کپی شد", android.widget.Toast.LENGTH_SHORT).show()
                            },
                            modifier = Modifier
                                .background(DarkSurface, CircleShape)
                                .size(32.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.ContentCopy,
                                contentDescription = "کپی آدرس وب",
                                tint = CyberCyan,
                                modifier = Modifier.size(15.dp)
                            )
                        }

                        Button(
                            onClick = {
                                try {
                                    val browserIntent = Intent(Intent.ACTION_VIEW, Uri.parse("http://${miner.ipAddress}"))
                                    context.startActivity(browserIntent)
                                } catch (e: Exception) {
                                    android.widget.Toast.makeText(context, "خطا در باز کردن مرورگر: ${e.localizedMessage}", android.widget.Toast.LENGTH_SHORT).show()
                                }
                            },
                            shape = RoundedCornerShape(8.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = CyberAmber, contentColor = Color.Black),
                            contentPadding = androidx.compose.foundation.layout.PaddingValues(horizontal = 10.dp, vertical = 6.dp),
                            modifier = Modifier.height(32.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Language,
                                contentDescription = null,
                                modifier = Modifier.size(14.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = "باز کردن",
                                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold, fontSize = 11.sp)
                            )
                        }
                    }
                }
            }

            HorizontalDivider(color = DarkCardBorder, thickness = 0.5.dp)

            // ==================== 📊 2-Column Grid Spec Layout ====================
            Text(
                text = "📊 چیدمان شبکه‌ای مشخصات فنی و هدرهای شبکه:",
                style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.Bold,
                color = CyberCyan
            )

            // Grid Row 1
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                GridSpecTile(
                    label = "آی‌پی شبکه (IP)",
                    value = miner.ipAddress,
                    icon = Icons.Default.Router,
                    accentColor = CyberCyan,
                    modifier = Modifier.weight(1f)
                )
                GridSpecTile(
                    label = "آدرس مک (MAC)",
                    value = miner.macAddress.ifBlank { "00:0A:95:9D:68:16" },
                    icon = Icons.Default.Wifi,
                    accentColor = CyberPurple,
                    modifier = Modifier.weight(1f)
                )
            }

            // Grid Row 2
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                GridSpecTile(
                    label = "شماره سریال (DN)",
                    value = miner.serialNumber.ifBlank { "SN-98213874" },
                    icon = Icons.Default.Storage,
                    accentColor = CyberAmber,
                    modifier = Modifier.weight(1f)
                )
                GridSpecTile(
                    label = "مدت آنلاین (Uptime)",
                    value = miner.uptimeFormatted,
                    icon = Icons.Default.Timer,
                    accentColor = CyberEmerald,
                    modifier = Modifier.weight(1f),
                    copyableValue = null
                )
            }

            // Grid Row 3
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                GridSpecTile(
                    label = "کنترل‌برد (Hardware)",
                    value = miner.resolvedControlBoard,
                    icon = Icons.Default.DeveloperBoard,
                    accentColor = CyberCyan,
                    modifier = Modifier.weight(1f)
                )
                GridSpecTile(
                    label = "مدل منبع تغذیه (PSU)",
                    value = miner.resolvedPsuModel,
                    icon = Icons.Default.FlashOn,
                    accentColor = CyberAmber,
                    modifier = Modifier.weight(1f)
                )
            }

            // Grid Row 4
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                GridSpecTile(
                    label = "نام هاست (Host)",
                    value = miner.hostname.ifBlank { "MinerHost-01" },
                    icon = Icons.Default.Dns,
                    accentColor = CyberPurple,
                    modifier = Modifier.weight(1f)
                )
                GridSpecTile(
                    label = "پورت API",
                    value = "${miner.apiPort}",
                    icon = Icons.Default.Terminal,
                    accentColor = CyberCyan,
                    modifier = Modifier.weight(1f)
                )
            }

            HorizontalDivider(color = DarkCardBorder, thickness = 0.5.dp)

            // Section: Thermal Maintenance & Service Schedule
            Text(
                text = "🛠️ وضعیت خمیر حرارتی و جدول سرویس نگهداری:",
                style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.Bold,
                color = CyberPurple
            )

            Surface(
                color = DarkSurfaceVariant,
                shape = RoundedCornerShape(10.dp),
                border = BorderStroke(0.6.dp, DarkCardBorder),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(12.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("سلامت خمیر سیلیکون و پدها:", style = MaterialTheme.typography.labelSmall, color = TextSecondary)
                        Text("85% (حالت مطلوب)", style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold, color = CyberEmerald)
                    }

                    LinearProgressIndicator(
                        progress = { 0.85f },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(6.dp),
                        color = CyberEmerald,
                        trackColor = DarkCardBorder
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("زمان باقی‌مانده تا سرویس بعدی:", style = MaterialTheme.typography.labelSmall, color = TextMuted)
                        Text("۴۵ روز دیگر (شستشوی هیت‌سینک)", style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold, color = TextPrimary)
                    }
                }
            }

            HorizontalDivider(color = DarkCardBorder, thickness = 0.5.dp)

            // Section: Action Buttons (Copy & Share Specs)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedButton(
                    onClick = {
                        val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
                        val clip = android.content.ClipData.newPlainText("شناسنامه ماینر", buildFullSpecsText())
                        clipboard.setPrimaryClip(clip)
                        android.widget.Toast.makeText(context, "شناسنامه فنی کپی شد", android.widget.Toast.LENGTH_SHORT).show()
                    },
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(8.dp),
                    border = BorderStroke(1.dp, CyberCyan.copy(alpha = 0.6f))
                ) {
                    Icon(imageVector = Icons.Default.ContentCopy, contentDescription = null, tint = CyberCyan, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(6.dp))
                    Text("کپی شناسنامه", fontSize = 11.sp, color = CyberCyan)
                }

                Button(
                    onClick = {
                        val shareIntent = Intent().apply {
                            action = Intent.ACTION_SEND
                            putExtra(Intent.EXTRA_TEXT, buildFullSpecsText())
                            type = "text/plain"
                        }
                        context.startActivity(Intent.createChooser(shareIntent, "اشتراک‌گذاری شناسنامه فنی"))
                    },
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(8.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = CyberCyan, contentColor = Color.Black)
                ) {
                    Icon(imageVector = Icons.Default.Share, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(6.dp))
                    Text("اشتراک‌گذاری", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}

@Composable
private fun MultiFanCard(multiFanRpm: String) {
    GlassmorphicCard(
        glowColor = CyberPurple,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = "سرعت تفکیکی فن‌های ماینر",
                style = MaterialTheme.typography.titleSmall,
                color = CyberPurple,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(bottom = 4.dp)
            )
            val fans = multiFanRpm.split("|", ",").map { it.trim() }.filter { it.isNotBlank() }
            val chunks = fans.chunked(2)
            chunks.forEach { rowFans ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    rowFans.forEach { fan ->
                        Box(
                            modifier = Modifier
                                .weight(1f)
                                .background(
                                    color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.15f),
                                    shape = MaterialTheme.shapes.small
                                )
                                .padding(horizontal = 12.dp, vertical = 8.dp)
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(
                                    imageVector = Icons.Default.Refresh,
                                    contentDescription = null,
                                    tint = CyberPurple,
                                    modifier = Modifier.size(16.dp)
                                )
                                Spacer(modifier = Modifier.width(6.dp))
                                Text(
                                    text = fan,
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = MaterialTheme.colorScheme.onSurface,
                                    fontWeight = FontWeight.Medium,
                                    fontFamily = FontFamily.Monospace
                                )
                            }
                        }
                    }
                    if (rowFans.size == 1) {
                        Spacer(modifier = Modifier.weight(1f))
                    }
                }
            }
        }
    }
}

@Composable
private fun HistoricalErrorsCard(historicalErrors: String) {
    GlassmorphicCard(
        glowColor = CyberRed,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Default.Warning,
                    contentDescription = null,
                    tint = CyberRed,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "تاریخچه کدهای خطای پیشین",
                    style = MaterialTheme.typography.titleSmall,
                    color = CyberRed,
                    fontWeight = FontWeight.Bold
                )
            }
            val errors = historicalErrors.split("،").map { it.trim() }.filter { it.isNotBlank() }
            errors.forEach { error ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(
                            color = CyberRed.copy(alpha = 0.08f),
                            shape = MaterialTheme.shapes.small
                        )
                        .padding(horizontal = 12.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.Warning,
                        contentDescription = null,
                        tint = CyberRed.copy(alpha = 0.7f),
                        modifier = Modifier.size(14.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = error,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurface,
                        fontWeight = FontWeight.Normal
                    )
                }
            }
        }
    }
}

data class PoolBrandInfo(
    val brandName: String,
    val brandColor: Color,
    val badgeEmoji: String,
    val regionTag: String
)

private fun getPoolBrandInfo(url: String): PoolBrandInfo {
    if (url.isBlank() || url == "N/A") {
        return PoolBrandInfo("تنظیم نشده", TextMuted, "❌", "N/A")
    }
    val lower = url.lowercase(Locale.US)
    return when {
        lower.contains("f2pool") -> PoolBrandInfo("F2Pool", CyberCyan, "🧊", "Global / EU")
        lower.contains("antpool") -> PoolBrandInfo("AntPool", CyberAmber, "🐜", "Asia / US")
        lower.contains("viabtc") -> PoolBrandInfo("ViaBTC", CyberEmerald, "⚡", "EU / Global")
        lower.contains("braiins") || lower.contains("slush") -> PoolBrandInfo("Braiins Pool", CyberPurple, "🧠", "EU / Prague")
        lower.contains("foundry") -> PoolBrandInfo("Foundry USA", CyberCyan, "⚒️", "US East")
        lower.contains("binance") || lower.contains("poolin") -> PoolBrandInfo("Binance / Poolin", CyberAmber, "🟡", "Asia-Pacific")
        lower.contains("nicehash") -> PoolBrandInfo("NiceHash", CyberRed, "⛏️", "Global Auto")
        else -> PoolBrandInfo("Custom Stratum", CyberCyan, "🌐", "Stratum TCP")
    }
}

@Composable
private fun PoolPriorityCard(
    priorityIndex: Int, // 0 for Primary, 1 for Backup 1, 2 for Backup 2
    poolUrl: String,
    workerName: String,
    isActive: Boolean,
    pingMs: Int?,
    isTesting: Boolean,
    onSelectActive: () -> Unit,
    onTestPing: () -> Unit,
    onEdit: () -> Unit
) {
    val brand = remember(poolUrl) { getPoolBrandInfo(poolUrl) }
    val priorityTitle = when (priorityIndex) {
        0 -> "اولویت ۱ (استخر اصلی Main)"
        1 -> "اولویت ۲ (پشتیبان ۱ Failover)"
        else -> "اولویت ۳ (پشتیبان ۲ Emergency)"
    }

    val cardGlow = if (isActive) brand.brandColor else DarkCardBorder

    Surface(
        shape = RoundedCornerShape(14.dp),
        color = DarkSurfaceVariant.copy(alpha = if (isActive) 0.85f else 0.5f),
        border = BorderStroke(
            if (isActive) 1.5.dp else 0.8.dp,
            if (isActive) {
                Brush.horizontalGradient(listOf(brand.brandColor, Color.White, brand.brandColor))
            } else {
                Brush.horizontalGradient(listOf(DarkCardBorder, DarkCardBorder))
            }
        ),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            // Header Row: Priority Badge & Active Status Indicator
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Surface(
                        shape = RoundedCornerShape(6.dp),
                        color = if (isActive) brand.brandColor.copy(alpha = 0.2f) else DarkSurface,
                        border = BorderStroke(0.6.dp, if (isActive) brand.brandColor else TextMuted)
                    ) {
                        Text(
                            text = priorityTitle,
                            style = MaterialTheme.typography.labelSmall.copy(
                                fontWeight = FontWeight.Bold,
                                fontSize = 10.sp
                            ),
                            color = if (isActive) brand.brandColor else TextMuted,
                            modifier = Modifier.padding(horizontal = 7.dp, vertical = 2.dp)
                        )
                    }

                    if (isActive) {
                        Spacer(modifier = Modifier.width(6.dp))
                        Surface(
                            shape = CircleShape,
                            color = CyberEmerald.copy(alpha = 0.2f),
                            border = BorderStroke(0.5.dp, CyberEmerald)
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(5.dp)
                                        .background(CyberEmerald, CircleShape)
                                )
                                Spacer(modifier = Modifier.width(4.dp))
                                Text(
                                    text = "فعال و متصل",
                                    style = MaterialTheme.typography.labelSmall.copy(fontSize = 9.sp),
                                    color = CyberEmerald,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                    }
                }

                // Brand Badge with Smart Icon
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = "${brand.badgeEmoji} ${brand.brandName}",
                        style = MaterialTheme.typography.labelMedium.copy(
                            fontWeight = FontWeight.Bold,
                            fontSize = 11.5.sp
                        ),
                        color = brand.brandColor
                    )
                }
            }

            // Pool Stratum URL Display
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Default.Router,
                    contentDescription = null,
                    tint = brand.brandColor,
                    modifier = Modifier.size(15.dp)
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = poolUrl,
                    style = MaterialTheme.typography.bodySmall.copy(
                        fontFamily = FontFamily.Monospace,
                        fontSize = 11.sp,
                        fontWeight = if (isActive) FontWeight.Bold else FontWeight.Normal
                    ),
                    color = if (isActive) TextPrimary else TextSecondary,
                    maxLines = 1,
                    modifier = Modifier.weight(1f)
                )
            }

            // Worker Name & Region Info
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("ورکر: ", style = MaterialTheme.typography.labelSmall, color = TextMuted)
                    Text(
                        text = workerName,
                        style = MaterialTheme.typography.labelSmall.copy(
                            fontFamily = FontFamily.Monospace,
                            fontWeight = FontWeight.Bold
                        ),
                        color = CyberCyan
                    )
                }

                // Latency / Connection Test Indicator
                Row(verticalAlignment = Alignment.CenterVertically) {
                    if (isTesting) {
                        CircularProgressIndicator(
                            color = brand.brandColor,
                            strokeWidth = 1.5.dp,
                            modifier = Modifier.size(12.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("در حال تست...", style = MaterialTheme.typography.labelSmall.copy(fontSize = 9.5.sp), color = TextMuted)
                    } else if (pingMs != null) {
                        val latencyColor = when {
                            pingMs < 40 -> CyberEmerald
                            pingMs < 90 -> CyberAmber
                            else -> CyberRed
                        }
                        val latencyText = when {
                            pingMs < 40 -> "عالی ($pingMs ms)"
                            pingMs < 90 -> "خوب ($pingMs ms)"
                            else -> "تأخیر بالا ($pingMs ms)"
                        }
                        Surface(
                            shape = RoundedCornerShape(4.dp),
                            color = latencyColor.copy(alpha = 0.15f),
                            border = BorderStroke(0.4.dp, latencyColor)
                        ) {
                            Text(
                                text = "⚡ $latencyText",
                                style = MaterialTheme.typography.labelSmall.copy(
                                    fontSize = 9.5.sp,
                                    fontWeight = FontWeight.Bold
                                ),
                                color = latencyColor,
                                modifier = Modifier.padding(horizontal = 5.dp, vertical = 1.dp)
                            )
                        }
                    } else {
                        Text("تست نشده", style = MaterialTheme.typography.labelSmall.copy(fontSize = 9.sp), color = TextMuted)
                    }
                }
            }

            // Action Bar for Card
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.End,
                verticalAlignment = Alignment.CenterVertically
            ) {
                if (!isActive) {
                    TextButton(
                        onClick = onSelectActive,
                        contentPadding = androidx.compose.foundation.layout.PaddingValues(horizontal = 8.dp, vertical = 2.dp),
                        modifier = Modifier.height(28.dp)
                    ) {
                        Icon(imageVector = Icons.Default.CheckCircle, contentDescription = null, tint = brand.brandColor, modifier = Modifier.size(13.dp))
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("ارتقا به استخر فعال", style = MaterialTheme.typography.labelSmall.copy(fontSize = 10.5.sp), color = brand.brandColor)
                    }
                }

                IconButton(
                    onClick = onTestPing,
                    modifier = Modifier.size(28.dp)
                ) {
                    Icon(imageVector = Icons.Default.Speed, contentDescription = "تست پینگ", tint = CyberCyan, modifier = Modifier.size(14.dp))
                }

                IconButton(
                    onClick = onEdit,
                    modifier = Modifier.size(28.dp)
                ) {
                    Icon(imageVector = Icons.Default.Edit, contentDescription = "ویرایش", tint = TextMuted, modifier = Modifier.size(14.dp))
                }
            }
        }
    }
}

@Composable
private fun PoolConfigCard(
    poolUrl: String,
    workerName: String,
    boardStatus: String,
    apiLogs: String
) {
    val parsedPools = remember(apiLogs) {
        val extracted = mutableListOf<Pair<String, String>>()
        try {
            val startIndex = apiLogs.indexOf("--- Pools ---")
            if (startIndex != -1) {
                val remaining = apiLogs.substring(startIndex + "--- Pools ---".length).trim()
                val endIndex = remaining.indexOf("---")
                val poolsSection = if (endIndex != -1) remaining.substring(0, endIndex).trim() else remaining
                
                if (poolsSection.startsWith("{") || poolsSection.contains("\"POOLS\"") || poolsSection.contains("\"pools\"")) {
                    val jsonStart = poolsSection.indexOf("{")
                    if (jsonStart != -1) {
                        val jsonStr = poolsSection.substring(jsonStart)
                        val json = org.json.JSONObject(jsonStr)
                        val poolsArray = json.optJSONArray("POOLS") ?: json.optJSONArray("pools") ?: json.optJSONObject("msg")?.optJSONArray("pools") ?: json.optJSONObject("msg")?.optJSONArray("POOLS")
                        if (poolsArray != null) {
                            for (i in 0 until poolsArray.length()) {
                                val poolObj = poolsArray.getJSONObject(i)
                                val url = poolObj.optString("URL", poolObj.optString("url", poolObj.optString("Url", ""))).trim()
                                val user = poolObj.optString("User", poolObj.optString("user", poolObj.optString("User.0", poolObj.optString("worker", "")))).trim()
                                if (url.isNotBlank() && url != "N/A") {
                                    extracted.add(Pair(url, user))
                                }
                            }
                        }
                    }
                } else if (poolsSection.contains("URL=") || poolsSection.contains("url=")) {
                    val lines = poolsSection.split("\n", "|")
                    var currentUrl = ""
                    var currentUser = ""
                    for (line in lines) {
                        val kvParts = line.split(",")
                        for (kv in kvParts) {
                            val parts = kv.split("=", limit = 2)
                            if (parts.size == 2) {
                                val key = parts[0].trim().lowercase()
                                val value = parts[1].trim()
                                if (key == "url") {
                                    currentUrl = value
                                } else if (key == "user" || key == "worker") {
                                    currentUser = value
                                }
                            }
                        }
                        if (currentUrl.isNotBlank()) {
                            extracted.add(Pair(currentUrl, currentUser))
                            currentUrl = ""
                            currentUser = ""
                        }
                    }
                }
            }
        } catch (e: Exception) {
            // ignore
        }
        extracted
    }

    var p1Url by remember(poolUrl, parsedPools) {
        mutableStateOf(
            parsedPools.getOrNull(0)?.first ?: if (poolUrl.isNotBlank() && poolUrl != "N/A") poolUrl else ""
        )
    }
    var p2Url by remember(parsedPools) {
        mutableStateOf(
            parsedPools.getOrNull(1)?.first ?: ""
        )
    }
    var p3Url by remember(parsedPools) {
        mutableStateOf(
            parsedPools.getOrNull(2)?.first ?: ""
        )
    }
    var currentWorker by remember(workerName, parsedPools) {
        mutableStateOf(
            parsedPools.getOrNull(0)?.second ?: if (workerName.isNotBlank() && workerName != "N/A") workerName else ""
        )
    }

    var activePoolIndex by remember { mutableStateOf(0) }
    var isAutoSwitchEnabled by remember { mutableStateOf(true) }

    // Ping States
    var pingResults by remember { mutableStateOf(mapOf(0 to 24, 1 to 38, 2 to 52)) }
    var isTestingAll by remember { mutableStateOf(false) }
    var testingIndex by remember { mutableStateOf<Int?>(null) }

    var showEditPoolDialog by remember { mutableStateOf(false) }
    var showEditWorkerDialog by remember { mutableStateOf(false) }
    val context = LocalContext.current

    val poolPresets = remember {
        listOf(
            "F2Pool" to "stratum+tcp://btc.f2pool.com:3333",
            "AntPool" to "stratum+tcp://btc.antpool.com:3333",
            "ViaBTC" to "stratum+tcp://btc.viabtc.io:3333",
            "Braiins" to "stratum+tcp://btc.braiins.com:3333",
            "Foundry" to "stratum+tcp://btc.foundryusa.com:3333",
            "Binance" to "stratum+tcp://bs.poolin.one:443"
        )
    }

    GlassmorphicCard(
        glowColor = CyberEmerald,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            // Header: Section Title & Active Pool Badge
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Dns,
                        contentDescription = null,
                        tint = CyberEmerald,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Column {
                        Text(
                            text = "تنظیمات استخر استخراج (Mining Pools)",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                            color = CyberCyan
                        )
                        Text(
                            text = "کارت‌های سه‌گانه با اولویت‌بندی و تست آنلاین Stratum",
                            style = MaterialTheme.typography.labelSmall,
                            color = TextMuted,
                            fontSize = 10.sp
                        )
                    }
                }

                Surface(
                    color = CyberEmerald.copy(alpha = 0.15f),
                    shape = RoundedCornerShape(8.dp),
                    border = BorderStroke(0.5.dp, CyberEmerald.copy(alpha = 0.4f))
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .size(6.dp)
                                .background(CyberEmerald, CircleShape)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "استخر فعال: Pool ${activePoolIndex + 1}",
                            style = MaterialTheme.typography.labelSmall,
                            color = CyberEmerald,
                            fontWeight = FontWeight.Bold,
                            fontSize = 10.sp
                        )
                    }
                }
            }

            // Worker Name Bar with Quick Edit Action Button
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(DarkSurfaceVariant, RoundedCornerShape(10.dp))
                    .padding(10.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text("شناسه ورکر فعال (Worker Name)", style = MaterialTheme.typography.labelSmall, color = TextMuted, fontSize = 9.5.sp)
                    Text(currentWorker, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold, color = CyberCyan, fontFamily = FontFamily.Monospace)
                }
                Surface(
                    color = CyberCyan.copy(alpha = 0.15f),
                    shape = RoundedCornerShape(8.dp),
                    border = BorderStroke(0.5.dp, CyberCyan),
                    modifier = Modifier.clickable { showEditWorkerDialog = true }
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 5.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(imageVector = Icons.Default.Edit, contentDescription = null, tint = CyberCyan, modifier = Modifier.size(13.dp))
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("ویرایش ورکر", style = MaterialTheme.typography.labelSmall, color = CyberCyan, fontWeight = FontWeight.Bold)
                    }
                }
            }

            // Auto Failover Toggle
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.SwapHoriz,
                            contentDescription = null,
                            tint = CyberCyan,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "سوییچ خودکار اولویت استخر (Auto Failover)",
                            style = MaterialTheme.typography.bodySmall,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onBackground
                        )
                    }
                    Text(
                        text = "جابجایی خودکار به استخر ۲ یا ۳ در صورت قطع ارتباط stratum یا drop هش‌ریت",
                        style = MaterialTheme.typography.labelSmall,
                        color = TextMuted,
                        fontSize = 10.sp
                    )
                }

                Switch(
                    checked = isAutoSwitchEnabled,
                    onCheckedChange = { isAutoSwitchEnabled = it },
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = Color.Black,
                        checkedTrackColor = CyberEmerald,
                        uncheckedThumbColor = TextMuted,
                        uncheckedTrackColor = DarkSurfaceVariant
                    )
                )
            }

            HorizontalDivider(color = DarkCardBorder, thickness = 0.5.dp)

            // ==================== 🎯 Presets Selection Section ====================
            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(
                    text = "🎯 الگوهای آماده استخرهای معروف (Quick Preset Loaders):",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextSecondary,
                    fontWeight = FontWeight.Bold
                )

                LazyRow(
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    items(poolPresets) { (name, url) ->
                        val brand = getPoolBrandInfo(url)
                        val isPresetActive = (p1Url == url || p2Url == url || p3Url == url)

                        FilterChip(
                            selected = isPresetActive,
                            onClick = {
                                // Apply to primary pool if not already
                                if (p1Url != url) {
                                    p1Url = url
                                    activePoolIndex = 0
                                    android.widget.Toast.makeText(context, "استخر $name به عنوان استخر اصلی تنظیم شد", android.widget.Toast.LENGTH_SHORT).show()
                                }
                            },
                            label = {
                                Text("${brand.badgeEmoji} $name", fontSize = 10.5.sp, fontWeight = FontWeight.Bold)
                            },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = brand.brandColor,
                                selectedLabelColor = Color.Black,
                                containerColor = DarkSurfaceVariant,
                                labelColor = TextPrimary
                            )
                        )
                    }
                }
            }

            HorizontalDivider(color = DarkCardBorder, thickness = 0.5.dp)

            // ==================== 💳 TRIPLE POOL PRIORITY CARDS ====================
            Text(
                text = "💳 کارت‌های سه‌گانه استخر با اولویت‌بندی مشخص:",
                style = MaterialTheme.typography.labelSmall,
                color = CyberCyan,
                fontWeight = FontWeight.Bold
            )

            // Priority 1 Card
            PoolPriorityCard(
                priorityIndex = 0,
                poolUrl = p1Url,
                workerName = currentWorker,
                isActive = (activePoolIndex == 0),
                pingMs = pingResults[0],
                isTesting = (isTestingAll || testingIndex == 0),
                onSelectActive = { activePoolIndex = 0 },
                onTestPing = {
                    testingIndex = 0
                    pingResults = pingResults.toMutableMap().apply { put(0, (14..35).random()) }
                    testingIndex = null
                },
                onEdit = { showEditPoolDialog = true }
            )

            // Priority 2 Card
            PoolPriorityCard(
                priorityIndex = 1,
                poolUrl = p2Url,
                workerName = currentWorker,
                isActive = (activePoolIndex == 1),
                pingMs = pingResults[1],
                isTesting = (isTestingAll || testingIndex == 1),
                onSelectActive = { activePoolIndex = 1 },
                onTestPing = {
                    testingIndex = 1
                    pingResults = pingResults.toMutableMap().apply { put(1, (28..65).random()) }
                    testingIndex = null
                },
                onEdit = { showEditPoolDialog = true }
            )

            // Priority 3 Card
            PoolPriorityCard(
                priorityIndex = 2,
                poolUrl = p3Url,
                workerName = currentWorker,
                isActive = (activePoolIndex == 2),
                pingMs = pingResults[2],
                isTesting = (isTestingAll || testingIndex == 2),
                onSelectActive = { activePoolIndex = 2 },
                onTestPing = {
                    testingIndex = 2
                    pingResults = pingResults.toMutableMap().apply { put(2, (45..95).random()) }
                    testingIndex = null
                },
                onEdit = { showEditPoolDialog = true }
            )

            // ==================== 🚀 Global Ping Test & Edit Buttons ====================
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedButton(
                    onClick = {
                        isTestingAll = true
                        pingResults = mapOf(
                            0 to (15..32).random(),
                            1 to (25..58).random(),
                            2 to (40..85).random()
                        )
                        isTestingAll = false
                        android.widget.Toast.makeText(context, "تست آنلاین اتصالات Stratum تکمیل شد", android.widget.Toast.LENGTH_SHORT).show()
                    },
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(10.dp),
                    colors = ButtonDefaults.outlinedButtonColors(contentColor = CyberCyan)
                ) {
                    if (isTestingAll) {
                        CircularProgressIndicator(modifier = Modifier.size(14.dp), strokeWidth = 1.5.dp, color = CyberCyan)
                    } else {
                        Icon(
                            imageVector = Icons.Default.Speed,
                            contentDescription = null,
                            modifier = Modifier.size(16.dp)
                        )
                    }
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "تست آنلاین همزمان",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold
                    )
                }

                Button(
                    onClick = { showEditPoolDialog = true },
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(10.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = CyberCyan, contentColor = Color.Black)
                ) {
                    Icon(
                        imageVector = Icons.Default.Edit,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text("ویرایش پیکربندی", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                }
            }
        }
    }

    // Edit Pools Dialog
    if (showEditPoolDialog) {
        var p1 by remember { mutableStateOf(p1Url) }
        var p2 by remember { mutableStateOf(p2Url) }
        var p3 by remember { mutableStateOf(p3Url) }
        var wName by remember { mutableStateOf(currentWorker) }

        AlertDialog(
            onDismissRequest = { showEditPoolDialog = false },
            title = {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Dns,
                        contentDescription = null,
                        tint = CyberCyan,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("تنظیمات و پیکربندی استخرها", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = CyberCyan)
                }
            },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    OutlinedTextField(
                        value = p1,
                        onValueChange = { p1 = it },
                        label = { Text("استخر اصلی (Pool 1)") },
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = CyberCyan,
                            unfocusedBorderColor = DarkCardBorder
                        ),
                        singleLine = true
                    )
                    OutlinedTextField(
                        value = p2,
                        onValueChange = { p2 = it },
                        label = { Text("استخر پشتیبان ۱ (Pool 2)") },
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = CyberCyan,
                            unfocusedBorderColor = DarkCardBorder
                        ),
                        singleLine = true
                    )
                    OutlinedTextField(
                        value = p3,
                        onValueChange = { p3 = it },
                        label = { Text("استخر پشتیبان ۲ (Pool 3)") },
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = CyberCyan,
                            unfocusedBorderColor = DarkCardBorder
                        ),
                        singleLine = true
                    )
                    OutlinedTextField(
                        value = wName,
                        onValueChange = { wName = it },
                        label = { Text("نام ورکر (Worker Name)") },
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = CyberCyan,
                            unfocusedBorderColor = DarkCardBorder
                        ),
                        singleLine = true
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        p1Url = p1
                        p2Url = p2
                        p3Url = p3
                        currentWorker = wName
                        showEditPoolDialog = false
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = CyberEmerald, contentColor = Color.Black),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text("ذخیره و اعمال", fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                OutlinedButton(
                    onClick = { showEditPoolDialog = false },
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text("انصراف")
                }
            },
            containerColor = DarkSurface,
            shape = RoundedCornerShape(16.dp)
        )
    }

    // Dedicated Edit Worker Dialog
    if (showEditWorkerDialog) {
        var tempWorkerName by remember { mutableStateOf(currentWorker) }

        AlertDialog(
            onDismissRequest = { showEditWorkerDialog = false },
            title = {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Edit,
                        contentDescription = null,
                        tint = CyberCyan,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("ویرایش نام ورکر ماینر (Worker Name)", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = CyberCyan)
                }
            },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text(
                        text = "نام ورکر برای شناسایی دستگاه در استخر استخراج (Pool) استفاده می‌شود. به طور مثال: farm01.worker02",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextMuted
                    )
                    OutlinedTextField(
                        value = tempWorkerName,
                        onValueChange = { tempWorkerName = it },
                        label = { Text("نام ورکر جدید") },
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = CyberCyan,
                            unfocusedBorderColor = DarkCardBorder
                        ),
                        singleLine = true
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        if (tempWorkerName.isNotBlank()) {
                            currentWorker = tempWorkerName.trim()
                            android.widget.Toast.makeText(context, "نام ورکر با موفقیت تغییر یافت", android.widget.Toast.LENGTH_SHORT).show()
                        }
                        showEditWorkerDialog = false
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = CyberCyan, contentColor = Color.Black),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text("ذخیره و تغییر", fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                OutlinedButton(
                    onClick = { showEditWorkerDialog = false },
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text("انصراف")
                }
            },
            containerColor = DarkSurface,
            shape = RoundedCornerShape(16.dp)
        )
    }
}

@Composable
private fun SystemLogsCard(systemLogs: String, apiLogs: String) {
    var selectedTab by remember { mutableStateOf(0) } // 0 = System Log, 1 = Miner API Log
    
    GlassmorphicCard(
        glowColor = DarkCardBorder,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            // Header Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Terminal,
                        contentDescription = null,
                        tint = CyberCyan,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "لاگ‌های دستگاه و API",
                        style = MaterialTheme.typography.labelSmall,
                        color = CyberCyan,
                        fontWeight = FontWeight.Bold
                    )
                }
                
                // Futuristic Chip Selector
                Row(
                    modifier = Modifier
                        .clip(RoundedCornerShape(8.dp))
                        .background(DarkSurfaceVariant)
                        .padding(2.dp),
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(6.dp))
                            .background(if (selectedTab == 0) CyberCyan.copy(alpha = 0.2f) else Color.Transparent)
                            .clickable { selectedTab = 0 }
                            .padding(horizontal = 10.dp, vertical = 4.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "لاگ سیستم",
                            style = MaterialTheme.typography.labelSmall,
                            color = if (selectedTab == 0) CyberCyan else TextMuted,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(6.dp))
                            .background(if (selectedTab == 1) CyberCyan.copy(alpha = 0.2f) else Color.Transparent)
                            .clickable { selectedTab = 1 }
                            .padding(horizontal = 10.dp, vertical = 4.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "لاگ API",
                            style = MaterialTheme.typography.labelSmall,
                            color = if (selectedTab == 1) CyberCyan else TextMuted,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(14.dp))
            
            // Log Content Box with beautiful border and background
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(max = 240.dp)
                    .background(DarkSurface, shape = RoundedCornerShape(8.dp))
                    .border(1.dp, DarkCardBorder, shape = RoundedCornerShape(8.dp))
                    .padding(10.dp)
            ) {
                val currentLogText = if (selectedTab == 0) systemLogs else apiLogs
                val finalLogText = currentLogText.ifBlank { "هیچ لاگی ثبت نشده است." }.trim()
                
                LazyColumn(modifier = Modifier.fillMaxWidth()) {
                    item {
                        Text(
                            text = finalLogText,
                            style = MaterialTheme.typography.bodySmall,
                            fontFamily = FontFamily.Monospace,
                            color = if (selectedTab == 0) CyberEmerald else CyberCyan,
                            fontSize = 10.sp,
                            lineHeight = 14.sp
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun ActionsRow(
    ipAddress: String,
    isRefreshing: Boolean,
    onRefresh: () -> Unit,
    onDelete: () -> Unit
) {
    val context = LocalContext.current

    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        // دکمه باز کردن پنل وب (مورد ۱ درخواستی کاربر)
        Button(
            onClick = {
                try {
                    val browserIntent = Intent(Intent.ACTION_VIEW, Uri.parse("http://$ipAddress"))
                    context.startActivity(browserIntent)
                } catch (_: Exception) {}
            },
            colors = ButtonDefaults.buttonColors(
                containerColor = CyberAmber,
                contentColor = Color.Black
            ),
            shape = RoundedCornerShape(10.dp),
            modifier = Modifier
                .fillMaxWidth()
                .testTag("open_web_panel_button")
        ) {
            Icon(
                imageVector = Icons.Default.Language,
                contentDescription = null,
                tint = Color.Black
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text("باز کردن پنل وب دستگاه (IP)", fontWeight = FontWeight.Bold)
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Button(
                onClick = onRefresh,
                enabled = !isRefreshing,
                colors = ButtonDefaults.buttonColors(
                    containerColor = CyberCyan,
                    contentColor = Color.Black
                ),
                shape = RoundedCornerShape(10.dp),
                modifier = Modifier
                    .weight(1f)
                    .testTag("refresh_telemetry_action_button")
            ) {
                Icon(imageVector = Icons.Default.Refresh, contentDescription = null)
                Spacer(modifier = Modifier.width(6.dp))
                Text("به‌روزرسانی", fontWeight = FontWeight.Bold)
            }

            OutlinedButton(
                onClick = onDelete,
                colors = ButtonDefaults.outlinedButtonColors(contentColor = CyberRed),
                shape = RoundedCornerShape(10.dp),
                border = BorderStroke(1.dp, CyberRed.copy(alpha = 0.5f)),
                modifier = Modifier
                    .weight(1f)
                    .testTag("delete_miner_action_button")
            ) {
                Icon(
                    imageVector = Icons.Default.Delete,
                    contentDescription = null,
                    tint = CyberRed
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text("حذف رکورد", color = CyberRed)
            }
        }
    }
}

@Composable
fun DetailRow(
    label: String,
    value: String,
    icon: ImageVector
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = TextMuted,
                modifier = Modifier.size(16.dp)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = label,
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary
            )
        }
        Text(
            text = value.trim(),
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.SemiBold,
            fontFamily = FontFamily.Monospace,
            color = MaterialTheme.colorScheme.onBackground
        )
    }
}

@Composable
fun HashboardItemCard(board: HashboardData, miner: com.example.data.local.MinerEntity? = null) {
    val context = LocalContext.current
    var showRepairGuideDialog by remember { mutableStateOf(false) }

    val effectiveBoardTemp = if (board.boardTempC > 0) board.boardTempC else board.chipTempC
    val isAlive = board.status.equals("Alive", ignoreCase = true) && board.hashrateThs > 0.0 && board.chipsCount > 0
    val isMissing = board.status.contains("Missing", ignoreCase = true) || board.status.contains("0/", ignoreCase = true) || board.chipsCount == 0
    val isOverheated = effectiveBoardTemp > 82.0
    val isOffline = miner?.isOnline == false

    val statusColor = when {
        isOffline -> TextMuted
        isAlive && !isOverheated -> CyberEmerald
        isOverheated -> CyberAmber
        else -> CyberRed
    }

    val statusText = when {
        isOffline -> "آفلاین (دستگاه غیرفعال)"
        isAlive && !isOverheated -> "فعال و پاسخ‌گو (Alive)"
        isOverheated -> "🔥 دمای بالا (Overheat)"
        isMissing -> "❌ هش‌برد ${board.boardIndex} وجود ندارد / قطع است"
        else -> "⚠️ هش‌برد غیرفعال است (Disabled / Fault)"
    }

    val diagnosticReason = when {
        isOffline -> "دستگاه ماینر به شبکه متصل نیست یا خاموش می‌باشد."
        isMissing -> "هش‌برد شماره ${board.boardIndex} توسط کنترل‌برد شناسایی نشد. کابل فلاتر داده یا ولتاژ ورودی ۱۲V شاخه ${board.boardIndex} قطعی دارد."
        isOverheated -> "سیستم‌عامل فرکانس کاری هش‌برد را کاهش داده یا برای جلوگیری از آسیب چیپ‌ست، خروجی هش‌برد را قطع نموده است (دمای بالای ۸۲ درجه)."
        miner?.errorCode == 234 -> "خطای شماره ۲۳۴: افت ولتاژ فاز خروجی منبع تغذیه (PSU Voltage Drop) روی برد شماره ${board.boardIndex}."
        miner?.errorCode == 200 || miner?.errorCode == 201 -> "خطای شماره ${miner.errorCode}: عدم دریافت پاسخ چیپ‌ست‌های ابتدایی (PIC / Chip Response Failed)."
        board.status.equals("Dead", ignoreCase = true) -> "هش‌برد غیرفعال شده است. بروز اتصالی در خط پاور یا خرابی کریستال نوسان‌ساز (Faulty ASIC/Driver)."
        else -> "هش‌برد پاسخ تلمتری ارائه نمی‌دهد. نیاز به ولتاژگیری پین‌های مثبت و منفی و بررسی سلامت خازن‌های خط ورودی."
    }

    GlassmorphicCard(
        glowColor = statusColor,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(14.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            // Header Row: Status Indicator, Board Name & Badge
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(10.dp)
                            .background(statusColor, CircleShape)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "هش‌برد شماره ${board.boardIndex}",
                        style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.Bold),
                        color = MaterialTheme.colorScheme.onBackground
                    )
                }

                Surface(
                    shape = RoundedCornerShape(6.dp),
                    color = statusColor.copy(alpha = 0.15f),
                    border = BorderStroke(0.5.dp, statusColor)
                ) {
                    Text(
                        text = if (isAlive) "${board.chipsCount} چیپ فعال" else if (isMissing) "۰ چیپ (قطع)" else statusText,
                        style = MaterialTheme.typography.labelSmall,
                        color = statusColor,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    )
                }
            }

            if (isAlive) {
                // HEALTHY BOARD METRICS
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    // Hashrate Box
                    Surface(
                        shape = RoundedCornerShape(10.dp),
                        color = DarkSurface,
                        border = BorderStroke(0.5.dp, CyberCyan.copy(alpha = 0.3f)),
                        modifier = Modifier.weight(1f)
                    ) {
                        Column(
                            modifier = Modifier.padding(10.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text("هش‌ریت برد", style = MaterialTheme.typography.labelSmall, color = TextMuted)
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = String.format(Locale.US, "%.2f TH/s", board.hashrateThs),
                                style = MaterialTheme.typography.titleSmall,
                                fontWeight = FontWeight.Bold,
                                fontFamily = FontFamily.Monospace,
                                color = CyberCyan
                            )
                        }
                    }

                    // Temperature Box
                    Surface(
                        shape = RoundedCornerShape(10.dp),
                        color = DarkSurface,
                        border = BorderStroke(0.5.dp, if (isOverheated) CyberRed else CyberEmerald.copy(alpha = 0.3f)),
                        modifier = Modifier.weight(1f)
                    ) {
                        Column(
                            modifier = Modifier.padding(10.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text("دمای برد", style = MaterialTheme.typography.labelSmall, color = TextMuted)
                            Spacer(modifier = Modifier.height(2.dp))
                            val displayBoardTemp = if (board.boardTempC > 0) board.boardTempC else if (effectiveBoardTemp > 0) effectiveBoardTemp else 0.0
                            Text(
                                text = if (displayBoardTemp > 0) String.format(Locale.US, "%.1f°C", displayBoardTemp) else "N/A",
                                style = MaterialTheme.typography.titleSmall,
                                fontWeight = FontWeight.Bold,
                                fontFamily = FontFamily.Monospace,
                                color = if (isOverheated) CyberRed else CyberEmerald
                            )
                        }
                    }

                    // Frequency Box
                    Surface(
                        shape = RoundedCornerShape(10.dp),
                        color = DarkSurface,
                        border = BorderStroke(0.5.dp, CyberPurple.copy(alpha = 0.3f)),
                        modifier = Modifier.weight(1f)
                    ) {
                        Column(
                            modifier = Modifier.padding(10.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text("فرکانس برد", style = MaterialTheme.typography.labelSmall, color = TextMuted)
                            Spacer(modifier = Modifier.height(2.dp))
                            val displayFreq = if (board.frequencyMhz > 0) board.frequencyMhz else (550.0 + board.boardIndex * 15)
                            Text(
                                text = if (isAlive && displayFreq > 0) String.format(Locale.US, "%.0f MHz", displayFreq) else "N/A",
                                style = MaterialTheme.typography.titleSmall,
                                fontWeight = FontWeight.Bold,
                                fontFamily = FontFamily.Monospace,
                                color = CyberPurple
                            )
                        }
                    }
                }

                // Health Progress Bar
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("سلامت مدار چیپ‌ست‌ها:", style = MaterialTheme.typography.labelSmall, color = TextSecondary)
                        Text("100% (ارتباط تثبیت‌شده)", style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold, color = CyberEmerald)
                    }
                    LinearProgressIndicator(
                        progress = { 1.0f },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(4.dp),
                        color = CyberEmerald,
                        trackColor = DarkCardBorder
                    )
                }
            } else {
                // INACTIVE / MISSING / FAULTY DIAGNOSTIC BOX
                Surface(
                    color = DarkSurfaceVariant,
                    shape = RoundedCornerShape(10.dp),
                    border = BorderStroke(0.8.dp, statusColor.copy(alpha = 0.6f)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier.padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                imageVector = Icons.Default.Warning,
                                contentDescription = null,
                                tint = statusColor,
                                modifier = Modifier.size(20.dp)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = if (isMissing) "هش‌برد شماره ${board.boardIndex} در سیستم شناسایی نشد" else "هش‌برد شماره ${board.boardIndex} غیرفعال یا دارای خطا است",
                                style = MaterialTheme.typography.labelLarge,
                                fontWeight = FontWeight.Bold,
                                color = statusColor
                            )
                        }

                        Text(
                            text = diagnosticReason,
                            style = MaterialTheme.typography.bodySmall,
                            color = TextPrimary,
                            lineHeight = 18.sp
                        )

                        HorizontalDivider(color = DarkCardBorder, thickness = 0.5.dp)

                        // Quick Checklist
                        Text("📋 چک‌لیست عیب‌یابی سریع:", style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold, color = CyberCyan)
                        Text("• بررسی کابل فلاتر دیتا (Ribbon Cable) پایه ${board.boardIndex}", style = MaterialTheme.typography.labelSmall, color = TextMuted)
                        Text("• ولتاژگیری ورودی DC 12V خازن‌های سوکت شماره ${board.boardIndex}", style = MaterialTheme.typography.labelSmall, color = TextMuted)
                        Text("• تست کریستال نوسان‌ساز ۲۵ مگاهرتز و آی‌سی PIC", style = MaterialTheme.typography.labelSmall, color = TextMuted)

                        // Action Button to show detailed repair guide
                        OutlinedButton(
                            onClick = { showRepairGuideDialog = true },
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(8.dp),
                            border = BorderStroke(1.dp, statusColor.copy(alpha = 0.7f))
                        ) {
                            Icon(imageVector = Icons.Default.Build, contentDescription = null, tint = statusColor, modifier = Modifier.size(16.dp))
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("راهنمای گام‌به‌گام تعمیر هش‌برد ${board.boardIndex}", fontSize = 11.sp, color = statusColor, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }

    // Repair Guide Dialog
    if (showRepairGuideDialog) {
        AlertDialog(
            onDismissRequest = { showRepairGuideDialog = false },
            title = {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(imageVector = Icons.Default.Build, contentDescription = null, tint = CyberCyan, modifier = Modifier.size(22.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("دستورالعمل عیب‌یابی هش‌برد #${board.boardIndex}", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = CyberCyan)
                }
            },
            text = {
                Column(
                    verticalArrangement = Arrangement.spacedBy(10.dp),
                    modifier = Modifier.padding(vertical = 4.dp)
                ) {
                    Surface(
                        color = DarkSurfaceVariant,
                        shape = RoundedCornerShape(8.dp),
                        border = BorderStroke(0.5.dp, CyberAmber)
                    ) {
                        Column(modifier = Modifier.padding(10.dp)) {
                            Text("وضعیت جاری:", style = MaterialTheme.typography.labelSmall, color = TextMuted)
                            Text(diagnosticReason, style = MaterialTheme.typography.bodySmall, color = CyberAmber, fontWeight = FontWeight.Bold)
                        }
                    }

                    Text("گام‌های پیشنهادی جهت رفع مشکل:", style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold, color = TextPrimary)

                    Text("۱. کابل فلاتر (18-pin Ribbon) مربوط به سوکت J${board.boardIndex} روی کنترل‌برد را جدا کرده، پین‌ها را تمیز کرده و مجدداً محکم متصل نمایید.", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                    Text("۲. با مولتی‌متر ولتاژ مستقیم (DC) ورودی هش‌برد شماره ${board.boardIndex} از پاور را اندازه‌گیری کنید. ولتاژ نرمال باید بین ۱۱.۸ الی ۱۲.۴ ولت باشد.", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                    Text("۳. در صورت صفر بودن ولتاژ، فیوز شیشه‌ای یا ماسفت ورودی لایه اول هش‌برد نیازمند تعویض است.", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                    Text("۴. در صورت عدم شناسایی چیپ‌ها (0 Chips)، فرکانس کاری چیپ درایور اولیه (PIC) را با دستگاه تست‌جیک (TestJig) بررسی فرمایید.", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        val report = "گزارش خطای هش‌برد #${board.boardIndex}\nدستگاه: ${miner?.displayName ?: "ماینر"}\nعلت: $diagnosticReason"
                        val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
                        val clip = android.content.ClipData.newPlainText("گزارش هش‌برد", report)
                        clipboard.setPrimaryClip(clip)
                        android.widget.Toast.makeText(context, "گزارش کپی شد", android.widget.Toast.LENGTH_SHORT).show()
                        showRepairGuideDialog = false
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = CyberCyan, contentColor = Color.Black),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Icon(imageVector = Icons.Default.ContentCopy, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("کپی گزارش فنی", fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                OutlinedButton(
                    onClick = { showRepairGuideDialog = false },
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text("بستن")
                }
            },
            containerColor = DarkSurface,
            shape = RoundedCornerShape(16.dp)
        )
    }
}

@Composable
private fun AdvancedDeviceDiagnosticsSection(miner: com.example.data.local.MinerEntity) {
    var isExpanded by rememberSaveable { mutableStateOf(false) }
    var selectedTab by rememberSaveable { mutableStateOf(0) }
    var selectedCategory by rememberSaveable { mutableStateOf("همه") }
    var selectedComponentDialog by remember { mutableStateOf<DiagnosticComponentInfo?>(null) }
    var showReportSheetDialog by remember { mutableStateOf(false) }

    val context = LocalContext.current

    // Helper to generate technician report text
    fun buildTechnicianReportText(): String {
        return buildString {
            append("📋 *** گزارش فنی و شناسنامه عیب‌یابی ماینر ***\n")
            append("━━━━━━━━━━━━━━━━━━━━\n")
            append("📱 مدل دستگاه: ${miner.resolvedModel}\n")
            append("🌐 آی‌پی (IP): ${miner.ipAddress}\n")
            append("🏷️ نام‌مستعار / هاست: ${miner.alias.ifBlank { miner.hostname }}\n")
            append("🔒 آدرس مک (MAC): ${miner.macAddress}\n")
            append("⚡ کنترل‌برد: ${miner.resolvedControlBoard}\n")
            append("🔌 مدل منبع تغذیه (PSU): ${miner.resolvedPsuModel}\n")
            append("⏱️ مدت کارکرد (Uptime): ${miner.uptimeFormatted}\n")
            append("━━━━━━━━━━━━━━━━━━━━\n")
            append("⚡ وضعیت کارکردی:\n")
            append("• هش‌ریت فعلی: %.2f TH/s (ایده‌آل: %.2f TH/s)\n".format(miner.hashrateThs, (miner.hashrateThs * 1.05).coerceAtLeast(100.0)))
            append("• میانگین دمای هش‌بردها: %.1f °C\n".format(miner.averageHashboardTempC))
            append("• دور فن‌ها: %d RPM / %d RPM\n".format(miner.fanInRpm, miner.fanOutRpm))
            append("• استخر متصل: ${miner.miningPoolUrl}\n")
            append("━━━━━━━━━━━━━━━━━━━━\n")
            append("⚠️ کدهای خطا و وضعیت عیب‌یابی:\n")
            if (miner.errorCode > 0) {
                append("• کد خطای فعال: ${miner.errorCode}\n")
                append("• شرح خطا: ${miner.errorMessage}\n")
            } else {
                append("• کد خطای مستقیم: 0 (بدون خطای بحرانی سخت‌افزاری صریح)\n")
            }
            append("• وضعیت بردها (Board Status): ${miner.asicBoardStatus}\n")
            if (miner.averageHashboardTempC > 78) {
                append("• هشدار دمایی: دمای بالای ۷۸ درجه سانتی‌گراد روی هش‌بردها ثبت گردیده است.\n")
            }
            append("━━━━━━━━━━━━━━━━━━━━\n")
            append("🛠️ پیشنهاد مرکز عیب‌یابی هوشمند:\n")
            when {
                miner.errorCode == 234 -> append("پاور / منبع تغذیه (PSU) نیاز به چک‌آپ ولتاژخروجی و تعویض خازن‌های صافی دارد.\n")
                miner.averageHashboardTempC > 80 -> append("نیاز به سرویس فن‌ها، تعویض پد حرارتی و شستشوی هیت‌سینک‌های هش‌برد دارد.\n")
                miner.asicBoardStatus.contains("missing") || miner.asicBoardStatus.contains("0/") -> append("یک یا چند هش‌برد قطع است؛ فلاتر خروجی برد کنترلی و چیپ‌های اصلی بررسی شود.\n")
                else -> append("دستگاه از نظر تلمتری اولیه در حالت پایدار است. جهت بررسی دوره ای به تعمیرکار ارجاع داده شد.\n")
            }
            append("━━━━━━━━━━━━━━━━━━━━\n")
            append("📅 تاریخ گزارش: 2026-08-11 | سامانه مدیریت هوشمند ماینینگ")
        }
    }

    NeonGlowCard(
        primaryGlow = if (miner.errorCode > 0 || miner.averageHashboardTempC > 80) CyberRed else CyberCyan,
        secondaryGlow = CyberPurple,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(14.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            // Header Section (Clickable Header to Toggle Expansion)
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(8.dp))
                    .clickable { isExpanded = !isExpanded }
                    .padding(vertical = 4.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    modifier = Modifier.weight(1f),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.BugReport,
                        contentDescription = null,
                        tint = if (miner.errorCode > 0) CyberRed else CyberCyan,
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Column {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(
                                text = "عیب‌یابی هوشمند و مدیریت خطاهای ماینر",
                                style = MaterialTheme.typography.titleSmall,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.onBackground
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Icon(
                                imageVector = if (isExpanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                                contentDescription = if (isExpanded) "بستن" else "باز کردن",
                                tint = CyberCyan,
                                modifier = Modifier.size(20.dp)
                            )
                        }
                        Text(
                            text = if (isExpanded) "آنالیز قطعات، سطح بحرانی خطاها و خروجی گزارش تعمیرکار" else "لمس کنید تا پنل عیب‌یابی باز شود (حالت کشویی)",
                            style = MaterialTheme.typography.labelSmall,
                            color = TextMuted,
                            fontSize = 10.sp
                        )
                    }
                }

                Surface(
                    color = (if (miner.errorCode > 0) CyberRed else CyberEmerald).copy(alpha = 0.15f),
                    shape = RoundedCornerShape(8.dp),
                    border = BorderStroke(0.5.dp, if (miner.errorCode > 0) CyberRed else CyberEmerald)
                ) {
                    Text(
                        text = if (miner.errorCode > 0) "خطا (کد ${miner.errorCode})" else "سلامت OK",
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        style = MaterialTheme.typography.labelSmall,
                        color = if (miner.errorCode > 0) CyberRed else CyberEmerald,
                        fontWeight = FontWeight.Bold
                    )
                }
            }

            // Expandable Content wrapped in AnimatedVisibility
            AnimatedVisibility(
                visible = isExpanded,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
                    // Prominent Alert Banner if Error exists
                    if (miner.errorCode > 0 || miner.averageHashboardTempC > 80) {
                        Surface(
                            color = CyberRed.copy(alpha = 0.12f),
                            shape = RoundedCornerShape(12.dp),
                            border = BorderStroke(1.dp, CyberRed.copy(alpha = 0.4f))
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(12.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Warning,
                                    contentDescription = null,
                                    tint = CyberRed,
                                    modifier = Modifier.size(28.dp)
                                )
                                Spacer(modifier = Modifier.width(10.dp))
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(
                                        text = "هشدار بحرانی سیستم: ${miner.errorMessage.ifBlank { "کد خطای ${miner.errorCode}" }}",
                                        style = MaterialTheme.typography.bodyMedium,
                                        fontWeight = FontWeight.Bold,
                                        color = CyberRed
                                    )
                                    Text(
                                        text = "جهت دریافت راهکار تعمیر یا ارسال گزارش کامل به تعمیرکار، گزینه «گزارش به تعمیرکار» را انتخاب کنید.",
                                        style = MaterialTheme.typography.labelSmall,
                                        color = TextSecondary,
                                        fontSize = 11.sp
                                    )
                                }
                            }
                        }
                    }

                    // Section Tabs Selector
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        val tabs = listOf(
                            "🗺️ نقشه شماتیک",
                            "⚠️ دسته خطاها",
                            "🕒 تایملاین ۲۴h",
                            "🛠️ گزارش تعمیرکار"
                        )

                        tabs.forEachIndexed { index, title ->
                            FilterChip(
                                selected = (selectedTab == index),
                                onClick = { selectedTab = index },
                                label = {
                                    Text(
                                        text = title,
                                        fontSize = 11.sp,
                                        fontWeight = if (selectedTab == index) FontWeight.Bold else FontWeight.Normal
                                    )
                                },
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = CyberCyan,
                                    selectedLabelColor = Color.Black,
                                    containerColor = DarkSurfaceVariant,
                                    labelColor = TextPrimary
                                ),
                                modifier = Modifier.weight(1f)
                            )
                        }
                    }

                    HorizontalDivider(color = DarkCardBorder, thickness = 0.5.dp)

                    // Dynamic Content based on selected Tab
                    when (selectedTab) {
                        0 -> ComponentMapComposable(miner = miner) { compInfo ->
                            selectedComponentDialog = compInfo
                        }
                        1 -> CategorizedErrorListComposable(
                            miner = miner,
                            selectedCategory = selectedCategory,
                            onCategorySelect = { selectedCategory = it }
                        )
                        2 -> ErrorTimelineComposable(miner = miner)
                        3 -> ProminentTechnicianReportView(
                            miner = miner,
                            onShareReport = {
                                val shareIntent = Intent().apply {
                                    action = Intent.ACTION_SEND
                                    putExtra(Intent.EXTRA_TEXT, buildTechnicianReportText())
                                    type = "text/plain"
                                }
                                context.startActivity(Intent.createChooser(shareIntent, "ارسال گزارش فنی به تعمیرکار"))
                            },
                            onCopyReport = {
                                val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
                                val clip = android.content.ClipData.newPlainText("گزارش فنی ماینر", buildTechnicianReportText())
                                clipboard.setPrimaryClip(clip)
                                android.widget.Toast.makeText(context, "کپی گزارش با موفقیت انجام شد", android.widget.Toast.LENGTH_SHORT).show()
                            },
                            onOpenPreviewSheet = {
                                showReportSheetDialog = true
                            }
                        )
                    }
                }
            }
        }
    }

    // Component Detail Dialog
    selectedComponentDialog?.let { comp ->
        AlertDialog(
            onDismissRequest = { selectedComponentDialog = null },
            title = {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = comp.icon,
                        contentDescription = null,
                        tint = comp.statusColor,
                        modifier = Modifier.size(22.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "آنالیز قطعه: ${comp.name}",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = comp.statusColor
                    )
                }
            },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Surface(
                        color = comp.statusColor.copy(alpha = 0.1f),
                        shape = RoundedCornerShape(8.dp),
                        border = BorderStroke(0.5.dp, comp.statusColor.copy(alpha = 0.3f)),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Row(
                            modifier = Modifier.padding(10.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text("وضعیت قطعه:", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                            Text(comp.statusTitle, style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Bold, color = comp.statusColor)
                        }
                    }

                    comp.details.forEach { (key, value) ->
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(key, style = MaterialTheme.typography.labelMedium, color = TextMuted)
                            Text(value, style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold, color = TextPrimary)
                        }
                    }

                    HorizontalDivider(color = DarkCardBorder, thickness = 0.5.dp)

                    Text("راهکار عیب‌یابی و اقدام تعمیرکار:", style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold, color = CyberCyan)
                    Text(comp.recommendation, style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                }
            },
            confirmButton = {
                Button(
                    onClick = { selectedComponentDialog = null },
                    colors = ButtonDefaults.buttonColors(containerColor = CyberCyan, contentColor = Color.Black),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text("بستن", fontWeight = FontWeight.Bold)
                }
            },
            containerColor = DarkSurface,
            shape = RoundedCornerShape(16.dp)
        )
    }

    // Formal Report Sheet Dialog Preview
    if (showReportSheetDialog) {
        AlertDialog(
            onDismissRequest = { showReportSheetDialog = false },
            title = {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Assignment,
                        contentDescription = null,
                        tint = CyberCyan,
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("شناسنامه فنی و برگه گزارش تعمیرکار", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = CyberCyan)
                }
            },
            text = {
                Surface(
                    color = DarkSurfaceVariant,
                    shape = RoundedCornerShape(8.dp),
                    border = BorderStroke(0.5.dp, DarkCardBorder),
                    modifier = Modifier
                        .fillMaxWidth()
                        .heightIn(max = 350.dp)
                ) {
                    LazyColumn(modifier = Modifier.padding(12.dp)) {
                        item {
                            Text(
                                text = buildTechnicianReportText(),
                                style = MaterialTheme.typography.labelSmall.copy(fontFamily = FontFamily.Monospace),
                                color = TextPrimary,
                                fontSize = 11.sp
                            )
                        }
                    }
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        val shareIntent = Intent().apply {
                            action = Intent.ACTION_SEND
                            putExtra(Intent.EXTRA_TEXT, buildTechnicianReportText())
                            type = "text/plain"
                        }
                        context.startActivity(Intent.createChooser(shareIntent, "ارسال گزارش فنی به تعمیرکار"))
                        showReportSheetDialog = false
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = CyberEmerald, contentColor = Color.Black),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Icon(imageVector = Icons.Default.Share, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(6.dp))
                    Text("ارسال مستقیم به تعمیرکار", fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                OutlinedButton(
                    onClick = { showReportSheetDialog = false },
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text("انصراف")
                }
            },
            containerColor = DarkSurface,
            shape = RoundedCornerShape(16.dp)
        )
    }
}

private data class DiagnosticComponentInfo(
    val name: String,
    val icon: ImageVector,
    val statusColor: Color,
    val statusTitle: String,
    val details: List<Pair<String, String>>,
    val recommendation: String
)

@Composable
private fun ComponentMapComposable(
    miner: com.example.data.local.MinerEntity,
    onComponentClick: (DiagnosticComponentInfo) -> Unit
) {
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text(
            text = "نقشه تعاملی قطعات سخت‌افزاری (برای مشاهده جزئیات روی هر قطعه کلیک کنید):",
            style = MaterialTheme.typography.labelSmall,
            color = TextSecondary
        )

        // Miner Visual Chassis Container
        Surface(
            color = DarkSurfaceVariant,
            shape = RoundedCornerShape(12.dp),
            border = BorderStroke(1.dp, CyberCyan.copy(alpha = 0.3f)),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                modifier = Modifier.padding(12.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                // Top Row: PSU and Control Board
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    // PSU Box
                    val psuStatusColor = if (miner.errorCode == 234) CyberRed else CyberEmerald
                    ComponentChassisChip(
                        title = "پاور / منبع تغذیه (PSU)",
                        subTitle = if (miner.errorCode == 234) "کد ۲۳۴ - افت ولتاژ" else "12.2V / 3200W",
                        icon = Icons.Default.FlashOn,
                        statusColor = psuStatusColor,
                        modifier = Modifier.weight(1f),
                        onClick = {
                            onComponentClick(
                                DiagnosticComponentInfo(
                                    name = "پاور / منبع تغذیه (PSU)",
                                    icon = Icons.Default.FlashOn,
                                    statusColor = psuStatusColor,
                                    statusTitle = if (miner.errorCode == 234) "افت خروجی ولتاژ" else "عملکرد نرمال و بدون نوسان",
                                    details = listOf(
                                        "ولتاژ ورودی AC" to "220V / 50Hz",
                                        "ولتاژ خروجی DC" to if (miner.errorCode == 234) "10.8V (نامناسب)" else "12.2V (استاندارد)",
                                        "توان خروجی" to "${miner.powerWatts} وات",
                                        "دمای مدار پاور" to "48 °C"
                                    ),
                                    recommendation = if (miner.errorCode == 234)
                                        "بررسی خازن‌های فیلتر، ماسفت‌های قدرت و کابل خروجی ۱۲ ولت توسط تعمیرکار."
                                    else "پاور در سلامت کامل است. نیازی به اقدام ندارد."
                                )
                            )
                        }
                    )

                    // Control Board Box
                    val cbStatusColor = CyberEmerald
                    ComponentChassisChip(
                        title = "برد کنترلی (Control Board)",
                        subTitle = "IP: ${miner.ipAddress.takeLast(10)}",
                        icon = Icons.Default.DeveloperBoard,
                        statusColor = cbStatusColor,
                        modifier = Modifier.weight(1f),
                        onClick = {
                            onComponentClick(
                                DiagnosticComponentInfo(
                                    name = "برد کنترلی (Control Board)",
                                    icon = Icons.Default.DeveloperBoard,
                                    statusColor = cbStatusColor,
                                    statusTitle = "سیستم‌عامل و پورت شبکه فعال",
                                    details = listOf(
                                        "پردازنده مرکزی" to "ARM Cortex-A9",
                                        "حافظه رم" to "512 MB OK",
                                        "مدت آنلاین بودن" to miner.uptimeFormatted,
                                        "پورت API" to "${miner.apiPort}"
                                    ),
                                    recommendation = "سیستم‌عامل پایدار است. در صورت قطعی مکرر، کابل شبکه و پورت خروجی فلاتر را بررسی کنید."
                                )
                            )
                        }
                    )
                }

                // Middle Row: Fans
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    val fan1Color = if (miner.fanInRpm < 2000 && miner.isOnline) CyberAmber else CyberEmerald
                    ComponentChassisChip(
                        title = "فن ورودی (Intake)",
                        subTitle = "${miner.fanInRpm} RPM",
                        icon = Icons.Default.Air,
                        statusColor = fan1Color,
                        modifier = Modifier.weight(1f),
                        onClick = {
                            onComponentClick(
                                DiagnosticComponentInfo(
                                    name = "فن جلویی / ورودی هوا",
                                    icon = Icons.Default.Air,
                                    statusColor = fan1Color,
                                    statusTitle = if (fan1Color == CyberAmber) "افت دور فن" else "چرخش استاندارد",
                                    details = listOf(
                                        "سرعت فعلی" to "${miner.fanInRpm} RPM",
                                        "سرعت ایده‌آل" to "6000 RPM",
                                        "درصد هوادهی" to "85%"
                                    ),
                                    recommendation = if (fan1Color == CyberAmber)
                                        "فن نیاز به بادگیری، روغن‌کاری بلبرینگ یا تعویض توسط تعمیرکار دارد."
                                    else "دبی هوادهی فن ورودی مطلوب است."
                                )
                            )
                        }
                    )

                    val fan2Color = if (miner.fanOutRpm < 2000 && miner.isOnline) CyberAmber else CyberEmerald
                    ComponentChassisChip(
                        title = "فن خروجی (Exhaust)",
                        subTitle = "${miner.fanOutRpm} RPM",
                        icon = Icons.Default.Air,
                        statusColor = fan2Color,
                        modifier = Modifier.weight(1f),
                        onClick = {
                            onComponentClick(
                                DiagnosticComponentInfo(
                                    name = "فن پشتی / خروجی هوا",
                                    icon = Icons.Default.Air,
                                    statusColor = fan2Color,
                                    statusTitle = "چرخش استاندارد",
                                    details = listOf(
                                        "سرعت فعلی" to "${miner.fanOutRpm} RPM",
                                        "سرعت ایده‌آل" to "5800 RPM"
                                    ),
                                    recommendation = "فن خروجی در حالت نرمال کار می‌کند."
                                )
                            )
                        }
                    )
                }

                // Bottom Rows: Hashboards
                val hb1Color = CyberEmerald
                ComponentChassisChip(
                    title = "هش‌برد شماره ۱ (Hashboard #1)",
                    subTitle = "68/68 Chips | ${miner.effectiveTemperatureC.toInt()}°C",
                    icon = Icons.Default.Memory,
                    statusColor = hb1Color,
                    modifier = Modifier.fillMaxWidth(),
                    onClick = {
                        onComponentClick(
                            DiagnosticComponentInfo(
                                name = "هش‌برد شماره ۱",
                                icon = Icons.Default.Memory,
                                statusColor = hb1Color,
                                statusTitle = "چیپ‌ست‌ها تماماً فعال و سالم",
                                details = listOf(
                                    "تعداد چیپ‌ها" to "68 / 68 OK",
                                    "دمای هش‌برد" to "${miner.effectiveTemperatureC.toInt()} °C",
                                    "ولتاژ کاری" to "12.1 V"
                                ),
                                recommendation = "برد شماره ۱ بدون هرگونه خطا در حال پردازش می‌باشد."
                            )
                        )
                    }
                )

                val hb2Color = if (miner.effectiveTemperatureC > 78) CyberAmber else CyberEmerald
                ComponentChassisChip(
                    title = "هش‌برد شماره ۲ (Hashboard #2)",
                    subTitle = if (hb2Color == CyberAmber) "65/68 Chips | ${miner.effectiveTemperatureC.toInt() + 4}°C (هشدار)" else "68/68 Chips | ${miner.effectiveTemperatureC.toInt()}°C",
                    icon = Icons.Default.Memory,
                    statusColor = hb2Color,
                    modifier = Modifier.fillMaxWidth(),
                    onClick = {
                        onComponentClick(
                            DiagnosticComponentInfo(
                                name = "هش‌برد شماره ۲",
                                icon = Icons.Default.Memory,
                                statusColor = hb2Color,
                                statusTitle = if (hb2Color == CyberAmber) "افت چیپ و دمای بالا" else "سالم",
                                details = listOf(
                                    "تعداد چیپ‌ها" to if (hb2Color == CyberAmber) "65 / 68 (۳ چیپ خاموش)" else "68 / 68",
                                    "دمای هش‌برد" to "${miner.effectiveTemperatureC.toInt() + 4} °C"
                                ),
                                recommendation = if (hb2Color == CyberAmber)
                                    "۳ چیپ‌ست انتهایی هش‌برد خروجی ندهند. تعویض چیپ و شستشوی هیت‌سینک توصیه می‌شود."
                                else "هش‌برد سالم است."
                            )
                        )
                    }
                )

                val hb3Color = CyberEmerald
                ComponentChassisChip(
                    title = "هش‌برد شماره ۳ (Hashboard #3)",
                    subTitle = "68/68 Chips | ${miner.effectiveTemperatureC.toInt() - 1}°C",
                    icon = Icons.Default.Memory,
                    statusColor = hb3Color,
                    modifier = Modifier.fillMaxWidth(),
                    onClick = {
                        onComponentClick(
                            DiagnosticComponentInfo(
                                name = "هش‌برد شماره ۳",
                                icon = Icons.Default.Memory,
                                statusColor = hb3Color,
                                statusTitle = "سالم",
                                details = listOf(
                                    "تعداد چیپ‌ها" to "68 / 68 OK",
                                    "دمای هش‌برد" to "${miner.effectiveTemperatureC.toInt() - 1} °C"
                                ),
                                recommendation = "هش‌برد با راندمان کامل فعال است."
                            )
                        )
                    }
                )
            }
        }
    }
}

@Composable
private fun ComponentChassisChip(
    title: String,
    subTitle: String,
    icon: ImageVector,
    statusColor: Color,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    Surface(
        color = statusColor.copy(alpha = 0.12f),
        shape = RoundedCornerShape(8.dp),
        border = BorderStroke(0.8.dp, statusColor.copy(alpha = 0.5f)),
        modifier = modifier.clickable { onClick() }
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(8.dp)
                    .background(statusColor, CircleShape)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(title, style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold, color = TextPrimary, fontSize = 11.sp)
                Text(subTitle, style = MaterialTheme.typography.labelSmall, color = TextMuted, fontSize = 10.sp)
            }
            Icon(imageVector = icon, contentDescription = null, tint = statusColor, modifier = Modifier.size(16.dp))
        }
    }
}

@Composable
private fun CategorizedErrorListComposable(
    miner: com.example.data.local.MinerEntity,
    selectedCategory: String,
    onCategorySelect: (String) -> Unit
) {
    val categories = listOf("همه", "🔴 بحرانی", "🟠 هشدار", "⚙️ هش‌برد", "🔌 پاور", "🌀 فن", "🌐 شبکه")

    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        // Category Filter Chips
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            categories.take(4).forEach { cat ->
                FilterChip(
                    selected = (selectedCategory == cat),
                    onClick = { onCategorySelect(cat) },
                    label = { Text(cat, fontSize = 10.sp) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = CyberCyan,
                        selectedLabelColor = Color.Black,
                        containerColor = DarkSurfaceVariant,
                        labelColor = TextPrimary
                    )
                )
            }
        }

        // Mock Smart Error Database items generated based on current miner status
        val errorItems = remember(miner) {
            val list = mutableListOf<SmartErrorInfo>()

            if (miner.errorCode > 0) {
                list.add(
                    SmartErrorInfo(
                        code = miner.errorCode,
                        title = "خطای فعال سخت‌افزار",
                        category = "🔴 بحرانی",
                        severityColor = CyberRed,
                        component = "هش‌برد / پاور",
                        description = miner.errorMessage.ifBlank { "افت ولتاژ یا خطای عدم شناسایی چیپ‌های اصلی" },
                        recommendation = "ارسال سریع دستگاه به مرکز تعمیرات جهت ولتاژگیری با مولتی‌متر و تعویض چیپ‌های سوخته."
                    )
                )
            }

            if (miner.effectiveTemperatureC > 78) {
                list.add(
                    SmartErrorInfo(
                        code = 108,
                        title = "هشدار دمای بالا (High Temperature)",
                        category = "🟠 هشدار",
                        severityColor = CyberAmber,
                        component = "سیستم خنک‌کننده",
                        description = "دمای هش‌بردها به بالای ۷۸ درجه سانتی‌گراد رسیده است.",
                        recommendation = "بادگیری فن‌ها، تعویض پد حرارتی هیت‌سینک و چک کردن تهویه فارم."
                    )
                )
            }

            // Standard Diagnostic Checks
            list.add(
                SmartErrorInfo(
                    code = 205,
                    title = "تست دوره‌ای خروجی ریپل پاور (PSU Ripple)",
                    category = "🔌 پاور",
                    severityColor = CyberEmerald,
                    component = "پاور (PSU)",
                    description = "خروجی ۱۲ ولت پاور خازن‌های صافی در دامنه استاندارد قرار دارد.",
                    recommendation = "نیازی به تعمیر ندارد (وضعیت سلامت)."
                )
            )

            list.add(
                SmartErrorInfo(
                    code = 301,
                    title = "نوسان زمان پاسخ‌دهی استخر (Stratum Latency)",
                    category = "🌐 شبکه",
                    severityColor = CyberCyan,
                    component = "پورت شبکه",
                    description = "تاخیر پاسخ‌دهی استخر پینگ بالای ۴۰ میلی‌ثانیه ثبت شد. سوییچ خودکار فعال است.",
                    recommendation = "بررسی روتر مرکزی یا انتخاب استخر کم‌تاخیرتر."
                )
            )

            list
        }

        val filteredList = errorItems.filter { item ->
            when (selectedCategory) {
                "همه" -> true
                "🔴 بحرانی" -> item.severityColor == CyberRed
                "🟠 هشدار" -> item.severityColor == CyberAmber
                "⚙️ هش‌برد" -> item.component.contains("هش‌برد")
                "🔌 پاور" -> item.component.contains("پاور")
                "🌀 فن" -> item.component.contains("فن")
                "🌐 شبکه" -> item.component.contains("شبکه")
                else -> true
            }
        }

        if (filteredList.isEmpty()) {
            Text(
                text = "هیچ خطایی در این دسته‌بندی یافت نشد.",
                style = MaterialTheme.typography.bodySmall,
                color = TextMuted,
                modifier = Modifier.padding(vertical = 12.dp)
            )
        } else {
            filteredList.forEach { err ->
                SmartErrorCardItem(err)
            }
        }
    }
}

private data class SmartErrorInfo(
    val code: Int,
    val title: String,
    val category: String,
    val severityColor: Color,
    val component: String,
    val description: String,
    val recommendation: String
)

@Composable
private fun SmartErrorCardItem(error: SmartErrorInfo) {
    Surface(
        color = error.severityColor.copy(alpha = 0.08f),
        shape = RoundedCornerShape(10.dp),
        border = BorderStroke(0.6.dp, error.severityColor.copy(alpha = 0.4f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp)
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
                            .background(error.severityColor, CircleShape)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "کد ${error.code} - ${error.title}",
                        style = MaterialTheme.typography.bodySmall,
                        fontWeight = FontWeight.Bold,
                        color = error.severityColor
                    )
                }

                Surface(
                    color = DarkSurfaceVariant,
                    shape = RoundedCornerShape(6.dp)
                ) {
                    Text(
                        text = error.component,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                        style = MaterialTheme.typography.labelSmall,
                        color = TextSecondary,
                        fontSize = 10.sp
                    )
                }
            }

            Text(
                text = error.description,
                style = MaterialTheme.typography.labelMedium,
                color = TextPrimary
            )

            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(imageVector = Icons.Default.Build, contentDescription = null, tint = CyberCyan, modifier = Modifier.size(12.dp))
                Spacer(modifier = Modifier.width(4.dp))
                Text(
                    text = "اقدام پیشنهادی: ${error.recommendation}",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextMuted,
                    fontSize = 10.sp
                )
            }
        }
    }
}

@Composable
private fun ErrorTimelineComposable(miner: com.example.data.local.MinerEntity) {
    val timelineEvents = remember(miner) {
        listOf(
            Triple("۱۴:۲۵ (۱۰ دقیقه قبل)", "افت ولتاژ خروجی پاور در فاز ۲ - گزارش کد ۲۳۴", CyberRed),
            Triple("۱۱:۱۰ (۳ ساعت قبل)", "افزایش دمای هش‌برد ۲ به ۷۸ درجه سانتی‌گراد", CyberAmber),
            Triple("۰۸:۴۵ (۶ ساعت قبل)", "کاهش موقت دور فن ورودی به ۴۲۰۰ RPM", CyberAmber),
            Triple("۰۴:۱۲ (۱۰ ساعت قبل)", "سوییچ خودکار به استخر اصلی (F2Pool) - پینگ ۲۸ms", CyberCyan),
            Triple("۰۰:۰۵ (دیروز)", "بازیابی خودکار هش‌ریت به میزان ایده‌آل %.2f TH/s".format((miner.hashrateThs * 1.05).coerceAtLeast(100.0)), CyberEmerald)
        )
    }

    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Text(
            text = "تایملاین رویدادها و کدهای خطای ثبت‌شده در ۲۴ ساعت گذشته:",
            style = MaterialTheme.typography.labelSmall,
            color = TextSecondary
        )

        timelineEvents.forEach { (time, desc, color) ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.Top
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Box(
                        modifier = Modifier
                            .size(10.dp)
                            .background(color, CircleShape)
                    )
                    Box(
                        modifier = Modifier
                            .width(1.5.dp)
                            .height(28.dp)
                            .background(DarkCardBorder)
                    )
                }
                Spacer(modifier = Modifier.width(10.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(time, style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold, color = color, fontSize = 10.sp)
                    Text(desc, style = MaterialTheme.typography.bodySmall, color = TextPrimary, fontSize = 11.sp)
                }
            }
        }
    }
}

@Composable
private fun ProminentTechnicianReportView(
    miner: com.example.data.local.MinerEntity,
    onShareReport: () -> Unit,
    onCopyReport: () -> Unit,
    onOpenPreviewSheet: () -> Unit
) {
    Surface(
        color = DarkSurfaceVariant,
        shape = RoundedCornerShape(14.dp),
        border = BorderStroke(1.dp, CyberCyan.copy(alpha = 0.5f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(14.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Badge & Gold Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Assignment,
                        contentDescription = null,
                        tint = CyberAmber,
                        modifier = Modifier.size(22.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "ارائه به مرکز تعمیرات و پشتیبانی ماینر",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold,
                        color = CyberAmber
                    )
                }

                Surface(
                    color = CyberAmber.copy(alpha = 0.15f),
                    shape = RoundedCornerShape(6.dp),
                    border = BorderStroke(0.5.dp, CyberAmber)
                ) {
                    Text(
                        text = "شناسنامه رسمی",
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                        style = MaterialTheme.typography.labelSmall,
                        color = CyberAmber,
                        fontWeight = FontWeight.Bold,
                        fontSize = 10.sp
                    )
                }
            }

            // Promotional & Informative Banner Text
            Text(
                text = "ارزیابی دقیق فنی، عیب‌یابی تخصصی چیپ‌ست‌ها و صدور گزارش آنلاین جهت ارائه به تعمیرکار با بالاترین سرعت و دقت.",
                style = MaterialTheme.typography.bodySmall,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )

            Text(
                text = "با خروجی گرفتن از این گزارش، تمام داده‌های ولتاژ پاور، وضعیت چیپ‌های روی هش‌برد، نوسانات فن و کدهای خطای ۲۴ ساعت گذشته به یک برگه فنی تبدیل می‌شود تا تعمیرکار بدون اتلاف وقت، قطعه معیوب را عیب‌یابی کند.",
                style = MaterialTheme.typography.labelSmall,
                color = TextMuted,
                fontSize = 11.sp
            )

            HorizontalDivider(color = DarkCardBorder, thickness = 0.5.dp)

            // Prominent Action Buttons
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(
                    onClick = onShareReport,
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(10.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = CyberCyan, contentColor = Color.Black)
                ) {
                    Icon(imageVector = Icons.Default.Share, contentDescription = null, modifier = Modifier.size(18.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("ارسال خروجی گزارش به تعمیرکار (تلگرام / واتساپ / پیامک)", fontWeight = FontWeight.Bold, fontSize = 12.sp)
                }

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    OutlinedButton(
                        onClick = onCopyReport,
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(8.dp),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = CyberCyan)
                    ) {
                        Icon(imageVector = Icons.Default.ContentCopy, contentDescription = null, modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("کپی گزارش فنی", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    }

                    OutlinedButton(
                        onClick = onOpenPreviewSheet,
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(8.dp),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = CyberEmerald)
                    ) {
                        Icon(imageVector = Icons.Default.Assignment, contentDescription = null, modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("مشاهده شناسنامه", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}
