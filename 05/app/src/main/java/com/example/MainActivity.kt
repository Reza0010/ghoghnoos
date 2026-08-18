package com.example

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.core.view.WindowCompat
import com.example.ui.navigation.MainAppNavigation
import com.example.ui.theme.WhatsMinerScannerTheme

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ✅ Edge-to-Edge قبل از setContent
        enableEdgeToEdge()
        WindowCompat.setDecorFitsSystemWindows(window, false)

        // ✅ دسترسی به AppContainer از Application
        val appContainer = (application as WhatsMinerApplication).appContainer

        setContent {
            WhatsMinerScannerTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    MainAppNavigation(appContainer = appContainer)
                }
            }
        }
    }
}
