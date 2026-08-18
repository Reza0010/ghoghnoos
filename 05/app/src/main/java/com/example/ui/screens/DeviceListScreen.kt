package com.example.ui.screens

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
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
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.layout.heightIn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.Air
import androidx.compose.material.icons.filled.Checklist
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.DeleteForever
import androidx.compose.material.icons.filled.Deselect
import androidx.compose.material.icons.filled.DeveloperBoard
import androidx.compose.material.icons.filled.FilterList
import androidx.compose.material.icons.filled.GridView
import androidx.compose.material.icons.filled.Memory
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.SelectAll
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material.icons.filled.TableRows
import androidx.compose.material.icons.filled.Thermostat
import androidx.compose.material.icons.filled.ViewList
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CheckboxDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.local.HashboardData
import com.example.data.local.MinerEntity
import com.example.ui.components.GlassmorphicCard
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
import com.example.ui.viewmodels.DeviceListViewModel
import com.example.ui.viewmodels.FilterStatus
import com.example.ui.viewmodels.SortOption

enum class MinerListMode {
    DETAILED, // کارت کامل با گیج هشبرد و فن
    GRID,     // شبکه‌ای 2 ستونه
    COMPACT   // متراکم تک سطری
}

@Composable
fun DeviceListScreen(
    viewModel: DeviceListViewModel,
    onNavigateToDeviceDetails: (String) -> Unit
) {
    val miners by viewModel.filteredMiners.collectAsState()
    val searchQuery by viewModel.searchQuery.collectAsState()
    val selectedStatus by viewModel.selectedStatus.collectAsState()
    val sortOption by viewModel.sortOption.collectAsState()
    var listMode by remember { mutableStateOf(MinerListMode.DETAILED) }
    var minerToDelete by remember { mutableStateOf<MinerEntity?>(null) }

    // Batch Selection States
    var isSelectionMode by remember { mutableStateOf(false) }
    val selectedIps = remember { mutableStateListOf<String>() }
    var showBatchDeleteDialog by remember { mutableStateOf(false) }
    val context = LocalContext.current

    // Single Miner Delete Dialog
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

    // Batch Delete Dialog
    if (showBatchDeleteDialog) {
        AlertDialog(
            onDismissRequest = { showBatchDeleteDialog = false },
            title = {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.DeleteForever,
                        contentDescription = null,
                        tint = CyberRed,
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "حذف گروهی ${selectedIps.size} ماینر",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = CyberRed
                    )
                }
            },
            text = {
                Column(
                    verticalArrangement = Arrangement.spacedBy(10.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = "آیا از حذف دائمی ${selectedIps.size} ماینر انتخاب‌شده از پایگاه‌داده اطمینان دارید؟ تمام سوابق، هش‌ریت و تنظیمات این دستگاه‌ها پاک خواهد شد.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = TextSecondary
                    )

                    // Selected IPs Preview Container
                    Surface(
                        color = DarkSurfaceVariant,
                        shape = RoundedCornerShape(10.dp),
                        border = androidx.compose.foundation.BorderStroke(0.5.dp, CyberRed.copy(alpha = 0.5f)),
                        modifier = Modifier
                            .fillMaxWidth()
                            .heightIn(max = 130.dp)
                    ) {
                        Column(
                            modifier = Modifier
                                .padding(10.dp)
                                .verticalScroll(rememberScrollState()),
                            verticalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            selectedIps.forEach { ip ->
                                val m = miners.find { it.ipAddress == ip }
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(
                                        text = "• ${ip}",
                                        style = MaterialTheme.typography.bodySmall,
                                        fontFamily = FontFamily.Monospace,
                                        color = CyberCyan,
                                        fontWeight = FontWeight.Bold
                                    )
                                    Text(
                                        text = m?.alias?.ifBlank { m.model } ?: "",
                                        style = MaterialTheme.typography.labelSmall,
                                        color = TextMuted
                                    )
                                }
                            }
                        }
                    }
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        val count = selectedIps.size
                        viewModel.deleteMiners(selectedIps.toList())
                        android.widget.Toast.makeText(context, "$count ماینر با موفقیت حذف شدند", android.widget.Toast.LENGTH_SHORT).show()
                        selectedIps.clear()
                        isSelectionMode = false
                        showBatchDeleteDialog = false
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = CyberRed, contentColor = Color.White),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.DeleteForever,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("حذف قطعی (${selectedIps.size})", fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                OutlinedButton(
                    onClick = { showBatchDeleteDialog = false },
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
            .windowInsetsPadding(WindowInsets.navigationBars)
            .padding(horizontal = 16.dp)
            .testTag("device_list_screen")
            .semantics { contentDescription = "لیست ماینرها" },
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // ==================== Header & Batch Selection Switcher ====================
        item(key = "header") {
            Spacer(modifier = Modifier.height(8.dp))

            if (isSelectionMode) {
                // Cyberpunk Batch Selection Toolbar
                Surface(
                    shape = RoundedCornerShape(14.dp),
                    color = DarkSurfaceVariant,
                    border = androidx.compose.foundation.BorderStroke(1.dp, if (selectedIps.isNotEmpty()) CyberRed else CyberCyan),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 12.dp, vertical = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            IconButton(
                                onClick = {
                                    if (selectedIps.size == miners.size) {
                                        selectedIps.clear()
                                    } else {
                                        selectedIps.clear()
                                        selectedIps.addAll(miners.map { it.ipAddress })
                                    }
                                }
                            ) {
                                Icon(
                                    imageVector = if (selectedIps.size == miners.size && miners.isNotEmpty()) Icons.Default.Deselect else Icons.Default.SelectAll,
                                    contentDescription = "انتخاب همه",
                                    tint = CyberCyan
                                )
                            }

                            Column {
                                Text(
                                    text = if (selectedIps.isEmpty()) "انتخاب ماینرها" else "${selectedIps.size} از ${miners.size} ماینر انتخاب شده",
                                    style = MaterialTheme.typography.titleSmall,
                                    fontWeight = FontWeight.Bold,
                                    color = if (selectedIps.isNotEmpty()) CyberCyan else MaterialTheme.colorScheme.onBackground
                                )
                                Text(
                                    text = "برای حذف گروهی علامت‌گذاری فرمایید",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = TextMuted
                                )
                            }
                        }

                        Row(
                            horizontalArrangement = Arrangement.spacedBy(6.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            if (selectedIps.isNotEmpty()) {
                                Button(
                                    onClick = { showBatchDeleteDialog = true },
                                    colors = ButtonDefaults.buttonColors(containerColor = CyberRed, contentColor = Color.White),
                                    shape = RoundedCornerShape(10.dp)
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.DeleteForever,
                                        contentDescription = "حذف گروهی",
                                        modifier = Modifier.size(18.dp)
                                    )
                                    Spacer(modifier = Modifier.width(4.dp))
                                    Text(
                                        text = "حذف (${selectedIps.size})",
                                        style = MaterialTheme.typography.labelMedium,
                                        fontWeight = FontWeight.Bold
                                    )
                                }
                            }

                            IconButton(
                                onClick = {
                                    isSelectionMode = false
                                    selectedIps.clear()
                                }
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Close,
                                    contentDescription = "بستن حالت انتخاب",
                                    tint = TextMuted
                                )
                            }
                        }
                    }
                }
            } else {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "مدیریت و مانیتورینگ ماینرها",
                            style = MaterialTheme.typography.titleLarge.copy(
                                fontWeight = FontWeight.Bold
                            ),
                            color = MaterialTheme.colorScheme.onBackground
                        )
                        Text(
                            text = "${miners.size} ماینر فعال در شبکه",
                            style = MaterialTheme.typography.bodyMedium,
                            color = TextSecondary
                        )
                    }

                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        // Batch Delete Trigger Button
                        OutlinedButton(
                            onClick = {
                                isSelectionMode = true
                                selectedIps.clear()
                            },
                            shape = RoundedCornerShape(10.dp),
                            border = androidx.compose.foundation.BorderStroke(1.dp, CyberCyan.copy(alpha = 0.6f)),
                            colors = ButtonDefaults.outlinedButtonColors(contentColor = CyberCyan)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Checklist,
                                contentDescription = "انتخاب گروهی",
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("انتخاب گروهی", style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold)
                        }

                        // View Mode Switcher Toolbar
                        Surface(
                            shape = RoundedCornerShape(10.dp),
                            color = DarkSurfaceVariant,
                            border = androidx.compose.foundation.BorderStroke(0.5.dp, DarkCardBorder)
                        ) {
                            Row(
                                modifier = Modifier.padding(3.dp),
                                horizontalArrangement = Arrangement.spacedBy(2.dp)
                            ) {
                                ViewModeIconButton(
                                    icon = Icons.Default.ViewList,
                                    title = "کامل",
                                    isSelected = listMode == MinerListMode.DETAILED,
                                    onClick = { listMode = MinerListMode.DETAILED }
                                )
                                ViewModeIconButton(
                                    icon = Icons.Default.GridView,
                                    title = "شبکه",
                                    isSelected = listMode == MinerListMode.GRID,
                                    onClick = { listMode = MinerListMode.GRID }
                                )
                                ViewModeIconButton(
                                    icon = Icons.Default.TableRows,
                                    title = "فشرده",
                                    isSelected = listMode == MinerListMode.COMPACT,
                                    onClick = { listMode = MinerListMode.COMPACT }
                                )
                            }
                        }
                    }
                }
            }
        }

        // ==================== Advanced Search Bar ====================
        item(key = "search") {
            OutlinedTextField(
                value = searchQuery,
                onValueChange = { viewModel.onSearchQueryChanged(it) },
                placeholder = { Text("جستجو با آی‌پی، نام ورکر، مدل، مک یا استخر...") },
                leadingIcon = {
                    Icon(
                        imageVector = Icons.Default.Search,
                        contentDescription = "جستجو",
                        tint = CyberCyan
                    )
                },
                trailingIcon = {
                    if (searchQuery.isNotEmpty()) {
                        IconButton(onClick = { viewModel.onSearchQueryChanged("") }) {
                            Icon(
                                imageVector = Icons.Default.Clear,
                                contentDescription = "پاک کردن",
                                tint = TextMuted
                            )
                        }
                    }
                },
                singleLine = true,
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = CyberCyan,
                    unfocusedBorderColor = DarkCardBorder,
                    focusedLabelColor = CyberCyan,
                    cursorColor = CyberCyan,
                    focusedContainerColor = DarkSurface,
                    unfocusedContainerColor = DarkSurface
                ),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("device_search_input")
            )
        }

        // ==================== Quick Filter Chips ====================
        item(key = "filter_row") {
            LazyRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically,
                contentPadding = androidx.compose.foundation.layout.PaddingValues(vertical = 2.dp)
            ) {
                item {
                    Text(
                        text = "فیلتر:",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextMuted,
                        fontWeight = FontWeight.Bold
                    )
                }
                items(FilterStatus.entries) { status ->
                    val isSelected = selectedStatus == status
                    val chipColor = when (status) {
                        FilterStatus.ALL -> CyberCyan
                        FilterStatus.ONLINE -> CyberEmerald
                        FilterStatus.OFFLINE -> CyberRed
                        FilterStatus.HIGH_TEMP -> CyberAmber
                        FilterStatus.LOW_HASHRATE -> Color(0xFFFF9800)
                    }

                    FilterChip(
                        selected = isSelected,
                        onClick = { viewModel.onFilterStatusChanged(status) },
                        label = {
                            Text(
                                text = when (status) {
                                    FilterStatus.ALL -> "همه"
                                    FilterStatus.ONLINE -> "آنلاین"
                                    FilterStatus.OFFLINE -> "آفلاین"
                                    FilterStatus.HIGH_TEMP -> "دمای بالا (>75°C)"
                                    FilterStatus.LOW_HASHRATE -> "هش‌ریت کم"
                                },
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal
                            )
                        },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = chipColor.copy(alpha = 0.2f),
                            selectedLabelColor = chipColor,
                            containerColor = DarkSurface,
                            labelColor = TextSecondary
                        ),
                        border = FilterChipDefaults.filterChipBorder(
                            enabled = true,
                            selected = isSelected,
                            borderColor = DarkCardBorder,
                            selectedBorderColor = chipColor
                        ),
                        modifier = Modifier.semantics {
                            contentDescription = "فیلتر وضعیت: ${status.name}"
                        }
                    )
                }
            }
        }

        // ==================== Sort Options ====================
        item(key = "sort_row") {
            LazyRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically,
                contentPadding = androidx.compose.foundation.layout.PaddingValues(vertical = 2.dp)
            ) {
                item {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.FilterList,
                            contentDescription = null,
                            tint = TextMuted,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "مرتب‌سازی:",
                            style = MaterialTheme.typography.bodySmall,
                            color = TextMuted,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
                items(SortOption.entries) { sort ->
                    val isSelected = sortOption == sort
                    FilterChip(
                        selected = isSelected,
                        onClick = { viewModel.onSortOptionChanged(sort) },
                        label = {
                            Text(
                                text = when (sort) {
                                    SortOption.IP_ADDRESS -> "آی‌پی"
                                    SortOption.HASHRATE -> "هش‌ریت"
                                    SortOption.TEMPERATURE -> "دما"
                                    SortOption.MODEL -> "مدل"
                                },
                                style = MaterialTheme.typography.labelSmall
                            )
                        },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = CyberEmerald.copy(alpha = 0.2f),
                            selectedLabelColor = CyberEmerald,
                            containerColor = DarkSurface,
                            labelColor = TextSecondary
                        ),
                        border = FilterChipDefaults.filterChipBorder(
                            enabled = true,
                            selected = isSelected,
                            borderColor = DarkCardBorder,
                            selectedBorderColor = CyberEmerald
                        ),
                        modifier = Modifier.semantics {
                            contentDescription = "مرتب‌سازی: ${sort.name}"
                        }
                    )
                }
            }
        }

        // ==================== Devices List Content ====================
        if (miners.isEmpty()) {
            item(key = "empty_state") {
                EmptyDeviceListCard()
            }
        } else {
            when (listMode) {
                MinerListMode.DETAILED -> {
                    items(
                        items = miners,
                        key = { miner -> "detailed_${miner.ipAddress}" }
                    ) { miner ->
                        val isSelected = selectedIps.contains(miner.ipAddress)
                        DetailedGlassmorphicMinerCard(
                            miner = miner,
                            isSelectionMode = isSelectionMode,
                            isSelected = isSelected,
                            onSelectionToggle = {
                                if (isSelected) selectedIps.remove(miner.ipAddress) else selectedIps.add(miner.ipAddress)
                            },
                            onClick = {
                                if (isSelectionMode) {
                                    if (isSelected) selectedIps.remove(miner.ipAddress) else selectedIps.add(miner.ipAddress)
                                } else {
                                    onNavigateToDeviceDetails(miner.ipAddress)
                                }
                            },
                            onLongClick = {
                                if (!isSelectionMode) {
                                    isSelectionMode = true
                                    if (!selectedIps.contains(miner.ipAddress)) {
                                        selectedIps.add(miner.ipAddress)
                                    }
                                } else {
                                    minerToDelete = miner
                                }
                            }
                        )
                    }
                }
                MinerListMode.GRID -> {
                    val rows = miners.chunked(2)
                    items(
                        items = rows,
                        key = { row -> "grid_row_${row.first().ipAddress}" }
                    ) { rowMiners ->
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            rowMiners.forEach { miner ->
                                val isSelected = selectedIps.contains(miner.ipAddress)
                                GridGlassmorphicMinerCard(
                                    miner = miner,
                                    isSelectionMode = isSelectionMode,
                                    isSelected = isSelected,
                                    onSelectionToggle = {
                                        if (isSelected) selectedIps.remove(miner.ipAddress) else selectedIps.add(miner.ipAddress)
                                    },
                                    onClick = {
                                        if (isSelectionMode) {
                                            if (isSelected) selectedIps.remove(miner.ipAddress) else selectedIps.add(miner.ipAddress)
                                        } else {
                                            onNavigateToDeviceDetails(miner.ipAddress)
                                        }
                                    },
                                    onLongClick = {
                                        if (!isSelectionMode) {
                                            isSelectionMode = true
                                            if (!selectedIps.contains(miner.ipAddress)) {
                                                selectedIps.add(miner.ipAddress)
                                            }
                                        } else {
                                            minerToDelete = miner
                                        }
                                    },
                                    modifier = Modifier.weight(1f)
                                )
                            }
                            if (rowMiners.size == 1) {
                                Spacer(modifier = Modifier.weight(1f))
                            }
                        }
                    }
                }
                MinerListMode.COMPACT -> {
                    items(
                        items = miners,
                        key = { miner -> "compact_${miner.ipAddress}" }
                    ) { miner ->
                        val isSelected = selectedIps.contains(miner.ipAddress)
                        CompactGlassmorphicMinerCard(
                            miner = miner,
                            isSelectionMode = isSelectionMode,
                            isSelected = isSelected,
                            onSelectionToggle = {
                                if (isSelected) selectedIps.remove(miner.ipAddress) else selectedIps.add(miner.ipAddress)
                            },
                            onClick = {
                                if (isSelectionMode) {
                                    if (isSelected) selectedIps.remove(miner.ipAddress) else selectedIps.add(miner.ipAddress)
                                } else {
                                    onNavigateToDeviceDetails(miner.ipAddress)
                                }
                            },
                            onLongClick = {
                                if (!isSelectionMode) {
                                    isSelectionMode = true
                                    if (!selectedIps.contains(miner.ipAddress)) {
                                        selectedIps.add(miner.ipAddress)
                                    }
                                } else {
                                    minerToDelete = miner
                                }
                            }
                        )
                    }
                }
            }
        }

        item(key = "bottom_spacer") {
            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}

// ==================== Toolbar Button Component ====================

@Composable
private fun ViewModeIconButton(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    title: String,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(8.dp))
            .background(if (isSelected) CyberCyan.copy(alpha = 0.2f) else Color.Transparent)
            .clickable(onClick = onClick)
            .padding(horizontal = 8.dp, vertical = 4.dp),
        contentAlignment = Alignment.Center
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(
                imageVector = icon,
                contentDescription = title,
                tint = if (isSelected) CyberCyan else TextMuted,
                modifier = Modifier.size(16.dp)
            )
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = title,
                style = MaterialTheme.typography.labelSmall,
                color = if (isSelected) CyberCyan else TextMuted,
                fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                fontSize = 11.sp
            )
        }
    }
}

// ==================== 1. DETAILED GLASSMORPHIC CARD ====================

@Composable
fun DetailedGlassmorphicMinerCard(
    miner: MinerEntity,
    onClick: () -> Unit,
    onLongClick: (() -> Unit)? = null,
    isSelectionMode: Boolean = false,
    isSelected: Boolean = false,
    onSelectionToggle: (() -> Unit)? = null
) {
    val statusColor = if (miner.isOnline) CyberEmerald else CyberRed
    val cardGlowColor = if (isSelected) CyberCyan else if (miner.effectiveTemperatureC > 80) CyberAmber else statusColor

    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val pulseAlpha by infiniteTransition.animateFloat(
        initialValue = 0.4f,
        targetValue = 1.0f,
        animationSpec = infiniteRepeatable(
            animation = androidx.compose.animation.core.tween(1000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "alpha"
    )

    GlassmorphicCard(
        glowColor = cardGlowColor,
        onClick = onClick,
        onLongClick = onLongClick,
        modifier = Modifier
            .fillMaxWidth()
            .testTag("device_card_${miner.ipAddress}")
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            // Top Row: IP + Pulsing Status Dot + Badge / Selection Checkbox
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    // Pulsing Status Dot
                    Box(contentAlignment = Alignment.Center) {
                        if (miner.isOnline) {
                            Box(
                                modifier = Modifier
                                    .size(14.dp)
                                    .alpha(pulseAlpha)
                                    .background(CyberEmerald.copy(alpha = 0.3f), CircleShape)
                            )
                        }
                        Box(
                            modifier = Modifier
                                .size(8.dp)
                                .background(statusColor, CircleShape)
                        )
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    Column {
                        val titleText = miner.alias.ifBlank { miner.ipAddress }
                        Text(
                            text = titleText.trim(),
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = if (isSelected) CyberCyan else if (miner.alias.isNotBlank()) CyberCyan else MaterialTheme.colorScheme.onBackground
                        )
                        if (miner.alias.isNotBlank()) {
                            Text(
                                text = miner.ipAddress,
                                style = MaterialTheme.typography.labelSmall,
                                fontFamily = FontFamily.Monospace,
                                color = TextMuted
                            )
                        }
                    }
                }

                if (isSelectionMode) {
                    Checkbox(
                        checked = isSelected,
                        onCheckedChange = { onSelectionToggle?.invoke() },
                        colors = CheckboxDefaults.colors(
                            checkedColor = CyberCyan,
                            uncheckedColor = TextMuted,
                            checkmarkColor = Color.Black
                        )
                    )
                } else {
                    // Status Pill Badge
                    Surface(
                        color = statusColor.copy(alpha = 0.15f),
                        shape = RoundedCornerShape(8.dp),
                        border = androidx.compose.foundation.BorderStroke(0.5.dp, statusColor.copy(alpha = 0.4f))
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = if (miner.isOnline) "آنلاین" else "آفلاین",
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = FontWeight.Bold,
                                color = statusColor,
                                fontSize = 11.sp
                            )
                        }
                    }
                }
            }

            // Sub-info: Model & Worker
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Surface(
                    color = DarkSurfaceVariant,
                    shape = RoundedCornerShape(6.dp)
                ) {
                    Text(
                        text = miner.model.ifBlank { "WhatsMiner ASIC" },
                        style = MaterialTheme.typography.labelSmall,
                        color = CyberCyan,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Medium,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp)
                    )
                }

                if (miner.workerName.isNotBlank() && miner.workerName != "N/A") {
                    Text(
                        text = "ورکر: ${miner.workerName}",
                        style = MaterialTheme.typography.labelSmall,
                        color = TextSecondary,
                        fontSize = 11.sp
                    )
                }
            }

            // Sparkline Trend Mini Graph - Real current hashrate flat-line representation (no simulated seed fluctuations)
            val realSparklineData = remember(miner.hashrateThs) {
                List(12) { miner.hashrateThs }
            }
            SparklineGraph(
                dataPoints = realSparklineData,
                lineColor = if (miner.isOnline) CyberCyan else TextMuted,
                height = 28.dp
            )

            // Key Metrics Dashboard Row (Hashrate, Temp, Power)
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(DarkSurfaceVariant, RoundedCornerShape(10.dp))
                    .padding(horizontal = 12.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Hashrate
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Speed,
                        contentDescription = "هش‌ریت",
                        tint = CyberCyan,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Column {
                        Text(
                            text = "هش‌ریت",
                            style = MaterialTheme.typography.labelSmall,
                            color = TextMuted,
                            fontSize = 9.sp
                        )
                        Text(
                            text = miner.hashrateFormatted.trim(),
                            style = MaterialTheme.typography.bodySmall,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onBackground
                        )
                    }
                }

                // Temp
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Thermostat,
                        contentDescription = "دما",
                        tint = if (miner.effectiveTemperatureC > 80) CyberRed else CyberAmber,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Column {
                        Text(
                            text = "دما",
                            style = MaterialTheme.typography.labelSmall,
                            color = TextMuted,
                            fontSize = 9.sp
                        )
                        Text(
                            text = if (miner.effectiveTemperatureC > 0) "${miner.effectiveTemperatureC.toInt()} °C" else "نامشخص",
                            style = MaterialTheme.typography.bodySmall,
                            fontWeight = FontWeight.Bold,
                            color = if (miner.effectiveTemperatureC > 80) CyberRed else MaterialTheme.colorScheme.onBackground
                        )
                    }
                }

                // Power / Uptime
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Memory,
                        contentDescription = "پاور",
                        tint = CyberEmerald,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Column {
                        Text(
                            text = "مصرف برق",
                            style = MaterialTheme.typography.labelSmall,
                            color = TextMuted,
                            fontSize = 9.sp
                        )
                        Text(
                            text = if (miner.powerWatts > 0) "${miner.powerWatts} W" else "نرمال",
                            style = MaterialTheme.typography.bodySmall,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onBackground
                        )
                    }
                }
            }

            // ==================== Hashboard PCB Health Summary ====================
            BoardGaugeSummary(miner = miner)

            // ==================== Fan & Motor Live Monitoring ====================
            FanRpmMonitoringSummary(miner = miner)
        }
    }
}

// ==================== 2. HASHBOARD GAUGE SUMMARY ====================

@Composable
private fun BoardGaugeSummary(miner: MinerEntity) {
    val boards = miner.hashboardList
    val defaultBoards = if (boards.isNotEmpty()) boards else listOf(
        HashboardData(boardIndex = 1, status = if (miner.isOnline) "Alive" else "Dead", chipsCount = 108, hashrateThs = if (miner.isOnline) miner.hashrateThs / 3 else 0.0),
        HashboardData(boardIndex = 2, status = if (miner.isOnline) "Alive" else "Dead", chipsCount = 108, hashrateThs = if (miner.isOnline) miner.hashrateThs / 3 else 0.0),
        HashboardData(boardIndex = 3, status = if (miner.isOnline) "Alive" else "Dead", chipsCount = 108, hashrateThs = if (miner.isOnline) miner.hashrateThs / 3 else 0.0)
    )

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(DarkSurface, RoundedCornerShape(8.dp))
            .border(0.5.dp, DarkCardBorder, RoundedCornerShape(8.dp))
            .padding(8.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Default.DeveloperBoard,
                    contentDescription = null,
                    tint = CyberCyan,
                    modifier = Modifier.size(14.dp)
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text(
                    text = "هشبردها (Hashboards)",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextSecondary,
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Bold
                )
            }
            Text(
                text = "${defaultBoards.count { (it.isHealthy || it.status.equals("Alive", ignoreCase = true)) && miner.isOnline }}/${defaultBoards.size} فعال",
                style = MaterialTheme.typography.labelSmall,
                color = CyberCyan,
                fontSize = 10.sp
            )
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            defaultBoards.forEachIndexed { idx, board ->
                val boardOnline = (board.isHealthy || board.status.equals("Alive", ignoreCase = true)) && miner.isOnline
                val statusBg = if (boardOnline) CyberEmerald else CyberRed
                Surface(
                    shape = RoundedCornerShape(6.dp),
                    color = statusBg.copy(alpha = 0.12f),
                    border = androidx.compose.foundation.BorderStroke(0.5.dp, statusBg.copy(alpha = 0.3f)),
                    modifier = Modifier.weight(1f)
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(
                                modifier = Modifier
                                    .size(6.dp)
                                    .background(statusBg, CircleShape)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = "PCB ${board.boardIndex}",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onBackground,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                        Text(
                            text = if (boardOnline) "${board.chipsCount} chip" else "ERR",
                            style = MaterialTheme.typography.labelSmall,
                            color = if (boardOnline) TextMuted else CyberRed,
                            fontSize = 9.sp
                        )
                    }
                }
            }
        }
    }
}

// ==================== 3. LIVE FAN RPM MONITORING ====================

@Composable
private fun FanRpmMonitoringSummary(miner: MinerEntity) {
    val fanIn = if (miner.isOnline) {
        if (miner.fanInRpm > 0) miner.fanInRpm
        else if (miner.fanOutRpm == 0 && miner.fanSpeedRpm > 0) miner.fanSpeedRpm
        else 0
    } else 0

    val fanOut = if (miner.isOnline) {
        if (miner.fanOutRpm > 0) miner.fanOutRpm
        else if (miner.fanInRpm == 0 && miner.fanSpeedRpm > 0) miner.fanSpeedRpm
        else 0
    } else 0
    val maxRpm = 7200.0

    val fanInProgress = (fanIn / maxRpm).coerceIn(0.0, 1.0).toFloat()
    val fanOutProgress = (fanOut / maxRpm).coerceIn(0.0, 1.0).toFloat()

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(DarkSurface, RoundedCornerShape(8.dp))
            .border(0.5.dp, DarkCardBorder, RoundedCornerShape(8.dp))
            .padding(8.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Default.Air,
                    contentDescription = null,
                    tint = CyberAmber,
                    modifier = Modifier.size(14.dp)
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text(
                    text = "دور فن‌ها و تهویه (Fan RPM)",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextSecondary,
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Bold
                )
            }
            Text(
                text = if (miner.isOnline) "زنده / نرمال" else "متوقف",
                style = MaterialTheme.typography.labelSmall,
                color = if (miner.isOnline) CyberEmerald else CyberRed,
                fontSize = 10.sp,
                fontWeight = FontWeight.Bold
            )
        }

        // Fan 1 (Inlet)
        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "فن ورودی (Inlet): $fanIn RPM",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextMuted,
                    fontSize = 9.sp
                )
                Text(
                    text = "${(fanInProgress * 100).toInt()}%",
                    style = MaterialTheme.typography.labelSmall,
                    color = CyberCyan,
                    fontSize = 9.sp,
                    fontWeight = FontWeight.Bold
                )
            }
            LinearProgressIndicator(
                progress = { fanInProgress },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(4.dp)
                    .clip(RoundedCornerShape(2.dp)),
                color = if (fanIn > 6500) CyberAmber else CyberCyan,
                trackColor = DarkSurfaceVariant
            )
        }

        // Fan 2 (Outlet)
        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "فن خروجی (Outlet): $fanOut RPM",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextMuted,
                    fontSize = 9.sp
                )
                Text(
                    text = "${(fanOutProgress * 100).toInt()}%",
                    style = MaterialTheme.typography.labelSmall,
                    color = CyberCyan,
                    fontSize = 9.sp,
                    fontWeight = FontWeight.Bold
                )
            }
            LinearProgressIndicator(
                progress = { fanOutProgress },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(4.dp)
                    .clip(RoundedCornerShape(2.dp)),
                color = if (fanOut > 6500) CyberAmber else CyberCyan,
                trackColor = DarkSurfaceVariant
            )
        }
    }
}

// ==================== 4. GRID GLASSMORPHIC CARD ====================

@Composable
fun GridGlassmorphicMinerCard(
    miner: MinerEntity,
    onClick: () -> Unit,
    onLongClick: (() -> Unit)? = null,
    isSelectionMode: Boolean = false,
    isSelected: Boolean = false,
    onSelectionToggle: (() -> Unit)? = null,
    modifier: Modifier = Modifier
) {
    val statusColor = if (miner.isOnline) CyberEmerald else CyberRed
    val cardGlowColor = if (isSelected) CyberCyan else statusColor

    GlassmorphicCard(
        glowColor = cardGlowColor,
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
                            .background(statusColor, CircleShape)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = if (miner.isOnline) "آنلاین" else "آفلاین",
                        style = MaterialTheme.typography.labelSmall,
                        color = statusColor,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
                if (isSelectionMode) {
                    Checkbox(
                        checked = isSelected,
                        onCheckedChange = { onSelectionToggle?.invoke() },
                        colors = CheckboxDefaults.colors(
                            checkedColor = CyberCyan,
                            uncheckedColor = TextMuted,
                            checkmarkColor = Color.Black
                        )
                    )
                } else {
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                        contentDescription = "جزئیات",
                        tint = TextMuted,
                        modifier = Modifier.size(16.dp)
                    )
                }
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
                        fontSize = 12.sp
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

// ==================== 5. COMPACT GLASSMORPHIC CARD ====================

@Composable
fun CompactGlassmorphicMinerCard(
    miner: MinerEntity,
    onClick: () -> Unit,
    onLongClick: (() -> Unit)? = null,
    isSelectionMode: Boolean = false,
    isSelected: Boolean = false,
    onSelectionToggle: (() -> Unit)? = null
) {
    val statusColor = if (miner.isOnline) CyberEmerald else CyberRed
    val cardGlowColor = if (isSelected) CyberCyan else statusColor

    GlassmorphicCard(
        glowColor = cardGlowColor,
        onClick = onClick,
        onLongClick = onLongClick,
        modifier = Modifier
            .fillMaxWidth()
            .testTag("compact_miner_card_${miner.ipAddress}")
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp, vertical = 10.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.weight(1f)
            ) {
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .background(statusColor, CircleShape)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Column {
                    val displayName = miner.alias.ifBlank { miner.ipAddress }
                    Text(
                        text = displayName,
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold,
                        color = if (isSelected) CyberCyan else MaterialTheme.colorScheme.onBackground
                    )
                    Text(
                        text = "${miner.ipAddress} • ${miner.model.ifBlank { "ASIC" }}",
                        style = MaterialTheme.typography.labelSmall,
                        color = TextMuted,
                        fontSize = 10.sp
                    )
                }
            }

            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = miner.hashrateFormatted.trim(),
                        style = MaterialTheme.typography.bodySmall,
                        fontWeight = FontWeight.Bold,
                        color = CyberCyan
                    )
                    if (miner.effectiveTemperatureC > 0) {
                        Text(
                            text = "${miner.effectiveTemperatureC.toInt()} °C",
                            style = MaterialTheme.typography.labelSmall,
                            color = if (miner.effectiveTemperatureC > 80) CyberRed else CyberAmber,
                            fontSize = 10.sp
                        )
                    }
                }

                if (isSelectionMode) {
                    Checkbox(
                        checked = isSelected,
                        onCheckedChange = { onSelectionToggle?.invoke() },
                        colors = CheckboxDefaults.colors(
                            checkedColor = CyberCyan,
                            uncheckedColor = TextMuted,
                            checkmarkColor = Color.Black
                        )
                    )
                } else {
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                        contentDescription = "جزئیات",
                        tint = TextMuted,
                        modifier = Modifier.size(18.dp)
                    )
                }
            }
        }
    }
}

// ==================== EMPTY STATE ====================

@Composable
private fun EmptyDeviceListCard() {
    GlassmorphicCard(
        glowColor = DarkCardBorder,
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 16.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = Icons.Default.Memory,
                contentDescription = "خالی",
                tint = TextMuted,
                modifier = Modifier.size(40.dp)
            )
            Spacer(modifier = Modifier.height(12.dp))
            Text(
                text = "هیچ ماینری با مشخصات انتخابی یافت نشد",
                style = MaterialTheme.typography.titleSmall,
                color = TextSecondary
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "عبارت جستجو یا فیلترهای بالا را تغییر دهید.",
                style = MaterialTheme.typography.bodySmall,
                color = TextMuted
            )
        }
    }
}
