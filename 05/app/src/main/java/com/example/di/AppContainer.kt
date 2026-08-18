package com.example.di

import android.content.Context
import com.example.data.local.AppDatabase
import com.example.data.local.SettingsRepository
import com.example.data.network.SubnetDetector
import com.example.data.network.WhatsMinerApiClientImpl
import com.example.data.network.MinerApiClient
import com.example.data.repository.MinerRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel

/**
 * Manual Dependency Injection Container
 *
 * ⚠️ مهم: این کلاس باید در Application class ساخته شود، نه Activity
 * تا در configuration changes و process death زنده بماند.
 */
class AppContainer(context: Context) {

    val appContext: Context = context.applicationContext

    // ==================== Coroutine Scope ====================

    /**
     * Scope اصلی اپلیکیشن - در onDestroy Application cancel می‌شود
     */
    private val applicationScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    // ==================== Core Services ====================

    val settingsRepository: SettingsRepository by lazy {
        SettingsRepository(appContext)
    }

    val subnetDetector: SubnetDetector by lazy {
        SubnetDetector(appContext)
    }

    val minerApiClient: MinerApiClient by lazy {
        WhatsMinerApiClientImpl(
            dispatcher = Dispatchers.IO,
            enableLogging = true
        )
    }

    // ==================== Repositories ====================

    val minerRepository: MinerRepository by lazy {
        MinerRepository(appContext)
    }

    // ==================== Lifecycle ====================

    /**
     * باید در Application.onDestroy() صدا زده شود
     */
    fun cleanup() {
        applicationScope.cancel()
        minerRepository.cleanup()
        AppDatabase.destroyDatabase()
    }

    companion object {
        @Volatile
        private var INSTANCE: AppContainer? = null

        /**
         * Singleton access - برای استفاده در Application
         */
        fun getInstance(context: Context): AppContainer {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: AppContainer(context.applicationContext).also {
                    INSTANCE = it
                }
            }
        }
    }
}
