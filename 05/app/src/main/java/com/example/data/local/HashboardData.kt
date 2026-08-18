package com.example.data.local

import org.json.JSONArray
import org.json.JSONObject

/**
 * داده‌های یک برد هش (Hashboard) در ماینر WhatsMiner
 */
data class HashboardData(
    val boardIndex: Int = 1,
    val status: String = "Alive",
    val chipsCount: Int = 108,
    val hashrateThs: Double = 0.0,
    val boardTempC: Double = 0.0,
    val chipTempC: Double = 0.0,
    val voltage: Double = 0.0,
    val frequencyMhz: Double = 0.0,
    val errorCount: Int = 0
) {
    val boardStatus: BoardStatus
        get() = BoardStatus.fromString(status)

    /**
     * آیا برد سالم است؟
     */
    val isHealthy: Boolean
        get() = (boardStatus == BoardStatus.ALIVE || status.equals("Alive", ignoreCase = true)) && hashrateThs > 0

    /**
     * دمای بحرانی؟
     */
    val isOverheated: Boolean
        get() = maxOf(boardTempC, chipTempC) > 85.0

    /**
     * خلاصه وضعیت برای نمایش در UI
     */
    val statusSummary: String
        get() = buildString {
            append("برد #$boardIndex: ")
            append(String.format("%.1f", hashrateThs))
            append(" TH/s")
            if (chipTempC > 0) append(" | ${String.format("%.0f", chipTempC)}°C")
            if (!isHealthy) append(" ⚠️ ${boardStatus.displayName}")
        }

    fun toJson(): JSONObject {
        return JSONObject().apply {
            put("boardIndex", boardIndex)
            put("status", status)
            put("chipsCount", chipsCount)
            put("hashrateThs", hashrateThs)
            put("boardTempC", boardTempC)
            put("chipTempC", chipTempC)
            put("voltage", voltage)
            put("frequencyMhz", frequencyMhz)
            put("errorCount", errorCount)
        }
    }

    companion object {
        fun listToJsonString(list: List<HashboardData>): String {
            val jsonArray = JSONArray()
            list.forEach { jsonArray.put(it.toJson()) }
            return jsonArray.toString()
        }

        fun jsonStringToList(jsonStr: String): List<HashboardData> {
            if (jsonStr.isBlank()) return emptyList()
            return try {
                val jsonArray = JSONArray(jsonStr)
                val list = mutableListOf<HashboardData>()
                for (i in 0 until jsonArray.length()) {
                    val obj = jsonArray.getJSONObject(i)
                    list.add(
                        HashboardData(
                            boardIndex = obj.optInt("boardIndex", i + 1),
                            status = obj.optString("status", "Alive"),
                            chipsCount = obj.optInt("chipsCount", 0),
                            hashrateThs = obj.optDouble("hashrateThs", 0.0),
                            boardTempC = obj.optDouble("boardTempC", 0.0),
                            chipTempC = obj.optDouble("chipTempC", 0.0),
                            voltage = obj.optDouble("voltage", 0.0),
                            frequencyMhz = obj.optDouble("frequencyMhz", 0.0),
                            errorCount = obj.optInt("errorCount", 0)
                        )
                    )
                }
                list
            } catch (_: Exception) {
                emptyList()
            }
        }
    }
}

/**
 * وضعیت برد هش
 */
enum class BoardStatus(val displayName: String) {
    ALIVE("فعال"),
    DEAD("غیرفعال"),
    SICK("مشکل‌دار"),
    UNKNOWN("نامشخص");

    companion object {
        fun fromString(value: String): BoardStatus {
            return when (value.lowercase().trim()) {
                "alive", "ok", "active", "running" -> ALIVE
                "dead", "error", "fail", "failed" -> DEAD
                "sick", "warning", "degraded" -> SICK
                else -> UNKNOWN
            }
        }
    }
}
