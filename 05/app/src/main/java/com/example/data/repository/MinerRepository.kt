package com.example.data.repository

import android.content.Context
import android.util.Log
import androidx.room.withTransaction
import com.example.data.local.MinerDao
import com.example.data.local.MinerEntity
import com.example.data.local.SettingsRepository
import com.example.data.network.ArpReader
import com.example.data.network.SubnetDetector
import com.example.data.network.SubnetInfo
import com.example.data.network.WhatsMinerApiClient
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicInteger

/**
 * وضعیت اسکن شبکه
 */
data class ScanProgressState(
    val isScanning: Boolean = false,
    val scannedCount: Int = 0,
    val totalHosts: Int = 254,
    val foundCount: Int = 0,
    val currentScanningIp: String = "",
    val subnetCidr: String = "",
    val errorMessage: String? = null,
    val elapsedMs: Long = 0L
) {
    val progressPercent: Float
        get() = if (totalHosts > 0) (scannedCount.toFloat() / totalHosts * 100).coerceIn(0f, 100f) else 0f
}

/**
 * نتیجه اسکن یک IP
 */
private sealed class ScanResult {
    data class Found(val miner: MinerEntity) : ScanResult()
    object NotFound : ScanResult()
    data class Error(val message: String) : ScanResult()
}

/**
 * Repository مدیریت ماینرها با قابلیت اسکن شبکه
 */
class MinerRepository(context: Context) {

    companion object {
        private const val TAG = "MinerRepository"
        private const val UI_UPDATE_INTERVAL = 3  // آپدیت هر ۳ آیتم
        private const val BATCH_SAVE_SIZE = 10    // ذخیره batch هر ۱۰ ماینر
        private const val SCAN_TIMEOUT_MS = 5 * 60 * 1000L // ۵ دقیقه timeout کلی
    }

    private val appContext = context.applicationContext
    private val db = com.example.data.local.AppDatabase.getDatabase(appContext)
    private val dao: MinerDao = db.minerDao()

    val settingsRepo = SettingsRepository(appContext)
    val subnetDetector = SubnetDetector(appContext)

    // Scope با قابلیت cleanup
    private val supervisorJob = SupervisorJob()
    private val repositoryScope = CoroutineScope(supervisorJob + Dispatchers.IO)

    val allMiners: Flow<List<MinerEntity>> = dao.getAllMiners()

    private val _scanState = MutableStateFlow(ScanProgressState())
    val scanState: StateFlow<ScanProgressState> = _scanState.asStateFlow()

    private var scanJob: Job? = null

    // ==================== Query Methods ====================

    suspend fun getAllMinersList(): List<MinerEntity> = dao.getAllMinersList()

    fun getMinerByIp(ipAddress: String): Flow<MinerEntity?> = dao.getMinerByIp(ipAddress)

    suspend fun getMinerByIpSync(ipAddress: String): MinerEntity? = dao.getMinerByIpSync(ipAddress)

    suspend fun getSubnetInfo(customSubnet: String = ""): SubnetInfo =
        subnetDetector.getSubnetInfo(customSubnet)

    // ==================== Scan Methods ====================

    /**
     * شروع اسکن شبکه با Worker Pool بهینه
     */
    fun startSubnetScan(customSubnet: String = "") {
        if (_scanState.value.isScanning) {
            Log.w(TAG, "Scan already in progress, ignoring")
            return
        }

        scanJob?.cancel()
        scanJob = repositoryScope.launch {
            try {
                executeScan(customSubnet)
            } catch (e: CancellationException) {
                Log.i(TAG, "Scan cancelled")
                _scanState.value = _scanState.value.copy(
                    isScanning = false,
                    currentScanningIp = "Scan Cancelled"
                )
            } catch (e: Exception) {
                Log.e(TAG, "Scan failed", e)
                _scanState.value = _scanState.value.copy(
                    isScanning = false,
                    errorMessage = e.message ?: "Unknown error during scan"
                )
            }
        }
    }

    fun startSubnetScan(scope: CoroutineScope, customSubnet: String = "") {
        startSubnetScan(customSubnet)
    }

    /**
     * توقف اسکن
     */
    fun stopScan() {
        scanJob?.cancel()
        scanJob = null
        _scanState.value = _scanState.value.copy(
            isScanning = false,
            currentScanningIp = "Scan Stopped"
        )
    }

    /**
     * Cleanup: برای زمان نابودی ViewModel/Repository
     */
    fun cleanup() {
        scanJob?.cancel()
        supervisorJob.cancel()
    }

    // ==================== Single Miner Operations ====================

    suspend fun refreshSingleMiner(ipAddress: String) {
        val settings = settingsRepo.getSettings()
        try {
            val updatedMiner = WhatsMinerApiClient.queryMinerDetails(
                ipAddress, settings.apiPort, settings.timeoutMs
            )
            saveOrUpdateMinerPreservingAlias(updatedMiner)
        } catch (e: Exception) {
            Log.w(TAG, "Failed to refresh miner $ipAddress: ${e.message}")
        }
    }

    suspend fun saveAlias(ipAddress: String, alias: String) {
        dao.updateAlias(ipAddress, alias)
    }

    suspend fun deleteMiner(ipAddress: String) {
        dao.deleteByIp(ipAddress)
    }

    suspend fun deleteMiners(ipAddresses: List<String>) {
        dao.deleteByIps(ipAddresses)
    }

    suspend fun clearAllMiners() {
        dao.clearAll()
    }

    // ==================== Private: Scan Logic ====================

    private suspend fun executeScan(customSubnet: String) {
        val startTime = System.currentTimeMillis()
        val settings = settingsRepo.getSettings()
        
        val cleanInput = if (customSubnet.startsWith("0.0.0")) "" else customSubnet
        val cleanSetting = if (settings.customSubnet.startsWith("0.0.0")) "" else settings.customSubnet
        
        var subnetInfo = subnetDetector.getSubnetInfo(
            cleanInput.ifBlank { cleanSetting }
        )

        if (!subnetInfo.isValid || subnetInfo.baseIp.startsWith("0.0.0") || subnetInfo.localIp == "0.0.0.0") {
            Log.w(TAG, "Detected subnet is 0.0.0.0 or invalid, using fallback modem subnet 192.168.1.0/24")
            subnetInfo = SubnetInfo(
                localIp = "192.168.1.1",
                subnetMask = "255.255.255.0",
                subnetCidr = "192.168.1.0/24",
                baseIp = "192.168.1.",
                totalHosts = 254,
                interfaceName = "fallback-default",
                isWifiConnected = subnetDetector.isNetworkConnected()
            )
        }

        Log.i(TAG, "Starting scan: ${subnetInfo.subnetCidr} (${subnetInfo.totalHosts} hosts, concurrency=${settings.concurrency})")

        _scanState.value = ScanProgressState(
            isScanning = true,
            scannedCount = 0,
            totalHosts = subnetInfo.totalHosts,
            foundCount = 0,
            currentScanningIp = "${subnetInfo.baseIp}1",
            subnetCidr = subnetInfo.subnetCidr
        )

        val baseIp = subnetInfo.baseIp
        val totalHosts = subnetInfo.totalHosts
        val concurrency = settings.concurrency.coerceIn(1, 20)

        val scannedCounter = AtomicInteger(0)
        val foundCounter = AtomicInteger(0)
        val batchBuffer = mutableListOf<MinerEntity>()
        val batchMutex = Mutex()

        // Warm up ARP cache
        ArpReader.forceRefresh()

        try {
            withTimeout(SCAN_TIMEOUT_MS) {
                coroutineScope {
                    val ipList = (1..totalHosts).map { "$baseIp$it" }
                    val chunks = ipList.chunked((totalHosts / concurrency).coerceAtLeast(1))

                    for (chunk in chunks) {
                        launch(Dispatchers.IO) {
                            for (ip in chunk) {
                                if (!isActive) break

                                val result = scanSingleIp(ip, settings.apiPort, settings.timeoutMs)

                                when (result) {
                                    is ScanResult.Found -> {
                                        foundCounter.incrementAndGet()
                                        var toSave: List<MinerEntity>? = null
                                        batchMutex.withLock {
                                            batchBuffer.add(result.miner)
                                            if (batchBuffer.size >= BATCH_SAVE_SIZE) {
                                                toSave = batchBuffer.toList()
                                                batchBuffer.clear()
                                            }
                                        }
                                        toSave?.let { saveBatch(it) }
                                    }
                                    is ScanResult.Error -> {
                                        Log.d(TAG, "Error scanning $ip: ${result.message}")
                                    }
                                    ScanResult.NotFound -> { /* ignore */ }
                                }

                                val currentScanned = scannedCounter.incrementAndGet()

                                // Throttle UI Update
                                if (currentScanned % UI_UPDATE_INTERVAL == 0 || currentScanned == totalHosts) {
                                    _scanState.value = _scanState.value.copy(
                                        scannedCount = currentScanned,
                                        foundCount = foundCounter.get(),
                                        currentScanningIp = ip,
                                        elapsedMs = System.currentTimeMillis() - startTime
                                    )
                                }
                            }
                        }
                    }
                }
            }
        } catch (e: TimeoutCancellationException) {
            Log.w(TAG, "Scan timed out after ${SCAN_TIMEOUT_MS}ms")
        }

        // ذخیره batch باقیمانده
        val remaining = batchMutex.withLock {
            val items = batchBuffer.toList()
            batchBuffer.clear()
            items
        }
        if (remaining.isNotEmpty()) {
            saveBatch(remaining)
        }

        // آپدیت نهایی
        _scanState.value = _scanState.value.copy(
            isScanning = false,
            scannedCount = totalHosts,
            foundCount = foundCounter.get(),
            currentScanningIp = "Scan Completed",
            elapsedMs = System.currentTimeMillis() - startTime
        )

        Log.i(TAG, "Scan completed: ${foundCounter.get()} miners found in ${System.currentTimeMillis() - startTime}ms")
    }

    private suspend fun scanSingleIp(
        ip: String,
        apiPort: Int,
        timeoutMs: Int
    ): ScanResult = withContext(Dispatchers.IO) {
        try {
            val isReachable = WhatsMinerApiClient.probeHostSuspend(ip, apiPort, timeoutMs)
            if (!isReachable) return@withContext ScanResult.NotFound

            val miner = WhatsMinerApiClient.queryMinerDetailsSuspend(ip, apiPort, timeoutMs)
            if (miner.isOnline) {
                ScanResult.Found(miner)
            } else {
                ScanResult.NotFound
            }
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            ScanResult.Error(e.message ?: "Unknown error")
        }
    }

    private suspend fun saveBatch(miners: List<MinerEntity>) {
        if (miners.isEmpty()) return
        try {
            withContext(Dispatchers.IO) {
                db.withTransaction {
                    for (miner in miners) {
                        val existing = dao.getMinerByIpSync(miner.ipAddress)
                        val finalMiner = if (existing != null && existing.alias.isNotBlank()) {
                            miner.copy(alias = existing.alias)
                        } else {
                            miner
                        }
                        dao.insertOrUpdate(finalMiner)
                    }
                }
            }
            Log.d(TAG, "Batch saved: ${miners.size} miners")
        } catch (e: Exception) {
            Log.w(TAG, "Batch save failed: ${e.message}")
        }
    }

    private suspend fun saveOrUpdateMinerPreservingAlias(miner: MinerEntity) {
        withContext(Dispatchers.IO) {
            db.withTransaction {
                val existing = dao.getMinerByIpSync(miner.ipAddress)
                val finalMiner = if (existing != null && existing.alias.isNotBlank()) {
                    miner.copy(alias = existing.alias)
                } else {
                    miner
                }
                dao.insertOrUpdate(finalMiner)
            }
        }
    }
}
