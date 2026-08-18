package com.example.data.network

import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.FileReader

/**
 * خواننده ARP Table با caching و بهینه‌سازی برای اسکن شبکه
 *
 * فرمت /proc/net/arp:
 * IP address       HW type     Flags       HW address            Mask     Device
 * 192.168.1.1      0x1         0x2         AA:BB:CC:DD:EE:FF     *        wlan0
 */
object ArpReader {

    private const val TAG = "ArpReader"
    private const val ARP_FILE = "/proc/net/arp"
    private const val CACHE_TTL_MS = 10_000L // 10 ثانیه کش

    // Regex کامپایل شده (یک بار)
    private val MAC_REGEX = Regex("^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")
    private val INVALID_MACS = setOf(
        "00:00:00:00:00:00",
        "FF:FF:FF:FF:FF:FF",
        ""
    )

    // Cache: IP -> MAC
    private val arpCache = mutableMapOf<String, String>()
    private var lastCacheTime = 0L
    private val mutex = Mutex()

    /**
     * دریافت MAC از ARP cache با caching خودکار
     * برای استفاده در اسکن شبکه (بهترین عملکرد)
     */
    fun getMacFromArpCache(ipAddress: String): String {
        // Validation سریع
        if (ipAddress.isBlank() || !isValidIpv4(ipAddress)) return "N/A"

        // بررسی cache
        val now = System.currentTimeMillis()
        if (now - lastCacheTime < CACHE_TTL_MS) {
            arpCache[ipAddress]?.let { return it }
        }

        // خواندن کامل ARP table
        return try {
            refreshArpCache()
            arpCache[ipAddress] ?: "N/A"
        } catch (e: Exception) {
            Log.w(TAG, "ARP read failed: ${e.message}")
            "N/A"
        }
    }

    /**
     * نسخه suspend برای استفاده با Coroutines
     */
    suspend fun getMacFromArpCacheSuspend(ipAddress: String): String =
        withContext(Dispatchers.IO) {
            getMacFromArpCache(ipAddress)
        }

    /**
     * دریافت MAC برای چندین IP به صورت batch (بهینه برای اسکن)
     */
    suspend fun getMacsForIps(ips: List<String>): Map<String, String> =
        withContext(Dispatchers.IO) {
            refreshArpCache()
            ips.associateWith { ip ->
                arpCache[ip] ?: "N/A"
            }
        }

    /**
     * دریافت MAC و IP به صورت Map کامل
     */
    suspend fun getFullArpTable(): Map<String, ArpEntry> =
        withContext(Dispatchers.IO) {
            parseArpFile()
        }

    /**
     * پینگ کردن IP برای اضافه شدن به ARP cache
     * (قبل از خواندن ARP، باید IP در cache باشد)
     */
    suspend fun pingToRefreshArp(ip: String, timeoutMs: Int = 1000): Boolean =
        withContext(Dispatchers.IO) {
            try {
                val process = Runtime.getRuntime().exec(arrayOf(
                    "ping", "-c", "1", "-W", (timeoutMs / 1000).coerceAtLeast(1).toString(), ip
                ))
                val exitCode = process.waitFor()
                exitCode == 0
            } catch (e: Exception) {
                false
            }
        }

    /**
     * Force refresh کردن ARP cache
     */
    suspend fun forceRefresh(): Unit = withContext(Dispatchers.IO) {
        mutex.withLock {
            arpCache.clear()
            lastCacheTime = 0L
        }
        refreshArpCache()
    }

    // ==================== Private Methods ====================

    private fun refreshArpCache() {
        val now = System.currentTimeMillis()
        if (now - lastCacheTime < CACHE_TTL_MS && arpCache.isNotEmpty()) return

        try {
            BufferedReader(FileReader(ARP_FILE)).use { reader ->
                val newCache = mutableMapOf<String, String>()

                // Skip header line
                reader.readLine()

                var line: String?
                while (reader.readLine().also { line = it } != null) {
                    val entry = parseArpLine(line ?: continue) ?: continue
                    newCache[entry.ip] = entry.mac
                }

                // Atomic update
                synchronized(arpCache) {
                    arpCache.clear()
                    arpCache.putAll(newCache)
                    lastCacheTime = now
                }

                Log.d(TAG, "ARP cache refreshed: ${newCache.size} entries")
            }
        } catch (e: Exception) {
            Log.w(TAG, "Failed to refresh ARP cache: ${e.message}")
        }
    }

    private fun parseArpFile(): Map<String, ArpEntry> {
        val result = mutableMapOf<String, ArpEntry>()
        try {
            BufferedReader(FileReader(ARP_FILE)).use { reader ->
                reader.readLine() // Skip header

                var line: String?
                while (reader.readLine().also { line = it } != null) {
                    val tokens = (line ?: continue).trim().split("\\s+".toRegex())
                    if (tokens.size < 6) continue

                    val ip = tokens[0]
                    val flags = tokens[2]
                    val mac = tokens[3]
                    val device = tokens[5]

                    // فقط entry های complete (flag 0x2)
                    if (!isCompleteEntry(flags)) continue
                    if (!isValidMac(mac)) continue

                    result[ip] = ArpEntry(
                        ip = ip,
                        mac = mac.uppercase(),
                        device = device,
                        flags = flags
                    )
                }
            }
        } catch (e: Exception) {
            Log.w(TAG, "Parse ARP file failed: ${e.message}")
        }
        return result
    }

    private fun parseArpLine(line: String): ArpEntry? {
        val trimmed = line.trim()
        if (trimmed.isBlank()) return null

        val tokens = trimmed.split("\\s+".toRegex())
        if (tokens.size < 6) return null

        val ip = tokens[0]
        val flags = tokens[2]
        val mac = tokens[3]
        val device = tokens[5]

        // Validation
        if (!isValidIpv4(ip)) return null
        if (!isValidMac(mac)) return null
        if (!isCompleteEntry(flags)) return null

        return ArpEntry(ip, mac.uppercase(), device, flags)
    }

    private fun isValidMac(mac: String): Boolean {
        if (mac.length != 17) return false
        if (mac.uppercase() in INVALID_MACS) return false
        return MAC_REGEX.matches(mac)
    }

    private fun isValidIpv4(ip: String): Boolean {
        val parts = ip.split(".")
        if (parts.size != 4) return false
        return parts.all { part ->
            val num = part.toIntOrNull() ?: return false
            num in 0..255
        }
    }

    /**
     * بررسی اینکه آیا ARP entry کامل است
     * Flag 0x2 = Complete, 0x0 = Incomplete
     */
    private fun isCompleteEntry(flags: String): Boolean {
        return try {
            val flagValue = flags.removePrefix("0x").toInt(16)
            (flagValue and 0x2) != 0
        } catch (e: Exception) {
            false
        }
    }
}

/**
 * یک entry در ARP table
 */
data class ArpEntry(
    val ip: String,
    val mac: String,
    val device: String,
    val flags: String
) {
    val isComplete: Boolean
        get() = try {
            val flagValue = flags.removePrefix("0x").toInt(16)
            (flagValue and 0x2) != 0
        } catch (e: Exception) {
            false
        }
}
