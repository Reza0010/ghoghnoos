package com.example.ui.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.example.data.network.SubnetInfo
import com.example.data.repository.MinerRepository
import com.example.data.repository.ScanProgressState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.launch

class ScanViewModel(private val repository: MinerRepository) : ViewModel() {

    val scanState: StateFlow<ScanProgressState> = repository.scanState
    val allMiners = repository.allMiners
    val minerCount = repository.allMiners.map { it.size }

    private val _targetSubnetInput = MutableStateFlow("")
    val targetSubnetInput: StateFlow<String> = _targetSubnetInput.asStateFlow()

    private val _detectedSubnetInfo = MutableStateFlow(SubnetInfo())
    val detectedSubnetInfo: StateFlow<SubnetInfo> = _detectedSubnetInfo.asStateFlow()

    init {
        autoDetectAndStartScan()
    }

    fun autoDetectAndStartScan() {
        viewModelScope.launch {
            val info = repository.getSubnetInfo()
            _detectedSubnetInfo.value = info
            _targetSubnetInput.value = info.subnetCidr
            
            if (!scanState.value.isScanning) {
                startScan()
            }
        }
    }

    fun refreshAutoDetectedSubnet() {
        autoDetectAndStartScan()
    }

    fun onSubnetInputChange(input: String) {
        _targetSubnetInput.value = input
    }

    fun startScan() {
        repository.startSubnetScan(_targetSubnetInput.value.trim())
    }

    fun stopScan() {
        repository.stopScan()
    }

    class Factory(private val repository: MinerRepository) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            return ScanViewModel(repository) as T
        }
    }
}

