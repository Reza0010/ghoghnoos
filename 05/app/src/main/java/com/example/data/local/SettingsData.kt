package com.example.data.local

import android.content.Context
import android.content.SharedPreferences
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import org.json.JSONArray
import org.json.JSONObject

data class PasswordProfile(
    val id: String = java.util.UUID.randomUUID().toString(),
    val title: String,
    val username: String = "admin",
    val password: String = "admin"
)

data class ScanSettings(
    val apiPort: Int = 4028,
    val timeoutMs: Int = 1500,
    val concurrency: Int = 30,
    val autoRefreshSec: Int = 10,
    val customSubnet: String = "",
    val pool1Url: String = "stratum+tcp://btc.f2pool.com:3333",
    val pool1Worker: String = "user.worker1",
    val pool1Pass: String = "123",
    val pool2Url: String = "stratum+tcp://btc.antpool.com:3333",
    val pool2Worker: String = "user.worker2",
    val pool2Pass: String = "123",
    val pool3Url: String = "stratum+tcp://btc.viabtc.top:3333",
    val pool3Worker: String = "user.worker3",
    val pool3Pass: String = "123"
) {
    companion object {
        val DEFAULT = ScanSettings()
    }

    /**
     * اعتبارسنجی و محدودسازی مقادیر
     */
    fun validated(): ScanSettings = copy(
        apiPort = apiPort.coerceIn(1, 65535),
        timeoutMs = timeoutMs.coerceIn(500, 30_000),
        concurrency = concurrency.coerceIn(1, 50),
        autoRefreshSec = autoRefreshSec.coerceIn(3, 300),
        customSubnet = customSubnet.trim(),
        pool1Url = pool1Url.trim(),
        pool1Worker = pool1Worker.trim(),
        pool1Pass = pool1Pass.trim(),
        pool2Url = pool2Url.trim(),
        pool2Worker = pool2Worker.trim(),
        pool2Pass = pool2Pass.trim(),
        pool3Url = pool3Url.trim(),
        pool3Worker = pool3Worker.trim(),
        pool3Pass = pool3Pass.trim()
    )
}

class SettingsRepository(context: Context) {

    private val prefs: SharedPreferences =
        context.applicationContext.getSharedPreferences("whatsminer_prefs", Context.MODE_PRIVATE)

    private val _settingsFlow = MutableStateFlow(getSettings())
    val settingsFlow: StateFlow<ScanSettings> = _settingsFlow.asStateFlow()

    private val _profilesFlow = MutableStateFlow(readStoredProfiles())
    val profilesFlow: StateFlow<List<PasswordProfile>> = _profilesFlow.asStateFlow()

    fun getSettings(): ScanSettings {
        val defaults = ScanSettings.DEFAULT
        return ScanSettings(
            apiPort = prefs.getInt("api_port", defaults.apiPort),
            timeoutMs = prefs.getInt("timeout_ms", defaults.timeoutMs),
            concurrency = prefs.getInt("concurrency", defaults.concurrency),
            autoRefreshSec = prefs.getInt("auto_refresh_sec", defaults.autoRefreshSec),
            customSubnet = prefs.getString("custom_subnet", defaults.customSubnet)?.trim() ?: "",
            pool1Url = prefs.getString("pool1_url", defaults.pool1Url)?.trim() ?: defaults.pool1Url,
            pool1Worker = prefs.getString("pool1_worker", defaults.pool1Worker)?.trim() ?: defaults.pool1Worker,
            pool1Pass = prefs.getString("pool1_pass", defaults.pool1Pass)?.trim() ?: defaults.pool1Pass,
            pool2Url = prefs.getString("pool2_url", defaults.pool2Url)?.trim() ?: defaults.pool2Url,
            pool2Worker = prefs.getString("pool2_worker", defaults.pool2Worker)?.trim() ?: defaults.pool2Worker,
            pool2Pass = prefs.getString("pool2_pass", defaults.pool2Pass)?.trim() ?: defaults.pool2Pass,
            pool3Url = prefs.getString("pool3_url", defaults.pool3Url)?.trim() ?: defaults.pool3Url,
            pool3Worker = prefs.getString("pool3_worker", defaults.pool3Worker)?.trim() ?: defaults.pool3Worker,
            pool3Pass = prefs.getString("pool3_pass", defaults.pool3Pass)?.trim() ?: defaults.pool3Pass
        ).validated()
    }

    fun saveSettings(settings: ScanSettings) {
        val valSettings = settings.validated()
        prefs.edit()
            .putInt("api_port", valSettings.apiPort)
            .putInt("timeout_ms", valSettings.timeoutMs)
            .putInt("concurrency", valSettings.concurrency)
            .putInt("auto_refresh_sec", valSettings.autoRefreshSec)
            .putString("custom_subnet", valSettings.customSubnet)
            .putString("pool1_url", valSettings.pool1Url)
            .putString("pool1_worker", valSettings.pool1Worker)
            .putString("pool1_pass", valSettings.pool1Pass)
            .putString("pool2_url", valSettings.pool2Url)
            .putString("pool2_worker", valSettings.pool2Worker)
            .putString("pool2_pass", valSettings.pool2Pass)
            .putString("pool3_url", valSettings.pool3Url)
            .putString("pool3_worker", valSettings.pool3Worker)
            .putString("pool3_pass", valSettings.pool3Pass)
            .apply()

        _settingsFlow.value = valSettings
    }

    private fun readStoredProfiles(): List<PasswordProfile> {
        val raw = prefs.getString("password_profiles_json", null)
        if (raw.isNullOrBlank()) {
            val defaults = getDefaultProfiles()
            persistProfilesToPrefs(defaults)
            return defaults
        }
        val list = mutableListOf<PasswordProfile>()
        try {
            val array = JSONArray(raw)
            for (i in 0 until array.length()) {
                val obj = array.getJSONObject(i)
                list.add(
                    PasswordProfile(
                        id = obj.optString("id", java.util.UUID.randomUUID().toString()),
                        title = obj.optString("title", "پروفایل"),
                        username = obj.optString("username", "admin"),
                        password = obj.optString("password", "admin")
                    )
                )
            }
        } catch (_: Exception) {}

        return if (list.isEmpty()) {
            val defaults = getDefaultProfiles()
            persistProfilesToPrefs(defaults)
            defaults
        } else {
            list
        }
    }

    private fun getDefaultProfiles(): List<PasswordProfile> = listOf(
        PasswordProfile(
            title = "پیش‌فرض واتس‌ماینر (admin / admin)",
            username = "admin",
            password = "admin"
        ),
        PasswordProfile(
            title = "پیش‌فرض فکتوری (admin / 123456)",
            username = "admin",
            password = "123456"
        )
    )

    private fun persistProfilesToPrefs(profiles: List<PasswordProfile>) {
        val array = JSONArray()
        profiles.forEach { profile ->
            val obj = JSONObject()
            obj.put("id", profile.id)
            obj.put("title", profile.title)
            obj.put("username", profile.username)
            obj.put("password", profile.password)
            array.put(obj)
        }
        prefs.edit().putString("password_profiles_json", array.toString()).apply()
    }

    fun getPasswordProfiles(): List<PasswordProfile> = _profilesFlow.value

    fun savePasswordProfiles(profiles: List<PasswordProfile>) {
        persistProfilesToPrefs(profiles)
        _profilesFlow.value = profiles
    }

    fun addPasswordProfile(profile: PasswordProfile) {
        val current = _profilesFlow.value.toMutableList()
        current.add(profile)
        savePasswordProfiles(current)
    }

    fun deletePasswordProfile(id: String) {
        val current = _profilesFlow.value.filterNot { it.id == id }
        savePasswordProfiles(current)
    }

    fun updatePasswordProfile(profile: PasswordProfile) {
        val current = _profilesFlow.value.map {
            if (it.id == profile.id) profile else it
        }
        savePasswordProfiles(current)
    }
}
