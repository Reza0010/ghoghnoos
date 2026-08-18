package com.example.ui.screens

import android.content.Intent
import android.net.Uri
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.expandVertically
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccessTime
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.Calculate
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material.icons.filled.ElectricalServices
import androidx.compose.material.icons.filled.ExpandLess
import androidx.compose.material.icons.filled.ExpandMore
import androidx.compose.material.icons.filled.FlashOn
import androidx.compose.material.icons.filled.HelpOutline
import androidx.compose.material.icons.filled.Inbox
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Language
import androidx.compose.material.icons.filled.LocalShipping
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Memory
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material.icons.filled.Psychology
import androidx.compose.material.icons.filled.Public
import androidx.compose.material.icons.filled.QrCodeScanner
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.SupportAgent
import androidx.compose.material.icons.filled.VerifiedUser
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.BuildConfig
import com.example.R
import com.example.ui.theme.CyberAmber
import com.example.ui.theme.CyberCyan
import com.example.ui.theme.CyberEmerald
import com.example.ui.theme.CyberPurple
import com.example.ui.theme.DarkCardBorder
import com.example.ui.theme.DarkSurface
import com.example.ui.theme.DarkSurfaceVariant
import com.example.ui.theme.TextMuted
import com.example.ui.theme.TextPrimary
import com.example.ui.theme.TextSecondary
import java.util.Calendar

@Composable
fun AboutScreen() {
    val context = LocalContext.current
    val uriHandler = LocalUriHandler.current

    val goldGradient = Brush.horizontalGradient(
        listOf(
            Color(0xFFFFD700),
            Color(0xFFFFA500),
            CyberAmber
        )
    )

    val isOpenNow = remember { checkIsCenterOpen() }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .windowInsetsPadding(WindowInsets.statusBars)
            .windowInsetsPadding(WindowInsets.navigationBars)
            .padding(horizontal = 16.dp)
            .testTag("about_screen")
            .semantics { contentDescription = "صفحه درباره مرکز تعمیرات Fix Board" },
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // ==================== Top Hero & Brand Header ====================
        item(key = "hero") {
            Spacer(modifier = Modifier.height(8.dp))
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkSurface),
                shape = RoundedCornerShape(24.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(
                        1.5.dp,
                        goldGradient,
                        RoundedCornerShape(24.dp)
                    )
                    .testTag("fixboard_hero_card")
            ) {
                Column(
                    modifier = Modifier.padding(20.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    // Logo Image with Glowing Ring
                    Box(
                        modifier = Modifier
                            .size(110.dp)
                            .background(DarkSurfaceVariant, CircleShape)
                            .border(3.dp, goldGradient, CircleShape)
                            .padding(4.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Image(
                            painter = painterResource(id = R.drawable.ic_fixboard_logo),
                            contentDescription = "لوگو مرکز تعمیرات Fix Board",
                            contentScale = ContentScale.Fit,
                            modifier = Modifier
                                .fillMaxSize()
                                .clip(CircleShape)
                        )
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    Text(
                        text = "🛠 مرکز تخصصی تعمیرات ماینر | Fix Board",
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.Bold,
                            fontSize = 18.sp
                        ),
                        color = Color(0xFFFFD700),
                        textAlign = TextAlign.Center
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Surface(
                        color = Color(0xFFFFA500).copy(alpha = 0.15f),
                        shape = RoundedCornerShape(20.dp),
                        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFFFA500).copy(alpha = 0.4f))
                    ) {
                        Text(
                            text = "مرکز عیب‌یابی و تخصصی‌ترین خدمات سخت‌افزاری ماینینگ",
                            style = MaterialTheme.typography.labelSmall,
                            color = Color(0xFFFFD700),
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Medium,
                            modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp)
                        )
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    Text(
                        text = "ما در این مجموعه با سال‌ها تجربه تخصصی و بهره‌گیری از تجهیزات پیشرفته، تمامی خدمات مربوط به عیب‌یابی و تعمیرات تخصصی انواع دستگاه‌های ماینر را با ضمانت ارائه می‌دهیم.",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                        textAlign = TextAlign.Center,
                        lineHeight = 22.sp
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    // Primary Action: Fast Call Button
                    Button(
                        onClick = {
                            try {
                                val intent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:09120084198"))
                                context.startActivity(intent)
                            } catch (_: Exception) {}
                        },
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFFFFD700),
                            contentColor = Color.Black
                        ),
                        shape = RoundedCornerShape(12.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Icon(
                            imageVector = Icons.Default.Call,
                            contentDescription = null,
                            modifier = Modifier.size(18.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "تماس و مشاوره رایگان: ۰۹۱۲۰۰۸۴۱۹۸",
                            fontWeight = FontWeight.Bold,
                            fontSize = 14.sp
                        )
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    // NEW ACTION 1: Quick Price Estimate with Photo via Telegram
                    Button(
                        onClick = {
                            try {
                                uriHandler.openUri("http://t.me/fixb_051_admin")
                            } catch (_: Exception) {}
                        },
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF0088CC), // Telegram Cyan Blue
                            contentColor = Color.White
                        ),
                        shape = RoundedCornerShape(12.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Icon(
                            imageVector = Icons.Default.CameraAlt,
                            contentDescription = null,
                            modifier = Modifier.size(18.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "📸 استعلام قیمت سریع با ارسال عکس برد",
                            fontWeight = FontWeight.Bold,
                            fontSize = 13.sp
                        )
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    // NEW ACTION 3: Share Digital Business Card
                    OutlinedButton(
                        onClick = {
                            try {
                                val shareIntent = Intent(Intent.ACTION_SEND).apply {
                                    type = "text/plain"
                                    putExtra(
                                        Intent.EXTRA_TEXT,
                                        """
                                        🛠 مرکز تخصصی تعمیرات ماینر | Fix Board
                                        
                                        ⚙️ ارائه خدمات تخصصی عیب‌یابی و تعمیرات:
                                        • انواع هشبرد (Antminer, Whatsminer, ...)
                                        • کنترل‌برد و تعویض آی‌سی‌ها
                                        • پاورهای صنعتی و ماینر با تست زیر بار
                                        
                                        🌟 با ضمانت کیفیت، تست کامل و تحویل سریع
                                        
                                        🌐 وب‌سایت: https://fixb.ir
                                        📞 تماس و مشاوره: 09120084198
                                        💬 تلگرام پشتیبانی: https://t.me/fixb_051_admin
                                        📷 اینستاگرام: https://www.instagram.com/fixb_051
                                        """.trimIndent()
                                    )
                                }
                                context.startActivity(Intent.createChooser(shareIntent, "اشتراک‌گذاری کارت ویزیت Fix Board"))
                            } catch (_: Exception) {}
                        },
                        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFFFD700).copy(alpha = 0.6f)),
                        shape = RoundedCornerShape(12.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Icon(
                            imageVector = Icons.Default.Share,
                            contentDescription = null,
                            tint = Color(0xFFFFD700),
                            modifier = Modifier.size(18.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "اشتراک‌گذاری کارت ویزیت آنلاین",
                            color = Color(0xFFFFD700),
                            fontWeight = FontWeight.Bold,
                            fontSize = 13.sp
                        )
                    }
                }
            }
        }

        // ==================== NEW ACTION 4: Working Hours & Online Status Badge ====================
        item(key = "business_hours") {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkSurface),
                shape = RoundedCornerShape(20.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(1.dp, DarkCardBorder, RoundedCornerShape(20.dp))
            ) {
                Column(
                    modifier = Modifier.padding(18.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                imageVector = Icons.Default.AccessTime,
                                contentDescription = null,
                                tint = CyberCyan
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = "ساعات کاری و پاسخگویی",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.onBackground
                            )
                        }

                        // Live Online Badge
                        Surface(
                            color = if (isOpenNow) CyberEmerald.copy(alpha = 0.15f) else Color.Red.copy(alpha = 0.15f),
                            shape = RoundedCornerShape(20.dp),
                            border = androidx.compose.foundation.BorderStroke(
                                1.dp,
                                if (isOpenNow) CyberEmerald else Color.Red
                            )
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(8.dp)
                                        .background(if (isOpenNow) CyberEmerald else Color.Red, CircleShape)
                                )
                                Spacer(modifier = Modifier.width(6.dp))
                                Text(
                                    text = if (isOpenNow) "هم‌اکنون آنلاین و فعال" else "خارج از ساعات کاری",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = if (isOpenNow) CyberEmerald else Color.Red,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 11.sp
                                )
                            }
                        }
                    }

                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(DarkSurfaceVariant, RoundedCornerShape(12.dp))
                            .padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = "شنبه تا چهارشنبه:",
                                style = MaterialTheme.typography.bodyMedium,
                                color = TextSecondary
                            )
                            Text(
                                text = "۹:۰۰ الی ۱۸:۰۰",
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.onBackground,
                                fontFamily = FontFamily.Monospace
                            )
                        }

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = "پنج‌شنبه‌ها:",
                                style = MaterialTheme.typography.bodyMedium,
                                color = TextSecondary
                            )
                            Text(
                                text = "۹:۰۰ الی ۱۴:۰۰",
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.onBackground,
                                fontFamily = FontFamily.Monospace
                            )
                        }

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = "جمعه‌ها و ایام تعطیل:",
                                style = MaterialTheme.typography.bodyMedium,
                                color = TextSecondary
                            )
                            Text(
                                text = "پشتیبانی پیامکی/تلگرام",
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.Bold,
                                color = CyberAmber
                            )
                        }
                    }
                }
            }
        }

        // ==================== Why Fix Board? (مزایای رقابتی) ====================
        item(key = "why_fixboard") {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkSurface),
                shape = RoundedCornerShape(20.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(1.dp, DarkCardBorder, RoundedCornerShape(20.dp))
            ) {
                Column(
                    modifier = Modifier.padding(18.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.Star,
                            contentDescription = null,
                            tint = Color(0xFFFFD700)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "چرا Fix Board؟",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onBackground
                        )
                    }

                    FeatureRow(
                        icon = Icons.Default.VerifiedUser,
                        iconTint = CyberAmber,
                        title = "تخصص و تجربه",
                        description = "تیم فنی مجرب و باسابقه در حوزه تخصصی سخت‌افزار ماینینگ"
                    )

                    FeatureRow(
                        icon = Icons.Default.FlashOn,
                        iconTint = CyberCyan,
                        title = "تحویل سریع",
                        description = "تعمیر و عیب‌یابی در کوتاه‌ترین زمان ممکن برای کاهش زمان خواب دستگاه"
                    )

                    FeatureRow(
                        icon = Icons.Default.Shield,
                        iconTint = CyberEmerald,
                        title = "ضمانت خدمات",
                        description = "تست کامل قطعات قبل از ارسال و ارائه ضمانت عملکرد"
                    )

                    FeatureRow(
                        icon = Icons.Default.LocalShipping,
                        iconTint = CyberPurple,
                        title = "پذیرش از سراسر کشور",
                        description = "دریافت و ارسال ایمن دستگاه‌ها از تمامی نقاط ایران"
                    )

                    FeatureRow(
                        icon = Icons.Default.Search,
                        iconTint = Color(0xFFFFD700),
                        title = "شفافیت کامل",
                        description = "اعلام دقیق هزینه‌ها و مشکلات پیش از شروع فرآیند تعمیر"
                    )
                }
            }
        }

        // ==================== Specialized Services ====================
        item(key = "services") {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkSurface),
                shape = RoundedCornerShape(20.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(1.dp, DarkCardBorder, RoundedCornerShape(20.dp))
            ) {
                Column(
                    modifier = Modifier.padding(18.dp),
                    verticalArrangement = Arrangement.spacedBy(14.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.Build,
                            contentDescription = null,
                            tint = CyberCyan
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "⚙️ خدمات تخصصی مجموعه Fix Board",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onBackground
                        )
                    }

                    ServiceItem(
                        icon = Icons.Default.Memory,
                        iconTint = CyberAmber,
                        title = "تعمیر انواع هشبرد (Hashboard)",
                        detail = "• عیب‌یابی دقیق و تعمیر تخصصی انواع هشبردهای Whatsminer, Antminer و ...\n• تعویض چیپ، ریبال و ترمیم خطوط تغذیه"
                    )

                    ServiceItem(
                        icon = Icons.Default.Psychology,
                        iconTint = CyberCyan,
                        title = "تعمیر انواع کنترل‌برد (Control Board)",
                        detail = "• تعمیر سخت‌افزاری، پروگرام، پروگرم کردن آی‌سی‌ها و رفع مشکلات نرم‌افزاری با ضمانت"
                    )

                    ServiceItem(
                        icon = Icons.Default.ElectricalServices,
                        iconTint = CyberEmerald,
                        title = "تعمیر انواع پاور (Power Supply)",
                        detail = "• عیب‌یابی و تعمیر پاورهای صنعتی و ماینر همراه با تست زیر بار و تضمین کیفیت"
                    )
                }
            }
        }

        // ==================== Order & Repair Process ====================
        item(key = "process") {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkSurface),
                shape = RoundedCornerShape(20.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(1.dp, DarkCardBorder, RoundedCornerShape(20.dp))
            ) {
                Column(
                    modifier = Modifier.padding(18.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.CheckCircle,
                            contentDescription = null,
                            tint = CyberEmerald
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "🔄 فرآیند ثبت سفارش و تعمیرات",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onBackground
                        )
                    }

                    ProcessStep(
                        stepNum = "1",
                        icon = Icons.Default.Inbox,
                        iconTint = CyberCyan,
                        title = "دریافت دستگاه",
                        detail = "ثبت مشخصات، بررسی اولیه و پذیرش کارگاهی"
                    )
                    ProcessStep(
                        stepNum = "2",
                        icon = Icons.Default.Search,
                        iconTint = CyberAmber,
                        title = "عیب‌یابی تخصصی",
                        detail = "عیب‌یابی عمیق مدارات با اسکوپ و تجهیزات پیشرفته"
                    )
                    ProcessStep(
                        stepNum = "3",
                        icon = Icons.Default.Build,
                        iconTint = CyberEmerald,
                        title = "تعمیر و تست زیر بار",
                        detail = "استفاده از قطعات اورجینال و تست پایداری ۲۴ ساعته"
                    )
                    ProcessStep(
                        stepNum = "4",
                        icon = Icons.Default.LocalShipping,
                        iconTint = CyberPurple,
                        title = "بسته‌بندی و ارسال",
                        detail = "بسته‌بندی ایمن ضدضربه و ارسال سریع به سراسر کشور"
                    )
                }
            }
        }

        // ==================== INTERACTIVE FEATURE: Postal Shipping & Packaging Guide ====================
        item(key = "shipping_guide") {
            ShippingGuideCard()
        }

        // ==================== INTERACTIVE FEATURE 5: Customer Reviews & Ratings ====================
        item(key = "customer_reviews") {
            CustomerReviewsCard()
        }

        // ==================== NEW ACTION 2: FAQ Accordion ====================
        item(key = "faq_section") {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkSurface),
                shape = RoundedCornerShape(20.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(1.dp, DarkCardBorder, RoundedCornerShape(20.dp))
            ) {
                Column(
                    modifier = Modifier.padding(18.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.HelpOutline,
                            contentDescription = null,
                            tint = CyberAmber
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "❓ سوالات متداول مشتریان",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onBackground
                        )
                    }

                    FaqItem(
                        question = "زمان تقریبی عیب‌یابی و تعمیرات چقدر است؟",
                        answer = "معمولاً عیب‌یابی اولیه ظرف ۱۲ الی ۲۴ ساعت و فرآیند کامل تعمیر و تست زیر بار بین ۱ تا ۳ روز کاری زمان می‌برد."
                    )

                    FaqItem(
                        question = "آیا امکان ارسال قطعات از سراسر کشور وجود دارد؟",
                        answer = "بله، پذیرش از تمامی استان‌ها از طریق پست پیشتاز، تیپاکس، کالارسان و باربری امکان‌پذیر است."
                    )

                    FaqItem(
                        question = "آیا قطعات تعمیر شده دارای ضمانت و مهلت تست هستند؟",
                        answer = "بله، تمامی قطعات تعمیری پیش از تحویل حداقل ۲۴ ساعت زیر بار تست دقیق شده و دارای ضمانت عملکرد می‌باشند."
                    )

                    FaqItem(
                        question = "هزینه تعمیرات چگونه محاسبه و اعلام می‌شود؟",
                        answer = "پیش از شروع فرآیند تعمیر، عیب‌یابی انجام شده و هزینه دقیق قطعات و دستمزد به اطلاع شما می‌رسد و پس از تأیید شما فرآیند تعمیر آغاز می‌گردد."
                    )
                }
            }
        }

        // ==================== Contact & Social Channels ====================
        item(key = "contacts") {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkSurface),
                shape = RoundedCornerShape(24.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(
                        1.dp,
                        Brush.horizontalGradient(listOf(CyberCyan, CyberEmerald)),
                        RoundedCornerShape(24.dp)
                    )
            ) {
                Column(
                    modifier = Modifier.padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(14.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(38.dp)
                                .background(CyberCyan.copy(alpha = 0.15f), CircleShape)
                                .border(1.dp, CyberCyan.copy(alpha = 0.4f), CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.SupportAgent,
                                contentDescription = null,
                                tint = CyberCyan,
                                modifier = Modifier.size(20.dp)
                            )
                        }
                        Spacer(modifier = Modifier.width(10.dp))
                        Column {
                            Text(
                                text = "راه‌های ارتباطی و ثبت سفارش",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.onBackground
                            )
                            Text(
                                text = "پشتیبانی آنلاین و ارتباط مستقیم با واحد خدمات",
                                style = MaterialTheme.typography.labelSmall,
                                color = TextSecondary
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(2.dp))

                    // 1. Phone Call Channel
                    ProfessionalChannelCard(
                        icon = Icons.Default.Call,
                        iconTint = CyberAmber,
                        title = "تماس مستقیم و مشاوره رایگان",
                        subtitle = "پاسخگویی سریع واحد فنی و عیب‌یابی اولیه",
                        buttonText = "تماس تلفنی با کارشناس",
                        buttonColor = CyberAmber,
                        buttonTextColor = Color.Black,
                        badgeText = "۰۹۱۲۰۰۸۴۱۹۸",
                        onClick = {
                            try {
                                val intent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:09120084198"))
                                context.startActivity(intent)
                            } catch (_: Exception) {}
                        }
                    )

                    // 2. Telegram Support Channel
                    ProfessionalChannelCard(
                        icon = Icons.Default.Send,
                        iconTint = Color(0xFF29B6F6),
                        title = "پشتیبانی و ثبت سفارش تلگرام",
                        subtitle = "ارسال مشخصات برد و استعلام فوری هزینه تعمیرات",
                        buttonText = "ارتباط با ادمین در تلگرام",
                        buttonColor = Color(0xFF0088CC),
                        buttonTextColor = Color.White,
                        badgeText = "پاسخ آنلاین",
                        onClick = {
                            try {
                                uriHandler.openUri("http://t.me/fixb_051_admin")
                            } catch (_: Exception) {}
                        }
                    )

                    // 3. Instagram Channel
                    ProfessionalChannelCard(
                        icon = Icons.Default.CameraAlt,
                        iconTint = Color(0xFFE1306C),
                        title = "صفحه رسمی اینستاگرام Fix Board",
                        subtitle = "مشاهده ویدیوهای تعمیرات، تست زیر بار و نمونه کارها",
                        buttonText = "مشاهده پیج اینستاگرام",
                        buttonColor = Color(0xFFE1306C),
                        buttonTextColor = Color.White,
                        badgeText = "نمونه کارها",
                        onClick = {
                            try {
                                uriHandler.openUri("https://www.instagram.com/fixb_051")
                            } catch (_: Exception) {}
                        }
                    )

                    // 4. Official Website Channel
                    ProfessionalChannelCard(
                        icon = Icons.Default.Language,
                        iconTint = CyberCyan,
                        title = "وب‌سایت رسمی مرکز تعمیرات",
                        subtitle = "اطلاعات کامل خدمات، مقالات آموزشی و معرفی مجموعه",
                        buttonText = "ورود به سایت Fix Board",
                        buttonColor = CyberCyan.copy(alpha = 0.2f),
                        buttonTextColor = CyberCyan,
                        isOutlined = true,
                        badgeText = "fixb.ir",
                        onClick = {
                            try {
                                uriHandler.openUri("https://fixb.ir")
                            } catch (_: Exception) {}
                        }
                    )
                }
            }
        }

        // ==================== App Technical Info ====================
        item(key = "app_info") {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkSurface),
                shape = RoundedCornerShape(16.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(1.dp, DarkCardBorder, RoundedCornerShape(16.dp))
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.Info,
                            contentDescription = null,
                            tint = TextMuted,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "نرم‌افزار اسکنر واتس‌ماینر | نسخه ${BuildConfig.VERSION_NAME}",
                            style = MaterialTheme.typography.bodySmall,
                            fontFamily = FontFamily.Monospace,
                            color = TextMuted
                        )
                    }
                    Text(
                        text = "ارتباط ۱۰۰٪ محلی سوکت - بدون ارسال داده به سرورهای خارجی. طراحی شده ویژه تکنسین‌ها و فارم‌داران ماینینگ.",
                        style = MaterialTheme.typography.labelSmall,
                        color = TextMuted,
                        fontSize = 10.sp,
                        lineHeight = 16.sp
                    )
                }
            }
        }

        item(key = "bottom_spacer") {
            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}

// ==================== Helper Functions & Sub-Components ====================

private fun checkIsCenterOpen(): Boolean {
    return try {
        val calendar = Calendar.getInstance()
        val dayOfWeek = calendar.get(Calendar.DAY_OF_WEEK)
        val hour = calendar.get(Calendar.HOUR_OF_DAY)

        when (dayOfWeek) {
            Calendar.SATURDAY, Calendar.SUNDAY, Calendar.MONDAY, Calendar.TUESDAY, Calendar.WEDNESDAY -> {
                hour in 9..17 // 9:00 to 18:00
            }
            Calendar.THURSDAY -> {
                hour in 9..13 // 9:00 to 14:00
            }
            else -> false // Friday
        }
    } catch (_: Exception) {
        true
    }
}

@Composable
private fun FaqItem(
    question: String,
    answer: String
) {
    var expanded by remember { mutableStateOf(false) }

    Surface(
        color = DarkSurfaceVariant.copy(alpha = 0.6f),
        shape = RoundedCornerShape(12.dp),
        border = androidx.compose.foundation.BorderStroke(
            1.dp,
            if (expanded) CyberAmber.copy(alpha = 0.5f) else DarkCardBorder
        ),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier
                .clickable { expanded = !expanded }
                .padding(14.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = question,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onBackground,
                    modifier = Modifier.weight(1f)
                )
                Icon(
                    imageVector = if (expanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                    contentDescription = null,
                    tint = CyberAmber
                )
            }

            AnimatedVisibility(
                visible = expanded,
                enter = expandVertically() + fadeIn(),
                exit = shrinkVertically() + fadeOut()
            ) {
                Column {
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = answer,
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                        lineHeight = 20.sp
                    )
                }
            }
        }
    }
}

@Composable
private fun FeatureRow(
    icon: ImageVector,
    iconTint: Color,
    title: String,
    description: String
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.Top
    ) {
        Box(
            modifier = Modifier
                .size(36.dp)
                .background(iconTint.copy(alpha = 0.15f), CircleShape)
                .border(1.dp, iconTint.copy(alpha = 0.4f), CircleShape),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = iconTint,
                modifier = Modifier.size(18.dp)
            )
        }
        Spacer(modifier = Modifier.width(12.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onBackground
            )
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = description,
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary,
                lineHeight = 18.sp
            )
        }
    }
}

@Composable
private fun ServiceItem(
    icon: ImageVector,
    iconTint: Color,
    title: String,
    detail: String
) {
    Surface(
        color = DarkSurfaceVariant.copy(alpha = 0.5f),
        shape = RoundedCornerShape(12.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, iconTint.copy(alpha = 0.25f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.padding(12.dp),
            verticalAlignment = Alignment.Top
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = iconTint,
                modifier = Modifier
                    .size(24.dp)
                    .padding(top = 2.dp)
            )
            Spacer(modifier = Modifier.width(10.dp))
            Column {
                Text(
                    text = title,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Bold,
                    color = iconTint
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = detail,
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                    lineHeight = 18.sp
                )
            }
        }
    }
}

@Composable
private fun ProcessStep(
    stepNum: String,
    icon: ImageVector,
    iconTint: Color,
    title: String,
    detail: String
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            contentAlignment = Alignment.Center
        ) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .background(iconTint.copy(alpha = 0.15f), CircleShape)
                    .border(1.dp, iconTint.copy(alpha = 0.5f), CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = iconTint,
                    modifier = Modifier.size(20.dp)
                )
            }
            Surface(
                color = iconTint,
                shape = CircleShape,
                modifier = Modifier
                    .size(16.dp)
                    .align(Alignment.BottomEnd)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Text(
                        text = stepNum,
                        color = Color.Black,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.ExtraBold,
                        textAlign = TextAlign.Center
                    )
                }
            }
        }
        Spacer(modifier = Modifier.width(12.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onBackground
            )
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = detail,
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary,
                lineHeight = 18.sp
            )
        }
    }
}

@Composable
private fun ProfessionalChannelCard(
    icon: ImageVector,
    iconTint: Color,
    title: String,
    subtitle: String,
    buttonText: String,
    buttonColor: Color,
    buttonTextColor: Color,
    badgeText: String,
    isOutlined: Boolean = false,
    onClick: () -> Unit
) {
    Surface(
        color = DarkSurfaceVariant.copy(alpha = 0.6f),
        shape = RoundedCornerShape(16.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, iconTint.copy(alpha = 0.3f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(14.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.weight(1f)
                ) {
                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .background(iconTint.copy(alpha = 0.15f), CircleShape)
                            .border(1.dp, iconTint.copy(alpha = 0.4f), CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = icon,
                            contentDescription = null,
                            tint = iconTint,
                            modifier = Modifier.size(18.dp)
                        )
                    }
                    Spacer(modifier = Modifier.width(10.dp))
                    Column {
                        Text(
                            text = title,
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onBackground
                        )
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            text = subtitle,
                            style = MaterialTheme.typography.labelSmall,
                            color = TextSecondary,
                            fontSize = 11.sp
                        )
                    }
                }

                Spacer(modifier = Modifier.width(8.dp))

                Surface(
                    color = iconTint.copy(alpha = 0.15f),
                    shape = RoundedCornerShape(12.dp),
                    border = androidx.compose.foundation.BorderStroke(0.5.dp, iconTint.copy(alpha = 0.4f))
                ) {
                    Text(
                        text = badgeText,
                        style = MaterialTheme.typography.labelSmall,
                        color = iconTint,
                        fontWeight = FontWeight.Bold,
                        fontSize = 10.sp,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                    )
                }
            }

            if (isOutlined) {
                OutlinedButton(
                    onClick = onClick,
                    border = androidx.compose.foundation.BorderStroke(1.dp, iconTint),
                    shape = RoundedCornerShape(10.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Icon(
                        imageVector = icon,
                        contentDescription = null,
                        tint = buttonTextColor,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = buttonText,
                        color = buttonTextColor,
                        fontWeight = FontWeight.Bold,
                        fontSize = 12.sp
                    )
                }
            } else {
                Button(
                    onClick = onClick,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = buttonColor,
                        contentColor = buttonTextColor
                    ),
                    shape = RoundedCornerShape(10.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Icon(
                        imageVector = icon,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = buttonText,
                        fontWeight = FontWeight.Bold,
                        fontSize = 12.sp
                    )
                }
            }
        }
    }
}

// ==================== INTERACTIVE FEATURE COMPONENT ====================

// ==================== INTERACTIVE FEATURE COMPONENT 4 ====================

@Composable
private fun ShippingGuideCard() {
    val clipboardManager = LocalClipboardManager.current
    var copied by remember { mutableStateOf(false) }

    val fullAddress = "مشهد، خیابان امام رضا، دفتر پذیرش و تعمیرات تخصصی Fix Board (کدپستی: ۹۱۷۳۵۱۴۹۸۱)"

    Card(
        colors = CardDefaults.cardColors(containerColor = DarkSurface),
        shape = RoundedCornerShape(20.dp),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, DarkCardBorder, RoundedCornerShape(20.dp))
    ) {
        Column(
            modifier = Modifier.padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Default.LocationOn,
                    contentDescription = null,
                    tint = CyberPurple
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "📮 آدرس دفتر پذیرش و راهنمای ارسال پستی",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onBackground
                )
            }

            Surface(
                color = DarkSurfaceVariant,
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text("آدرس جهت ارسال پستی / تیپاکس / باربری:", style = MaterialTheme.typography.labelSmall, color = TextMuted)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(fullAddress, style = MaterialTheme.typography.bodySmall, color = TextPrimary, lineHeight = 20.sp)
                    Spacer(modifier = Modifier.height(8.dp))
                    OutlinedButton(
                        onClick = {
                            clipboardManager.setText(AnnotatedString(fullAddress))
                            copied = true
                        },
                        shape = RoundedCornerShape(8.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Icon(Icons.Default.ContentCopy, contentDescription = null, modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(if (copied) "آدرس کپی شد ✓" else "کپی آدرس پستی جهت ارسال", fontSize = 12.sp)
                    }
                }
            }

            Text("💡 نکته امنیتی بسته‌بندی:", style = MaterialTheme.typography.labelSmall, color = CyberAmber)
            Text(
                "لطفاً هش‌بردها و کنترل‌بردها را حتماً بین دو لایه فوم فشرده یا نایلون حباب‌دار محکم کنید تا از شکستگی پایه‌های هیت‌سینک در حمل‌ونقل جلوگیری شود.",
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary,
                lineHeight = 18.sp
            )
        }
    }
}

// ==================== INTERACTIVE FEATURE COMPONENT 5 ====================

@Composable
private fun CustomerReviewsCard() {
    val reviews = listOf(
        "مهندس رضایی (فارم مشهد)" to "۱۰ عدد هش‌برد M20S که همه عیب پیچیده داشتند رو ظرف ۲ روز عیب‌یابی و با تست زیر بار تحویل دادند. واقعاً باسابقه و حرفه‌ای.",
        "علیرضا حسینی (تبریز)" to "پاور ۳۳۰۰ وات خاموش رو فرستادم تیپاکس، خیلی تمیز تعمیر شد و برام فرستادن. گارانتی کتبی هم داده بودند.",
        "تکنسین فارم فاروق (شیراز)" to "کنترل‌بردهای واتس‌ماینر که کلاً بالا نمیومد رو پروگرام زدن و عالی کار میکنه. ممنون از مجموعه Fix Board."
    )

    Card(
        colors = CardDefaults.cardColors(containerColor = DarkSurface),
        shape = RoundedCornerShape(20.dp),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, DarkCardBorder, RoundedCornerShape(20.dp))
    ) {
        Column(
            modifier = Modifier.padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Star,
                        contentDescription = null,
                        tint = Color(0xFFFFD700)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "⭐ رضایت‌مندی مشتریان و فارم‌داران",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onBackground
                    )
                }

                Surface(
                    color = Color(0xFFFFD700).copy(alpha = 0.15f),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text(
                        text = "امتیاز ۴.۹ از ۵",
                        style = MaterialTheme.typography.labelSmall,
                        color = Color(0xFFFFD700),
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    )
                }
            }

            reviews.forEach { (author, comment) ->
                Surface(
                    color = DarkSurfaceVariant,
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.VerifiedUser, contentDescription = null, tint = CyberEmerald, modifier = Modifier.size(16.dp))
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(author, style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Bold, color = TextPrimary)
                        }
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(comment, style = MaterialTheme.typography.bodySmall, color = TextSecondary, lineHeight = 18.sp)
                    }
                }
            }
        }
    }
}

