package com.example.ui.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.example.data.repository.MinerRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

class DeviceDetailsViewModel(
    private val repository: MinerRepository,
    val ipAddress: String
) : ViewModel() {

    val minerState = repository.getMinerByIp(ipAddress)

    private val _isRefreshing = MutableStateFlow(false)
    val isRefreshing: StateFlow<Boolean> = _isRefreshing.asStateFlow()

    private var pollingJob: Job? = null

    init {
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

                // 🚀 فقط اگر ماینر آنلاین است refresh کن
                val currentMiner = repository.getMinerByIpSync(ipAddress)
                if (currentMiner?.isOnline == true) {
                    repository.refreshSingleMiner(ipAddress)
                }
            }
        }
    }

    fun refreshMiner() {
        viewModelScope.launch(Dispatchers.IO) {
            _isRefreshing.value = true
            try {
                repository.refreshSingleMiner(ipAddress)
            } finally {
                _isRefreshing.value = false
            }
        }
    }

    fun deleteMiner() {
        viewModelScope.launch {
            repository.deleteMiner(ipAddress)
        }
    }

    fun saveAlias(alias: String) {
        viewModelScope.launch {
            repository.saveAlias(ipAddress, alias.trim())
        }
    }

    class Factory(
        private val repository: MinerRepository,
        private val ipAddress: String
    ) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            return DeviceDetailsViewModel(repository, ipAddress) as T
        }
    }
}
