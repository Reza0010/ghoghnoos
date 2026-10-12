# MinerMedia AI — Smart Mining & Crypto Channel Manager

<p align="center">
  <img src="https://img.shields.io/badge/MinerMedia_AI-v2.0.1-f7931a?style=for-the-badge&labelColor=0b0f14" alt="version"/>
  <img src="https://img.shields.io/badge/Python-3.11+-ffffff?style=for-the-badge&logo=python&logoColor=white&labelColor=0b0f14"/>
  <img src="https://img.shields.io/badge/PySide6-RTL_فارسی-ffffff?style=for-the-badge&labelColor=0b0f14"/>
</p>

**MinerMedia AI** بازسازی حرفه‌ای و تخصصی پروژه TeleAI-AutoPoster است: یک
دسکتاپ‌اپ مدیریت کانال تلگرام برای حوزه **تعمیرات ماینر، عیب‌یابی هش‌برد/کنترل‌برد،
پاور و صنعت ماینینگ** — با قیمت لحظه‌ای نوبیتکس، تولید محتوای AI با گردش کار
تأیید، دریافت اخبار، چندکاناله و زمان‌بند مستقل و مقاوم.

> سورس اصلی (v1.0.2) دست‌نخورده در پوشه `original_source/` نگهداری شده و
> گزارش کامل تحلیل ایرادها در `docs/analysis_report.md` آمده است.

> **v2.0.1 — سخت‌سازی پایداری:** خاموش‌شدن امن (توقف واقعی Workerها قبل از بستن
> دیتابیس)، بازیابی صحیح صف پس از خاموشی (بدون «unknown» اشتباه)، تفکیک خطای
> دسته/نرخ نوبیتکس با حذف درخواست‌های اضافی در 429، Worker زمان‌بندی‌شده اخبار،
> آلبوم + صوت در UI با اعتبارسنجی قبل از زمان‌بندی، و تاریخچه تلاش‌های ارسال.
> جزئیات: `CHANGELOG.md` — تست: ۱۲۰ پاس + ۲ زنده (گزارش: `docs/TEST_REPORT.md`).

---

## قابلیت‌ها

| بخش | توضیح |
|---|---|
| 🏠 نمای کلی | کارت‌های وضعیت از داده واقعی دیتابیس/API؛ بدون هیچ عدد ساختگی |
| 📡 مدیریت کانال‌ها | چندکاناله، توکن مستقل (Credential Manager)، آزمون اتصال واقعی Bot API |
| 🗓 صف انتشار | وضعیت‌های کامل draft/pending/processing/sent/failed/unknown/cancelled + لغو/بازارسال امن |
| ✨ استودیو AI | ۱۲ دسته تخصصی ماینینگ × ۱۰ نوع محتوا، گردش کار تأیید، تزریق قیمت واقعی |
| 💰 بازار ارز | قیمت ریالی/تومانی/دلاری نوبیتکس، نمودار ۱س/۲۴س (محلی) و ۷ر/۳۰ر (بازار)، برچسب صریح منبع/واحد |
| 📰 اخبار | RSS منابع قابل مدیریت، dedupe، گردش کار تأیید، خلاصه‌سازی اختیاری |
| 🖼 کتابخانه رسانه | اعتبارسنجی محدودیت‌های واقعی Bot API (۱۰MB عکس/۵۰MB بقیه) |
| 📊 گزارش‌ها | انتشار روزانه، وضعیت هر کانال، تاریخچه تولید AI — همه از SQL واقعی |
| ⚙️ تنظیمات | نام محصول قابل شخصی‌سازی، منطقه زمانی، پشتیبان‌گیری، پاک‌سازی نگهداری |

## امنیت
- توکن ربات و کلید AI در **Windows Credential Manager** (کتابخانه keyring) —
  هرگز در فایل JSON/لاگ/پیام خطا.
- پاک‌سازی خودکار توکن/کلید از همه لاگ‌ها (`core/redact.py` + تست).
- پیش‌فرض‌های ایمن: انتشار خودکار خاموش، الزام تأیید خبر، حداقل فاصله ۳۰ ثانیه
  برای بازار، عدم ارسال مجدد خودکار در نتیجه مبهم.

## اجرا (ویندوز)
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
راهنمای کامل: [`docs/INSTALL.md`](docs/INSTALL.md) • توکن ربات: [`docs/BOT_TOKEN.md`](docs/BOT_TOKEN.md)
• نوبیتکس: [`docs/NOBITEX_API.md`](docs/NOBITEX_API.md) • AI: [`docs/AI_SETUP.md`](docs/AI_SETUP.md)
• پشتیبان‌گیری: [`docs/BACKUP_RESTORE.md`](docs/BACKUP_RESTORE.md) • محدودیت‌ها: [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md)

## تست‌ها
> **توجه:** `requirements-dev.txt` فقط ابزار تست (pytest) است و وابستگی‌های
> اصلی برنامه (PySide6/feedparser/keyring/requests) را نصب نمی‌کند — برای
> اجرای خود برنامه اول `pip install -r requirements.txt` لازم است.
```powershell
pip install -r requirements-dev.txt
python -m pytest tests/                              # ۱۲۰ تست
python -m pytest tests/test_live_nobitex.py --live   # ۲ تست زنده API عمومی نوبیتکس
```
گزارش اجرای واقعی: [`docs/TEST_REPORT.md`](docs/TEST_REPORT.md)

## ساختار
```
MinerMediaAI/
├── app.py                  # نقطه ورود و سیم‌کشی لایه‌ها
├── config/                 # پیش‌فرض‌ها + تنظیمات
├── core/                   # خطاها، لاگ امن، زمان، واحد پول، مسیرها
├── models/                 # dataclassها و enumها
├── database/               # SQLite + مهاجرت نسخه‌بندی‌شده + ریپازیتوری‌ها
├── security/               # SecretStore (Credential Manager / فایل توسعه)
├── services/
│   ├── telegram/           # کلاینت Bot API + اعتبارسنجی رسانه
│   ├── nobitex/            # کلاینت عمومی مستندمحور نوبیتکس
│   ├── market_data/        # تفسیر واحد، staleness، تخمین، تاریخچه
│   ├── ai/                 # ارائه‌دهنده سازگار OpenAI + استودیو محتوا
│   ├── news/               # RSS با dedupe و گردش کار
│   └── media/              # کتابخانه رسانه
├── workers/                # Scheduler مستقل + MarketWorker (بدون فریز UI)
├── ui/                     # ۹ صفحه، تم تیره RTL، نمودارهای واقعی
├── tests/                  # ۸۸ تست (۸۶ + ۲ live)
├── docs/                   # مستندات کامل
└── original_source/        # سورس اصلی TeleAI-AutoPoster v1.0.2 (بدون تغییر)
```

## مجوز و نسب‌شناسی
سورس اولیه تحت MIT (BSHF-PER). نسخه بازسازی‌شده بر همان پایه توسعه یافته و
نسب‌شناسی در `CHANGELOG.md` ثبت است. فونت وزیرمتن (OFL) از پروژه
[rastikerdar/vazirmatn](https://github.com/rastikerdar/vazirmatn).

---

### English (brief)
MinerMedia AI is a professional rebuild of TeleAI-AutoPoster: a PySide6 desktop
manager for Persian mining-repair Telegram channels — multi-channel Bot API
publishing with a persistent scheduler (atomic claims, 429/retry_after handling,
explicit `unknown` state instead of blind resends), live Nobitex market data
(documented public endpoints, explicit Rial/Toman unit policy with verified
10× ratio), AI content studio with mandatory approval workflow, RSS news
pipeline with dedupe, secure secret storage (Windows Credential Manager via
keyring), and a dark RTL Persian UI. No fake numbers anywhere: missing data is
shown as "ناموجود", stale data is labeled. See `docs/` for full documentation.
