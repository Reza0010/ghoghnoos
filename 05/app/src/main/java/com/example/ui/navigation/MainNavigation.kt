package com.example.ui.navigation

import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Memory
import androidx.compose.material.icons.filled.Radar
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Badge
import androidx.compose.material3.BadgedBox
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import androidx.navigation.navDeepLink
import com.example.di.AppContainer
import com.example.ui.screens.AboutScreen
import com.example.ui.screens.DeviceDetailsScreen
import com.example.ui.screens.DeviceListScreen
import com.example.ui.screens.HomeScreen
import com.example.ui.screens.ScanScreen
import com.example.ui.screens.SettingsScreen
import com.example.ui.screens.SplashScreen
import com.example.ui.theme.CyberCyan
import com.example.ui.theme.DarkCardBorder
import com.example.ui.theme.DarkSurface
import com.example.ui.theme.TextMuted
import com.example.ui.theme.TextSecondary
import com.example.ui.viewmodels.DeviceDetailsViewModel
import com.example.ui.viewmodels.DeviceListViewModel
import com.example.ui.viewmodels.HomeViewModel
import com.example.ui.viewmodels.ScanViewModel
import com.example.ui.viewmodels.SettingsViewModel

// ==================== Route Definitions ====================

sealed class Screen(
    val route: String,
    val title: String,
    val icon: ImageVector? = null
) {
    data object Splash : Screen("splash", "اسپلش")
    data object Home : Screen("home", "خانه", Icons.Default.Home)
    data object Scan : Screen("scan", "اسکن", Icons.Default.Radar)
    data object DeviceList : Screen("device_list", "ماینرها", Icons.Default.Memory)
    data object DeviceDetails : Screen("device_details/{ipAddress}", "جزئیات") {
        fun createRoute(ipAddress: String): String = "device_details/$ipAddress"
        const val ARG_IP_ADDRESS = "ipAddress"
    }
    data object Settings : Screen("settings", "تنظیمات", Icons.Default.Settings)
    data object About : Screen("about", "درباره", Icons.Default.Info)
}

val BOTTOM_NAV_ROUTES = setOf(
    Screen.Home.route,
    Screen.Scan.route,
    Screen.DeviceList.route,
    Screen.Settings.route,
    Screen.About.route
)

val BOTTOM_NAV_SCREENS = listOf(
    Screen.Home,
    Screen.Scan,
    Screen.DeviceList,
    Screen.Settings,
    Screen.About
)

// ==================== Navigation Animation ====================

private const val NAV_ANIMATION_DURATION = 300

// ==================== Main Navigation ====================

@Composable
fun MainAppNavigation(appContainer: AppContainer) {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    val repository = appContainer.minerRepository

    val homeViewModel: HomeViewModel = viewModel(
        factory = HomeViewModel.Factory(repository)
    )

    val dashboardState by homeViewModel.dashboardState.collectAsState()
    val activeCount = dashboardState.activeCount

    val showBottomBar = currentRoute != null && currentRoute in BOTTOM_NAV_ROUTES

    Scaffold(
        bottomBar = {
            if (showBottomBar) {
                NavigationBar(
                    containerColor = DarkSurface,
                    tonalElevation = 8.dp,
                    modifier = Modifier.testTag("bottom_navigation_bar")
                ) {
                    BOTTOM_NAV_SCREENS.forEach { screen ->
                        val selected = currentRoute == screen.route
                        val icon = screen.icon

                        NavigationBarItem(
                            selected = selected,
                            onClick = {
                                if (currentRoute != screen.route) {
                                    navController.navigateToTopLevel(screen.route)
                                }
                            },
                            icon = {
                                if (icon != null) {
                                    if (screen is Screen.DeviceList && activeCount > 0) {
                                        BadgedBox(
                                            badge = {
                                                Badge(containerColor = CyberCyan) {
                                                    Text("$activeCount")
                                                }
                                            }
                                        ) {
                                            Icon(
                                                imageVector = icon,
                                                contentDescription = screen.title
                                            )
                                        }
                                    } else {
                                        Icon(
                                            imageVector = icon,
                                            contentDescription = screen.title
                                        )
                                    }
                                }
                            },
                            label = { Text(screen.title) },
                            colors = NavigationBarItemDefaults.colors(
                                selectedIconColor = CyberCyan,
                                selectedTextColor = CyberCyan,
                                indicatorColor = DarkCardBorder,
                                unselectedIconColor = TextMuted,
                                unselectedTextColor = TextSecondary
                            ),
                            modifier = Modifier.testTag("nav_item_${screen.route}")
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Splash.route,
            modifier = Modifier.padding(innerPadding),
            enterTransition = {
                fadeIn(animationSpec = tween(NAV_ANIMATION_DURATION))
            },
            exitTransition = {
                fadeOut(animationSpec = tween(NAV_ANIMATION_DURATION))
            },
            popEnterTransition = {
                fadeIn(animationSpec = tween(NAV_ANIMATION_DURATION))
            },
            popExitTransition = {
                fadeOut(animationSpec = tween(NAV_ANIMATION_DURATION))
            }
        ) {
            // ==================== Splash ====================
            composable(
                route = Screen.Splash.route,
                enterTransition = { fadeIn() },
                exitTransition = { fadeOut() }
            ) {
                SplashScreen(
                    onSplashFinished = {
                        navController.navigate(Screen.Home.route) {
                            popUpTo(Screen.Splash.route) { inclusive = true }
                        }
                    }
                )
            }

            // ==================== Home ====================
            composable(Screen.Home.route) {
                HomeScreen(
                    viewModel = homeViewModel,
                    onNavigateToScan = {
                        navController.navigateToTopLevel(Screen.Scan.route)
                    },
                    onNavigateToDeviceList = {
                        navController.navigateToTopLevel(Screen.DeviceList.route)
                    },
                    onNavigateToDeviceDetails = { ip ->
                        navController.navigate(Screen.DeviceDetails.createRoute(ip))
                    }
                )
            }

            // ==================== Scan ====================
            composable(Screen.Scan.route) {
                val scanViewModel: ScanViewModel = viewModel(
                    factory = ScanViewModel.Factory(repository)
                )
                ScanScreen(
                    viewModel = scanViewModel,
                    onNavigateToDeviceList = {
                        navController.navigateToTopLevel(Screen.DeviceList.route)
                    }
                )
            }

            // ==================== Device List ====================
            composable(Screen.DeviceList.route) {
                val deviceListViewModel: DeviceListViewModel = viewModel(
                    factory = DeviceListViewModel.Factory(repository)
                )
                DeviceListScreen(
                    viewModel = deviceListViewModel,
                    onNavigateToDeviceDetails = { ip ->
                        navController.navigate(Screen.DeviceDetails.createRoute(ip))
                    }
                )
            }

            // ==================== Device Details ====================
            composable(
                route = Screen.DeviceDetails.route,
                arguments = listOf(
                    navArgument(Screen.DeviceDetails.ARG_IP_ADDRESS) {
                        type = NavType.StringType
                    }
                ),
                deepLinks = listOf(
                    navDeepLink {
                        uriPattern = "whatsminer://device/{ipAddress}"
                    }
                )
            ) { backStackEntry ->
                val ipAddress = backStackEntry.arguments
                    ?.getString(Screen.DeviceDetails.ARG_IP_ADDRESS) ?: ""

                val detailsViewModel: DeviceDetailsViewModel = viewModel(
                    key = "device_details_$ipAddress",
                    factory = DeviceDetailsViewModel.Factory(repository, ipAddress)
                )

                DeviceDetailsScreen(
                    viewModel = detailsViewModel,
                    onNavigateBack = { navController.popBackStack() }
                )
            }

            // ==================== Settings ====================
            composable(Screen.Settings.route) {
                val settingsViewModel: SettingsViewModel = viewModel(
                    factory = SettingsViewModel.Factory(repository)
                )
                SettingsScreen(viewModel = settingsViewModel)
            }

            // ==================== About ====================
            composable(Screen.About.route) {
                AboutScreen()
            }
        }
    }
}

// ==================== Navigation Extensions ====================

private fun NavHostController.navigateToTopLevel(route: String) {
    navigate(route) {
        popUpTo(graph.findStartDestination().id) {
            saveState = true
        }
        launchSingleTop = true
        restoreState = true
    }
}
