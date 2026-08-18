package com.example.data.network

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.wifi.WifiManager
import android.os.Build
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.net.Inet4Address
import java.net.NetworkInterface

/**
 * اطلاعات ساب‌نت شبکه
 */
data class SubnetInfo(
    val localIp: String = "0.0.0.0",
    val subnetMask: String = "255.255.255.0",
    val subnetCidr: String = "0.0.0.0/24",
    val baseIp: String = "0.0.0.0.",
    val totalHosts: Int = 254,
    val interfaceName: String = "unknown",
    val isWifiConnected: Boolean = false,
    val gateway: String = "",
    val dns1: String = "",
    val dns2: String = ""
) {
    val isValid: Boolean
        get() = localIp != "0.0.0.0" && baseIp.isNotEmpty()

    override fun toString(): String {
        return "SubnetInfo($localIp/$subnetCidr on $interfaceName, hosts=$totalHosts, wifi=$isWifiConnected)"
    }
}

/**
 * شناسایی خودکار ساب‌نت شبکه محلی
 * با پشتیبانی از Android 12+ و fallback های چندگانه
 */
class SubnetDetector(private val appContext: Context) {

    companion object {
        private const val TAG = "SubnetDetector"
        private const val DEFAULT_PREFIX = 24
        private const val DEFAULT_HOSTS = 254

        // پورت‌های رایج ماینر برای probe
        val MINER_PORTS = listOf(4028, 4433, 80, 8080, 8081, 8888)

        // رنج‌های خصوصی IPv4
        private val PRIVATE_RANGES = listOf(
            "192.168.", "10.", "172.16.", "172.17.", "172.18.",
            "172.19.", "172.20.", "172.21.", "172.22.", "172.23.",
            "172.24.", "172.25.", "172.26.", "172.27.", "172.28.",
            "172.29.", "172.30.", "172.31."
        )
    }

    /**
     * دریافت اطلاعات ساب‌نت با اولویت‌بندی روش‌ها
     */
    suspend fun getSubnetInfo(customSubnetOverride: String = ""): SubnetInfo =
        withContext(Dispatchers.IO) {

            // ۱. Custom Override
            if (customSubnetOverride.isNotBlank() && !customSubnetOverride.startsWith("0.0.0.")) {
                parseCustomSubnet(customSubnetOverride)?.let {
                    Log.d(TAG, "Using custom subnet: $it")
                    return@withContext sanitizeSubnetInfo(it)
                }
            }

            // ۲. Android 12+ - LinkProperties (جدیدترین روش)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                getSubnetFromLinkProperties()?.let {
                    Log.d(TAG, "LinkProperties: $it")
                    return@withContext sanitizeSubnetInfo(it)
                }
            }

            // ۳. WifiManager DHCP (Deprecated ولی هنوز کار می‌کند)
            getSubnetFromDhcp()?.let {
                Log.d(TAG, "DHCP: $it")
                return@withContext sanitizeSubnetInfo(it)
            }

            // ۴. NetworkInterface Enumeration
            getSubnetFromNetworkInterfaces()?.let {
                Log.d(TAG, "NetworkInterface: $it")
                return@withContext sanitizeSubnetInfo(it)
            }

            // ۵. Fallback نهایی: رنج پیش‌فرض مودم‌های خانگی و صنعتی (192.168.1.0/24) به جای 0.0.0.0
            Log.w(TAG, "All methods failed, using fallback standard modem subnet 192.168.1.0/24")
            SubnetInfo(
                localIp = "192.168.1.1",
                subnetMask = "255.255.255.0",
                subnetCidr = "192.168.1.0/24",
                baseIp = "192.168.1.",
                totalHosts = DEFAULT_HOSTS,
                interfaceName = "fallback-default",
                isWifiConnected = isNetworkConnected()
            )
        }

    /**
     * اسکن سریع: فقط base IP و تعداد هاست‌ها
     */
    suspend fun getScanRange(customSubnet: String = ""): Pair<String, Int> {
        val info = getSubnetInfo(customSubnet)
        return Pair(info.baseIp, info.totalHosts)
    }

    // ==================== Method 1: Custom Subnet ====================

    private fun parseCustomSubnet(override: String): SubnetInfo? {
        return try {
            val trimmed = override.trim()
            if (!trimmed.contains("/")) return null

            val parts = trimmed.split("/")
            val ip = parts[0].trim()
            val prefix = parts[1].trim().toIntOrNull() ?: DEFAULT_PREFIX

            if (!isValidIpv4(ip)) return null
            if (ip == "0.0.0.0" || ip.startsWith("0.0.0.")) return null
            if (prefix !in 8..30) return null

            val lastDot = ip.lastIndexOf('.')
            if (lastDot == -1) return null

            val base = ip.substring(0, lastDot + 1)
            val totalHosts = calculateHostsForPrefix(prefix)
            val networkAddress = calculateNetworkAddress(ip, prefix)

            SubnetInfo(
                localIp = ip,
                subnetMask = prefixToMask(prefix),
                subnetCidr = "$networkAddress/$prefix",
                baseIp = base,
                totalHosts = totalHosts,
                interfaceName = "Custom",
                isWifiConnected = isNetworkConnected()
            )
        } catch (e: Exception) {
            Log.w(TAG, "Failed to parse custom subnet: $override", e)
            null
        }
    }

    // ==================== Method 2: LinkProperties (API 31+) ====================

    private fun getSubnetFromLinkProperties(): SubnetInfo? {
        return try {
            val cm = appContext.getSystemService(Context.CONNECTIVITY_SERVICE) as? ConnectivityManager
                ?: return null
            val activeNetwork = cm.activeNetwork ?: return null
            val linkProperties = cm.getLinkProperties(activeNetwork) ?: return null

            val linkAddress = linkProperties.linkAddresses.firstOrNull { addr ->
                addr.address is Inet4Address && !addr.address.isLoopbackAddress
            } ?: return null

            val inet4 = linkAddress.address as Inet4Address
            val hostAddress = inet4.hostAddress ?: return null
            val prefix = linkAddress.prefixLength

            // فیلتر: فقط رنج‌های خصوصی
            if (!isPrivateAddress(hostAddress)) return null

            val lastDot = hostAddress.lastIndexOf('.')
            if (lastDot == -1) return null

            val baseIp = hostAddress.substring(0, lastDot + 1)
            val networkAddress = calculateNetworkAddress(hostAddress, prefix)
            val gateway = linkProperties.routes.firstOrNull { it.isDefaultRoute }
                ?.gateway?.hostAddress ?: ""
            val dnsServers = linkProperties.dnsServers.map { it.hostAddress ?: "" }

            SubnetInfo(
                localIp = hostAddress,
                subnetMask = prefixToMask(prefix),
                subnetCidr = "$networkAddress/$prefix",
                baseIp = baseIp,
                totalHosts = calculateHostsForPrefix(prefix),
                interfaceName = "LinkProperties",
                isWifiConnected = isNetworkConnected(),
                gateway = gateway,
                dns1 = dnsServers.getOrElse(0) { "" },
                dns2 = dnsServers.getOrElse(1) { "" }
            )
        } catch (e: Exception) {
            Log.d(TAG, "LinkProperties failed: ${e.message}")
            null
        }
    }

    // ==================== Method 3: WifiManager DHCP ====================

    @Suppress("DEPRECATION")
    private fun getSubnetFromDhcp(): SubnetInfo? {
        return try {
            val wifiManager = appContext.applicationContext
                .getSystemService(Context.WIFI_SERVICE) as? WifiManager ?: return null

            val dhcpInfo = wifiManager.dhcpInfo ?: return null
            if (dhcpInfo.ipAddress == 0) return null

            // dhcpInfo همیشه little-endian است
            val ipInt = dhcpInfo.ipAddress
            val ipBytes = byteArrayOf(
                (ipInt and 0xFF).toByte(),
                ((ipInt shr 8) and 0xFF).toByte(),
                ((ipInt shr 16) and 0xFF).toByte(),
                ((ipInt shr 24) and 0xFF).toByte()
            )
            val localIp = ipBytes.joinToString(".") { it.toInt().and(0xFF).toString() }

            // فیلتر: فقط رنج‌های خصوصی
            if (!isPrivateAddress(localIp)) return null

            val maskInt = dhcpInfo.netmask
            val prefix = if (maskInt != 0) {
                Integer.bitCount(maskInt).coerceIn(8, 30)
            } else {
                DEFAULT_PREFIX
            }

            val maskBytes = byteArrayOf(
                (maskInt and 0xFF).toByte(),
                ((maskInt shr 8) and 0xFF).toByte(),
                ((maskInt shr 16) and 0xFF).toByte(),
                ((maskInt shr 24) and 0xFF).toByte()
            )
            val subnetMask = maskBytes.joinToString(".") { it.toInt().and(0xFF).toString() }

            val networkIp = calculateNetworkAddress(localIp, prefix)

            val gatewayBytes = byteArrayOf(
                (dhcpInfo.gateway and 0xFF).toByte(),
                ((dhcpInfo.gateway shr 8) and 0xFF).toByte(),
                ((dhcpInfo.gateway shr 16) and 0xFF).toByte(),
                ((dhcpInfo.gateway shr 24) and 0xFF).toByte()
            )
            val gateway = gatewayBytes.joinToString(".") { it.toInt().and(0xFF).toString() }

            val dns1Bytes = byteArrayOf(
                (dhcpInfo.dns1 and 0xFF).toByte(),
                ((dhcpInfo.dns1 shr 8) and 0xFF).toByte(),
                ((dhcpInfo.dns1 shr 16) and 0xFF).toByte(),
                ((dhcpInfo.dns1 shr 24) and 0xFF).toByte()
            )
            val dns2Bytes = byteArrayOf(
                (dhcpInfo.dns2 and 0xFF).toByte(),
                ((dhcpInfo.dns2 shr 8) and 0xFF).toByte(),
                ((dhcpInfo.dns2 shr 16) and 0xFF).toByte(),
                ((dhcpInfo.dns2 shr 24) and 0xFF).toByte()
            )

            val lastDot = localIp.lastIndexOf('.')
            val baseIp = if (lastDot != -1) localIp.substring(0, lastDot + 1) else ""

            SubnetInfo(
                localIp = localIp,
                subnetMask = subnetMask,
                subnetCidr = "$networkIp/$prefix",
                baseIp = baseIp,
                totalHosts = calculateHostsForPrefix(prefix),
                interfaceName = "wlan0 (DHCP)",
                isWifiConnected = isNetworkConnected(),
                gateway = gateway,
                dns1 = dns1Bytes.joinToString(".") { it.toInt().and(0xFF).toString() },
                dns2 = dns2Bytes.joinToString(".") { it.toInt().and(0xFF).toString() }
            )
        } catch (e: Exception) {
            Log.d(TAG, "DHCP method failed: ${e.message}")
            null
        }
    }

    // ==================== Method 4: NetworkInterface Enumeration ====================

    private fun getSubnetFromNetworkInterfaces(): SubnetInfo? {
        return try {
            val interfaces = NetworkInterface.getNetworkInterfaces() ?: return null
            val candidates = mutableListOf<SubnetInfo>()

            while (interfaces.hasMoreElements()) {
                val networkInterface = interfaces.nextElement()

                // Skip: loopback, down, virtual, VPN
                if (networkInterface.isLoopback) continue
                if (!networkInterface.isUp) continue
                if (networkInterface.isVirtual) continue
                val name = networkInterface.name ?: ""
                if (name.startsWith("tun") || name.startsWith("ppp")) continue

                for (interfaceAddr in networkInterface.interfaceAddresses) {
                    val addr = interfaceAddr.address
                    if (addr !is Inet4Address) continue
                    if (addr.isLoopbackAddress) continue

                    val hostAddress = addr.hostAddress ?: continue
                    if (!isPrivateAddress(hostAddress)) continue

                    val prefix = interfaceAddr.networkPrefixLength.toInt().coerceIn(8, 30)
                    val lastDot = hostAddress.lastIndexOf('.')
                    if (lastDot == -1) continue

                    val baseIp = hostAddress.substring(0, lastDot + 1)
                    val networkAddress = calculateNetworkAddress(hostAddress, prefix)

                    candidates.add(
                        SubnetInfo(
                            localIp = hostAddress,
                            subnetMask = prefixToMask(prefix),
                            subnetCidr = "$networkAddress/$prefix",
                            baseIp = baseIp,
                            totalHosts = calculateHostsForPrefix(prefix),
                            interfaceName = name,
                            isWifiConnected = isNetworkConnected()
                        )
                    )
                }
            }

            // اولویت: wlan > eth > بقیه
            candidates.firstOrNull { it.interfaceName.startsWith("wlan") }
                ?: candidates.firstOrNull { it.interfaceName.startsWith("eth") }
                ?: candidates.firstOrNull()

        } catch (e: Exception) {
            Log.d(TAG, "NetworkInterface enumeration failed: ${e.message}")
            null
        }
    }

    // ==================== Utility Functions ====================

    /**
     * محاسبه تعداد هاست‌های قابل اسکن
     */
    fun calculateHostsForPrefix(prefix: Int): Int {
        return when {
            prefix >= 30 -> 2
            prefix == 29 -> 6
            prefix == 28 -> 14
            prefix == 27 -> 30
            prefix == 26 -> 62
            prefix == 25 -> 126
            prefix == 24 -> 254
            prefix == 23 -> 510
            prefix == 22 -> 1022
            prefix == 21 -> 2046
            prefix == 20 -> 4094
            prefix == 19 -> 8190
            prefix == 18 -> 16382
            prefix == 17 -> 32766
            prefix == 16 -> 65534
            prefix < 16 -> 65534.coerceAtMost(65534)
            else -> DEFAULT_HOSTS
        }
    }

    /**
     * تبدیل prefix به subnet mask
     */
    fun prefixToMask(prefix: Int): String {
        val maskInt = if (prefix == 0) 0 else (-1 shl (32 - prefix))
        return byteArrayOf(
            ((maskInt shr 24) and 0xFF).toByte(),
            ((maskInt shr 16) and 0xFF).toByte(),
            ((maskInt shr 8) and 0xFF).toByte(),
            (maskInt and 0xFF).toByte()
        ).joinToString(".") { it.toInt().and(0xFF).toString() }
    }

    /**
     * پاکسازی و تصحیح اطلاعات زیرشبکه (جلوگیری از آی‌پی‌های 0.0.0.0 در زمان اتصال وای‌فای)
     */
    private fun sanitizeSubnetInfo(info: SubnetInfo): SubnetInfo {
        if (info.localIp == "0.0.0.0" || !isValidIpv4(info.localIp)) {
            return info
        }

        val lastDot = info.localIp.lastIndexOf('.')
        if (lastDot == -1) return info

        val baseIp = info.localIp.substring(0, lastDot + 1)
        val prefix = parsePrefixFromCidr(info.subnetCidr) ?: DEFAULT_PREFIX
        val networkAddress = calculateNetworkAddress(info.localIp, prefix)

        return info.copy(
            subnetCidr = "$networkAddress/$prefix",
            baseIp = baseIp
        )
    }

    private fun parsePrefixFromCidr(cidr: String): Int? {
        val parts = cidr.split("/")
        return if (parts.size == 2) parts[1].trim().toIntOrNull() else null
    }

    /**
     * محاسبه آدرس شبکه از IP و prefix
     */
    private fun calculateNetworkAddress(ip: String, prefix: Int): String {
        return try {
            val parts = ip.split(".").map { it.toIntOrNull() ?: return ip }
            if (parts.size != 4) return ip

            if (prefix == 24) {
                return "${parts[0]}.${parts[1]}.${parts[2]}.0"
            }
            if (prefix == 16) {
                return "${parts[0]}.${parts[1]}.0.0"
            }
            if (prefix == 8) {
                return "${parts[0]}.0.0.0"
            }

            val ipInt = ((parts[0] and 0xFF) shl 24) or
                        ((parts[1] and 0xFF) shl 16) or
                        ((parts[2] and 0xFF) shl 8) or
                        (parts[3] and 0xFF)

            val maskInt = if (prefix == 0) 0 else (-1 shl (32 - prefix))
            val netInt = ipInt and maskInt

            val p0 = (netInt ushr 24) and 0xFF
            val p1 = (netInt ushr 16) and 0xFF
            val p2 = (netInt ushr 8) and 0xFF
            val p3 = netInt and 0xFF

            "$p0.$p1.$p2.$p3"
        } catch (e: Exception) {
            ip
        }
    }

    /**
     * بررسی اینکه آیا IP در رنج خصوصی است
     */
    fun isPrivateAddress(ip: String): Boolean {
        return PRIVATE_RANGES.any { ip.startsWith(it) }
    }

    /**
     * اعتبارسنجی فرمت IPv4
     */
    fun isValidIpv4(ip: String): Boolean {
        val parts = ip.split(".")
        if (parts.size != 4) return false
        return parts.all { part ->
            val num = part.toIntOrNull() ?: return false
            num in 0..255 && part == num.toString()
        }
    }

    /**
     * بررسی اتصال شبکه
     */
    fun isNetworkConnected(): Boolean {
        return try {
            val cm = appContext.getSystemService(Context.CONNECTIVITY_SERVICE) as? ConnectivityManager
                ?: return false
            val activeNetwork = cm.activeNetwork ?: return false
            val capabilities = cm.getNetworkCapabilities(activeNetwork) ?: return false
            capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) &&
                (capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) ||
                 capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET))
        } catch (e: Exception) {
            false
        }
    }

    /**
     * بررسی اینکه آیا یک IP در ساب‌نت فعلی است
     */
    suspend fun isInCurrentSubnet(ip: String, subnetInfo: SubnetInfo? = null): Boolean {
        val info = subnetInfo ?: getSubnetInfo()
        if (!info.isValid) return false

        return try {
            val parts = ip.split(".")
            if (parts.size != 4) return false
            ip.startsWith(info.baseIp)
        } catch (e: Exception) {
            false
        }
    }
}
