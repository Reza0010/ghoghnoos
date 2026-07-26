import 'package:flutter/material.dart';

class ErrorCodeItem {
  final String code;
  final String titleFa;
  final String symptomsFa;
  final String causeFa;
  final List<String> resolutionStepsFa;

  const ErrorCodeItem({
    required this.code,
    required this.titleFa,
    required this.symptomsFa,
    required this.causeFa,
    required this.resolutionStepsFa,
  });
}

class RepairKbPage extends StatefulWidget {
  const RepairKbPage({super.key});

  @override
  State<RepairKbPage> createState() => _RepairKbPageState();
}

class _RepairKbPageState extends State<RepairKbPage> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';

  // Comprehensive offline database of Antminer & Whatsminer Error Codes in Persian
  final List<ErrorCodeItem> _antminerErrors = const [
    ErrorCodeItem(
      code: 'Code 15',
      titleFa: 'خطای بررسی آی‌سی PIC (PIC Check Fail)',
      symptomsFa: 'دستگاه استارت نمی‌زند و هش‌بردها شناسایی نمی‌شوند. در لاگ خطای pic init fail درج می‌گردد.',
      causeFa: 'خرابی سفت‌افزار یا سخت‌افزار تراشه کنترلی PIC روی هش‌برد یا قطعی کابل دیتا.',
      resolutionStepsFa: [
        'کابل فلت دیتای متصل به هش‌برد را تمیز یا تعویض کنید.',
        'فریمور کنترل‌برد را مجدداً با کارت حافظه SD فلش کنید.',
        'آی‌سی PIC باید توسط تستر ریست یا تعویض و پروگرام شود.',
      ],
    ),
    ErrorCodeItem(
      code: 'Code 234',
      titleFa: 'دمای بحرانی و خاموشی خودکار (Over Temp Protection)',
      symptomsFa: 'ماینر ناگهان تراهش صفر می‌دهد و یکی از فن‌ها با حداکثر سرعت ۱۰۰٪ کار می‌کند.',
      causeFa: 'افزایش دمای هیت‌سینک‌ها به بالای ۸۵ درجه به دلیل گرفتگی هوا یا خشکی خمیر سیلیکون.',
      resolutionStepsFa: [
        'خروجی هوای گرم ماینر و لوله‌های تخلیه را بازرسی کنید.',
        'هش‌برد را بادگیری کنید تا گرد و خاک بین پره‌های هیت‌سینک پاک شود.',
        'در صورت قدیمی بودن دستگاه، خمیر سیلیکون هیت‌سینک‌ها را تعویض کنید.',
      ],
    ),
    ErrorCodeItem(
      code: 'Code 10',
      titleFa: 'عدم شناسایی یا دور پایین فن (Fan Lost / Low RPM)',
      symptomsFa: 'چراغ قرمز خطا روی ماینر چشمک می‌زند و دستگاه شروع به ماین نمی‌کند.',
      causeFa: 'خرابی سیم سنسور دور موتور فن (سیم زرد یا آبی) یا سوختگی موتور بلبرینگ فن.',
      resolutionStepsFa: [
        'اتصال فیش فن به سوکت کنترل‌برد را بررسی کنید.',
        'پروانه فن را بچرخانید تا از عدم وجود مانع فیزیکی مطمئن شوید.',
        'سوکت فن خراب را روی کنترل‌برد جابجا کنید تا عیب یابی کنترل‌برد محقق شود.',
        'در صورت خرابی قطعی، فن ۴ سیمه ۱۲ ولت دبل بلبرینگ اصلی جایگزین کنید.',
      ],
    ),
    ErrorCodeItem(
      code: 'Code 86',
      titleFa: 'خطای خواندن تراشه رام هش‌برد (EEPROM Error)',
      symptomsFa: 'فرکانس هش‌برد روی صفر قفل شده و در لاگ خطای EEPROM Checksum Error دیده می‌شود.',
      causeFa: 'پریدن رام هش‌برد یا خرابی خازن‌های تغذیه آی‌سی رام روی برد.',
      resolutionStepsFa: [
        'دستگاه را ریبوت کنید تا رام دوباره خوانده شود.',
        'فایل فریمور با فرکانس متغیر (اتوتیونینگ) نصب کنید.',
        'آی‌سی EEPROM روی هش‌برد باید از طریق پروگرمر فیزیکی پروگرام مجدد شود.',
      ],
    ),
  ];

  final List<ErrorCodeItem> _whatsminerErrors = const [
    ErrorCodeItem(
      code: 'Code 200',
      titleFa: 'خطای ارتباطی پاور با کنترل‌برد (PSU Comm Failure)',
      symptomsFa: 'ماینر روشن می‌شود ولی کنترل‌برد با پاور ارتباط برقرار نمی‌کند و تراهش صفر است.',
      causeFa: 'قطع کابل دیتای هوشمند متصل بین پاور و کنترل‌برد یا خرابی مدار کنترل پاور.',
      resolutionStepsFa: [
        'کابل ریبونی دیتای پاور به کنترل‌برد را جدا و دوباره محکم متصل کنید.',
        'ولتاژ پریز ورودی پاور را بسنجید (باید در محدوده ۲۰0 الی ۲۴۰ ولت باشد).',
        'در صورت تداوم خطا، کنترلر داخلی پاور معیوب است و نیاز به تعمیر تخصصی دارد.',
      ],
    ),
    ErrorCodeItem(
      code: 'Code 301',
      titleFa: 'عدم شناسایی زنجیره هش‌برد ۳ (Board 3 Absent)',
      symptomsFa: 'کاهش ۳۳ درصدی تراهش ماینر و نمایش علامت ضربدر یا عدم حضور برد ۳ در پنل تنظیمات.',
      causeFa: 'عدم دریافت ولتاژ راه‌اندازی توسط برد ۳ یا خرابی تراشه اول خط اسیک روی برد.',
      resolutionStepsFa: [
        'پیچ‌های شینه‌های مسی مسی انتقال برق پاور به هش‌برد ۳ را سفت کنید.',
        'کابل فلت خاکستری متصل به برد ۳ را جابجا کنید.',
        'تست ولتاژ هش‌برد را با مولتی‌متر انجام دهید.',
      ],
    ),
    ErrorCodeItem(
      code: 'Code 540',
      titleFa: 'دمای بالای هوای ورودی محیط (High Inlet Air Temp)',
      symptomsFa: 'کاهش اتوماتیک فرکانس کاری ماینر جهت محافظت و افت تراهش محسوس.',
      causeFa: 'دمای محیط فارم یا ورودی هوای ماینر بالای ۳۸ درجه سانتی‌گراد است.',
      resolutionStepsFa: [
        'سیستم سرمایش فارم (پد سلولزی یا کولر) را بررسی کنید.',
        'از عدم بازگشت هوای گرم خروجی ماینر به داخل محیط ورودی مطمئن شوید.',
        'فاصله بین ماینرها را افزایش دهید تا جریان باد روان باشد.',
      ],
    ),
    ErrorCodeItem(
      code: 'Code 260',
      titleFa: 'عدم تعادل ولتاژ هش‌بردها (Voltage Imbalance)',
      symptomsFa: 'ماینر پس از چند دقیقه کارکرد متوقف شده و خطای عدم تطابق ولتاژ در پنل می‌دهد.',
      causeFa: 'ضعیف شدن یکی از بردهای سه‌گانه یا نوسان خروجی ریل‌های تغذیه پاور.',
      resolutionStepsFa: [
        'تمام کابل‌های مسی متصل به پاور را تمیز کنید (رسوب زدایی).',
        'ماینر را تک‌برد تست کنید تا برد ضعیف‌تر شناسایی شود.',
        'پاور ماینر نیاز به کالیبراسیون ولتاژ یا تعمیر بخش خروجی دارد.',
      ],
    ),
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  List<ErrorCodeItem> _filterErrors(List<ErrorCodeItem> originalList) {
    if (_searchQuery.isEmpty) return originalList;
    final query = _searchQuery.toLowerCase();
    return originalList.where((item) {
      return item.code.toLowerCase().contains(query) ||
          item.titleFa.toLowerCase().contains(query) ||
          item.causeFa.toLowerCase().contains(query);
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('دانشنامه کدهای خطا و تعمیرات'),
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: const Color(0xFFFFD700),
            labelColor: const Color(0xFFFFD700),
            unselectedLabelColor: Colors.white,
            tabs: const [
              Tab(text: 'کدهای خطا Antminer'),
              Tab(text: 'کدهای خطا Whatsminer'),
            ],
          ),
        ),
        body: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: isDark
                  ? [const Color(0xFF121212), const Color(0xFF1E1E1E)]
                  : [const Color(0xFFF5F7FA), const Color(0xFFE4E9F0)],
            ),
          ),
          child: Column(
            children: [
              // Search Input Section
              Padding(
                padding: const EdgeInsets.all(16),
                child: TextField(
                  controller: _searchController,
                  decoration: InputDecoration(
                    labelText: 'جستجوی کد خطا یا کلمات کلیدی...',
                    prefixIcon: const Icon(Icons.search, color: Color(0xFF0D47A1)),
                    suffixIcon: _searchQuery.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear),
                            onPressed: () {
                              setState(() {
                                _searchController.clear();
                                _searchQuery = '';
                              });
                            },
                          )
                        : null,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  onChanged: (value) {
                    setState(() {
                      _searchQuery = value;
                    });
                  },
                ),
              ),

              // Tab Views
              Expanded(
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildErrorList(_filterErrors(_antminerErrors)),
                    _buildErrorList(_filterErrors(_whatsminerErrors)),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildErrorList(List<ErrorCodeItem> errors) {
    if (errors.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search_off_outlined, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            const Text(
              'هیچ موردی متناسب با جستجوی شما یافت نشد.',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      itemCount: errors.length,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      itemBuilder: (context, index) {
        final error = errors[index];
        return Card(
          margin: const EdgeInsets.symmetric(vertical: 8),
          elevation: 3,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: ExpansionTile(
            title: Text(
              error.code,
              style: const TextStyle(
                fontFamily: 'monospace',
                fontWeight: FontWeight.w900,
                fontSize: 18,
                color: Color(0xFF0D47A1),
              ),
            ),
            subtitle: Text(
              error.titleFa,
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.grey),
            ),
            children: [
              Padding(
                padding: const EdgeInsets.only(left: 16, right: 16, bottom: 16, top: 8),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Divider(),
                    _buildDetailRow('علائم خرابی:', error.symptomsFa, Colors.amber[900]!),
                    const SizedBox(height: 10),
                    _buildDetailRow('علت ریشه‌ای:', error.causeFa, Colors.red[900]!),
                    const SizedBox(height: 16),
                    const Text(
                      'مراحل عیب‌یابی و تعمیر قطعی:',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF0D47A1)),
                    ),
                    const SizedBox(height: 8),
                    ...error.resolutionStepsFa.asMap().entries.map((stepEntry) {
                      final sIdx = stepEntry.key;
                      final sText = stepEntry.value;
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            CircleAvatar(
                              radius: 9,
                              backgroundColor: const Color(0xFF0D47A1).withOpacity(0.12),
                              child: Text(
                                '${sIdx + 1}',
                                style: const TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Color(0xFF0D47A1)),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                sText,
                                style: const TextStyle(fontSize: 12.5, height: 1.5),
                              ),
                            ),
                          ],
                        ),
                      );
                    }),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildDetailRow(String label, String value, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12.5, color: color),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(fontSize: 13, height: 1.5),
        ),
      ],
    );
  }
}
