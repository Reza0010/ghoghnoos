package com.example.ui.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.example.data.local.MinerEntity
import com.example.data.network.SubnetInfo
import com.example.data.repository.MinerRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.supervisorScope

data class HomeDashboardState(
    val miners: List<MinerEntity> = emptyList(),
    val totalHashrateThs: Double = 0.0,
    val smoothedHashrateThs: Double = 0.0,
    val activeCount: Int = 0,
    val totalCount: Int = 0,
    val avgTempC: Double = 0.0,
    val smoothedAvgTempC: Double = 0.0,
    val totalPowerWatts: Int = 0,
    val subnetInfo: SubnetInfo = SubnetInfo(),
    val refreshIntervalSec: Int = 10,
    val lastUpdatedMillis: Long = System.currentTimeMillis()
)

class HomeViewModel(private val repository: MinerRepository) : ViewModel() {

    private var pollingJob: Job? = null

    init {
        // 🚀 مشاهده تغییرات settings و restart polling
        viewModelScope.launch {
            repository.settingsRepo.settingsFlow.collect { settings ->
                restartAutoPolling(settings.autoRefreshSec)
            }
        }
    }

    private fun restartAutoPolling(intervalSec: Int) {
        pollingJob?.cancel()
        if (intervalSec <= 0) return

        pollingJob = viewModelScope.launch(Dispatchers.IO) {
            while (isActive) {
                delay(intervalSec * 1000L)

                // 🚀 بهینه‌سازی: Refresh موازی با محدودیت concurrency
                val currentMiners = repository.getAllMinersList()
                val onlineMiners = currentMiners.filter { it.isOnline }

                if (onlineMiners.isNotEmpty()) {
                    supervisorScope {
                        val settings = repository.settingsRepo.getSettings()
                        val semaphore = kotlinx.coroutines.sync.Semaphore(settings.concurrency.coerceAtMost(10))

                        onlineMiners.map { miner ->
                            async {
                                semaphore.acquire()
                                try {
                                    repository.refreshSingleMiner(miner.ipAddress)
                                } finally {
                                    semaphore.release()
                                }
                            }
                        }.awaitAll()
                    }
                }
            }
        }
    }

    private var prevSmoothedHash = 0.0
    private var prevSmoothedTemp = 0.0

    // 🚀 SubnetInfo اکنون reactive است و با settings آپدیت می‌شود
    val dashboardState: StateFlow<HomeDashboardState> = combine(
        repository.allMiners,
        repository.settingsRepo.settingsFlow
    ) { miners, settings ->
        val active = miners.filter { it.isOnline }
        val totalGhs = active.sumOf { it.hashrateGhs }
        val totalThs = totalGhs / 1000.0
        val avgTemp = if (active.isNotEmpty()) {
            active.map { it.temperatureC }.filter { it > 0 }.let { temps ->
                if (temps.isNotEmpty()) temps.average() else 0.0
            }
        } else 0.0
        val totalPower = active.sumOf { it.powerWatts }

        // 🚀 الگوریتم میانگین‌گیری متحرک نمایی (EMA Smoothing Alpha = 0.35)
        val alpha = 0.35
        val smoothedHash = if (prevSmoothedHash == 0.0) totalThs else (alpha * totalThs + (1 - alpha) * prevSmoothedHash)
        val smoothedTemp = if (prevSmoothedTemp == 0.0) avgTemp else (alpha * avgTemp + (1 - alpha) * prevSmoothedTemp)

        prevSmoothedHash = smoothedHash
        prevSmoothedTemp = smoothedTemp

        // 🚀 SubnetInfo همیشه به‌روز
        val subnetInfo = repository.getSubnetInfo(settings.customSubnet)

        HomeDashboardState(
            miners = miners,
            totalHashrateThs = totalThs,
            smoothedHashrateThs = smoothedHash,
            activeCount = active.size,
            totalCount = miners.size,
            avgTempC = avgTemp,
            smoothedAvgTempC = smoothedTemp,
            totalPowerWatts = totalPower,
            subnetInfo = subnetInfo,
            refreshIntervalSec = settings.autoRefreshSec,
            lastUpdatedMillis = System.currentTimeMillis()
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = HomeDashboardState()
    )

    fun startQuickScan() {
        // 🚀 تطبیق با امضای جدید Repository (بدون scope)
        repository.startSubnetScan()
    }

    fun refreshAll() {
        viewModelScope.launch(Dispatchers.IO) {
            val miners = dashboardState.value.miners
            supervisorScope {
                miners.map { miner ->
                    async { repository.refreshSingleMiner(miner.ipAddress) }
                }.awaitAll()
            }
        }
    }

    fun setRefreshInterval(intervalSec: Int) {
        val currentSettings = repository.settingsRepo.getSettings()
        repository.settingsRepo.saveSettings(currentSettings.copy(autoRefreshSec = intervalSec))
    }

    fun deleteMiner(ipAddress: String) {
        viewModelScope.launch {
            repository.deleteMiner(ipAddress)
        }
    }

    class Factory(private val repository: MinerRepository) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            return HomeViewModel(repository) as T
        }
    }
}
