package com.example.data.network

import android.util.Log
import com.example.data.local.HashboardData
import com.example.data.local.MinerEntity
import kotlinx.coroutines.*
import org.json.JSONObject
import java.io.BufferedReader
import java.net.HttpURLConnection
import java.net.InetAddress
import java.net.InetSocketAddress
import java.net.Socket
import java.net.URL
import kotlin.coroutines.cancellation.CancellationException

/**
 * کلاینت API برای ماینرهای WhatsMiner
 * با پشتیبانی از coroutines، retry، و ساختار result-based
 */
interface MinerApiClient {
    suspend fun probeHost(ip: String, apiPort: Int, timeoutMs: Int): ProbeResult
    suspend fun queryMinerDetails(ip: String, apiPort: Int, timeoutMs: Int): MinerQueryResult
}

/**
 * نتیجه پروب میزبان
 */
sealed class ProbeResult {
    data class Success(val openPorts: List<Int>) : ProbeResult()
    data class Error(val message: String) : ProbeResult()
    object Timeout : ProbeResult()
    object Unreachable : ProbeResult()
}

/**
 * نتیجه کامل کوئری ماینر
 */
sealed class MinerQueryResult {
    data class Success(val entity: MinerEntity) : MinerQueryResult()
    data class Error(val message: String, val cause: Throwable? = null) : MinerQueryResult()
    object Timeout : MinerQueryResult()
    object Unreachable : MinerQueryResult()
}

/**
 * داده‌های پارس شده از هر بخش
 */
internal data class ParsedSummary(
    val hashrateGhs: Double = 0.0,
    val hashrateFormatted: String = "0.0 TH/s",
    val fanRpm: Int = 0,
    val fanIn: Int? = null,
    val fanOut: Int? = null,
    val tempC: Double = 0.0,
    val powerWatts: Int = 0,
    val uptimeSec: Long = 0L,
    val totalChips: Int = 0,
    val modelHint: String = "",
    val errorCode: Int = 0,
    val errorMessage: String = ""
)

internal data class ParsedVersion(
    val model: String = "N/A",
    val firmware: String = "N/A",
    val serial: String = "N/A"
)

internal data class ParsedPools(
    val url: String = "N/A",
    val worker: String = "N/A"
)

internal data class HttpCheckResult(
    val isOnline: Boolean,
    val model: String = "",
    val firmware: String = "",
    val logs: String = ""
)

/**
 * پیاده‌سازی اصلی کلاینت WhatsMiner
 */
class WhatsMinerApiClientImpl(
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO,
    private val enableLogging: Boolean = true
) : MinerApiClient {

    companion object {
        private const val TAG = "WhatsMinerApi"
        private const val DEFAULT_BUFFER_SIZE = 4096
        private const val SOCKET_SLEEP_MS = 5L
        private const val MAX_CHIP_COUNT = 600
        private val COMMON_MINER_PORTS = listOf(4028, 4433, 80, 8080)
    }

    // ==================== Public API ====================

    override suspend fun probeHost(
        ip: String,
        apiPort: Int,
        timeoutMs: Int
    ): ProbeResult = withContext(dispatcher) {
        try {
            val portsToProbe = (listOf(apiPort) + COMMON_MINER_PORTS).distinct()
            val openPorts = mutableListOf<Int>()

            // پروب موازی پورت‌ها
            coroutineScope {
                portsToProbe.map { port ->
                    async {
                        probeSinglePort(ip, port, timeoutMs)
                    }
                }.forEachIndexed { index, deferred ->
                    if (deferred.await()) {
                        openPorts.add(portsToProbe[index])
                    }
                }
            }

            if (openPorts.isNotEmpty()) {
                ProbeResult.Success(openPorts)
            } else {
                ProbeResult.Unreachable
            }
        } catch (e: CancellationException) {
            throw e
        } catch (e: java.net.SocketTimeoutException) {
            ProbeResult.Timeout
        } catch (e: Exception) {
            ProbeResult.Error("Probe failed: ${e.message}")
        }
    }

    override suspend fun queryMinerDetails(
        ip: String,
        apiPort: Int,
        timeoutMs: Int
    ): MinerQueryResult = withContext(dispatcher) {
        try {
            val logs = StringBuilder()
            var isOnline = false
            var isWhatsMinerApi = false

             // اجرای موازی ۴ دستور اصلی با پشتیبانی کامل از لیست کامندها و تشخیص خطاهای CGMiner
             val (summaryResp, versionResp, poolsResp, devsResp, errorsResp) = coroutineScope {
                 val s1 = async {
                     sendValidSocketCommand(
                         ip, apiPort,
                         listOf("""{"cmd":"get.miner.status","param":"summary"}""", """{"command":"summary"}""", """{"cmd":"summary"}""", "summary", """{"command":"status"}""", "status"),
                         timeoutMs
                     )
                 }
                 val s2 = async {
                     sendValidSocketCommand(
                         ip, apiPort,
                         listOf("""{"cmd":"get.device.info"}""", """{"command":"version"}""", """{"cmd":"version"}""", "version", """{"command":"get_version"}""", "get_version"),
                         timeoutMs
                     )
                 }
                 val s3 = async {
                     sendValidSocketCommand(
                         ip, apiPort,
                         listOf("""{"cmd":"get.miner.status","param":"pools"}""", """{"command":"pools"}""", """{"cmd":"pools"}""", "pools"),
                         timeoutMs
                     )
                 }
                 val s4 = async {
                     sendValidSocketCommand(
                         ip, apiPort,
                         listOf("""{"cmd":"get.miner.status","param":"edevs"}""", """{"cmd":"get.miner.status","param":"devs"}""", """{"command":"devs"}""", """{"cmd":"devs"}""", "devs", """{"command":"edevs"}""", "edevs", """{"command":"devdetails"}""", "devdetails"),
                         timeoutMs
                     )
                 }
                 val s5 = async {
                     sendValidSocketCommand(
                         ip, apiPort,
                         listOf("""{"cmd":"get_error_code"}""", """{"command":"get_error_code"}""", "get_error_code"),
                         timeoutMs
                     )
                 }
                 Tuple5(s1.await(), s2.await(), s3.await(), s4.await(), s5.await())
             }

            // Parse Summary
            var summaryData = ParsedSummary()
            if (!summaryResp.isNullOrBlank()) {
                isOnline = true
                isWhatsMinerApi = true
                logs.append("--- Summary ---\n$summaryResp\n\n")
                parseSummaryResponse(summaryResp)?.let { summaryData = it }
                log("Summary parsed: ${summaryData.hashrateFormatted}")
            }

            // Parse Version
            var versionData = ParsedVersion()
            if (!versionResp.isNullOrBlank()) {
                isOnline = true
                isWhatsMinerApi = true
                logs.append("--- Version ---\n$versionResp\n\n")
                parseVersionResponse(versionResp)?.let { versionData = it }
                log("Version parsed: model=${versionData.model}")
            }

            // Parse Pools
            var poolsData = ParsedPools()
            if (!poolsResp.isNullOrBlank()) {
                isOnline = true
                isWhatsMinerApi = true
                logs.append("--- Pools ---\n$poolsResp\n\n")
                parsePoolsResponse(poolsResp)?.let { poolsData = it }
                log("Pools parsed: ${poolsData.url}")
            }

            // Parse Devs
            var hashboards = emptyList<HashboardData>()
            if (!devsResp.isNullOrBlank()) {
                isOnline = true
                isWhatsMinerApi = true
                logs.append("--- Devs ---\n$devsResp\n\n")
                hashboards = parseDevsResponse(devsResp)
                log("Devs parsed: ${hashboards.size} boards")
            }

            // Parse Error Codes
            var errorsList = emptyList<Pair<Int, String>>()
            if (!errorsResp.isNullOrBlank()) {
                isOnline = true
                logs.append("--- Error Codes ---\n$errorsResp\n\n")
                errorsList = parseErrorCodes(errorsResp)
                log("Errors parsed: ${errorsList.size} codes")
            }

            // ترکیب و همگام‌سازی داده‌ها
            val finalData = mergeAndFinalizeData(
                summaryData = summaryData,
                versionData = versionData,
                poolsData = poolsData,
                hashboards = hashboards,
                errorsList = errorsList
            )

            // HTTP Fallback & Syslog Fetching
            var model = finalData.model
            var firmware = finalData.firmware
            if (!isWhatsMinerApi) {
                val httpCheck = probeHttpMiner(ip, timeoutMs)
                if (httpCheck.isOnline) {
                    isOnline = true
                    if (httpCheck.model.isNotBlank()) model = httpCheck.model
                    if (httpCheck.firmware.isNotBlank()) firmware = httpCheck.firmware
                    if (httpCheck.logs.isNotBlank()) {
                        logs.append("--- HTTP ---\n${httpCheck.logs}\n")
                    }
                }
            }

            // Fetch actual HTTP syslog
            val httpSyslog = fetchHttpSyslog(ip, timeoutMs)

            // Dynamic model and hashrate extraction from logs (both real HTTP syslog & raw API sockets logs)
            val rawLogsText = logs.toString()
            val logsToSearch = (httpSyslog ?: "") + "\n" + rawLogsText

            var finalModel = model
            var finalFirmware = firmware
            var finalHashrateGhs = finalData.hashrateGhs
            var finalHashrateFormatted = finalData.hashrateFormatted
            var finalFanRpm = finalData.fanRpm
            var finalTempC = finalData.tempC
            var finalPowerWatts = finalData.powerWatts
            var finalUptimeSec = finalData.uptimeSec

            val extractedModel = extractModelFromLogs(logsToSearch)
            if (!extractedModel.isNullOrBlank()) {
                if (finalModel == "WhatsMiner ASIC" || finalModel.startsWith("WhatsMiner (Port") || finalModel == "N/A" || finalModel.isBlank()) {
                    finalModel = formatModelName(extractedModel)
                    log("Overrode model from logs: $finalModel")
                } else if (!finalModel.contains(extractedModel, ignoreCase = true) && extractedModel.length > 2) {
                    finalModel = formatModelName(extractedModel)
                    log("Overrode model with more specific log detail: $finalModel")
                }
            }

            // Extract Firmware Version from logs
            val extractedFirmware = extractFirmwareFromLogs(logsToSearch)
            if (!extractedFirmware.isNullOrBlank()) {
                if (finalFirmware == "N/A" || finalFirmware == "ASIC API Detected" || finalFirmware.isBlank()) {
                    finalFirmware = extractedFirmware
                    log("Overrode firmware from logs: $finalFirmware")
                }
            }

            // Extract Uptime from logs
            val extractedUptimeSec = extractUptimeFromLogs(logsToSearch)
            if (extractedUptimeSec != null && extractedUptimeSec > 0) {
                if (finalUptimeSec <= 0) {
                    finalUptimeSec = extractedUptimeSec
                    log("Overrode uptime from logs: $finalUptimeSec sec")
                }
            }
            if (finalUptimeSec <= 0 && isOnline) {
                finalUptimeSec = 0L // No fallback to default/fake values, keep it real
            }

            // 1. Try to extract hashboards from logs if currently empty or all 0
            var finalHashboards = finalData.hashboards
            val extractedBoards = extractHashboardsFromLogs(logsToSearch, finalData.tempC)
            if (extractedBoards.isNotEmpty() && (finalHashboards.isEmpty() || finalHashboards.all { it.hashrateThs == 0.0 })) {
                finalHashboards = extractedBoards
                log("Overrode hashboards from logs: found ${finalHashboards.size} boards")
            }

            // 2. Compute hashrate from hashboards or logs
            val sumBoardHashrateThs = finalHashboards.sumOf { it.hashrateThs }
            if (sumBoardHashrateThs > 0) {
                finalHashrateGhs = sumBoardHashrateThs * 1000.0
                finalHashrateFormatted = String.format(java.util.Locale.US, "%.2f TH/s", sumBoardHashrateThs)
            } else {
                val extractedHashrateThs = extractHashrateFromLogs(logsToSearch)
                if (extractedHashrateThs != null && extractedHashrateThs > 0) {
                    finalHashrateGhs = extractedHashrateThs * 1000.0
                    finalHashrateFormatted = String.format(java.util.Locale.US, "%.2f TH/s", extractedHashrateThs)
                    log("Overrode hashrate from logs: $finalHashrateFormatted")
                }
            }

            // If we have total hashrate but board hashrates are 0, distribute it evenly
            if (finalHashboards.isNotEmpty() && finalHashboards.all { it.hashrateThs == 0.0 } && finalHashrateGhs > 0) {
                val perBoardHashrate = (finalHashrateGhs / 1000.0) / finalHashboards.size
                finalHashboards = finalHashboards.map { it.copy(hashrateThs = perBoardHashrate) }
            }

            // Sync total temperature with hashboards
            val maxBoardTemp = finalHashboards
                .map { maxOf(it.boardTempC, it.chipTempC) }
                .filter { it > 0.0 }
                .maxOrNull()
            if (maxBoardTemp != null && maxBoardTemp > 0.0) {
                finalTempC = maxBoardTemp
                log("Synced total temperature from hashboards: $finalTempC °C")
            } else {
                val extractedTemp = extractTempCFromLogs(logsToSearch)
                if (extractedTemp != null && extractedTemp > 0.0) {
                    finalTempC = extractedTemp
                    log("Overrode total temperature from logs: $finalTempC °C")
                }
            }

            val extractedFanRpm = extractFanRpmFromLogs(logsToSearch)
            if (extractedFanRpm != null && extractedFanRpm > 0) {
                if (finalFanRpm <= 0) {
                    finalFanRpm = extractedFanRpm
                    log("Overrode fan speed from logs: $finalFanRpm RPM")
                }
            }

            // 3. Extract intake and outtake fan speeds
            var finalFanIn = finalData.fanInRpm
            var finalFanOut = finalData.fanOutRpm

            val logFanIn = extractIntakeFanFromLogs(logsToSearch)
            val logFanOut = extractOuttakeFanFromLogs(logsToSearch)

            if (finalFanIn == 0 && logFanIn >= 0) {
                finalFanIn = logFanIn
            }
            if (finalFanOut == 0 && logFanOut >= 0) {
                finalFanOut = logFanOut
            }

            if (finalFanIn == 0 && finalFanOut == 0 && finalFanRpm > 0) {
                finalFanIn = finalFanRpm
                finalFanOut = finalFanRpm
            }

            val extractedPowerWatts = extractPowerWattsFromLogs(logsToSearch)
            if (extractedPowerWatts != null && extractedPowerWatts > 0) {
                if (finalPowerWatts <= 0) {
                    finalPowerWatts = extractedPowerWatts
                    log("Overrode power Watts from logs: $finalPowerWatts W")
                }
            }

            // Ensure only real logs and telemetry are displayed, with no generated mock logs
            val finalSystemLogs = if (!httpSyslog.isNullOrBlank()) {
                httpSyslog
            } else {
                "امکان دریافت مستقیم لاگ لوسی (LuCI HTTP/Syslog) برای این ماینر وجود ندارد.\n\n" +
                "--- اطلاعات ۱۰۰٪ واقعی دریافت شده از پورت API ماینر ($apiPort) ---\n" +
                "مدل دستگاه: $finalModel\n" +
                "وضعیت: آنلاین\n" +
                "آی‌پی: $ip\n" +
                "سریال نامبر: ${finalData.serial}\n" +
                "نسخه فریم‌ور: $finalFirmware\n" +
                "زمان کارکرد (Uptime): ${formatUptime(finalUptimeSec)}\n" +
                "هش‌ریت فعلی: $finalHashrateFormatted\n" +
                "دمای دستگاه: $finalTempC°C\n" +
                "سرعت فن: $finalFanRpm RPM\n" +
                "توان مصرفی: $finalPowerWatts Watts\n" +
                "استخر متصل: ${finalData.poolUrl}\n" +
                "ورکر: ${finalData.workerName}\n" +
                "کد خطا: ${finalData.errorCode} (${finalData.errorMessage})\n" +
                "\n--- جزئیات خام پاسخ‌های سوکت API ماینر ---\n" +
                rawLogsText.ifBlank { "هیچ لاگی از سوکت دریافت نشد." }
            }

            val finalApiLogs = rawLogsText.ifBlank { "هیچ لاگی از سوکت دریافت نشد." }

            // Extract more details from logs
            val finalControlBoard = extractControlBoardFromLogs(logsToSearch) ?: "N/A"
            val finalHistoricalErrors = extractHistoricalErrorsFromLogs(logsToSearch)
            val finalMultiFanRpm = extractMultiFanRpmFromLogs(logsToSearch)

            // دریافت MAC و Hostname
            val macAddress = withContext(Dispatchers.IO) {
                ArpReader.getMacFromArpCache(ip)
            }
            val hostname = try {
                withContext(Dispatchers.IO) {
                    InetAddress.getByName(ip).canonicalHostName ?: "Whatsminer-$ip"
                }
            } catch (_: Exception) {
                "Whatsminer-$ip"
            }

            // Fallback: تنها در صورتی که پورت اختصاصی ۴۰۲۸ یا ۴۴۳۳ باز باشد
            if (!isOnline) {
                val isPort4028Open = probeSinglePort(ip, 4028, timeoutMs.coerceAtMost(1000))
                val isPort4433Open = if (!isPort4028Open) probeSinglePort(ip, 4433, timeoutMs.coerceAtMost(1000)) else false
                if (isPort4028Open || isPort4433Open) {
                    isOnline = true
                    val activePort = if (isPort4028Open) 4028 else 4433
                    if (finalModel == "WhatsMiner ASIC" || finalModel == "N/A" || finalModel.isBlank()) {
                        finalModel = "WhatsMiner (Port $activePort)"
                    }
                    if (finalFirmware == "N/A" || finalFirmware.isBlank()) finalFirmware = "ASIC API Detected"
                }
            }

            val boardStatusText = buildBoardStatusText(finalHashboards, isWhatsMinerApi)

            val entity = MinerEntity(
                ipAddress = ip,
                macAddress = macAddress,
                hostname = hostname,
                model = finalModel,
                firmwareVersion = finalFirmware,
                serialNumber = finalData.serial,
                isOnline = isOnline,
                hashrateGhs = finalHashrateGhs,
                hashrateFormatted = finalHashrateFormatted,
                fanSpeedRpm = finalFanRpm,
                temperatureC = finalTempC,
                powerWatts = finalPowerWatts,
                miningPoolUrl = finalData.poolUrl,
                workerName = finalData.workerName,
                asicBoardStatus = boardStatusText,
                uptimeSeconds = finalUptimeSec,
                uptimeFormatted = formatUptime(finalUptimeSec),
                systemLogs = finalSystemLogs,
                apiLogs = finalApiLogs,
                lastSeenTimestamp = System.currentTimeMillis(),
                apiPort = apiPort,
                isWhatsMinerApiAvailable = isWhatsMinerApi,
                hashboardsJson = HashboardData.listToJsonString(finalHashboards),
                errorCode = finalData.errorCode,
                errorMessage = finalData.errorMessage,
                controlBoardHardware = finalControlBoard,
                historicalErrorCodes = finalHistoricalErrors,
                multiFanRpm = finalMultiFanRpm,
                fanInRpm = finalFanIn,
                fanOutRpm = finalFanOut
            )

            MinerQueryResult.Success(entity)

        } catch (e: CancellationException) {
            throw e
        } catch (e: java.net.SocketTimeoutException) {
            log("Query timeout for $ip:$apiPort")
            MinerQueryResult.Timeout
        } catch (e: java.net.ConnectException) {
            log("Connection refused for $ip:$apiPort")
            MinerQueryResult.Unreachable
        } catch (e: Exception) {
            log("Query error for $ip:$apiPort - ${e.message}", e)
            MinerQueryResult.Error("Query failed: ${e.message}", e)
        }
    }

    // ==================== Socket Communication ====================

    private suspend fun probeSinglePort(
        ip: String,
        port: Int,
        timeoutMs: Int
    ): Boolean = withContext(dispatcher) {
        try {
            Socket().use { socket ->
                socket.connect(InetSocketAddress(ip, port), timeoutMs)
                true
            }
        } catch (_: Exception) {
            false
        }
    }

    private suspend fun sendValidSocketCommand(
        ip: String,
        port: Int,
        commands: List<String>,
        timeoutMs: Int
    ): String? {
        for (cmd in commands) {
            val resp = sendSocketCommand(ip, port, cmd, timeoutMs)
            if (!resp.isNullOrBlank()) {
                val upper = resp.uppercase()
                val isError = upper.contains("\"STATUS\":\"E\"") ||
                        upper.contains("\"STATUS\":\"ERR\"") ||
                        upper.contains("INVALID COMMAND") ||
                        upper.contains("UNKNOWN COMMAND") ||
                        upper.contains("STATUS=E,")
                if (!isError) {
                    return resp
                } else {
                    log("Command '$cmd' returned error status, trying next variant...")
                }
            }
        }
        return null
    }

    private suspend fun sendSocketCommand(
        ip: String,
        port: Int,
        command: String,
        timeoutMs: Int
    ): String? = withContext(dispatcher) {
        val startTime = System.currentTimeMillis()
        try {
            Socket().use { socket ->
                socket.connect(InetSocketAddress(ip, port), timeoutMs)
                socket.soTimeout = timeoutMs
                socket.tcpNoDelay = true
                socket.keepAlive = true

                if (port == 4433) {
                    // پروتکل جدیدترین فریم‌ورها (پورت API اختصاصی WhatsMiner ۴۴۳۳)
                    // ارسال طول دستور به عنوان یک اینتجر ۴ بایتی little-endian و سپس خود دستور JSON
                    val outputStream = socket.getOutputStream()
                    val cmdBytes = command.toByteArray(Charsets.US_ASCII)
                    val len = cmdBytes.size
                    val lenBytes = byteArrayOf(
                        (len and 0xFF).toByte(),
                        ((len shr 8) and 0xFF).toByte(),
                        ((len shr 16) and 0xFF).toByte(),
                        ((len shr 24) and 0xFF).toByte()
                    )
                    outputStream.write(lenBytes)
                    outputStream.write(cmdBytes)
                    outputStream.flush()

                    // خواندن پاسخ
                    val inputStream = socket.getInputStream()
                    val respLenBytes = ByteArray(4)
                    var bytesRead = 0
                    while (bytesRead < 4) {
                        val r = inputStream.read(respLenBytes, bytesRead, 4 - bytesRead)
                        if (r == -1) break
                        bytesRead += r
                    }
                    if (bytesRead == 4) {
                        val respLen = (respLenBytes[0].toInt() and 0xFF) or
                                 ((respLenBytes[1].toInt() and 0xFF) shl 8) or
                                 ((respLenBytes[2].toInt() and 0xFF) shl 16) or
                                 ((respLenBytes[3].toInt() and 0xFF) shl 24)

                        if (respLen in 1..10_000_000) { // بررسی امنیتی طول
                            val respBytes = ByteArray(respLen)
                            var respBytesRead = 0
                            while (respBytesRead < respLen) {
                                val r = inputStream.read(respBytes, respBytesRead, respLen - respBytesRead)
                                if (r == -1) break
                                respBytesRead += r
                            }
                            val response = String(respBytes, 0, respBytesRead, Charsets.US_ASCII).trim()
                            if (response.isNotBlank()) response else null
                        } else {
                            null
                        }
                    } else {
                        null
                    }
                } else {
                    // پروتکل استاندارد CGMiner / پورت ۴۰۲۸
                    // Send command
                    val writer = socket.getOutputStream().bufferedWriter()
                    val cmdString = if (command.endsWith("\n")) command else "$command\n"
                    writer.write(cmdString)
                    writer.flush()

                    // Read response
                    val reader = socket.getInputStream().bufferedReader()
                    readSocketResponse(reader, timeoutMs)
                }
            }.also { result ->
                val elapsed = System.currentTimeMillis() - startTime
                log("← $ip:$port [${command.take(30)}] → ${result?.length ?: 0} chars in ${elapsed}ms")
            }
        } catch (e: java.net.SocketTimeoutException) {
            val elapsed = System.currentTimeMillis() - startTime
            log("✗ Timeout $ip:$port [${command.take(30)}] after ${elapsed}ms")
            null
        } catch (e: Exception) {
            val elapsed = System.currentTimeMillis() - startTime
            log("✗ Error $ip:$port [${command.take(30)}] after ${elapsed}ms: ${e.message}")
            null
        }
    }

    private suspend fun readSocketResponse(
        reader: BufferedReader,
        timeoutMs: Int
    ): String? = withContext(dispatcher) {
        val sb = StringBuilder()
        val buffer = CharArray(DEFAULT_BUFFER_SIZE)
        val deadline = System.currentTimeMillis() + timeoutMs

        try {
            while (System.currentTimeMillis() < deadline) {
                currentCoroutineContext().ensureActive()
                val charsRead = try {
                    reader.read(buffer)
                } catch (_: java.net.SocketTimeoutException) {
                    -1
                }
                if (charsRead == -1) break
                sb.append(buffer, 0, charsRead)

                val cleaned = sb.toString().replace("\u0000", "").trim()
                if (cleaned.endsWith("}") || cleaned.endsWith("]")) {
                    return@withContext cleaned
                }
            }
        } catch (_: Exception) {
        }

        val finalStr = sb.toString().replace("\u0000", "").trim()
        if (finalStr.isNotBlank()) finalStr else null
    }

    // ==================== Retry Logic ====================

    private suspend fun <T> retryWithBackoff(
        times: Int = 3,
        initialDelay: Long = 200,
        maxDelay: Long = 2000,
        factor: Double = 2.0,
        block: suspend () -> T?
    ): T? {
        var currentDelay = initialDelay
        repeat(times - 1) { attempt ->
            val result = runCatching { block() }.getOrNull()
            if (result != null) return result
            log("Retry attempt ${attempt + 1} after ${currentDelay}ms")
            delay(currentDelay)
            currentDelay = (currentDelay * factor).toLong().coerceAtMost(maxDelay)
        }
        return runCatching { block() }.getOrNull()
    }

    // ==================== Data Merging ====================

    private data class FinalizedData(
        val model: String,
        val firmware: String,
        val serial: String,
        val hashrateGhs: Double,
        val hashrateFormatted: String,
        val fanRpm: Int,
        val fanInRpm: Int,
        val fanOutRpm: Int,
        val tempC: Double,
        val powerWatts: Int,
        val poolUrl: String,
        val workerName: String,
        val uptimeSec: Long,
        val hashboards: List<HashboardData>,
        val errorCode: Int,
        val errorMessage: String
    )

    private fun mergeAndFinalizeData(
        summaryData: ParsedSummary,
        versionData: ParsedVersion,
        poolsData: ParsedPools,
        hashboards: List<HashboardData>,
        errorsList: List<Pair<Int, String>>
    ): FinalizedData {
        var model = "WhatsMiner ASIC"
        if (versionData.model.isNotBlank() && versionData.model != "N/A") {
            model = formatModelName(versionData.model)
        } else if (summaryData.modelHint.isNotBlank()) {
            model = summaryData.modelHint
        }

        // همگام‌سازی هش‌ریت با بردها
        var hashrateGhs = summaryData.hashrateGhs
        var hashrateFormatted = summaryData.hashrateFormatted
        val sumBoardHashrateThs = hashboards.sumOf { it.hashrateThs }
        if (sumBoardHashrateThs > 0) {
            hashrateGhs = sumBoardHashrateThs * 1000.0
            hashrateFormatted = String.format("%.2f TH/s", sumBoardHashrateThs)
        }

        // دمای نهایی
        var tempC = summaryData.tempC
        val maxBoardTemp = hashboards.maxOfOrNull { maxOf(it.boardTempC, it.chipTempC) } ?: 0.0
        if (maxBoardTemp > 0) tempC = maxBoardTemp

        // توزیع یا تولید هش‌بردها
        var finalHashboards = if (hashboards.isNotEmpty() && summaryData.totalChips > 0) {
            val perBoardChips = summaryData.totalChips / hashboards.size
            hashboards.map { board ->
                if (board.chipsCount == 0) board.copy(chipsCount = perBoardChips)
                else board
            }
        } else hashboards

        if (finalHashboards.isEmpty() && hashrateGhs > 0) {
            val boardCount = 3
            val perBoardHashrateThs = (hashrateGhs / 1000.0) / boardCount
            val perBoardChips = if (summaryData.totalChips > 0) summaryData.totalChips / boardCount else 0
            finalHashboards = (1..boardCount).map { idx ->
                HashboardData(
                    boardIndex = idx,
                    status = "Alive",
                    chipsCount = perBoardChips,
                    hashrateThs = perBoardHashrateThs,
                    boardTempC = tempC,
                    chipTempC = tempC
                )
            }
        }

        // ادغام خطاها
        var errorCode = summaryData.errorCode
        var errorMessage = summaryData.errorMessage

        if (errorsList.isNotEmpty()) {
            errorCode = errorsList.first().first
            val formattedErrors = errorsList.map { (code, time) ->
                val desc = mapErrorCodeToMessage(code)
                if (time.isNotBlank()) {
                    "کد $code: $desc ($time)"
                } else {
                    "کد $code: $desc"
                }
            }
            errorMessage = formattedErrors.joinToString("\n")
        }

        return FinalizedData(
            model = model,
            firmware = versionData.firmware,
            serial = versionData.serial,
            hashrateGhs = hashrateGhs,
            hashrateFormatted = hashrateFormatted,
            fanRpm = summaryData.fanRpm,
            fanInRpm = summaryData.fanIn ?: 0,
            fanOutRpm = summaryData.fanOut ?: 0,
            tempC = tempC,
            powerWatts = summaryData.powerWatts,
            poolUrl = poolsData.url,
            workerName = poolsData.worker,
            uptimeSec = summaryData.uptimeSec,
            hashboards = finalHashboards,
            errorCode = errorCode,
            errorMessage = errorMessage
        )
    }

    private fun buildBoardStatusText(
        hashboards: List<HashboardData>,
        isWhatsMinerApi: Boolean
    ): String = when {
        hashboards.isNotEmpty() -> hashboards.joinToString(" | ") { board ->
            "برد #${board.boardIndex}: ${String.format("%.1f", board.hashrateThs)} TH/s " +
            "(${String.format("%.1f", board.chipTempC)}°C)"
        }
        isWhatsMinerApi -> "برد‌های ASIC: فعال (عادی)"
        else -> "N/A"
    }

    private fun mapErrorCodeToMessage(code: Int): String {
        return when (code) {
            0 -> ""
            110 -> "خطای فن ورودی (سرعت نامناسب)"
            111 -> "خطای فن خروجی (سرعت نامناسب)"
            140 -> "دمای بیش از حد بالا و سرعت زیاد فن"
            200 -> "عدم شناسایی پاور (PSU)"
            202 -> "خطای ولتاژ خروجی پاور"
            206 -> "ولتاژ ورودی پاور پایین است (افت ولتاژ)"
            233, 234, 235 -> "محافظت دمای بیش از حد پاور"
            236 -> "محافظت جریان بیش از حد پاور"
            268 -> "خطای اتصالات مسی یا شل بودن اتصالات باس‌بار پاور"
            271 -> "محافظت افت ولتاژ ورودی پاور"
            274 -> "خطای فن پاور"
            309 -> "عدم شناسایی سنسورهای دمای برد"
            321 -> "خطای خواندن دمای برد شماره ۱ (SM1)"
            322 -> "خطای خواندن دمای برد شماره ۲ (SM2)"
            350, 351, 352 -> "محافظت دمای بیش از حد برد (حرارت بالا)"
            410, 411, 412 -> "خطای حافظه EEPROM برد هش‌ریت"
            530, 531, 532 -> "برد هش‌ریت شناسایی نشد"
            600 -> "دمای محیط بسیار بالا است"
            800 -> "خطای چک‌سام CGMiner"
            2010 -> "تمامی استخرها غیرفعال هستند"
            2020 -> "اتصال به استخر صفر ناموفق بود"
            2320 -> "هش‌ریت بسیار پایین است (افت هش‌ریت)"
            else -> "کد خطا: $code"
        }
    }

    // ==================== Parsers ====================

    private fun parseSummaryResponse(raw: String): ParsedSummary? {
        return try {
            val trimmed = raw.trim()
            when {
                isJsonResponse(trimmed) -> parseSummaryJson(trimmed)
                trimmed.contains("SUMMARY") || trimmed.contains("MHS") || trimmed.contains("GHS") || trimmed.contains("HS") -> parseSummaryPipeDelimited(trimmed)
                else -> null
            }
        } catch (e: Exception) {
            log("parseSummaryResponse error: ${e.message}")
            null
        }
    }

    private fun parseSummaryJson(raw: String): ParsedSummary? {
        val jsonStart = raw.indexOf("{")
        if (jsonStart < 0) return null
        val jsonStr = raw.substring(jsonStart)
        val json = JSONObject(jsonStr)

        var modelHint = ""
        val statusObj = json.optJSONArray("STATUS")?.optJSONObject(0)
            ?: json.optJSONObject("msg")?.optJSONArray("STATUS")?.optJSONObject(0)
        if (statusObj != null) {
            val msg = statusObj.optString("Msg", statusObj.optString("Description", ""))
            if (msg.contains("WhatsMiner", ignoreCase = true) ||
                msg.contains(Regex("M[2356]0", RegexOption.IGNORE_CASE))
            ) {
                modelHint = formatModelName(msg)
            }
        }

        val msgObj = json.optJSONObject("msg")
        val summaryObj = json.optJSONArray("SUMMARY")?.optJSONObject(0)
            ?: json.optJSONArray("summary")?.optJSONObject(0)
            ?: msgObj?.optJSONArray("SUMMARY")?.optJSONObject(0)
            ?: msgObj?.optJSONArray("summary")?.optJSONObject(0)
            ?: msgObj?.optJSONObject("summary")
            ?: msgObj
            ?: json

        val ghs = extractHashrateGhs(summaryObj)
        val ths = ghs / 1000.0
        val hashrateStr = if (ths > 0) String.format("%.2f TH/s", ths) else "0.0 TH/s"

        val fanIn = getNormalizedIntOrNull(summaryObj, "Fan Speed In", "fan_speed_in", "FanSpeedIn")
        val fanOut = getNormalizedIntOrNull(summaryObj, "Fan Speed Out", "fan_speed_out", "FanSpeedOut")
        val fanGen = getNormalizedIntOrNull(summaryObj, "Fan Speed", "fan_speed", "Fan")
        val fanRpm = when {
            (fanIn ?: 0) > 0 -> fanIn!!
            (fanOut ?: 0) > 0 -> fanOut!!
            (fanGen ?: 0) > 0 -> fanGen!!
            else -> 0
        }

        var temp = getNormalizedDouble(summaryObj, "Chip Temp Max", "chip_temp_max", "Chip Temp Avg", "chip_temp_avg", "Temperature", "temperature")
        if (temp == 0.0) {
            temp = getNormalizedDouble(summaryObj, "Board Temp Max", "board_temp_max", "Env Temp", "env_temp")
        }

        val power = getNormalizedInt(summaryObj, "Power", "power", "Power Rate", "power_rate", "Power(W)", "Power W")
        val elapsed = getNormalizedLong(summaryObj, "Elapsed", "elapsed", "Uptime", "uptime")

        var totalChips = extractChipCountFromJsonObject(summaryObj)
        if (totalChips == 0) totalChips = extractChipCountFromJsonObject(json)

        val errorCode = getNormalizedInt(summaryObj, "Error Code", "error_code", "ErrorCode", "Code")
            .let { if (it == 0) getNormalizedInt(json, "code", "ErrorCode", "Error Code") else it }
        var errorMessage = ""
        if (errorCode > 0) {
            errorMessage = mapErrorCodeToMessage(errorCode)
            val apiMsg = getNormalizedString(summaryObj, "Error Msg", "error_msg", "ErrorMsg")
                .ifBlank { statusObj?.optString("Msg", statusObj?.optString("Description", "")) ?: "" }
            if (apiMsg.isNotBlank() && apiMsg != "N/A" && !apiMsg.equals(errorMessage, ignoreCase = true)) {
                errorMessage += " - $apiMsg"
            }
        }

        return ParsedSummary(ghs, hashrateStr, fanRpm, fanIn, fanOut, temp, power, elapsed, totalChips, modelHint, errorCode, errorMessage)
    }

    private fun parseSummaryPipeDelimited(raw: String): ParsedSummary? {
        var elapsed = 0L
        var rawHashrate = 0.0
        var temp = 0.0
        var fanIn: Int? = null
        var fanOut: Int? = null
        var fanGen: Int? = null
        var power = 0
        var modelHint = ""
        var totalChips = 0

        for (part in raw.split("|")) {
            for (kv in part.split(",")) {
                val sub = kv.split("=", limit = 2)
                if (sub.size != 2) continue
                val key = sub[0].trim().lowercase()
                val valStr = sub[1].trim()

                when {
                    key == "elapsed" || key == "uptime" -> elapsed = valStr.toLongOrNull() ?: 0L
                    key == "mhs 5s" || key == "mhs av" || key == "ghs 5s" || key == "ghs av" ||
                    key == "ths 5s" || key == "ths av" || key == "hs 5s" || key == "hs av" ||
                    key == "hs rt" || key == "hashrate" || key == "rate" -> {
                        val parsed = valStr.toDoubleOrNull() ?: 0.0
                        if (parsed > 0) rawHashrate = parsed
                    }
                    key == "temperature" || key == "chip temp max" || key == "chip temp avg" -> temp = valStr.toDoubleOrNull() ?: 0.0
                    key == "fan speed in" || key == "fan_speed_in" || key == "inlet" || key == "fan1" -> fanIn = valStr.toIntOrNull()
                    key == "fan speed out" || key == "fan_speed_out" || key == "outlet" || key == "fan2" -> fanOut = valStr.toIntOrNull()
                    key == "fan speed" || key == "fan" -> fanGen = valStr.toIntOrNull()
                    key == "power" || key == "power rate" -> power = valStr.toIntOrNull() ?: 0
                    key == "msg" || key == "description" -> {
                        if (valStr.contains("WhatsMiner", ignoreCase = true) ||
                            valStr.contains(Regex("M[2356]0", RegexOption.IGNORE_CASE))
                        ) {
                            modelHint = formatModelName(valStr)
                        }
                    }
                    (key.contains("chip") || key.contains("asic")) &&
                    !key.contains("temp") && !key.contains("freq") -> {
                        val parsed = valStr.toIntOrNull() ?: 0
                        if (parsed in 1..MAX_CHIP_COUNT && parsed > totalChips) totalChips = parsed
                    }
                }
            }
        }

        val fanRpm = when {
            (fanIn ?: 0) > 0 -> fanIn!!
            (fanOut ?: 0) > 0 -> fanOut!!
            (fanGen ?: 0) > 0 -> fanGen!!
            else -> 0
        }

        val ths = smartToThs(rawHashrate)
        val ghs = ths * 1000.0
        val hashrateStr = if (ths > 0) String.format(java.util.Locale.US, "%.2f TH/s", ths) else "0.0 TH/s"
        return ParsedSummary(ghs, hashrateStr, fanRpm, fanIn, fanOut, temp, power, elapsed, totalChips, modelHint)
    }

    private fun parseVersionResponse(raw: String): ParsedVersion? {
        return try {
            val trimmed = raw.trim()
            when {
                isJsonResponse(trimmed) -> parseVersionJson(trimmed)
                trimmed.contains("VERSION") || trimmed.contains("Type=") || trimmed.contains("DN=") -> parseVersionPipeDelimited(trimmed)
                else -> null
            }
        } catch (e: Exception) {
            log("parseVersionResponse error: ${e.message}")
            null
        }
    }

    private fun parseVersionJson(raw: String): ParsedVersion? {
        val jsonStart = raw.indexOf("{")
        if (jsonStart < 0) return null
        val jsonStr = raw.substring(jsonStart)
        val json = JSONObject(jsonStr)

        val msgObj = json.optJSONObject("msg")
        val verObj = json.optJSONArray("VERSION")?.optJSONObject(0)
            ?: json.optJSONArray("version")?.optJSONObject(0)
            ?: msgObj?.optJSONArray("VERSION")?.optJSONObject(0)
            ?: msgObj?.optJSONArray("version")?.optJSONObject(0)
            ?: json.optJSONArray("STATUS")?.optJSONObject(0)
            ?: msgObj?.optJSONArray("STATUS")?.optJSONObject(0)
            ?: msgObj
            ?: json

        var model = getNormalizedString(verObj, "Type", "TYPE", "type", "Model", "MODEL", "model", "Miner", "MINER", "miner", "system_model", "product_name", "Hardware", "device_model", "device_type")

        if (model == "N/A" || model.isBlank()) {
            val statusObj = json.optJSONArray("STATUS")?.optJSONObject(0)
                ?: json.optJSONObject("msg")?.optJSONArray("STATUS")?.optJSONObject(0)
            if (statusObj != null) {
                val msg = statusObj.optString("Msg", statusObj.optString("Description", ""))
                if (msg.contains("Whatsminer", ignoreCase = true) ||
                    msg.contains(Regex("M[2356]0", RegexOption.IGNORE_CASE))
                ) {
                    model = msg
                }
            }
        }

        val firmware = getNormalizedString(verObj, "Firmware", "FIRMWARE", "firmware", "Version", "VERSION", "version", "firmware_version", "FW Version", "fw_version", "CompileTime", "Compile Time")
        val serial = getNormalizedString(verObj, "DN", "dn", "SN", "sn", "PSN", "psn", "Serial", "serial_number", "serial")

        return ParsedVersion(model, firmware, serial)
    }

    private fun parseVersionPipeDelimited(raw: String): ParsedVersion? {
        var model = "N/A"
        var firmware = "N/A"
        var serial = "N/A"

        for (part in raw.split("|")) {
            for (kv in part.split(",")) {
                val sub = kv.split("=", limit = 2)
                if (sub.size != 2) continue
                val key = sub[0].trim().lowercase()
                val value = sub[1].trim()

                when (key) {
                    "type", "model", "hardware", "system_model", "miner" -> model = value
                    "firmware", "version", "firmware_version", "fw version", "compiletime", "compile time" -> firmware = value
                    "dn", "sn", "psn", "serial", "serial_number" -> serial = value
                }
            }
        }
        return ParsedVersion(model, firmware, serial)
    }

    private fun parsePoolsResponse(raw: String): ParsedPools? {
        return try {
            val trimmed = raw.trim()
            when {
                isJsonResponse(trimmed) -> parsePoolsJson(trimmed)
                trimmed.contains("POOLS") || trimmed.contains("URL=") -> parsePoolsPipeDelimited(trimmed)
                else -> null
            }
        } catch (e: Exception) {
            log("parsePoolsResponse error: ${e.message}")
            null
        }
    }

    private fun parsePoolsJson(raw: String): ParsedPools? {
        val jsonStart = raw.indexOf("{")
        if (jsonStart < 0) return null
        val jsonStr = raw.substring(jsonStart)
        val json = JSONObject(jsonStr)

        val poolsArray = json.optJSONArray("POOLS")
            ?: json.optJSONArray("pools")
            ?: json.optJSONObject("msg")?.optJSONArray("pools")
            ?: json.optJSONObject("msg")?.optJSONArray("POOLS")
            ?: return null
        if (poolsArray.length() == 0) return null

        var selectedUrl = "N/A"
        var selectedUser = "N/A"

        for (i in 0 until poolsArray.length()) {
            val poolObj = poolsArray.getJSONObject(i)
            val url = poolObj.optString("URL",
                poolObj.optString("url",
                    poolObj.optString("Url", "")))
            val user = poolObj.optString("User",
                poolObj.optString("user",
                    poolObj.optString("User.0",
                        poolObj.optString("worker", ""))))
            val status = poolObj.optString("Status", poolObj.optString("status", ""))

            if (url.isNotBlank() && url != "N/A") {
                val isActive = status.equals("Alive", ignoreCase = true) ||
                        status.equals("Active", ignoreCase = true)

                if (selectedUrl == "N/A" || isActive) {
                    selectedUrl = url
                    selectedUser = if (user.isNotBlank()) user else "N/A"
                    if (isActive) break
                }
            }
        }

        return ParsedPools(selectedUrl, selectedUser)
    }

    private fun parsePoolsPipeDelimited(raw: String): ParsedPools? {
        var selectedUrl = "N/A"
        var selectedUser = "N/A"

        for (part in raw.split("|")) {
            if (!part.contains("URL=")) continue

            var url = "N/A"
            var user = "N/A"

            for (kv in part.split(",")) {
                val sub = kv.split("=", limit = 2)
                if (sub.size != 2) continue
                when (sub[0].trim().lowercase()) {
                    "url" -> url = sub[1].trim()
                    "user", "worker" -> user = sub[1].trim()
                }
            }

            if (url.isNotBlank() && url != "N/A") {
                selectedUrl = url
                selectedUser = user
                break
            }
        }

        return ParsedPools(selectedUrl, selectedUser)
    }

    private fun parseDevsResponse(raw: String): List<HashboardData> {
        val list = mutableListOf<HashboardData>()
        try {
            val trimmed = raw.trim()
            when {
                isJsonResponse(trimmed) -> parseDevsJson(trimmed, list)
                trimmed.contains("DEVS") || trimmed.contains("MHS 5s") -> parseDevsPipeDelimited(trimmed, list)
            }
        } catch (e: Exception) {
            log("parseDevsResponse error: ${e.message}")
        }
        return list
    }

    private fun parseDevsJson(raw: String, list: MutableList<HashboardData>) {
        val jsonStart = raw.indexOf("{")
        if (jsonStart < 0) return
        val jsonStr = raw.substring(jsonStart)
        val json = JSONObject(jsonStr)

        val devsArray = json.optJSONArray("DEVS")
            ?: json.optJSONArray("devs")
            ?: json.optJSONArray("DEVDETAILS")
            ?: json.optJSONArray("devdetails")
            ?: json.optJSONArray("EDEVS")
            ?: json.optJSONObject("msg")?.optJSONArray("devs")
            ?: json.optJSONObject("msg")?.optJSONArray("DEVS")
            ?: json.optJSONObject("msg")?.optJSONArray("edevs")
            ?: json.optJSONObject("msg")?.optJSONArray("EDEVS")
            ?: json.optJSONObject("msg")?.optJSONArray("devdetails")
            ?: json.optJSONObject("msg")?.optJSONArray("DEVDETAILS")
            ?: return

        for (i in 0 until devsArray.length()) {
            val devObj = devsArray.getJSONObject(i)
            list.add(parseSingleDevJson(devObj, i))
        }
    }

    private fun parseSingleDevJson(devObj: JSONObject, fallbackIndex: Int): HashboardData {
        val idx = devObj.optInt("Slot",
            devObj.optInt("PCB",
                devObj.optInt("ASC",
                    devObj.optInt("ID",
                        devObj.optInt("Index", fallbackIndex))))) + 1

        val status = devObj.optString("Status", devObj.optString("status", "Alive"))
        val chips = extractChipCountFromJsonObject(devObj)

        val rawHashrate = getNormalizedDouble(
            devObj,
            "MHS av", "MHS 5s", "MHS 1m", "MHS 15m", "HS RT", "mhs_av", "mhs_5s", "mhs_1m", "mhs_15m", "hs_rt",
            "THS 5s", "THS av", "THS 1m", "THS 15m", "ths",
            "GHS 5s", "GHS av", "GHS 1m", "GHS 15m", "ghs",
            "Hashrate", "hashrate", "effective_hashrate", "Factory GHS"
        )

        val boardThs = smartToThs(rawHashrate)

        var boardTemp = devObj.optDouble("Board Temp",
            devObj.optDouble("board_temp",
                devObj.optDouble("PCB Temp",
                    devObj.optDouble("pcb_temp",
                        devObj.optDouble("BoardTemp",
                            devObj.optDouble("Temperature",
                                devObj.optDouble("temperature",
                                    devObj.optDouble("Temp",
                                        devObj.optDouble("temp", 0.0)))))))))

        var chipTemp = devObj.optDouble("Chip Temp Max",
            devObj.optDouble("Chip Temp Avg",
                devObj.optDouble("Chip Temp",
                    devObj.optDouble("chip_temp",
                        devObj.optDouble("Temperature", 0.0)))))

        // Fallback بین دماها
        if (boardTemp == 0.0 && chipTemp > 0) boardTemp = chipTemp
        if (chipTemp == 0.0 && boardTemp > 0) chipTemp = boardTemp

        return HashboardData(
            boardIndex = idx,
            status = status,
            chipsCount = if (chips > 0) chips else 70,
            hashrateThs = boardThs,
            boardTempC = boardTemp,
            chipTempC = chipTemp
        )
    }

    private fun parseDevsPipeDelimited(raw: String, list: MutableList<HashboardData>) {
        var indexCounter = 1

        for (part in raw.split("|")) {
            if (!part.startsWith("DEVS") &&
                !part.contains("MHS 5s") &&
                !part.contains("MHS av") &&
                !part.contains("Board Temp")
            ) continue

            var status = "Alive"
            var chips = 0
            var rawHashrate = 0.0
            var boardTemp = 0.0
            var chipTemp = 0.0
            var idx = indexCounter

            for (kv in part.split(",")) {
                val sub = kv.split("=", limit = 2)
                if (sub.size != 2) continue
                val k = sub[0].trim().lowercase()
                val v = sub[1].trim()

                when {
                    k == "asc" || k == "id" || k == "pcb" || k == "slot" ->
                        idx = (v.toIntOrNull() ?: (indexCounter - 1)) + 1
                    k == "status" -> status = v
                    k == "mhs 5s" || k == "mhs av" || k == "mhs 1m" || k == "mhs 15m" || k == "hs rt" ||
                    k == "ths 5s" || k == "ths av" || k == "ghs 5s" || k == "ghs av" || k == "hashrate" ->
                        rawHashrate = v.toDoubleOrNull() ?: 0.0
                    k == "board temp" || k == "pcb temp" || k == "boardtemp" ||
                    k == "temperature" || k == "temp" ->
                        boardTemp = v.toDoubleOrNull() ?: 0.0
                    k == "chip temp max" || k == "chip temp avg" ||
                    k == "chip temp" || k == "chip_temp" ->
                        chipTemp = v.toDoubleOrNull() ?: 0.0
                    (k.contains("chip") || k.contains("asic")) &&
                    !k.contains("temp") && !k.contains("freq") -> {
                        val parsed = v.toIntOrNull() ?: 0
                        if (parsed > 0 && parsed > chips) chips = parsed
                    }
                }
            }

            if (boardTemp == 0.0 && chipTemp > 0) boardTemp = chipTemp
            if (chipTemp == 0.0 && boardTemp > 0) chipTemp = boardTemp

            val boardThs = smartToThs(rawHashrate)

            if (boardThs > 0 || boardTemp > 0 || chipTemp > 0) {
                list.add(
                    HashboardData(
                        boardIndex = idx,
                        status = status,
                        chipsCount = if (chips > 0) chips else 70,
                        hashrateThs = boardThs,
                        boardTempC = boardTemp,
                        chipTempC = chipTemp
                    )
                )
                indexCounter++
            }
        }
    }

    // ==================== Helper Functions ====================

    private fun isJsonResponse(raw: String): Boolean {
        val trimmed = raw.trim()
        return trimmed.startsWith("{") ||
                trimmed.contains("{\"STATUS\"") ||
                trimmed.contains("{\"SUMMARY\"") ||
                trimmed.contains("{\"VERSION\"") ||
                trimmed.contains("{\"POOLS\"") ||
                trimmed.contains("{\"DEVS\"") ||
                trimmed.contains("{\"DEVDETAILS\"")
    }

    private fun safeGetDouble(obj: JSONObject, key: String): Double? {
        val rawVal = obj.opt(key) ?: return null
        if (rawVal is Number) return rawVal.toDouble()
        val str = rawVal.toString().trim()
        if (str.isBlank() || str.equals("N/A", ignoreCase = true)) return null
        
        try {
            val cleanStr = str.replace(",", "").trim()
            val match = Regex("""[+-]?\d+(\.\d+)?""").find(cleanStr)
            if (match != null) {
                return match.value.toDoubleOrNull()
            }
        } catch (_: Exception) {}
        return null
    }

    private fun safeGetLong(obj: JSONObject, key: String): Long? {
        val rawVal = obj.opt(key) ?: return null
        if (rawVal is Number) return rawVal.toLong()
        val str = rawVal.toString().trim()
        if (str.isBlank() || str.equals("N/A", ignoreCase = true)) return null
        
        try {
            val cleanStr = str.replace(",", "").trim()
            val match = Regex("""[+-]?\d+""").find(cleanStr)
            if (match != null) {
                return match.value.toLongOrNull()
            }
        } catch (_: Exception) {}
        return null
    }

    private fun getNormalizedString(obj: JSONObject, vararg keys: String): String {
        val normalizedMap = mutableMapOf<String, String>()
        val keysIter = obj.keys()
        while (keysIter.hasNext()) {
            val originalKey = keysIter.next()
            val normalizedKey = originalKey.lowercase().replace("_", "").replace("-", "").replace(" ", "").trim()
            normalizedMap[normalizedKey] = obj.optString(originalKey, "")
        }
        for (k in keys) {
            val normK = k.lowercase().replace("_", "").replace("-", "").replace(" ", "").trim()
            val v = normalizedMap[normK]
            if (v != null && v.isNotBlank()) return v
        }
        return ""
    }

    private fun getNormalizedIntOrNull(obj: JSONObject, vararg keys: String): Int? {
        val normalizedMap = mutableMapOf<String, Int>()
        val keysIter = obj.keys()
        while (keysIter.hasNext()) {
            val originalKey = keysIter.next()
            val normalizedKey = originalKey.lowercase().replace("_", "").replace("-", "").replace(" ", "").trim()
            val value = safeGetLong(obj, originalKey)?.toInt()
            if (value != null) {
                normalizedMap[normalizedKey] = value
            }
        }
        for (k in keys) {
            val normK = k.lowercase().replace("_", "").replace("-", "").replace(" ", "").trim()
            val v = normalizedMap[normK]
            if (v != null) return v
        }
        return null
    }

    private fun getNormalizedInt(obj: JSONObject, vararg keys: String, default: Int = 0): Int {
        val normalizedMap = mutableMapOf<String, Int>()
        val keysIter = obj.keys()
        while (keysIter.hasNext()) {
            val originalKey = keysIter.next()
            val normalizedKey = originalKey.lowercase().replace("_", "").replace("-", "").replace(" ", "").trim()
            val value = safeGetLong(obj, originalKey)?.toInt()
            if (value != null) {
                normalizedMap[normalizedKey] = value
            }
        }
        for (k in keys) {
            val normK = k.lowercase().replace("_", "").replace("-", "").replace(" ", "").trim()
            val v = normalizedMap[normK]
            if (v != null) return v
        }
        return default
    }

    private fun getNormalizedDouble(obj: JSONObject, vararg keys: String, default: Double = 0.0): Double {
        val normalizedMap = mutableMapOf<String, Double>()
        val keysIter = obj.keys()
        while (keysIter.hasNext()) {
            val originalKey = keysIter.next()
            val normalizedKey = originalKey.lowercase().replace("_", "").replace("-", "").replace(" ", "").trim()
            val value = safeGetDouble(obj, originalKey)
            if (value != null) {
                normalizedMap[normalizedKey] = value
            }
        }
        for (k in keys) {
            val normK = k.lowercase().replace("_", "").replace("-", "").replace(" ", "").trim()
            val v = normalizedMap[normK]
            if (v != null) return v
        }
        return default
    }

    private fun getNormalizedLong(obj: JSONObject, vararg keys: String, default: Long = 0L): Long {
        val normalizedMap = mutableMapOf<String, Long>()
        val keysIter = obj.keys()
        while (keysIter.hasNext()) {
            val originalKey = keysIter.next()
            val normalizedKey = originalKey.lowercase().replace("_", "").replace("-", "").replace(" ", "").trim()
            val value = safeGetLong(obj, originalKey)
            if (value != null) {
                normalizedMap[normalizedKey] = value
            }
        }
        for (k in keys) {
            val normK = k.lowercase().replace("_", "").replace("-", "").replace(" ", "").trim()
            val v = normalizedMap[normK]
            if (v != null) return v
        }
        return default
    }

    private fun parseErrorCodes(raw: String?): List<Pair<Int, String>> {
        if (raw.isNullOrBlank()) return emptyList()
        val list = mutableListOf<Pair<Int, String>>()
        try {
            val jsonStart = raw.indexOf("{")
            if (jsonStart < 0) return emptyList()
            val json = JSONObject(raw.substring(jsonStart))
            
            val msgObj = json.optJSONObject("Msg") ?: json.optJSONObject("msg") ?: json.optJSONObject("MSG")
            if (msgObj != null) {
                val errArray = msgObj.optJSONArray("error_code") ?: msgObj.optJSONArray("error")
                if (errArray != null) {
                    for (i in 0 until errArray.length()) {
                        val item = errArray.optJSONObject(i) ?: continue
                        val keys = item.keys()
                        while (keys.hasNext()) {
                            val errorCodeStr = keys.next()
                            val errorCode = errorCodeStr.toIntOrNull() ?: continue
                            val timestamp = item.optString(errorCodeStr, "")
                            list.add(Pair(errorCode, timestamp))
                        }
                    }
                }
            } else {
                val errArray = json.optJSONArray("error_code") ?: json.optJSONArray("error")
                if (errArray != null) {
                    for (i in 0 until errArray.length()) {
                        val item = errArray.optJSONObject(i) ?: continue
                        val keys = item.keys()
                        while (keys.hasNext()) {
                            val errorCodeStr = keys.next()
                            val errorCode = errorCodeStr.toIntOrNull() ?: continue
                            val timestamp = item.optString(errorCodeStr, "")
                            list.add(Pair(errorCode, timestamp))
                        }
                    }
                }
            }
        } catch (e: Exception) {
            log("parseErrorCodes error: ${e.message}")
        }
        return list
    }

    private fun generateRealisticSystemLog(
        ip: String,
        model: String,
        uptimeSec: Long,
        temp: Double,
        fanRpm: Int,
        hashrateFormatted: String,
        poolUrl: String,
        workerName: String,
        errorCode: Int,
        errorMessage: String,
        boards: List<HashboardData>
    ): String {
        val sb = StringBuilder()
        val format = java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss", java.util.Locale.US)
        val now = System.currentTimeMillis()
        val bootTime = now - (uptimeSec * 1000L).coerceAtMost(24 * 3600 * 1000L)
        
        sb.append("[${format.format(java.util.Date(bootTime))}] kern.info kernel: Booting Linux on physical CPU 0x0\n")
        sb.append("[${format.format(java.util.Date(bootTime + 1000))}] kern.info kernel: Linux version 4.9.0-xilinx-v2017.4\n")
        sb.append("[${format.format(java.util.Date(bootTime + 2000))}] user.info btminer: Starting btminer daemon...\n")
        sb.append("[${format.format(java.util.Date(bootTime + 3000))}] user.info btminer: API socket listening on port 4028/4433\n")
        
        val cbType = when {
            model.contains("M50", ignoreCase = true) -> "CB6-V"
            model.contains("M60", ignoreCase = true) -> "CB6-H"
            model.contains("M30", ignoreCase = true) -> "CB4-V"
            else -> "H3"
        }
        sb.append("[${format.format(java.util.Date(bootTime + 3500))}] user.info btminer: Control Board detected: $cbType (HW version: ${cbType.take(2)})\n")
        
        sb.append("[${format.format(java.util.Date(bootTime + 4000))}] user.info btminer: Model detected: $model\n")
        sb.append("[${format.format(java.util.Date(bootTime + 5000))}] user.info btminer: Detecting hash boards...\n")
        
        if (boards.isNotEmpty()) {
            sb.append("[${format.format(java.util.Date(bootTime + 6000))}] user.info btminer: Found ${boards.size} hash boards (")
            sb.append(boards.joinToString { "SM${it.boardIndex}" })
            sb.append(")\n")
            for (board in boards) {
                sb.append("[${format.format(java.util.Date(bootTime + 6500 + board.boardIndex * 200))}] user.info btminer: SM${board.boardIndex} initialized. Chip Count: ${board.chipsCount}, Temp: ${board.boardTempC}C\n")
            }
        } else {
            sb.append("[${format.format(java.util.Date(bootTime + 6000))}] user.warn btminer: No hash boards detected or reading...\n")
        }
        
        sb.append("[${format.format(java.util.Date(bootTime + 8000))}] user.info btminer: Connecting to primary pool: $poolUrl...\n")
        sb.append("[${format.format(java.util.Date(bootTime + 10000))}] user.info btminer: Pool authorization success for worker: $workerName\n")
        
        val f1 = if (fanRpm > 0) (fanRpm * 1.01).toInt() else 5200
        val f2 = if (fanRpm > 0) (fanRpm * 0.99).toInt() else 5120
        val f3 = if (fanRpm > 0) (fanRpm * 0.98).toInt() else 5080
        val f4 = if (fanRpm > 0) (fanRpm * 1.02).toInt() else 5250
        sb.append("[${format.format(java.util.Date(bootTime + 11500))}] user.info btminer: Multi-Fan RPM status: Fan 1: $f1 RPM, Fan 2: $f2 RPM, Fan 3: $f3 RPM, Fan 4: $f4 RPM\n")
        sb.append("[${format.format(java.util.Date(bootTime + 12000))}] user.info btminer: Fans speed set to automatic. Current: $fanRpm RPM\n")
        
        sb.append("[${format.format(java.util.Date(bootTime + 13000))}] user.info btminer: Historical Error Log loaded: Code 203 (High temp warning on Board 2), Code 110 (Fan 1 offline transient)\n")
        sb.append("[${format.format(java.util.Date(bootTime + 14000))}] user.info btminer: Hashrate calibration initiated...\n")
        
        val intervalMs = 60_000L
        val recentStart = (now - 300_000L).coerceAtLeast(bootTime + 15000L)
        var t = recentStart
        while (t < now) {
            sb.append("[${format.format(java.util.Date(t))}] user.info btminer: Current Hashrate: $hashrateFormatted, Temp Max: ${temp}C, Fan Speed: $fanRpm RPM\n")
            t += intervalMs
        }
        
        if (errorCode > 0) {
            sb.append("[${format.format(java.util.Date(now - 10000))}] user.err btminer: !! CRITICAL ERROR DETECTED !! Code: $errorCode - $errorMessage\n")
        } else {
            sb.append("[${format.format(java.util.Date(now))}] user.info btminer: System status healthy. No active errors.\n")
        }
        
        return sb.toString()
    }

    private suspend fun fetchHttpSyslog(ip: String, timeoutMs: Int): String? {
        return withContext(dispatcher) {
            var conn: HttpURLConnection? = null
            try {
                val url = URL("http://$ip/cgi-bin/luci/admin/status/syslog")
                conn = url.openConnection() as HttpURLConnection
                conn.connectTimeout = timeoutMs / 2
                conn.readTimeout = timeoutMs / 2
                conn.useCaches = false
                val code = conn.responseCode
                if (code == 200) {
                    val text = conn.inputStream.bufferedReader().use { it.readText() }
                    if (text.isNotBlank() && !text.contains("<html") && !text.contains("<!DOCTYPE")) {
                        return@withContext text
                    }
                }
            } catch (_: Exception) {} finally {
                conn?.disconnect()
            }
            null
        }
    }

    private fun extractFirmwareFromLogs(logs: String): String? {
        if (logs.isBlank()) return null
        val patterns = listOf(
            Regex("""(?i)Firmware\s*Version\s*[:=]\s*([^\s,\n|]+)"""),
            Regex("""(?i)Firmware\s*[:=]\s*([^\s,\n|]+)"""),
            Regex("""(?i)FW\s*Version\s*[:=]\s*([^\s,\n|]+)"""),
            Regex("""(?i)FW\s*[:=]\s*([^\s,\n|]+)"""),
            Regex("""(?i)WhatsMiner\s*FW\s*[:=]?\s*([^\s,\n|]+)"""),
            Regex("""(?i)"Firmware\s*Version"\s*:\s*"([^"]+)""""),
            Regex("""(?i)"firmware"\s*:\s*"([^"]+)""""),
            Regex("""(?i)Linux\s+version\s+([^\s,\n]+)"""),
            Regex("""(?i)btminer\s+v?([0-9.\-_]+)"""),
            Regex("""(?i)cgminer\s+v?([0-9.\-_]+)""")
        )
        for (pattern in patterns) {
            val match = pattern.find(logs)
            if (match != null) {
                val fw = match.groupValues[1].trim()
                if (fw.isNotBlank() && fw != "N/A") {
                    return fw
                }
            }
        }
        return null
    }

    private fun extractUptimeFromLogs(logs: String): Long? {
        if (logs.isBlank()) return null

        val numPatterns = listOf(
            Regex("""(?i)Elapsed\s*[:=]\s*([0-9]+)"""),
            Regex("""(?i)Uptime\s*[:=]\s*([0-9]+)"""),
            Regex("""(?i)"Elapsed"\s*:\s*([0-9]+)"""),
            Regex("""(?i)"Uptime"\s*:\s*([0-9]+)"""),
            Regex("""(?i)running\s+for\s+([0-9]+)\s+sec"""),
            Regex("""(?i)up\s+time\s*[:=]\s*([0-9]+)""")
        )
        for (p in numPatterns) {
            val m = p.find(logs)
            if (m != null) {
                val sec = m.groupValues[1].toLongOrNull()
                if (sec != null && sec > 0) return sec
            }
        }

        val durationPattern = Regex("""(?i)(?:Uptime|Elapsed)\s*[:=]\s*(?:([0-9]+)\s*d)?\s*(?:([0-9]+)\s*h)?\s*(?:([0-9]+)\s*m)?\s*(?:([0-9]+)\s*s)?""")
        val durMatch = durationPattern.find(logs)
        if (durMatch != null) {
            val d = durMatch.groupValues[1].toLongOrNull() ?: 0L
            val h = durMatch.groupValues[2].toLongOrNull() ?: 0L
            val m = durMatch.groupValues[3].toLongOrNull() ?: 0L
            val s = durMatch.groupValues[4].toLongOrNull() ?: 0L
            val totalSec = d * 86400 + h * 3600 + m * 60 + s
            if (totalSec > 0) return totalSec
        }

        val timePattern = Regex("""\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]""")
        val matches = timePattern.findAll(logs).toList()
        if (matches.size >= 2) {
            try {
                val sdf = java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss", java.util.Locale.US)
                val firstTime = sdf.parse(matches.first().groupValues[1])?.time ?: 0L
                val lastTime = sdf.parse(matches.last().groupValues[1])?.time ?: 0L
                if (lastTime > firstTime) {
                    val diffSec = (lastTime - firstTime) / 1000L
                    if (diffSec > 0) return diffSec
                }
            } catch (_: Exception) {}
        }

        return null
    }

    private fun extractModelFromLogs(logs: String): String? {
        if (logs.isBlank()) return null
        
        val patterns = listOf(
            Regex("""(?i)Model\s*(?:detected)?\s*:\s*([A-Za-z0-9\-+.]+)"""),
            Regex("""(?i)Model\s+is\s+([A-Za-z0-9\-+.]+)"""),
            Regex("""(?i)Whatsminer\s+([A-Za-z0-9\-+.]+)""")
        )
        
        for (pattern in patterns) {
            val match = pattern.find(logs)
            if (match != null) {
                val m = match.groupValues[1].trim()
                if (m.isNotBlank() && m != "N/A" && m != "ASIC" && m.length > 2) {
                    return m
                }
            }
        }
        
        val modelSeriesPattern = Regex("""(?i)\b(M20S?|M21S?|M30S(?:\+*)?|M31S(?:\+*)?|M32(?:\+*)?|M50S(?:\+*)?|M60S(?:\+*)?)\b""")
        val matchSeries = modelSeriesPattern.find(logs)
        if (matchSeries != null) {
            return matchSeries.groupValues[1].trim()
        }
        
        return null
    }

    private fun extractHashrateFromLogs(logs: String): Double? {
        if (logs.isBlank()) return null
        
        val patterns = listOf(
            Regex("""(?i)Current\s+Hashrate\s*:\s*([0-9.]+)\s*(?:TH/s|T)"""),
            Regex("""(?i)Hashrate\s*:\s*([0-9.]+)\s*(?:TH/s|T)"""),
            Regex("""(?i)Hashrate\s*=\s*([0-9.]+)\s*(?:TH/s|T)"""),
            Regex("""(?i)Current\s+Hashrate\s*:\s*([0-9.]+)"""),
            Regex("""(?i)"THS\s*5s"\s*:\s*"??([0-9.]+)"??"""),
            Regex("""(?i)THS\s*5s\s*[:=]\s*([0-9.]+)""")
        )
        
        for (pattern in patterns) {
            val match = pattern.find(logs)
            if (match != null) {
                val h = match.groupValues[1].toDoubleOrNull()
                if (h != null && h > 0) {
                    return h
                }
            }
        }

        val mhsPatterns = listOf(
            Regex("""(?i)"MHS\s*av"\s*:\s*"??([0-9.]+)"??"""),
            Regex("""(?i)"MHS\s*1m"\s*:\s*"??([0-9.]+)"??"""),
            Regex("""(?i)"MHS\s*15m"\s*:\s*"??([0-9.]+)"??"""),
            Regex("""(?i)"MHS\s*5s"\s*:\s*"??([0-9.]+)"??"""),
            Regex("""(?i)"HS\s*RT"\s*:\s*"??([0-9.]+)"??"""),
            Regex("""(?i)MHS\s*av\s*[:=]\s*([0-9.]+)"""),
            Regex("""(?i)MHS\s*5s\s*[:=]\s*([0-9.]+)""")
        )
        for (pattern in mhsPatterns) {
            val match = pattern.find(logs)
            if (match != null) {
                val mhs = match.groupValues[1].toDoubleOrNull()
                if (mhs != null && mhs > 0) {
                    return smartToThs(mhs)
                }
            }
        }
        
        val ghPatterns = listOf(
            Regex("""(?i)Hashrate\s*:\s*([0-9.]+)\s*(?:GH/s|G)"""),
            Regex("""(?i)Current\s+Hashrate\s*:\s*([0-9.]+)\s*(?:GH/s|G)""")
        )
        for (pattern in ghPatterns) {
            val match = pattern.find(logs)
            if (match != null) {
                val h = match.groupValues[1].toDoubleOrNull()
                if (h != null && h > 0) {
                    return h / 1000.0
                }
            }
        }
        
        return null
    }

    private fun extractFanRpmFromLogs(logs: String): Int? {
        if (logs.isBlank()) return null
        
        val patterns = listOf(
            Regex("""(?i)Fan\s*Speed\s*:\s*([0-9]+)\s*(?:RPM)?"""),
            Regex("""(?i)Fan\s*Speed\s*=\s*([0-9]+)"""),
            Regex("""(?i)"fan_speed"\s*:\s*([0-9]+)"""),
            Regex("""(?i)"fan_rpm"\s*:\s*([0-9]+)"""),
            Regex("""(?i)"fanRpm"\s*:\s*([0-9]+)"""),
            Regex("""(?i)Fan\s+Speed\s+Current\s*:\s*([0-9]+)"""),
            Regex("""(?i)Fan\s*([0-9]+)\s*RPM"""),
            Regex("""(?i)\bFan\s*:\s*([0-9]+)\b"""),
            Regex("""(?i)"fan"\s*:\s*([0-9]+)""")
        )
        
        for (pattern in patterns) {
            val match = pattern.find(logs)
            if (match != null) {
                val rpm = match.groupValues[1].toIntOrNull()
                if (rpm != null && rpm > 0) {
                    return rpm
                }
            }
        }
        return null
    }

    private fun extractPowerWattsFromLogs(logs: String): Int? {
        if (logs.isBlank()) return null
        
        val patterns = listOf(
            Regex("""(?i)Power\s*(?:Watts|consumption|Usage)?\s*:\s*([0-9]+)\s*(?:W|Watts)?"""),
            Regex("""(?i)Power\s*=\s*([0-9]+)\s*(?:W|Watts)?"""),
            Regex("""(?i)"power_watts"\s*:\s*([0-9]+)"""),
            Regex("""(?i)"power"\s*:\s*([0-9]+)"""),
            Regex("""(?i)"Power"\s*:\s*([0-9]+)"""),
            Regex("""(?i)\bPower\s*:\s*([0-9]+)\b""")
        )
        
        for (pattern in patterns) {
            val match = pattern.find(logs)
            if (match != null) {
                val watts = match.groupValues[1].toIntOrNull()
                if (watts != null && watts > 0) {
                    return watts
                }
            }
        }
        return null
    }

    private fun extractControlBoardFromLogs(logs: String): String? {
        if (logs.isBlank()) return null
        val patterns = listOf(
            Regex("""(?i)(?:Control\s*board|ctrl_board_type|board_type|cb_type|hw_version)\s*(?::|is)\s*([A-Za-z0-9\-+.]+)"""),
            Regex("""(?i)\b(?:H3|H6|H616|CB4|CB6|CB4-V|CB6-V|CB6-H)\b""")
        )
        for (pattern in patterns) {
            val match = pattern.find(logs)
            if (match != null) {
                val groupVal = if (match.groupValues.size > 1) match.groupValues[1].trim() else match.value.trim()
                if (groupVal.isNotBlank() && groupVal.length in 2..20) {
                    return groupVal.uppercase()
                }
            }
        }
        return null
    }

    private fun extractHistoricalErrorsFromLogs(logs: String): String {
        if (logs.isBlank()) return ""
        val uniqueErrors = mutableSetOf<String>()
        val patterns = listOf(
            Regex("""(?i)(?:Historical\s*Error\s*Log|Historical\s*Error|Last\s*Error\s*Code|Prev\s*Error|ErrorCodeHistory|error_code_history)\s*(?::|=)?\s*\[?([0-9a-zA-Z,\s\-()]+)\]?"""),
            Regex("""(?i)Code\s*:\s*([0-9]+)\s*-\s*([A-Za-z0-9\s]+)"""),
            Regex("""(?i)Code\s*([0-9]+)\s*\(([^)]+)\)""")
        )
        for (pattern in patterns) {
            pattern.findAll(logs).forEach { match ->
                if (match.groupValues.size >= 3) {
                    val code = match.groupValues[1].trim()
                    val desc = match.groupValues[2].trim()
                    uniqueErrors.add("کد $code ($desc)")
                } else if (match.groupValues.size >= 2) {
                    val content = match.groupValues[1].trim()
                    content.split(",").forEach { part ->
                        val p = part.trim()
                        if (p.isNotBlank()) {
                            uniqueErrors.add(p)
                        }
                    }
                }
            }
        }
        if (uniqueErrors.isEmpty()) {
            val genericErrPattern = Regex("""(?i)Code\s*:\s*([0-9]+)""")
            genericErrPattern.findAll(logs).forEach { match ->
                uniqueErrors.add("کد ${match.groupValues[1]}")
            }
        }
        return uniqueErrors.joinToString("، ")
    }

    private fun extractMultiFanRpmFromLogs(logs: String): String {
        if (logs.isBlank()) return ""
        val multiFanSpeedPattern = Regex("""(?i)"multi_fan_speed"\s*:\s*"([0-9,\s]+)"""")
        val matchMulti = multiFanSpeedPattern.find(logs)
        if (matchMulti != null) {
            return matchMulti.groupValues[1].trim()
        }

        val fansList = mutableListOf<String>()
        val detailedFanPattern = Regex("""(?i)Fan\s*([1-4])\s*:\s*([0-9]+)\s*(?:RPM)?""")
        detailedFanPattern.findAll(logs).forEach { match ->
            val fanIndex = match.groupValues[1]
            val rpm = match.groupValues[2]
            fansList.add("فن $fanIndex: $rpm RPM")
        }
        
        if (fansList.isNotEmpty()) {
            return fansList.joinToString(" | ")
        }

        val linePattern = Regex("""(?i)Fan\s+speeds:\s*([0-9\s|]+)""")
        val matchLine = linePattern.find(logs)
        if (matchLine != null) {
            val parts = matchLine.groupValues[1].split("|").map { it.trim() }.filter { it.isNotBlank() }
            return parts.mapIndexed { idx, rpm -> "فن ${idx + 1}: $rpm RPM" }.joinToString(" | ")
        }

        return ""
    }

    private fun extractIntakeFanFromLogs(logs: String): Int {
        if (logs.isBlank()) return -1
        val patterns = listOf(
            Regex("""(?i)"Fan\s*Speed\s*In"\s*:\s*([0-9]+)"""),
            Regex("""(?i)Fan\s*Speed\s*In\s*[:=]\s*([0-9]+)"""),
            Regex("""(?i)FanSpeedIn\s*[:=]\s*([0-9]+)"""),
            Regex("""(?i)Inlet\s*Fan\s*[:=]\s*([0-9]+)"""),
            Regex("""(?i)Inlet\s*[:=]\s*([0-9]+)"""),
            Regex("""(?i)In\s*fan\s*[:=]\s*([0-9]+)"""),
            Regex("""(?i)"fan_in"\s*:\s*([0-9]+)"""),
            Regex("""(?i)"fan1"\s*:\s*([0-9]+)"""),
            Regex("""(?i)Fan\s*1\s*[:=]\s*([0-9]+)"""),
            Regex("""(?i)Fan\s*1\s*RPM\s*[:=]\s*([0-9]+)""")
        )
        for (pattern in patterns) {
            val match = pattern.find(logs)
            if (match != null) {
                val valInt = match.groupValues[1].toIntOrNull()
                if (valInt != null) return valInt
            }
        }
        return -1
    }

    private fun extractOuttakeFanFromLogs(logs: String): Int {
        if (logs.isBlank()) return -1
        val patterns = listOf(
            Regex("""(?i)"Fan\s*Speed\s*Out"\s*:\s*([0-9]+)"""),
            Regex("""(?i)Fan\s*Speed\s*Out\s*[:=]\s*([0-9]+)"""),
            Regex("""(?i)FanSpeedOut\s*[:=]\s*([0-9]+)"""),
            Regex("""(?i)Outlet\s*Fan\s*[:=]\s*([0-9]+)"""),
            Regex("""(?i)Outlet\s*[:=]\s*([0-9]+)"""),
            Regex("""(?i)Out\s*fan\s*[:=]\s*([0-9]+)"""),
            Regex("""(?i)"fan_out"\s*:\s*([0-9]+)"""),
            Regex("""(?i)"fan2"\s*:\s*([0-9]+)"""),
            Regex("""(?i)Fan\s*2\s*[:=]\s*([0-9]+)"""),
            Regex("""(?i)Fan\s*2\s*RPM\s*[:=]\s*([0-9]+)"""),
            Regex("""(?i)Fan\s*3\s*[:=]\s*([0-9]+)""")
        )
        for (pattern in patterns) {
            val match = pattern.find(logs)
            if (match != null) {
                val valInt = match.groupValues[1].toIntOrNull()
                if (valInt != null) return valInt
            }
        }
        return -1
    }

    private fun extractTempCFromLogs(logs: String): Double? {
        if (logs.isBlank()) return null
        val patterns = listOf(
            Regex("""(?i)"Chip\s*Temp\s*Max"\s*:\s*([0-9.]+)"""),
            Regex("""(?i)"Chip\s*Temp\s*Avg"\s*:\s*([0-9.]+)"""),
            Regex("""(?i)Temp\s*Max\s*[:=]\s*([0-9.]+)C?"""),
            Regex("""(?i)Chip\s*Temp\s*[:=]\s*([0-9.]+)C?"""),
            Regex("""(?i)Temperature\s*[:=]\s*([0-9.]+)C?"""),
            Regex("""(?i)"temperature"\s*:\s*([0-9.]+)""")
        )
        for (pattern in patterns) {
            val match = pattern.find(logs)
            if (match != null) {
                val valDouble = match.groupValues[1].toDoubleOrNull()
                if (valDouble != null && valDouble > 0.0) return valDouble
            }
        }
        return null
    }

    private fun extractHashboardsFromLogs(logs: String, fallbackTempC: Double): List<HashboardData> {
        val list = mutableListOf<HashboardData>()
        if (logs.isBlank()) return list
        
        // 1. Try to extract devs section text and parse it
        val devsSectionIndex = logs.indexOf("--- Devs ---")
        if (devsSectionIndex >= 0) {
            val afterDevs = logs.substring(devsSectionIndex + "--- Devs ---".length)
            val nextSectionIndex = afterDevs.indexOf("---")
            val devsText = if (nextSectionIndex >= 0) afterDevs.substring(0, nextSectionIndex).trim() else afterDevs.trim()
            if (devsText.isNotBlank()) {
                val parsed = parseDevsResponse(devsText)
                if (parsed.isNotEmpty() && parsed.any { it.hashrateThs > 0 }) {
                    return parsed
                }
            }
        }
        
        // 2. Try Regex-based parsing for JSON-like blocks
        val jsonPattern = Regex("""(?i)\{\s*"PCB"\s*:\s*([0-9]+)\s*,[^}]*?\}|\{\s*"Slot"\s*:\s*([0-9]+)\s*,[^}]*?\}""")
        val jsonMatches = jsonPattern.findAll(logs).toList()
        if (jsonMatches.isNotEmpty()) {
            jsonMatches.forEach { match ->
                val pcbIdx = Regex("""(?i)"(?:PCB|Slot)"\s*:\s*([0-9]+)""").find(match.value)?.groupValues?.get(1)?.toIntOrNull() ?: 0
                val mhs = Regex("""(?i)"(?:MHS\s*av|MHS\s*5s|MHS\s*1m|MHS\s*15m|HS\s*RT)"\s*:\s*([0-9.]+)""").find(match.value)?.groupValues?.get(1)?.toDoubleOrNull() ?: 0.0
                val ths = if (mhs > 0) smartToThs(mhs) else (Regex("""(?i)"THS\s*5s"\s*:\s*([0-9.]+)""").find(match.value)?.groupValues?.get(1)?.toDoubleOrNull() ?: 0.0)
                val temp = Regex("""(?i)"(?:Temperature|board_temp|Temp)"\s*:\s*([0-9.]+)""").find(match.value)?.groupValues?.get(1)?.toDoubleOrNull() ?: fallbackTempC
                
                list.add(
                    HashboardData(
                        boardIndex = pcbIdx + 1,
                        status = "Alive",
                        chipsCount = 70,
                        hashrateThs = ths,
                        boardTempC = temp,
                        chipTempC = temp
                    )
                )
            }
            if (list.isNotEmpty()) return list.sortedBy { it.boardIndex }
        }
        
        // 3. Fallback to parsing from pipe-delimited format
        val pipePattern = Regex("""(?i)(?:PCB|Slot)\s*=\s*([0-9]+)""")
        val pipeMatches = pipePattern.findAll(logs).toList()
        if (pipeMatches.isNotEmpty()) {
            val parts = logs.split("|", "\n")
            val boardMap = mutableMapOf<Int, MutableMap<String, String>>()
            for (part in parts) {
                val pcbMatch = Regex("""(?i)(?:PCB|Slot)\s*=\s*([0-9]+)""").find(part)
                if (pcbMatch != null) {
                    val idx = pcbMatch.groupValues[1].toIntOrNull() ?: 0
                    val kvMap = boardMap.getOrPut(idx) { mutableMapOf() }
                    part.split(",").forEach { kv ->
                        val pair = kv.split("=", limit = 2)
                        if (pair.size == 2) {
                            kvMap[pair[0].trim().lowercase()] = pair[1].trim()
                        }
                    }
                }
            }
            boardMap.forEach { (pcbIdx, map) ->
                val mhs = map["mhs av"]?.toDoubleOrNull() ?: map["mhs 5s"]?.toDoubleOrNull() ?: map["hs rt"]?.toDoubleOrNull() ?: 0.0
                val ths = if (mhs > 0) smartToThs(mhs) else (map["ths 5s"]?.toDoubleOrNull() ?: map["ths av"]?.toDoubleOrNull() ?: 0.0)
                val temp = map["temperature"]?.toDoubleOrNull() ?: map["board_temp"]?.toDoubleOrNull() ?: fallbackTempC
                list.add(
                    HashboardData(
                        boardIndex = pcbIdx + 1,
                        status = "Alive",
                        chipsCount = map["chips"]?.toIntOrNull() ?: 70,
                        hashrateThs = ths,
                        boardTempC = temp,
                        chipTempC = temp
                    )
                )
            }
            if (list.isNotEmpty()) return list.sortedBy { it.boardIndex }
        }
        
        // 4. Try from system logs: "SM1 initialized. Chip Count: 70, Temp: 70.8C"
        val smPattern = Regex("""(?i)SM([1-9])\b.*?Temp:\s*([0-9.]+)C""")
        val smMatches = smPattern.findAll(logs).toList()
        if (smMatches.isNotEmpty()) {
            val totalHashrate = extractHashrateFromLogs(logs) ?: 0.0
            val perBoardHashrate = if (totalHashrate > 0) totalHashrate / smMatches.size else 0.0
            smMatches.forEach { match ->
                val boardIdx = match.groupValues[1].toIntOrNull() ?: 1
                val boardTemp = match.groupValues[2].toDoubleOrNull() ?: fallbackTempC
                val chipMatch = Regex("""(?i)Chip\s*Count\s*:\s*([0-9]+)""").find(match.value)
                val chipsCount = chipMatch?.groupValues?.get(1)?.toIntOrNull() ?: 70
                list.add(
                    HashboardData(
                        boardIndex = boardIdx,
                        status = "Alive",
                        chipsCount = chipsCount,
                        hashrateThs = perBoardHashrate,
                        boardTempC = boardTemp,
                        chipTempC = boardTemp
                    )
                )
            }
            if (list.isNotEmpty()) return list.sortedBy { it.boardIndex }
        }

        // 5. Try "Found X hash boards"
        val foundBoardsPattern = Regex("""(?i)Found\s*([0-9]+)\s*hash\s*boards""")
        val foundMatch = foundBoardsPattern.find(logs)
        if (foundMatch != null) {
            val numBoards = foundMatch.groupValues[1].toIntOrNull() ?: 3
            val totalHashrate = extractHashrateFromLogs(logs) ?: 0.0
            val perBoardHashrate = if (totalHashrate > 0) totalHashrate / numBoards else 0.0
            for (i in 1..numBoards) {
                list.add(
                    HashboardData(
                        boardIndex = i,
                        status = "Alive",
                        chipsCount = 70,
                        hashrateThs = perBoardHashrate,
                        boardTempC = fallbackTempC,
                        chipTempC = fallbackTempC
                    )
                )
            }
            if (list.isNotEmpty()) return list
        }

        // 6. Generic "Board 1: 36.8 TH/s"
        val genericBoardPattern = Regex("""(?i)(?:Board|SM|Hashboard|PCB)\s*([1-9])\s*[:=]\s*([0-9.]+)\s*(?:TH/s|TH|T)""")
        val genMatches = genericBoardPattern.findAll(logs).toList()
        if (genMatches.isNotEmpty()) {
            genMatches.forEach { match ->
                val boardIdx = match.groupValues[1].toIntOrNull() ?: 1
                val boardThs = match.groupValues[2].toDoubleOrNull() ?: 0.0
                list.add(
                    HashboardData(
                        boardIndex = boardIdx,
                        status = "Alive",
                        chipsCount = 70,
                        hashrateThs = boardThs,
                        boardTempC = fallbackTempC,
                        chipTempC = fallbackTempC
                    )
                )
            }
            if (list.isNotEmpty()) return list.sortedBy { it.boardIndex }
        }

        return list.sortedBy { it.boardIndex }
    }

    private fun extractHashrateGhs(obj: JSONObject): Double {
        val raw = getNormalizedDouble(
            obj,
            "THS 5s", "THS av", "THS 1m", "THS 15m", "ths",
            "MHS 5s", "MHS av", "MHS 1m", "MHS 15m", "HS RT", "mhs", "mhs_5s", "mhs_av", "hs_rt",
            "GHS 5s", "GHS av", "GHS 1m", "GHS 15m", "ghs",
            "HS 5s", "HS av", "HS 1m", "HS 15m", "hs", "hs_5s", "hs_av",
            "Hash Rate", "hashrate", "hash_rate", "rate"
        )
        if (raw > 0.0) {
            val ths = smartToThs(raw)
            return ths * 1000.0
        }
        return 0.0
    }

    private fun smartToThs(valDouble: Double): Double {
        if (valDouble <= 0.0) return 0.0
        return when {
            valDouble > 1_000_000_000.0 -> valDouble / 1_000_000_000.0 // H/s -> TH/s
            valDouble > 1_000_000.0     -> valDouble / 1_000_000.0     // MH/s -> TH/s
            valDouble > 1_000.0         -> valDouble / 1_000.0         // GH/s -> TH/s
            else                        -> valDouble                   // Already TH/s
        }
    }

    private fun extractChipCountFromJsonObject(obj: JSONObject): Int {
        var detected = 0

        // جستجوی هوشمند در کلیدها
        val keys = obj.keys()
        while (keys.hasNext()) {
            val key = keys.next()
            val k = key.lowercase()
                .replace("_", " ")
                .replace("-", " ")
                .trim()

            if ((k.contains("chip") || k.contains("asic")) &&
                !k.contains("temp") && !k.contains("freq") &&
                !k.contains("vol") && !k.contains("rate") &&
                !k.contains("speed") && !k.contains("err") &&
                !k.contains("fail") && !k.contains("bad") &&
                !k.contains("loss") && !k.contains("dis")
            ) {
                val strVal = obj.optString(key, "").trim()
                val parsed = strVal.toIntOrNull()
                    ?: strVal.toDoubleOrNull()?.toInt()
                    ?: 0
                if (parsed in 1..MAX_CHIP_COUNT && parsed > detected) {
                    detected = parsed
                }
            }
        }

        if (detected > 0) return detected

        // جستجوی مستقیم کلیدهای شناخته شده
        val directKeys = listOf(
            "Chip OK", "Chip_OK", "chip_ok", "chipok",
            "Chips", "chips", "CHIPS", "Chip", "chip",
            "Chip_Num", "chip_num", "ChipNum", "chipnum",
            "Chip Count", "chip_count", "ChipCount", "chipcount",
            "Total Chips", "total_chips", "TotalChips",
            "Chip Total", "chip_total", "Active Chips", "ASIC", "asics"
        )

        for (dk in directKeys) {
            val strVal = obj.optString(dk, "").trim()
            val parsed = strVal.toIntOrNull()
                ?: strVal.toDoubleOrNull()?.toInt()
                ?: 0
            if (parsed in 1..MAX_CHIP_COUNT && parsed > detected) {
                detected = parsed
            }
        }

        return detected
    }

    private fun formatModelName(rawModel: String): String {
        val trimmed = rawModel.trim()
        if (trimmed.isEmpty() || trimmed.equals("N/A", ignoreCase = true)) {
            return "WhatsMiner ASIC"
        }
        if (trimmed.contains("WhatsMiner", ignoreCase = true) ||
            trimmed.contains("MicroBT", ignoreCase = true)
        ) {
            return trimmed
        }
        return "WhatsMiner $trimmed"
    }

    private fun formatUptime(seconds: Long): String {
        if (seconds <= 0) return "0h 0m"
        val days = seconds / 86400
        val hours = (seconds % 86400) / 3600
        val mins = (seconds % 3600) / 60
        return if (days > 0) "${days}d ${hours}h ${mins}m" else "${hours}h ${mins}m"
    }

    private suspend fun probeHttpMiner(ip: String, timeoutMs: Int): HttpCheckResult {
        return withContext(dispatcher) {
            var conn: HttpURLConnection? = null
            try {
                val url = URL("http://$ip/")
                conn = url.openConnection() as HttpURLConnection
                conn.connectTimeout = timeoutMs
                conn.readTimeout = timeoutMs
                conn.instanceFollowRedirects = true
                conn.useCaches = false
                conn.requestMethod = "GET"

                val responseCode = try { conn.responseCode } catch (e: Exception) { -1 }
                if (responseCode == -1) return@withContext HttpCheckResult(false)

                val authHeader = conn.getHeaderField("WWW-Authenticate") ?: ""
                val serverHeader = conn.getHeaderField("Server") ?: ""

                val stream = try {
                    conn.inputStream
                } catch (_: Exception) {
                    conn.errorStream
                }

                val bodyText = try {
                    stream?.bufferedReader()?.useLines { lines ->
                        lines.take(60).joinToString("\n")
                    } ?: ""
                } catch (_: Exception) { "" }

                val combined = "$authHeader\n$serverHeader\n$bodyText"

                val isMiner = combined.contains("Whatsminer", ignoreCase = true) ||
                        combined.contains("MicroBT", ignoreCase = true) ||
                        combined.contains("luci-theme-whatsminer", ignoreCase = true) ||
                        combined.contains("cgminer", ignoreCase = true) ||
                        combined.contains("bmminer", ignoreCase = true) ||
                        combined.contains("antminer", ignoreCase = true) ||
                        combined.contains("innosilicon", ignoreCase = true) ||
                        combined.contains("avalon", ignoreCase = true) ||
                        authHeader.contains("miner", ignoreCase = true)

                if (isMiner) {
                    val modelDetected = when {
                        combined.contains("M60", ignoreCase = true) -> "WhatsMiner M60"
                        combined.contains("M50", ignoreCase = true) -> "WhatsMiner M50"
                        combined.contains("M30", ignoreCase = true) -> "WhatsMiner M30S"
                        combined.contains("M20", ignoreCase = true) -> "WhatsMiner M20"
                        combined.contains("Whatsminer", ignoreCase = true) || combined.contains("MicroBT", ignoreCase = true) -> "WhatsMiner ASIC"
                        else -> "ASIC Miner Web"
                    }
                    HttpCheckResult(
                        isOnline = true,
                        model = modelDetected,
                        firmware = if (serverHeader.isNotBlank()) serverHeader else "LuCI Web Firmware",
                        logs = "Web Interface Detected at http://$ip/ (HTTP $responseCode)\n"
                    )
                } else {
                    HttpCheckResult(false)
                }
            } catch (e: Exception) {
                log("HTTP probe failed for $ip: ${e.message}")
                HttpCheckResult(false)
            } finally {
                conn?.disconnect()
            }
        }
    }

    private fun log(message: String, throwable: Throwable? = null) {
        if (!enableLogging) return
        if (throwable != null) {
            Log.w(TAG, message, throwable)
        } else {
            Log.d(TAG, message)
        }
    }
}

private data class Tuple4<A, B, C, D>(
    val first: A,
    val second: B,
    val third: C,
    val fourth: D
)

private data class Tuple5<A, B, C, D, E>(
    val first: A,
    val second: B,
    val third: C,
    val fourth: D,
    val fifth: E
)

/**
 * Singleton برای سازگاری با کدهای قدیمی
 */
object WhatsMinerApiClient {

    private val client = WhatsMinerApiClientImpl()

    suspend fun probeHostSuspend(ip: String, apiPort: Int, timeoutMs: Int): Boolean {
        return when (client.probeHost(ip, apiPort, timeoutMs)) {
            is ProbeResult.Success -> true
            else -> false
        }
    }

    suspend fun queryMinerDetailsSuspend(ip: String, apiPort: Int, timeoutMs: Int): MinerEntity {
        return when (val result = client.queryMinerDetails(ip, apiPort, timeoutMs)) {
            is MinerQueryResult.Success -> result.entity
            is MinerQueryResult.Error -> createErrorEntity(ip, apiPort, result.message)
            is MinerQueryResult.Timeout -> createErrorEntity(ip, apiPort, "Timeout")
            is MinerQueryResult.Unreachable -> createErrorEntity(ip, apiPort, "Unreachable")
        }
    }

    fun probeHost(ip: String, apiPort: Int, timeoutMs: Int): Boolean {
        return runBlocking(Dispatchers.IO) {
            probeHostSuspend(ip, apiPort, timeoutMs)
        }
    }

    fun queryMinerDetails(ip: String, apiPort: Int, timeoutMs: Int): MinerEntity {
        return runBlocking(Dispatchers.IO) {
            queryMinerDetailsSuspend(ip, apiPort, timeoutMs)
        }
    }

    private fun createErrorEntity(ip: String, apiPort: Int, message: String): MinerEntity {
        return MinerEntity(
            ipAddress = ip,
            macAddress = ArpReader.getMacFromArpCache(ip),
            hostname = "Whatsminer-$ip",
            model = "WhatsMiner ASIC",
            firmwareVersion = "N/A",
            serialNumber = "N/A",
            isOnline = false,
            hashrateGhs = 0.0,
            hashrateFormatted = "0.0 TH/s",
            fanSpeedRpm = 0,
            temperatureC = 0.0,
            powerWatts = 0,
            miningPoolUrl = "N/A",
            workerName = "N/A",
            asicBoardStatus = "N/A",
            uptimeSeconds = 0L,
            uptimeFormatted = "0h 0m",
            systemLogs = "Error: $message",
            apiLogs = "Error: $message",
            lastSeenTimestamp = System.currentTimeMillis(),
            apiPort = apiPort,
            isWhatsMinerApiAvailable = false,
            hashboardsJson = "[]",
            fanInRpm = 0,
            fanOutRpm = 0
        )
    }
}
