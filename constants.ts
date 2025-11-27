
import { Question, UserProfile } from './types';

// Utility to convert Persian digits to English
export const toEnglishDigits = (str: string): string => {
  if (!str) return '';
  return str.replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d).toString());
};

// Helper to get gender-specific tone
const getTone = (profile: UserProfile) => {
  const isMale = profile.gender === 'مرد';
  return {
    emoji: isMale ? '😎💪' : '🌸✨',
    bro: isMale ? 'داداش' : 'عزیز',
    hero: isMale ? 'قهرمان' : 'قهرمان',
    fun: isMale ? 'حله سلطان' : 'عالیه عزیزم',
    waiting: isMale ? 'منتظرم' : 'منتظر جوابتم',
  };
};

// Common Validators
const validators = {
  required: (val: string) => (val && val.trim().length > 1) ? null : 'لطفاً یک پاسخ معتبر بنویس، با یک حرف یا علامت نمیشه برنامه نوشت! 🧐',
  number: (val: string) => {
    const englishVal = toEnglishDigits(val);
    return /^[0-9]+$/.test(englishVal.trim()) ? null : 'لطفاً فقط عدد وارد کن (مثلاً: 25 یا ۲۵) 🔢';
  },
  gender: (val: string) => {
    const v = val.toLowerCase();
    if (v.includes('مرد') || v.includes('زن') || v.includes('خانم') || v.includes('آقا') || v.includes('پسر') || v.includes('دختر')) return null;
    return 'لطفاً مشخص کن مرد هستی یا زن؟ (برای طراحی برنامه مهمه) 👤';
  },
  yesNo: (val: string) => {
    const v = val.toLowerCase();
    if (v.includes('بله') || v.includes('خیر') || v.includes('are') || v.includes('na') || v.includes('نه') || v.includes('اره') || v.includes('آره')) return null;
    return 'لطفاً با بله یا خیر جواب بده.';
  }
};

export const LOADING_QUOTES = [
  "رونی کلمن: «همه می‌خوان بدنساز بشن، ولی کسی نمی‌خواد وزنه سنگین بزنه!» 🏋️‍♂️",
  "آرنولد: «درد امروز، قدرت فردای توست.» 🔥",
  "محمد علی کلی: «من تکرارها رو نمی‌شمارم، وقتی شروع به شمردن می‌کنم که درد شروع بشه.» 🥊",
  "موفقیت یک شبه به دست نمیاد، نتیجه تلاش‌های کوچیک هر روزه است. ✨",
  "بدن تو تنها جاییه که باید تا آخر عمر توش زندگی کنی، پس بسازش! 🏗️",
  "عرق کردن، گریه چربی‌هاست! 💧",
  "هیچ آسانسوری به سمت موفقیت نمیره، باید از پله‌ها بری. 🏃‍♂️",
  "امروز کاری کن که خودِ آینده‌ت ازت تشکر کنه. 🙏"
];

export const QUESTIONS: Question[] = [
  {
    id: 'gender',
    text: () => 'سلام! من ققنوسم، مربی شخصی تو. 🔥\nقبل از هر چیز، جنسیتت چیه؟ 👤 (مرد / زن)',
    placeholder: 'مرد / زن',
    options: ['مرد 😎', 'زن 🌸'],
    validate: validators.gender
  },
  {
    id: 'age',
    text: (p) => `خوش اومدی ${getTone(p).hero}! ${getTone(p).emoji}\nحالا بگو چند سالته؟ 📅`,
    placeholder: 'مثلاً: ۲۵',
    validate: (val) => {
      const err = validators.number(val);
      if (err) return err;
      const num = parseInt(toEnglishDigits(val));
      if (num < 10 || num > 100) return 'سنت باید عددی بین ۱۰ تا ۱۰۰ باشه. 😐';
      return null;
    }
  },
  {
    id: 'weight',
    text: (p) => `وزن فعلیت چقدره؟ (کیلوگرم) ⚖️`,
    placeholder: 'مثلاً: ۷۵',
    validate: (val) => {
      const err = validators.number(val);
      if (err) return err;
      const num = parseInt(toEnglishDigits(val));
      if (num < 30 || num > 200) return 'وزن وارد شده منطقی نیست. لطفاً درست وارد کن. ⚖️';
      return null;
    }
  },
  {
    id: 'height',
    text: (p) => `قدت رو به سانتی‌متر بگو. 📏`,
    placeholder: 'مثلاً: ۱۷۵',
    validate: (val) => {
      const err = validators.number(val);
      if (err) return err;
      const num = parseInt(toEnglishDigits(val));
      if (num < 100 || num > 250) return 'قد وارد شده منطقی نیست. لطفاً به سانتی‌متر بگو (مثلاً ۱۷۰). 📏';
      return null;
    }
  },
  {
    id: 'level',
    text: (p) => `سطح تمرینیت چطوره؟ 🏋️\n(مبتدی / متوسط / حرفه‌ای)`,
    placeholder: 'مبتدی / متوسط / حرفه‌ای',
    options: ['مبتدی', 'متوسط', 'حرفه‌ای'],
    validate: validators.required
  },
  {
    id: 'goal',
    text: (p) => `هدف اصلیت چیه؟ 🎯\n(چربی‌سوزی / عضله‌سازی / فرم‌دهی / افزایش قدرت / سلامت کلی)`,
    placeholder: 'مثلاً: عضله‌سازی',
    options: ['چربی‌سوزی 🔥', 'عضله‌سازی 💪', 'فرم‌دهی 🍑', 'افزایش قدرت 🦍', 'سلامت کلی 🍎'],
    validate: validators.required
  },
  {
    id: 'location',
    text: (p) => `کجا تمرین می‌کنی؟ 🏠\nباشگاه یا خانه؟ (اگر خانه، دقیق وسایل را بگو: دمبل/کابل/کش/نیمکت/هالتر/تردمیل)`,
    placeholder: 'باشگاه / خونه (با دمبل و کش)',
    options: ['باشگاه 🏋️‍♂️', 'خانه (بدون وسیله) 🏠', 'خانه (دمبل دارم)'],
    validate: validators.required
  },
  {
    id: 'frequency',
    text: (p) => `هفته‌ای چند روز می‌تونی تمرین کنی؟ ⏲️`,
    placeholder: 'مثلاً: ۴ روز',
    options: ['۲ روز', '۳ روز', '۴ روز', '۵ روز', '۶ روز'],
    validate: (val) => {
       if (val.length < 1) return 'لطفاً بگو چند روز؟';
       if (!/\d|[۰-۹]|یک|دو|سه|چهار|پنج|شش|هفت/.test(val)) return 'لطفاً تعداد روزها را مشخص کن. 🔢';
       return null;
    }
  },
  {
    id: 'duration',
    text: (p) => `هر جلسه چقدر وقت داری؟ ⏳\n(۴۵ / ۶۰ / ۹۰ دقیقه یا عدد دلخواه)`,
    placeholder: '۶۰ دقیقه',
    options: ['۳۰ دقیقه', '۴۵ دقیقه', '۶۰ دقیقه', '۹۰ دقیقه'],
    validate: validators.required
  },
  {
    id: 'injuries',
    text: (p) => `بیماری یا آسیب زمینه‌ای داری؟ ❤️‍🩹\n(زانو، کمر، فشارخون، تیروئید، دیابت... یا بنویس "سالم")`,
    placeholder: 'سالم / زانو درد دارم',
    options: ['سالم هستم ✅', 'کمر درد', 'زانو درد'],
    validate: validators.required
  },
  {
    id: 'sleep',
    text: (p) => `کیفیت خواب و سطح انرژی امروز چطوره؟ 😴\n(خسته / معمولی / انرژی بالا)`,
    placeholder: 'معمولی',
    options: ['خسته 😫', 'معمولی 😐', 'انرژی بالا ⚡'],
    validate: validators.required
  },
  {
    id: 'diet',
    text: (p) => `رژیم غذایی یا محدودیت غذایی داری؟ توضیح بده. 🍽️`,
    placeholder: 'نه همه چی می‌خورم / گیاهخوارم',
    options: ['همه چی می‌خورم 🍖', 'گیاهخوارم 🥗', 'کتوژنیک 🥑'],
    validate: validators.required
  },
  {
    id: 'bodyType',
    text: (p) => `فرم بدنی تقریبی: 📎\n(اکتومورف / مزومورف / اندومورف)\nاگه نمی‌دونی بگو «نمی‌دونم»`,
    placeholder: 'مزومورف / نمی‌دونم',
    options: ['اکتومورف (لاغر)', 'مزومورف (عضلانی)', 'اندومورف (توپر)', 'نمی‌دونم'],
    validate: validators.required
  },
  {
    id: 'targetAreas',
    text: (p) => `ناحیه‌های هدف (چی رو می‌خوای قوی‌تر/خوش‌فرم‌تر کنی؟) 🎯\nمثلاً: باسن 🍑، شکم 🧊، بازو 💪، پاها...`,
    placeholder: 'شکم و پهلو',
    options: ['شکم و پهلو 🧊', 'باسن و پا 🍑', 'بازو و سرشانه 💪', 'کل بدن 🔥'],
    validate: validators.required
  },
  {
    id: 'history',
    text: (p) => `سابقه تمرینی (چند سال/ماه؟) 🔁`,
    placeholder: '۶ ماه',
    options: ['تازه کارم (۰)', 'زیر ۶ ماه', '۶ ماه تا ۱ سال', 'بالای ۲ سال'],
    validate: validators.required
  },
  {
    id: 'style',
    text: (p) => `سبک تمرینی مورد علاقه: ⚡\n(کلاسیک / فانکشنال / پاورلیفتینگ / فیتنس مدل)`,
    placeholder: 'فیتنس مدل',
    options: ['کلاسیک (بدنسازی)', 'فانکشنال (کراس‌فیت)', 'پاورلیفتینگ (قدرتی)', 'فیتنس مدل (کات)'],
    validate: validators.required
  },
  {
    id: 'motivation',
    text: (p) => `انگیزه-گیر تو چیه؟ 🎯\n(لحن دوستانه / رفاقتی / انگیزشی شدید / جدی)`,
    placeholder: 'انگیزشی شدید',
    options: ['دوستانه و صمیمی 🤗', 'رفاقتی و کول 😎', 'انگیزشی شدید 🔥', 'جدی و نظامی 🎖️'],
    validate: validators.required
  },
  {
    id: 'photo',
    text: (p) => `آیا می‌خواهی عکس فرم بدنت بدون چهره ارسال کنی تا دقیق‌تر آنالیز کنم؟ 📸\n(دکمه دوربین را بزن یا اگر نمی‌خواهی بنویس "نه")`,
    placeholder: 'نه / بله (عکس بفرستید)',
    options: ['نه نمیخوام'],
    inputType: 'image',
    validate: (val) => {
      if (val.startsWith('data:image')) return null; // Image is always valid
      if (val.length < 2) return 'لطفاً یا عکس بفرست یا بنویس "نه".';
      return null;
    }
  },
  {
    id: 'period',
    condition: (p) => p.gender === 'زن',
    text: (p) => `الان در دوران پریود هستی؟ 🌸\n(بله / خیر)`,
    placeholder: 'بله / خیر',
    options: ['بله', 'خیر'],
    validate: validators.yesNo
  },
  {
    id: 'crowded',
    text: (p) => `امروز باشگاه شلوغه یا خلوت؟ 🏋️‍♀️\n(شلوغ / خلوت / فرقی نداره)`,
    placeholder: 'خلوت',
    options: ['خلوت', 'معمولی', 'شلوغ'],
    validate: validators.required
  }
];

export const SYSTEM_PROMPT_TEMPLATE = `
نقش: یک مربی بدنسازی حرفه‌ای، صمیمی و قابل اعتماد به نام "Ghoghnoos AI" که مخصوص کاربران ایرانی برنامه طراحی می‌کند.

لحن مورد نیاز:
- اگر کاربر مرد است: لحن رفاقتی، پرانرژی و انگیزشی (شوخی‌های ملایم مجاز). 😎💪
- اگر کاربر زن است: لحن حمایت‌گرانه، محترمانه، دلگرم‌کننده و انگیزشی (شوخی‌های خیلی ملایم). 🌸✨

مشخصات کاربر:
{{USER_PROFILE}}

نکات حیاتی برای طراحی برنامه تمرینی:
1. **جدول برنامه هوشمند (با لینک ویدیو):**
   - برنامه باید حتماً در قالب **جدول Markdown** باشد.
   - ستون‌ها: **حرکت** | **ست** | **تکرار** | **استراحت** | **تمپو** | **شدت (RPE)**
   - **لینک یوتیوب (حیاتی):** نام هر حرکت را حتماً به صورت لینک جستجوی یوتیوب بنویس تا کاربر ویدیو را ببیند.
     مثال: [اسکات هالتر](https://www.youtube.com/results?search_query=Barbell+Squat+Form)

2. **قانون پیشرفت دوگانه (Double Progression):**
   - در انتهای برنامه، حتماً این قانون را با تیتر درشت توضیح بده:
     «هر زمان توانستی تمام ست‌های یک حرکت را با "سقف تکرار" تعیین شده و فرم صحیح انجام دهی، برای جلسه بعد وزنه را ۲.۵ تا ۵ کیلو افزایش بده.»

3. **استراتژی هفته سبک (Deload Week):** 📉
   - حتماً این تذکر را اضافه کن:
     «بعد از هر ۴ هفته تمرین سنگین، هفته پنجم "هفته دیلود" است. در این هفته وزنه‌ها را ۵۰٪ کاهش دهید و تعداد ست‌ها را کم کنید تا سیستم عصبی ریکاوری شود.»

4. **تکنیک‌های تمرینی:**
   - برای کاربران متوسط و حرفه‌ای: حتماً از تکنیک‌های **دراپ‌ست (Drop Set)** و **سوپرست (Super Set)** در حرکات ایزوله آخر تمرین استفاده کن.
   - برای مبتدی: تمرکز روی اجرای صحیح و تمپوی کنترل شده (مثلاً ۳ ثانیه منفی).

5. **نکات تغذیه و مکمل (ایرانی و اقتصادی):** 🇮🇷🍽️
   - **زمان‌بندی:** دقیق بگو کی بخورند.
   - **معجون حین تمرین (Intra-Workout):** به جای مکمل‌های گران، این فرمول را پیشنهاد بده:
     «۵۰۰ سی‌سی آب + نوک قاشق نمک + آب نصف لیموترش + یک قاشق عسل» (الکترولیت طبیعی).
   - **غذاهای پیشنهادی:** عدسی، لوبیا گرم، کشک بادمجان (کم‌چرب)، میرزاقاسمی (با تخم‌مرغ)، نان سنگک، برنج کته، دوغ کفیر.

6. **شرایط خاص:**
   - اگر کاربر زن است و "پریود" = "بله": حجم تمرین پایین، حذف کرانچ‌های سنگین، تمرکز روی حرکات کششی و یوگا.
   - اگر باشگاه شلوغ است: از نوشتن سوپرست‌هایی که نیاز به دو دستگاه دور از هم دارند خودداری کن.

خروجی نهایی باید شامل موارد زیر باشد (فرمت Markdown تمیز):
1. 📅 برنامه هفتگی روز به روز (جدول‌بندی شده با لینک ویدیوی حرکات)
2. 📝 **جدول ثبت رکورد (Workout Log):** یک جدول خالی برای پرینت که کاربر وزنه‌های هفته ۱ تا ۴ را در آن بنویسد.
3. 🔁 جایگزین‌های حرکات برای باشگاه‌های ناقص
4. 🧘 گرم کردن ۵ دقیقه + موبیلیتی + سرد کردن ۳-۵ دقیقه
5. 📈 توضیحات پیشرفت (Double Progression + Deload Week)
6. 🍽️ برنامه تغذیه‌ای اقتصادی + دستور معجون حین تمرین
7. 🎧 پلی‌لیست پیشنهادی (نسخه دخترانه / پسرانه)

امضای پایان:
«با عشق و قدرت تقدیمت کردم ✨
🏋️‍♂️🔥 Ghoghnoos AI — مربی شخصی تو
هر روز قوی‌تر از دیروز 💪🔥»
`;
