package com.example.ui.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.example.data.local.PasswordProfile
import com.example.data.local.ScanSettings
import com.example.data.network.WhatsMinerApiClient
import com.example.data.repository.MinerRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.net.InetSocketAddress
import java.net.Socket

data class PingTestResult(
    val ip: String,
    val port: Int,
    val isTesting: Boolean = false,
    val latencyMs: Long = -1,
    val isSuccess: Boolean = false,
    val isApiActive: Boolean = false,
    val message: String = ""
)

class SettingsViewModel(private val repository: MinerRepository) : ViewModel() {

    private val _settings = MutableStateFlow(repository.settingsRepo.getSettings())
    val settings: StateFlow<ScanSettings> = _settings.asStateFlow()

    val passwordProfiles: StateFlow<List<PasswordProfile>> = repository.settingsRepo.profilesFlow

    private val _pingResult = MutableStateFlow<PingTestResult?>(null)
    val pingResult: StateFlow<PingTestResult?> = _pingResult.asStateFlow()

    fun updateSettings(newSettings: ScanSettings) {
        _settings.value = newSettings
        repository.settingsRepo.saveSettings(newSettings)
    }

    fun addPasswordProfile(title: String, username: String, pass: String) {
        if (title.isBlank()) return
        val profile = PasswordProfile(
            title = title.trim(),
            username = username.trim().ifBlank { "admin" },
            password = pass
        )
        repository.settingsRepo.addPasswordProfile(profile)
    }

    fun deletePasswordProfile(id: String) {
        repository.settingsRepo.deletePasswordProfile(id)
    }

    /**
     * 🚀 بهینه‌سازی: Debounce با چک isTesting قبل از launch
     */
    fun runPingTest(targetIp: String, portText: String) {
        // جلوگیری از اجرای همزمان
        if (_pingResult.value?.isTesting == true) return

        val ip = targetIp.trim()
        if (ip.isBlank()) {
            _pingResult.value = PingTestResult(
                ip = "",
                port = 4028,
                isSuccess = false,
                message = "لطفاً آدرس IP معتبر وارد کنید."
            )
            return
        }

        val port = portText.toIntOrNull() ?: _settings.value.apiPort

        _pingResult.value = PingTestResult(
            ip = ip,
            port = port,
            isTesting = true,
            message = "در حال تست اتصال سوکت و پینگ به $ip:$port..."
        )

        viewModelScope.launch {
            val result = withContext(Dispatchers.IO) {
                val startTime = System.currentTimeMillis()
                var isSocketOk = false
                var isApiOk = false
                var errorMsg = ""

                try {
                    Socket().use { socket ->
                        socket.connect(InetSocketAddress(ip, port), 2000)
                        isSocketOk = true
                    }
                } catch (e: Exception) {
                    errorMsg = e.message ?: "عدم پاسخگویی سوکت"
                }

                val latency = System.currentTimeMillis() - startTime

                if (isSocketOk) {
                    val entity = WhatsMinerApiClient.queryMinerDetails(ip, port, 1500)
                    isApiOk = entity.isWhatsMinerApiAvailable || entity.isOnline
                }

                PingTestResult(
                    ip = ip,
                    port = port,
                    isTesting = false,
                    latencyMs = if (isSocketOk) latency else -1,
                    isSuccess = isSocketOk,
                    isApiActive = isApiOk,
                    message = if (isSocketOk) {
                        "🟢 اتصال سوکت برقرار شد! (زمان پاسخ: $latency میلی‌ثانیه)" +
                                if (isApiOk) " | ⚡ API واتس‌ماینر فعال است"
                                else " | ⚠️ پورت باز است اما API پاسخ نداد"
                    } else {
                        "🔴 خطا در اتصال به $ip:$port ($errorMsg)"
                    }
                )
            }
            _pingResult.value = result
        }
    }

    fun clearAllData() {
        viewModelScope.launch {
            repository.clearAllMiners()
        }
    }

    class Factory(private val repository: MinerRepository) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            return SettingsViewModel(repository) as T
        }
    }
}
