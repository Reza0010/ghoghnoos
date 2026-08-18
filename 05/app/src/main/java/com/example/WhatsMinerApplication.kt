package com.example

import android.app.Application
import com.example.di.AppContainer

class WhatsMinerApplication : Application() {

    lateinit var appContainer: AppContainer
        private set

    override fun onCreate() {
        super.onCreate()
        appContainer = AppContainer.getInstance(this)
    }

    override fun onTerminate() {
        super.onTerminate()
        appContainer.cleanup()
    }
}
