package com.example.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * موجودیت ماینر در دیتابیس Room
 */
@Entity(tableName = "miners")
data class MinerEntity(
    @PrimaryKey val ipAddress: String,
    val macAddress: String = "N/A",
    val hostname: String = "Whatsminer",
    val model: String = "WhatsMiner ASIC",
    val firmwareVersion: String = "N/A",
    val serialNumber: String = "N/A",
    val isOnline: Boolean = false,
    val hashrateGhs: Double = 0.0,
    val hashrateFormatted: String = "0.0 TH/s",
    val fanSpeedRpm: Int = 0,
    val temperatureC: Double = 0.0,
    val powerWatts: Int = 0,
    val miningPoolUrl: String = "N/A",
    val workerName: String = "N/A",
    val asicBoardStatus: String = "N/A",
    val uptimeSeconds: Long = 0L,
    val uptimeFormatted: String = "0h 0m",
    val systemLogs: String = "",
    val apiLogs: String = "",
    val lastSeenTimestamp: Long = System.currentTimeMillis(),
    val apiPort: Int = 4028,
    val isWhatsMinerApiAvailable: Boolean = false,
    val alias: String = "",
    val hashboardsJson: String = "",
    val errorCode: Int = 0,
    val errorMessage: String = "",
    val controlBoardHardware: String = "N/A",
    val historicalErrorCodes: String = "",
    val multiFanRpm: String = "",
    val fanInRpm: Int = 0,
    val fanOutRpm: Int = 0
) {

    // ==================== Computed Properties ====================

    val hashrateThs: Double
        get() = hashrateGhs / 1000.0

    val displayName: String
        get() = alias.ifBlank { hostname.ifBlank { ipAddress } }

    val isStale: Boolean
        get() = System.currentTimeMillis() - lastSeenTimestamp > 5 * 60 * 1000L // ۵ دقیقه

    val hashboardList: List<HashboardData>
        get() = HashboardData.jsonStringToList(hashboardsJson)

    val averageHashboardTempC: Double
        get() {
            val validTemps = hashboardList
                .flatMap { listOf(it.boardTempC, it.chipTempC) }
                .filter { it > 0.0 }
            return if (validTemps.isNotEmpty()) {
                validTemps.average()
            } else {
                if (temperatureC > 0) temperatureC else 72.0
            }
        }

    val resolvedModel: String
        get() {
            val trimmed = model.trim()
            if (trimmed.isNotBlank() &&
                !trimmed.equals("WhatsMiner ASIC", ignoreCase = true) &&
                !trimmed.equals("N/A", ignoreCase = true) &&
                !trimmed.contains("Port", ignoreCase = true)
            ) {
                return trimmed
            }
            return when {
                hashrateThs >= 115 -> "WhatsMiner M50S (126T)"
                hashrateThs >= 105 -> "WhatsMiner M50 (114T)"
                hashrateThs >= 98 -> "WhatsMiner M30S++ (108T)"
                hashrateThs >= 88 -> "WhatsMiner M30S+ (100T)"
                hashrateThs >= 78 -> "WhatsMiner M30S (88T)"
                hashrateThs >= 65 -> "WhatsMiner M20S (68T)"
                else -> "WhatsMiner M30S (88T)"
            }
        }

    val resolvedControlBoard: String
        get() {
            val cb = controlBoardHardware.trim()
            if (cb.isNotBlank() && !cb.equals("N/A", ignoreCase = true)) {
                return cb
            }
            return when {
                resolvedModel.contains("M50") -> "CB6-V10 (Linux H616)"
                resolvedModel.contains("M30S++") || resolvedModel.contains("M30S+") -> "CB4-V10 (Linux H6)"
                resolvedModel.contains("M30S") -> "CB4-V2 (Linux H3)"
                else -> "CB4-V2 (Linux H3)"
            }
        }

    val resolvedPsuModel: String
        get() {
            val pWatts = if (powerWatts > 0) powerWatts else 3400
            return when {
                pWatts >= 3400 -> "P222C / P221C (3500W Smart PSU)"
                pWatts >= 3100 -> "P221C / P21D (3300W High Efficiency)"
                pWatts >= 2800 -> "P21D / P21 (3100W Standard PSU)"
                else -> "P21-12V (2800W Integrated PSU)"
            }
        }

    val effectiveTemperatureC: Double
        get() {
            val boardMax = hashboardList.map { maxOf(it.boardTempC, it.chipTempC) }.filter { it > 0.0 }.maxOrNull()
            return if (boardMax != null && boardMax > 0.0) {
                boardMax
            } else {
                temperatureC
            }
        }

    val healthStatus: MinerHealth
        get() = when {
            !isOnline -> MinerHealth.OFFLINE
            isStale -> MinerHealth.STALE
            effectiveTemperatureC > 85 -> MinerHealth.OVERHEATED
            hashrateGhs <= 0 -> MinerHealth.NO_HASHRATE
            else -> MinerHealth.HEALTHY
        }

    // ==================== Validation ====================

    companion object {
        fun isValidIp(ip: String): Boolean {
            val parts = ip.split(".")
            return parts.size == 4 && parts.all {
                val num = it.toIntOrNull() ?: return false
                num in 0..255 && it == num.toString()
            }
        }
    }
}

/**
 * وضعیت سلامت ماینر
 */
enum class MinerHealth(val displayName: String, val colorHex: String) {
    HEALTHY("سالم", "#4CAF50"),
    OFFLINE("آفلاین", "#F44336"),
    STALE("قدیمی", "#FF9800"),
    OVERHEATED("داغ", "#FF5722"),
    NO_HASHRATE("بدون هش‌ریت", "#9E9E9E")
}
