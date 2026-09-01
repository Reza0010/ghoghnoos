class ParsedIssue {
  final String titleFa;
  final String descriptionFa;
  final String severity; // 'info', 'warning', 'critical'
  final List<String> stepsFa;

  ParsedIssue({
    required this.titleFa,
    required this.descriptionFa,
    required this.severity,
    required this.stepsFa,
  });
}

class DiagnosticReport {
  final String manufacturer; // 'Antminer', 'Whatsminer', 'Unknown'
  final String overallStatusFa;
  final List<ParsedIssue> issues;
  final int totalErrorsFound;

  DiagnosticReport({
    required this.manufacturer,
    required this.overallStatusFa,
    required this.issues,
    required this.totalErrorsFound,
  });
}

class LogParser {
  static DiagnosticReport parse(String rawLog) {
    final List<ParsedIssue> issues = [];
    String manufacturer = 'نامشخص';

    // Convert to lowercase for easy matching
    final String logLower = rawLog.toLowerCase();

    // Identify Manufacturer
    if (logLower.contains('antminer') || logLower.contains('bm13') || logLower.contains('cgminer')) {
      manufacturer = 'Antminer';
    } else if (logLower.contains('whatsminer') || logLower.contains('whats') || logLower.contains('btminer')) {
      manufacturer = 'Whatsminer';
    }

    // 1. Hashboard dead or missing check
    if (logLower.contains('board not found') ||
        logLower.contains('lost board') ||
        logLower.contains('hashboard dead') ||
        logLower.contains('chain not found') ||
        logLower.contains('find 0 chain')) {
      issues.add(ParsedIssue(
        titleFa: 'عدم شناسایی یا قطعی هش‌برد',
        descriptionFa: 'سیستم قادر به شناسایی یک یا چند هش‌برد نیست. این مشکل معمولاً ناشی از قطع کابل دیتا، آسیب فیزیکی به برد یا خرابی مدار تغذیه هش‌برد است.',
        severity: 'critical',
        stepsFa: [
          'کابل دیتای خاکستری (کابل فلت) بین کنترل‌برد و هش‌برد را بررسی کنید و در صورت نیاز تعویض کنید.',
          'اتصال کابل‌های برق هش‌برد از سمت پاور را بررسی کنید تا مطمئن شوید محکم هستند.',
          'پین‌های کانکتور روی هش‌برد را از نظر تغییر رنگ یا سوختگی ناشی از حرارت بالا بازرسی کنید.',
          'تست ولتاژ خروجی پاور به هش‌برد مربوطه را با مولتی‌متر انجام دهید.',
        ],
      ));
    }

    // 2. PIC controller failure
    if (logLower.contains('pic init failed') ||
        logLower.contains('read pic fail') ||
        logLower.contains('pic check error')) {
      issues.add(ParsedIssue(
        titleFa: 'خطای راه‌اندازی تراشه PIC',
        descriptionFa: 'میکروکنترلر PIC روی هش‌برد که مدیریت دما و سنسورها را بر عهده دارد پاسخ نمی‌دهد. این مشکل ناشی از خرابی سفت‌افزار PIC یا نقص سخت‌افزاری است.',
        severity: 'critical',
        stepsFa: [
          'دستگاه را یک‌بار به طور کامل خاموش و پس از ۲ دقیقه روشن کنید تا خازن‌ها دشارژ شوند.',
          'نسخه فریمور (سفت‌افزار) کنترل‌برد را به آخرین نسخه رسمی ارتقا دهید.',
          'در صورتی که خطا همچنان پابرجا بود، آی‌سی PIC روی هش‌برد باید مجدداً توسط تستر پروگرام یا تعویض شود.',
        ],
      ));
    }

    // 3. Fan lost / low speed
    if (logLower.contains('fan lost') ||
        logLower.contains('fan speed too low') ||
        logLower.contains('fan check failed') ||
        logLower.contains('fan0') && logLower.contains('0 rpm') ||
        logLower.contains('fan1') && logLower.contains('0 rpm')) {
      issues.add(ParsedIssue(
        titleFa: 'خرابی یا قطع اتصال فن خنک‌کننده',
        descriptionFa: 'سرعت چرخش فن به زیر حد مجاز رسیده یا ارتباط فن با کنترل‌برد به طور کامل قطع شده است. برای جلوگیری از سوختن هش‌بردها، سیستم به صورت خودکار متوقف شده است.',
        severity: 'critical',
        stepsFa: [
          'سوکت اتصال فن روی کنترل‌برد را بررسی کنید که محکم متصل باشد.',
          'پروانه‌های فن را بچرخانید تا مطمئن شوید گیر سخت‌افزاری یا جسم خارجی داخل آن نباشد.',
          'جای سوکت فن خراب را روی کنترل‌برد با یک فن سالم دیگر تعویض کنید تا متوجه شوید عیب از فن است یا سوکت کنترل‌برد.',
          'در صورت فرسودگی بلبرینگ فن یا معیوب بودن کابل آن، فن را تعویض کنید.',
        ],
      ));
    }

    // 4. Over temperature
    if (logLower.contains('over temperature') ||
        logLower.contains('temp high') ||
        logLower.contains('temp limit') ||
        logLower.contains('critical temp')) {
      issues.add(ParsedIssue(
        titleFa: 'افزایش بیش از حد دما (Over-Temp)',
        descriptionFa: 'دمای کاری تراشه‌ها یا محیط خروجی هش‌بردها از حد مجاز (معمولاً ۸۵ یا ۹۰ درجه سانتی‌گراد) فراتر رفته است و ماینر وارد حالت حفاظت حرارتی شده است.',
        severity: 'critical',
        stepsFa: [
          'تهویه و کانال خروجی هوای گرم ماینر را بررسی کنید که مسدود نشده باشد.',
          'دمای هوای ورودی محیط فارم را بسنجید (نباید بالای ۳۵ درجه سانتی‌گراد باشد).',
          'عملکرد فن‌های حلزونی ورودی و خروجی را بررسی کنید.',
          'هش‌برد را با پمپ باد تمیز کنید؛ تجمع گرد و خاک روی هیت‌سینک‌ها مانع خنک‌کاری مناسب می‌شود.',
        ],
      ));
    }

    // 5. Stratum connection lost
    if (logLower.contains('stratum connection lost') ||
        logLower.contains('socket connect failed') ||
        logLower.contains('fail to connect to pool') ||
        logLower.contains('cannot find pool')) {
      issues.add(ParsedIssue(
        titleFa: 'عدم اتصال به استخر استخراج (Pool Connection Failure)',
        descriptionFa: 'ماینر قادر به برقراری ارتباط با سرورهای استخر استخراج نیست. این مسئله معمولاً به دلیل قطعی اینترنت، فیلترینگ یا آدرس اشتباه استخر رخ می‌دهد.',
        severity: 'warning',
        stepsFa: [
          'اتصال کابل شبکه (LAN) به ماینر و روتر را بررسی کنید.',
          'تنظیمات DNS ماینر را روی مقادیر معتبر مثل 1.1.1.1 یا 8.8.8.8 تنظیم کنید.',
          'آدرس استخرها را در تنظیمات ماینر بررسی کنید و مطمئن شوید که سرورهای پشتیبان (Backup Pools) نیز ست شده‌اند.',
          'پورت استخر (مثلاً 3333 یا 443) را چک کنید تا توسط سرویس‌دهنده اینترنت مسدود نشده باشد.',
        ],
      ));
    }

    // 6. Power supply error
    if (logLower.contains('psu error') ||
        logLower.contains('power failure') ||
        logLower.contains('voltage mismatch') ||
        logLower.contains('low voltage') ||
        logLower.contains('power protection')) {
      issues.add(ParsedIssue(
        titleFa: 'خطای ولتاژ یا نقص منبع تغذیه (PSU)',
        descriptionFa: 'ماینر نوسان ولتاژ ورودی، افت جریان یا خطای ارتباطی با پاور هوشمند خود را تشخیص داده است.',
        severity: 'critical',
        stepsFa: [
          'ولتاژ برق ورودی ماینر (برق شهری یا ژنراتور) را بررسی کنید که افت نداشته باشد (باید بالای ۲۰۰ ولت باشد).',
          'کابل ارتباط دیتای پاور به کنترل‌برد را بازرسی کنید.',
          'در صورت امکان ماینر را با یک پاور جایگزین و هم‌مدل تست کنید.',
        ],
      ));
    }

    // 7. General Chip Check
    if (logLower.contains('asic check failed') ||
        logLower.contains('some chip is broken') ||
        logLower.contains('chip address error') ||
        logLower.contains('missing chip')) {
      issues.add(ParsedIssue(
        titleFa: 'نقص تراشه اسیک (ASIC Chip Error)',
        descriptionFa: 'یک یا چند تراشه پردازشی روی هش‌برد آسیب دیده و در فرکانس کاری مشخص شده پاسخ نمی‌دهد که باعث افت تراهش (Hashrate) ماینر شده است.',
        severity: 'warning',
        stepsFa: [
          'فرکانس هش‌بردها را در تنظیمات به میزان کمی کاهش دهید تا فشار کاری کمتر شود.',
          'سست نبودن هیت‌سینک‌های روی تراشه‌ها را بازرسی چشمی کنید.',
          'توسط یک تعمیرکار با تستر هش‌برد، تراشه معیوب را شناسایی کرده و اقدام به تعویض آن (ریبال یا تعویض اسیک) نمایید.',
        ],
      ));
    }

    // If no issues were detected, but some log text is pasted
    if (issues.isEmpty && rawLog.trim().isNotEmpty) {
      issues.add(ParsedIssue(
        titleFa: 'سیاهه رویدادها نرمال است',
        descriptionFa: 'در تحلیل اولیه خطا یا پیام بحرانی آشکاری در لاگ‌های ارسالی شما یافت نشد. به نظر می‌رسد سخت‌افزار در شرایط راه‌اندازی اولیه یا پایدار قرار دارد.',
        severity: 'info',
        stepsFa: [
          'مطمئن شوید لاگ ارسالی مربوط به زمان رخ دادن خطای فرضی شماست.',
          'ماینر را ریبوت کنید و لاگ جدید را پس از ۵ دقیقه کارکرد مجدداً اسکن کنید.',
          'محدوده تراهش لحظه‌ای در منوی وضعیت را بررسی نمایید.',
        ],
      ));
    }

    final String overallFa = issues.any((x) => x.severity == 'critical')
        ? 'بحرانی - نیاز به مداخله فوری سخت‌افزاری'
        : issues.any((x) => x.severity == 'warning')
            ? 'هشدار - کارایی ضعیف یا خطای ارتباطی'
            : 'سالم و پایدار';

    return DiagnosticReport(
      manufacturer: manufacturer,
      overallStatusFa: overallFa,
      issues: issues,
      totalErrorsFound: issues.where((x) => x.severity != 'info').length,
    );
  }
}
