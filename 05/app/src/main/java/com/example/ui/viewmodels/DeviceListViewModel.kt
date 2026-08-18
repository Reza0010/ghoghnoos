package com.example.ui.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.example.data.local.MinerEntity
import com.example.data.repository.MinerRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

enum class FilterStatus { ALL, ONLINE, OFFLINE, HIGH_TEMP, LOW_HASHRATE }
enum class SortOption { IP_ADDRESS, HASHRATE, TEMPERATURE, MODEL }

class DeviceListViewModel(private val repository: MinerRepository) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    private val _selectedStatus = MutableStateFlow(FilterStatus.ALL)
    val selectedStatus: StateFlow<FilterStatus> = _selectedStatus.asStateFlow()

    private val _sortOption = MutableStateFlow(SortOption.IP_ADDRESS)
    val sortOption: StateFlow<SortOption> = _sortOption.asStateFlow()

    val filteredMiners: StateFlow<List<MinerEntity>> = combine(
        repository.allMiners,
        _searchQuery,
        _selectedStatus,
        _sortOption
    ) { miners, query, status, sort ->
        miners.filter { miner ->
            val matchesQuery = query.isBlank() ||
                    miner.ipAddress.contains(query, ignoreCase = true) ||
                    miner.macAddress.contains(query, ignoreCase = true) ||
                    miner.model.contains(query, ignoreCase = true) ||
                    miner.hostname.contains(query, ignoreCase = true) ||
                    miner.workerName.contains(query, ignoreCase = true) ||
                    miner.alias.contains(query, ignoreCase = true)

            val matchesStatus = when (status) {
                FilterStatus.ALL -> true
                FilterStatus.ONLINE -> miner.isOnline
                FilterStatus.OFFLINE -> !miner.isOnline
                FilterStatus.HIGH_TEMP -> miner.temperatureC >= 75.0
                FilterStatus.LOW_HASHRATE -> miner.isOnline && miner.hashrateGhs < 10000.0
            }
            matchesQuery && matchesStatus
        }.sortedWith { a, b ->
            when (sort) {
                SortOption.IP_ADDRESS -> compareIps(a.ipAddress, b.ipAddress)
                SortOption.HASHRATE -> b.hashrateGhs.compareTo(a.hashrateGhs)
                SortOption.TEMPERATURE -> b.temperatureC.compareTo(a.temperatureC)
                SortOption.MODEL -> a.model.compareTo(b.model)
            }
        }
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = emptyList()
    )

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }

    fun onFilterStatusChanged(status: FilterStatus) {
        _selectedStatus.value = status
    }

    fun onSortOptionChanged(option: SortOption) {
        _sortOption.value = option
    }

    fun deleteMiner(ipAddress: String) {
        viewModelScope.launch {
            repository.deleteMiner(ipAddress)
        }
    }

    fun deleteMiners(ipAddresses: Collection<String>) {
        viewModelScope.launch {
            repository.deleteMiners(ipAddresses.toList())
        }
    }

    /**
     * 🚀 بهینه‌سازی: مقایسه عددی IP بدون allocation اضافی
     */
    private fun compareIps(ip1: String, ip2: String): Int {
        try {
            val parts1 = ip1.split(".")
            val parts2 = ip2.split(".")
            val size = minOf(parts1.size, parts2.size)
            for (i in 0 until size) {
                val n1 = parts1[i].toIntOrNull() ?: 0
                val n2 = parts2[i].toIntOrNull() ?: 0
                if (n1 != n2) return n1.compareTo(n2)
            }
            return parts1.size.compareTo(parts2.size)
        } catch (_: Exception) {
            return ip1.compareTo(ip2)
        }
    }

    class Factory(private val repository: MinerRepository) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            return DeviceListViewModel(repository) as T
        }
    }
}
