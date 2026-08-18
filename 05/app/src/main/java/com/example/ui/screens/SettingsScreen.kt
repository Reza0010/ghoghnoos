package com.example.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.BorderStroke
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.DeleteSweep
import androidx.compose.material.icons.filled.ExpandLess
import androidx.compose.material.icons.filled.ExpandMore
import androidx.compose.material.icons.filled.Key
import androidx.compose.material.icons.filled.Lan
import androidx.compose.material.icons.filled.NetworkCheck
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Save
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material.icons.filled.Storage
import androidx.compose.material.icons.filled.Wifi
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.local.ScanSettings
import com.example.ui.components.GlassmorphicCard
import com.example.ui.theme.CyberAmber
import com.example.ui.theme.CyberCyan
import com.example.ui.theme.CyberEmerald
import com.example.ui.theme.CyberPurple
import com.example.ui.theme.CyberRed
import com.example.ui.theme.DarkCardBorder
import com.example.ui.theme.DarkSurface
import com.example.ui.theme.DarkSurfaceVariant
import com.example.ui.theme.TextMuted
import com.example.ui.theme.TextSecondary
import com.example.ui.viewmodels.SettingsViewModel
import kotlinx.coroutines.launch

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun SettingsScreen(
    viewModel: SettingsViewModel
) {
    val currentSettings by viewModel.settings.collectAsState()
    val passwordProfiles by viewModel.passwordProfiles.collectAsState()
    val pingResult by viewModel.pingResult.collectAsState()

    var apiPortText by remember(currentSettings) {
        mutableStateOf(currentSettings.apiPort.toString())
    }
    var timeoutMsText by remember(currentSettings) {
        mutableStateOf(currentSettings.timeoutMs.toString())
    }
    var timeoutMsValue by remember(currentSettings) {
        mutableFloatStateOf(currentSettings.timeoutMs.toFloat())
    }
    var concurrencyValue by remember(currentSettings) {
        mutableFloatStateOf(currentSettings.concurrency.toFloat())
    }
    var selectedAutoRefreshSec by remember(currentSettings) {
        mutableStateOf(currentSettings.autoRefreshSec)
    }
    var customSubnetText by remember(currentSettings) {
        mutableStateOf(currentSettings.customSubnet)
    }

    // Collapsible Accordion States
    var isConfigExpanded by remember { mutableStateOf(true) }
    var isPoolsExpanded by remember { mutableStateOf(false) }

    // Pool Presets State
    var p1Url by remember(currentSettings) { mutableStateOf(currentSettings.pool1Url) }
    var p1Worker by remember(currentSettings) { mutableStateOf(currentSettings.pool1Worker) }
    var p1Pass by remember(currentSettings) { mutableStateOf(currentSettings.pool1Pass) }
    var p2Url by remember(currentSettings) { mutableStateOf(currentSettings.pool2Url) }
    var p2Worker by remember(currentSettings) { mutableStateOf(currentSettings.pool2Worker) }
    var p2Pass by remember(currentSettings) { mutableStateOf(currentSettings.pool2Pass) }
    var p3Url by remember(currentSettings) { mutableStateOf(currentSettings.pool3Url) }
    var p3Worker by remember(currentSettings) { mutableStateOf(currentSettings.pool3Worker) }
    var p3Pass by remember(currentSettings) { mutableStateOf(currentSettings.pool3Pass) }

    // Ping Test State
    var pingIpText by remember { mutableStateOf("192.168.1.100") }
    var pingPortText by remember(currentSettings.apiPort) {
        mutableStateOf(currentSettings.apiPort.toString())
    }

    // Dialogs State
    var showAddProfileDialog by remember { mutableStateOf(false) }
    var showClearDataDialog by remember { mutableStateOf(false) }
    var newProfileTitle by remember { mutableStateOf("") }
    var newProfileUser by remember { mutableStateOf("admin") }
    var newProfilePass by remember { mutableStateOf("admin") }

    var showSaveSuccess by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .windowInsetsPadding(WindowInsets.statusBars)
            .padding(horizontal = 16.dp)
            .testTag("settings_screen")
            .semantics { contentDescription = "صفحه تنظیمات دستگاه‌ها و شبکه" },
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // ==================== Header ====================
        item(key = "header") {
            Spacer(modifier = Modifier.height(8.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Default.Settings,
                    contentDescription = null,
                    tint = CyberCyan
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "تنظیمات دستگاه‌ها و شبکه",
                    style = MaterialTheme.typography.titleLarge.copy(
                        fontWeight = FontWeight.Bold
                    ),
                    color = MaterialTheme.colorScheme.onBackground
                )
            }
            Text(
                text = "تنظیمات پورت، سرعت اسکن، تست اتصال، رمزها و استخرهای استخراج",
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary
            )
        }

        // ==================== 1. NETWORK STATUS SUMMARY CARD ====================
        item(key = "network_summary_card") {
            GlassmorphicCard(
                glowColor = CyberCyan,
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("network_summary_card")
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(
                                modifier = Modifier
                                    .size(36.dp)
                                    .background(CyberCyan.copy(alpha = 0.15f), CircleShape)
                                    .border(1.dp, CyberCyan.copy(alpha = 0.5f), CircleShape),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Wifi,
                                    contentDescription = null,
                                    tint = CyberCyan,
                                    modifier = Modifier.size(20.dp)
                                )
                            }
                            Spacer(modifier = Modifier.width(10.dp))
                            Column {
                                Text(
                                    text = "وضعیت ارتباط با ماینرها",
                                    style = MaterialTheme.typography.titleMedium,
                                    fontWeight = FontWeight.Bold,
                                    color = MaterialTheme.colorScheme.onBackground
                                )
                                Text(
                                    text = "تنظیمات فعال اسکنر",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = TextMuted
                                )
                            }
                        }

                        // Status Badge
                        Surface(
                            color = CyberEmerald.copy(alpha = 0.15f),
                            shape = RoundedCornerShape(20.dp),
                            border = BorderStroke(1.dp, CyberEmerald)
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(8.dp)
                                        .background(CyberEmerald, CircleShape)
                                )
                                Spacer(modifier = Modifier.width(6.dp))
                                Text(
                                    text = "آماده اسکن",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = CyberEmerald,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                    }

                    // Grid of key metric chips
                    FlowRow(
                        horizontalArrangement = Arrangement.spacedBy(10.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        MetricSummaryChip(
                            label = "پورت ارتباطی",
                            value = apiPortText,
                            accentColor = CyberCyan,
                            modifier = Modifier.weight(1f)
                        )
                        MetricSummaryChip(
                            label = "زمان انتظار",
                            value = "${timeoutMsValue.toInt()} ms",
                            accentColor = CyberAmber,
                            modifier = Modifier.weight(1f)
                        )
                        MetricSummaryChip(
                            label = "سرعت اسکن",
                            value = "${concurrencyValue.toInt()} دستگاه",
                            accentColor = CyberEmerald,
                            modifier = Modifier.weight(1f)
                        )
                        MetricSummaryChip(
                            label = "بروزرسانی خودکار",
                            value = if (selectedAutoRefreshSec > 0) "${selectedAutoRefreshSec} ثانیه" else "دستی",
                            accentColor = CyberPurple,
                            modifier = Modifier.weight(1f)
                        )
                    }
                }
            }
        }

        // ==================== 2. COLLAPSIBLE CONFIGURATION (پیکربندی کشویی: پورت، آی‌پی و سرعت اسکن) ====================
        item(key = "collapsible_config_section") {
            GlassmorphicCard(
                glowColor = CyberCyan,
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    // Header Row with Toggle Button
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { isConfigExpanded = !isConfigExpanded },
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.weight(1f)
                        ) {
                            SectionTitle(
                                icon = Icons.Default.Lan,
                                iconTint = CyberCyan,
                                title = "⚙️ تنظیمات پورت و سرعت اسکن"
                            )
                        }
                        IconButton(onClick = { isConfigExpanded = !isConfigExpanded }) {
                            Icon(
                                imageVector = if (isConfigExpanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                                contentDescription = if (isConfigExpanded) "بستن" else "باز کردن",
                                tint = CyberCyan
                            )
                        }
                    }

                    if (!isConfigExpanded) {
                        Text(
                            text = "پورت: $apiPortText | سرعت: ${concurrencyValue.toInt()} | مهلت پاسخ: ${timeoutMsValue.toInt()}ms",
                            style = MaterialTheme.typography.bodySmall,
                            color = TextMuted
                        )
                    }

                    AnimatedVisibility(visible = isConfigExpanded) {
                        Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = "پورت پیش‌فرض ماینرهای واتس‌ماینر ۴۰۲۸ است. اگر پورت تغییر کرده یا پورت دیگری استفاده می‌کنید، آن را مشخص کنید.",
                                style = MaterialTheme.typography.bodySmall,
                                color = TextSecondary
                            )

                            OutlinedTextField(
                                value = apiPortText,
                                onValueChange = { apiPortText = it },
                                label = { Text("پورت ارتباط با ماینر (مثلاً ۴۰۲۸)") },
                                singleLine = true,
                                colors = OutlinedTextFieldDefaults.colors(
                                    focusedBorderColor = CyberCyan,
                                    unfocusedBorderColor = DarkCardBorder,
                                    focusedLabelColor = CyberCyan,
                                    cursorColor = CyberCyan
                                ),
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .testTag("api_port_input")
                            )

                            val portValidation = validatePort(apiPortText)
                            if (!portValidation.isValid) {
                                Text(
                                    text = portValidation.message,
                                    style = MaterialTheme.typography.bodySmall,
                                    color = CyberRed
                                )
                            }

                            Text(
                                text = "میانبرهای سریع پورت:",
                                style = MaterialTheme.typography.labelSmall,
                                color = TextMuted
                            )
                            FlowRow(
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                verticalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                val portPresets = listOf(
                                    "4028" to "۴۰۲۸ (اصلی)",
                                    "4433" to "۴۴۳۳ (واتس‌ماینر)",
                                    "4029" to "۴۰۲۹ (رزرو)",
                                    "80" to "۸۰ (وب)",
                                    "8080" to "۸۰۸۰ (پروکسی)"
                                )
                                portPresets.forEach { (portVal, label) ->
                                    val isSelected = apiPortText == portVal
                                    Surface(
                                        shape = RoundedCornerShape(8.dp),
                                        color = if (isSelected) CyberCyan.copy(alpha = 0.2f)
                                        else DarkSurface,
                                        border = BorderStroke(
                                            width = if (isSelected) 1.5.dp else 1.dp,
                                            color = if (isSelected) CyberCyan else DarkCardBorder
                                        ),
                                        modifier = Modifier.clickable { apiPortText = portVal }
                                    ) {
                                        Text(
                                            text = label,
                                            style = MaterialTheme.typography.labelMedium,
                                            color = if (isSelected) CyberCyan else TextSecondary,
                                            modifier = Modifier.padding(
                                                horizontal = 10.dp,
                                                vertical = 6.dp
                                            )
                                        )
                                    }
                                }
                            }

                            OutlinedTextField(
                                value = customSubnetText,
                                onValueChange = { customSubnetText = it },
                                label = { Text("محدوده آی‌پی سفارشی (اختیاری)") },
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
                                    .testTag("custom_subnet_input")
                            )

                            Spacer(modifier = Modifier.height(4.dp))

                            // Concurrency Slider
                            Column(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .background(DarkSurfaceVariant, RoundedCornerShape(12.dp))
                                    .padding(14.dp)
                            ) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(
                                        text = "تعداد اسکن هم‌زمان (سرعت)",
                                        style = MaterialTheme.typography.bodyMedium,
                                        fontWeight = FontWeight.Bold,
                                        color = MaterialTheme.colorScheme.onBackground
                                    )
                                    Surface(
                                        color = CyberCyan.copy(alpha = 0.2f),
                                        shape = RoundedCornerShape(8.dp),
                                        border = BorderStroke(1.dp, CyberCyan)
                                    ) {
                                        Text(
                                            text = "${concurrencyValue.toInt()} دستگاه همزمان",
                                            style = MaterialTheme.typography.labelSmall,
                                            color = CyberCyan,
                                            fontWeight = FontWeight.Bold,
                                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                        )
                                    }
                                }

                                Spacer(modifier = Modifier.height(6.dp))

                                Slider(
                                    value = concurrencyValue,
                                    onValueChange = { concurrencyValue = it },
                                    valueRange = 5f..50f,
                                    steps = 8,
                                    colors = SliderDefaults.colors(
                                        thumbColor = CyberCyan,
                                        activeTrackColor = CyberCyan,
                                        inactiveTrackColor = DarkCardBorder
                                    ),
                                    modifier = Modifier
                                        .testTag("concurrency_slider")
                                        .semantics { contentDescription = "تعداد اسکن هم‌زمان" }
                                )

                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Text(
                                        text = "🟢 ۵ (کند و مطمئن)",
                                        style = MaterialTheme.typography.labelSmall,
                                        color = TextMuted,
                                        fontSize = 10.sp
                                    )
                                    Text(
                                        text = "🚀 ۵۰ (خیلی سریع)",
                                        style = MaterialTheme.typography.labelSmall,
                                        color = TextMuted,
                                        fontSize = 10.sp
                                    )
                                }
                            }

                            // Timeout MS Slider
                            Column(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .background(DarkSurfaceVariant, RoundedCornerShape(12.dp))
                                    .padding(14.dp)
                            ) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(
                                        text = "زمان انتظار برای پاسخ ماینر (میلی‌ثانیه)",
                                        style = MaterialTheme.typography.bodyMedium,
                                        fontWeight = FontWeight.Bold,
                                        color = MaterialTheme.colorScheme.onBackground
                                    )
                                    Surface(
                                        color = CyberAmber.copy(alpha = 0.2f),
                                        shape = RoundedCornerShape(8.dp),
                                        border = BorderStroke(1.dp, CyberAmber)
                                    ) {
                                        Text(
                                            text = "${timeoutMsValue.toInt()} ms",
                                            style = MaterialTheme.typography.labelSmall,
                                            color = CyberAmber,
                                            fontWeight = FontWeight.Bold,
                                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                        )
                                    }
                                }

                                Spacer(modifier = Modifier.height(6.dp))

                                Slider(
                                    value = timeoutMsValue,
                                    onValueChange = {
                                        timeoutMsValue = it
                                        timeoutMsText = it.toInt().toString()
                                    },
                                    valueRange = 500f..5000f,
                                    steps = 8,
                                    colors = SliderDefaults.colors(
                                        thumbColor = CyberAmber,
                                        activeTrackColor = CyberAmber,
                                        inactiveTrackColor = DarkCardBorder
                                    )
                                )

                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Text(
                                        text = "⚡ ۵۰۰ms (شبکه پرسرعت)",
                                        style = MaterialTheme.typography.labelSmall,
                                        color = TextMuted,
                                        fontSize = 10.sp
                                    )
                                    Text(
                                        text = "🐢 ۵۰۰۰ms (شبکه ضعیف)",
                                        style = MaterialTheme.typography.labelSmall,
                                        color = TextMuted,
                                        fontSize = 10.sp
                                    )
                                }
                            }

                            // Auto Refresh Presets
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                SectionTitle(
                                    icon = Icons.Default.Refresh,
                                    iconTint = CyberCyan,
                                    title = "فاصله بروزرسانی خودکار اطلاعات"
                                )
                                val badgeColor = when (selectedAutoRefreshSec) {
                                    5 -> CyberCyan
                                    10 -> CyberEmerald
                                    30 -> CyberAmber
                                    60 -> TextSecondary
                                    else -> TextMuted
                                }
                                Surface(
                                    shape = RoundedCornerShape(20.dp),
                                    color = badgeColor.copy(alpha = 0.15f),
                                    border = BorderStroke(0.5.dp, badgeColor.copy(alpha = 0.4f))
                                ) {
                                    Text(
                                        text = when (selectedAutoRefreshSec) {
                                            5 -> "سریع"
                                            10 -> "متعادل"
                                            30 -> "بهینه"
                                            60 -> "کم‌مصرف"
                                            else -> "دستی"
                                        },
                                        style = MaterialTheme.typography.labelSmall,
                                        color = badgeColor,
                                        fontWeight = FontWeight.Bold,
                                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                    )
                                }
                            }

                            val presetOptions = listOf(
                                5 to "۵ ثانیه",
                                10 to "۱۰ ثانیه",
                                30 to "۳۰ ثانیه",
                                60 to "۶۰ ثانیه",
                                0 to "غیرفعال (دستی)"
                            )

                            FlowRow(
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                verticalArrangement = Arrangement.spacedBy(8.dp),
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                presetOptions.forEach { (sec, label) ->
                                    val isSelected = selectedAutoRefreshSec == sec
                                    Surface(
                                        shape = RoundedCornerShape(12.dp),
                                        color = if (isSelected) CyberCyan.copy(alpha = 0.2f)
                                        else DarkSurface,
                                        border = BorderStroke(
                                            width = if (isSelected) 1.5.dp else 1.dp,
                                            color = if (isSelected) CyberCyan else DarkCardBorder
                                        ),
                                        modifier = Modifier
                                            .clickable { selectedAutoRefreshSec = sec }
                                            .testTag("polling_option_$sec")
                                    ) {
                                        Text(
                                            text = label,
                                            style = MaterialTheme.typography.labelMedium.copy(
                                                fontWeight = if (isSelected) FontWeight.Bold
                                                else FontWeight.Normal
                                            ),
                                            color = if (isSelected) CyberCyan else TextSecondary,
                                            modifier = Modifier.padding(
                                                horizontal = 12.dp,
                                                vertical = 8.dp
                                            )
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        // ==================== 3. NETWORK PING TEST ====================
        item(key = "ping_test_section") {
            GlassmorphicCard(
                glowColor = CyberPurple,
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    SectionTitle(
                        icon = Icons.Default.NetworkCheck,
                        iconTint = CyberPurple,
                        title = "⚡ تست سریع اتصال به ماینر"
                    )
                    Text(
                        text = "برای اطمینان از روشن بودن ماینر و باز بودن پورت، آدرس آی‌پیش رو وارد کنید و تست بزنید.",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        OutlinedTextField(
                            value = pingIpText,
                            onValueChange = { pingIpText = it },
                            label = { Text("آدرس آی‌پی ماینر (IP)") },
                            singleLine = true,
                            modifier = Modifier.weight(2f),
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = CyberPurple,
                                unfocusedBorderColor = DarkCardBorder,
                                focusedLabelColor = CyberPurple
                            )
                        )
                        OutlinedTextField(
                            value = pingPortText,
                            onValueChange = { pingPortText = it },
                            label = { Text("پورت") },
                            singleLine = true,
                            modifier = Modifier.weight(1f),
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = CyberPurple,
                                unfocusedBorderColor = DarkCardBorder,
                                focusedLabelColor = CyberPurple
                            )
                        )
                    }

                    Button(
                        onClick = { viewModel.runPingTest(pingIpText, pingPortText) },
                        colors = ButtonDefaults.buttonColors(
                            containerColor = CyberPurple,
                            contentColor = Color.White
                        ),
                        shape = RoundedCornerShape(10.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        if (pingResult?.isTesting == true) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(18.dp),
                                color = Color.White,
                                strokeWidth = 2.dp
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("در حال بررسی اتصال...")
                        } else {
                            Icon(
                                imageVector = Icons.Default.NetworkCheck,
                                contentDescription = null
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("تست اتصال ماینر", fontWeight = FontWeight.Bold)
                        }
                    }

                    pingResult?.let { res ->
                        if (!res.isTesting && res.message.isNotBlank()) {
                            Surface(
                                shape = RoundedCornerShape(12.dp),
                                color = if (res.isSuccess) CyberEmerald.copy(alpha = 0.15f)
                                else CyberRed.copy(alpha = 0.15f),
                                border = BorderStroke(
                                    width = 1.dp,
                                    color = if (res.isSuccess) CyberEmerald else CyberRed
                                ),
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Column(modifier = Modifier.padding(12.dp)) {
                                    Text(
                                        text = res.message,
                                        style = MaterialTheme.typography.bodySmall.copy(
                                            fontWeight = FontWeight.SemiBold
                                        ),
                                        color = if (res.isSuccess) CyberEmerald else CyberRed,
                                        fontFamily = FontFamily.Monospace
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }

        // ==================== 4. PASSWORD PROFILES ====================
        item(key = "password_profiles_section") {
            GlassmorphicCard(
                glowColor = CyberEmerald,
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        SectionTitle(
                            icon = Icons.Default.Key,
                            iconTint = CyberEmerald,
                            title = "🔐 رمزهای ورود به ماینر"
                        )
                        IconButton(
                            onClick = { showAddProfileDialog = true },
                            modifier = Modifier.size(32.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Add,
                                contentDescription = "افزودن رمز جدید",
                                tint = CyberEmerald
                            )
                        }
                    }

                    Text(
                        text = "ذخیره نام کاربری و رمزهای ماینرها برای ورود و تغییرات سریع.",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary
                    )

                    if (passwordProfiles.isEmpty()) {
                        Text(
                            text = "هیچ رمزی ذخیره نشده است.",
                            style = MaterialTheme.typography.bodySmall,
                            color = TextMuted
                        )
                    } else {
                        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            passwordProfiles.forEach { profile ->
                                Card(
                                    colors = CardDefaults.cardColors(
                                        containerColor = DarkSurface
                                    ),
                                    shape = RoundedCornerShape(10.dp),
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .border(
                                            0.5.dp,
                                            DarkCardBorder,
                                            RoundedCornerShape(10.dp)
                                        )
                                ) {
                                    Row(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(12.dp),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Column(modifier = Modifier.weight(1f)) {
                                            Text(
                                                text = profile.title,
                                                style = MaterialTheme.typography.bodyMedium.copy(
                                                    fontWeight = FontWeight.Bold
                                                ),
                                                color = MaterialTheme.colorScheme.onBackground
                                            )
                                            Spacer(modifier = Modifier.height(2.dp))
                                            Text(
                                                text = "نام کاربری: ${profile.username} | رمز: ${
                                                    "*".repeat(profile.password.length.coerceAtMost(8))
                                                }",
                                                style = MaterialTheme.typography.bodySmall,
                                                color = TextSecondary,
                                                fontFamily = FontFamily.Monospace
                                            )
                                        }
                                        IconButton(
                                            onClick = {
                                                viewModel.deletePasswordProfile(profile.id)
                                            },
                                            modifier = Modifier.size(28.dp)
                                        ) {
                                            Icon(
                                                imageVector = Icons.Default.Delete,
                                                contentDescription = "حذف",
                                                tint = CyberRed,
                                                modifier = Modifier.size(18.dp)
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }

                    OutlinedButton(
                        onClick = { showAddProfileDialog = true },
                        colors = ButtonDefaults.outlinedButtonColors(
                            contentColor = CyberEmerald
                        ),
                        shape = RoundedCornerShape(10.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Icon(
                            imageVector = Icons.Default.Add,
                            contentDescription = null,
                            tint = CyberEmerald
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("افزودن رمز جدید", color = CyberEmerald)
                    }
                }
            }
        }

        // ==================== 5. COLLAPSIBLE POOL PRESETS (قسمت تنظیمات استخر کشویی) ====================
        item(key = "pools_preset_section") {
            GlassmorphicCard(
                glowColor = CyberAmber,
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    // Collapsible Header
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { isPoolsExpanded = !isPoolsExpanded },
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.weight(1f)
                        ) {
                            SectionTitle(
                                icon = Icons.Default.Storage,
                                iconTint = CyberAmber,
                                title = "⛏️ تنظیمات استخرهای استخراج (پوول‌ها)"
                            )
                        }
                        IconButton(onClick = { isPoolsExpanded = !isPoolsExpanded }) {
                            Icon(
                                imageVector = if (isPoolsExpanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                                contentDescription = if (isPoolsExpanded) "بستن" else "باز کردن",
                                tint = CyberAmber
                            )
                        }
                    }

                    if (!isPoolsExpanded) {
                        Text(
                            text = "استخر اصلی: ${if (p1Url.isNotBlank()) p1Url else "تنظیم نشده"}",
                            style = MaterialTheme.typography.bodySmall,
                            color = TextMuted,
                            maxLines = 1
                        )
                    }

                    AnimatedVisibility(visible = isPoolsExpanded) {
                        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = "آدرس و ورکر استخرهای ۱، ۲ و ۳ برای تنظیم روی دستگاه‌ها.",
                                style = MaterialTheme.typography.bodySmall,
                                color = TextSecondary
                            )

                            Text(
                                text = "استخرهای پیشنهادی:",
                                style = MaterialTheme.typography.labelSmall,
                                color = TextMuted
                            )
                            FlowRow(
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                verticalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                val quickPools = listOf(
                                    "F2Pool" to "stratum+tcp://btc.f2pool.com:3333",
                                    "AntPool" to "stratum+tcp://btc.antpool.com:3333",
                                    "ViaBTC" to "stratum+tcp://btc.viabtc.top:3333",
                                    "Binance" to "stratum+tcp://btc.poolbinance.com:3333"
                                )
                                quickPools.forEach { (name, url) ->
                                    Surface(
                                        shape = RoundedCornerShape(8.dp),
                                        color = DarkSurface,
                                        border = BorderStroke(
                                            1.dp,
                                            CyberAmber.copy(alpha = 0.5f)
                                        ),
                                        modifier = Modifier.clickable { p1Url = url }
                                    ) {
                                        Text(
                                            text = "⚡ $name",
                                            style = MaterialTheme.typography.labelSmall,
                                            color = CyberAmber,
                                            modifier = Modifier.padding(
                                                horizontal = 8.dp,
                                                vertical = 4.dp
                                            )
                                        )
                                    }
                                }
                            }

                            // Pool 1
                            PoolConfigSection(
                                title = "استخر اصلی (Pool 1)",
                                titleColor = CyberAmber,
                                url = p1Url,
                                onUrlChange = { p1Url = it },
                                worker = p1Worker,
                                onWorkerChange = { p1Worker = it },
                                pass = p1Pass,
                                onPassChange = { p1Pass = it }
                            )

                            // Pool 2
                            PoolConfigSection(
                                title = "استخر رزرو ۱ (Pool 2)",
                                titleColor = TextSecondary,
                                url = p2Url,
                                onUrlChange = { p2Url = it },
                                worker = p2Worker,
                                onWorkerChange = { p2Worker = it },
                                pass = p2Pass,
                                onPassChange = { p2Pass = it }
                            )

                            // Pool 3
                            PoolConfigSection(
                                title = "استخر رزرو ۲ (Pool 3)",
                                titleColor = TextMuted,
                                url = p3Url,
                                onUrlChange = { p3Url = it },
                                worker = p3Worker,
                                onWorkerChange = { p3Worker = it },
                                pass = p3Pass,
                                onPassChange = { p3Pass = it }
                            )
                        }
                    }
                }
            }
        }

        // ==================== Save & Clear Buttons ====================
        item(key = "save_reset_section") {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Button(
                    onClick = {
                        val portValidation = validatePort(apiPortText)
                        if (!portValidation.isValid) return@Button

                        val newSettings = ScanSettings(
                            apiPort = apiPortText.toIntOrNull() ?: 4028,
                            timeoutMs = timeoutMsValue.toInt(),
                            concurrency = concurrencyValue.toInt(),
                            autoRefreshSec = selectedAutoRefreshSec,
                            customSubnet = customSubnetText.trim(),
                            pool1Url = p1Url.trim(),
                            pool1Worker = p1Worker.trim(),
                            pool1Pass = p1Pass.trim(),
                            pool2Url = p2Url.trim(),
                            pool2Worker = p2Worker.trim(),
                            pool2Pass = p2Pass.trim(),
                            pool3Url = p3Url.trim(),
                            pool3Worker = p3Worker.trim(),
                            pool3Pass = p3Pass.trim()
                        ).validated()

                        viewModel.updateSettings(newSettings)

                        showSaveSuccess = true
                        scope.launch {
                            kotlinx.coroutines.delay(2000)
                            showSaveSuccess = false
                        }
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (showSaveSuccess) CyberEmerald else CyberCyan,
                        contentColor = Color.Black
                    ),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(50.dp)
                        .testTag("save_settings_button")
                ) {
                    if (showSaveSuccess) {
                        Icon(
                            imageVector = Icons.Default.Check,
                            contentDescription = null
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("تنظیمات با موفقیت ذخیره شد ✓", fontWeight = FontWeight.Bold)
                    } else {
                        Icon(
                            imageVector = Icons.Default.Save,
                            contentDescription = null
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("ذخیره تنظیمات", fontWeight = FontWeight.Bold)
                    }
                }

                OutlinedButton(
                    onClick = { showClearDataDialog = true },
                    colors = ButtonDefaults.outlinedButtonColors(
                        contentColor = CyberRed
                    ),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .testTag("clear_data_button")
                ) {
                    Icon(
                        imageVector = Icons.Default.DeleteSweep,
                        contentDescription = null,
                        tint = CyberRed
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text("پاک کردن اطلاعات ذخیره شده", color = CyberRed)
                }
            }
        }

        item(key = "bottom_spacer") {
            Spacer(modifier = Modifier.height(24.dp))
        }
    }

    // ==================== Dialogs ====================

    if (showAddProfileDialog) {
        AlertDialog(
            onDismissRequest = { showAddProfileDialog = false },
            title = {
                Text(
                    text = "افزودن رمز جدید",
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Bold
                    ),
                    color = CyberEmerald
                )
            },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    OutlinedTextField(
                        value = newProfileTitle,
                        onValueChange = { newProfileTitle = it },
                        label = { Text("نام/عنوان (مثلا: فارم ۱)") },
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = CyberEmerald,
                            unfocusedBorderColor = DarkCardBorder
                        )
                    )
                    OutlinedTextField(
                        value = newProfileUser,
                        onValueChange = { newProfileUser = it },
                        label = { Text("نام کاربری (مثلا: admin)") },
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = CyberEmerald,
                            unfocusedBorderColor = DarkCardBorder
                        )
                    )
                    OutlinedTextField(
                        value = newProfilePass,
                        onValueChange = { newProfilePass = it },
                        label = { Text("رمز عبور") },
                        singleLine = true,
                        visualTransformation = PasswordVisualTransformation(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = CyberEmerald,
                            unfocusedBorderColor = DarkCardBorder
                        )
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        if (newProfileTitle.isNotBlank()) {
                            viewModel.addPasswordProfile(
                                newProfileTitle,
                                newProfileUser,
                                newProfilePass
                            )
                            newProfileTitle = ""
                            newProfileUser = "admin"
                            newProfilePass = "admin"
                            showAddProfileDialog = false
                        }
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = CyberEmerald,
                        contentColor = Color.Black
                    )
                ) {
                    Text("ذخیره", fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                OutlinedButton(onClick = { showAddProfileDialog = false }) {
                    Text("انصراف", color = TextSecondary)
                }
            },
            containerColor = DarkSurface,
            shape = RoundedCornerShape(16.dp)
        )
    }

    if (showClearDataDialog) {
        AlertDialog(
            onDismissRequest = { showClearDataDialog = false },
            title = { Text("پاک کردن اطلاعات") },
            text = {
                Text(
                    "آیا از پاک کردن کامل اطلاعات ذخیره شده مطمئن هستید؟ " +
                    "تمام ماینرها و تنظیمات ذخیره شده حذف خواهند شد."
                )
            },
            confirmButton = {
                Button(
                    onClick = {
                        showClearDataDialog = false
                        viewModel.clearAllData()
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = CyberRed,
                        contentColor = Color.White
                    )
                ) {
                    Text("پاک کردن همه")
                }
            },
            dismissButton = {
                OutlinedButton(onClick = { showClearDataDialog = false }) {
                    Text("انصراف", color = TextSecondary)
                }
            },
            containerColor = DarkSurface,
            titleContentColor = MaterialTheme.colorScheme.onBackground,
            textContentColor = TextSecondary
        )
    }
}

// ==================== Helper Components ====================

@Composable
private fun MetricSummaryChip(
    label: String,
    value: String,
    accentColor: Color,
    modifier: Modifier = Modifier
) {
    Surface(
        color = DarkSurfaceVariant.copy(alpha = 0.6f),
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(1.dp, accentColor.copy(alpha = 0.3f)),
        modifier = modifier
    ) {
        Column(
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 8.dp),
            horizontalAlignment = Alignment.Start
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                color = TextMuted,
                fontSize = 10.sp
            )
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = value,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Bold,
                color = accentColor,
                fontFamily = FontFamily.Monospace
            )
        }
    }
}

@Composable
private fun SectionTitle(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    iconTint: Color,
    title: String
) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = iconTint
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = title,
            style = MaterialTheme.typography.titleMedium.copy(
                fontWeight = FontWeight.Bold
            ),
            color = MaterialTheme.colorScheme.onBackground
        )
    }
}

@Composable
private fun PoolConfigSection(
    title: String,
    titleColor: Color,
    url: String,
    onUrlChange: (String) -> Unit,
    worker: String,
    onWorkerChange: (String) -> Unit,
    pass: String,
    onPassChange: (String) -> Unit
) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(
            text = title,
            style = MaterialTheme.typography.labelMedium.copy(
                fontWeight = FontWeight.Bold
            ),
            color = titleColor
        )
        OutlinedTextField(
            value = url,
            onValueChange = onUrlChange,
            label = { Text("آدرس استخر (stratum+tcp://...)") },
            singleLine = true,
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = titleColor,
                unfocusedBorderColor = DarkCardBorder
            ),
            modifier = Modifier.fillMaxWidth()
        )
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedTextField(
                value = worker,
                onValueChange = onWorkerChange,
                label = { Text("نام ورکر") },
                singleLine = true,
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = titleColor,
                    unfocusedBorderColor = DarkCardBorder
                ),
                modifier = Modifier.weight(1f)
            )
            OutlinedTextField(
                value = pass,
                onValueChange = onPassChange,
                label = { Text("رمز استخر") },
                singleLine = true,
                visualTransformation = PasswordVisualTransformation(),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = titleColor,
                    unfocusedBorderColor = DarkCardBorder
                ),
                modifier = Modifier.weight(1f)
            )
        }
    }
}

// ==================== Validation Helpers ====================

private data class ValidationResult(
    val isValid: Boolean,
    val message: String = ""
)

private fun validatePort(portText: String): ValidationResult {
    val port = portText.toIntOrNull()
    return when {
        port == null -> ValidationResult(false, "پورت باید عدد باشد")
        port < 1 || port > 65535 -> ValidationResult(
            false,
            "پورت باید بین ۱ تا ۶۵۵۳۵ باشد"
        )
        else -> ValidationResult(true)
    }
}
