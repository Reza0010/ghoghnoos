import React, { useState } from 'react';
import {
  Settings,
  ShieldCheck,
  Save,
  Radio,
  Zap,
  Cpu,
  Clock,
  Key,
  CheckCircle2,
  HardDrive
} from 'lucide-react';

interface SettingsPageProps {
  settings: any;
  onSaveSettings: (settings: any) => Promise<void>;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({
  settings,
  onSaveSettings
}) => {
  const [appName, setAppName] = useState(settings?.app_name || 'MinerMedia AI');
  const [appSubtitle, setAppSubtitle] = useState(settings?.app_subtitle || 'Smart Mining & Crypto Channel Manager');
  const [timezone, setTimezone] = useState(settings?.timezone || 'Asia/Tehran');
  const [marketInterval, setMarketInterval] = useState(settings?.market_refresh_sec?.toString() || '60');
  const [aiModel, setAiModel] = useState(settings?.ai_model || 'gemini-2.5-flash');
  const [aiTemp, setAiTemp] = useState(settings?.ai_temperature?.toString() || '0.7');
  const [autoPublish, setAutoPublish] = useState(settings?.auto_publish || false);
  const [isSaving, setIsSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setSavedSuccess(false);
    try {
      await onSaveSettings({
        app_name: appName,
        app_subtitle: appSubtitle,
        timezone,
        market_refresh_sec: Number(marketInterval),
        ai_model: aiModel,
        ai_temperature: parseFloat(aiTemp),
        auto_publish: autoPublish
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-[#121a23] border border-[#22303f] p-5 rounded-xl">
        <div className="flex items-center gap-2">
          <Settings className="w-5 h-5 text-[#f7931a]" />
          <h2 className="text-base font-bold text-[#e8eef5]">
            تنظیمات پیکربندی، کلیدهای ارتباطی و امنیت
          </h2>
        </div>
        <p className="text-xs text-[#93a4b6] mt-1">
          تنظیمات عمومی سامانه، سقف نرخ‌های ارتباطی API نوبیتکس، و مدل‌های هوش مصنوعی.
        </p>
      </div>

      {savedSuccess && (
        <div className="p-3.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 rounded-xl text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>تنظیمات با موفقیت ذخیره شد و در کل سیستم اعمال گردید.</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* App Identity Section */}
        <div className="bg-[#121a23] border border-[#22303f] rounded-xl p-5 space-y-4 text-xs">
          <h3 className="text-sm font-bold text-[#e8eef5] flex items-center gap-2 pb-2 border-b border-[#22303f]">
            <HardDrive className="w-4 h-4 text-[#f7931a]" />
            هویت و منطقه زمانی نرم‌افزار
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-[#93a4b6] font-medium mb-1.5">
                نام برنامه:
              </label>
              <input
                type="text"
                value={appName}
                onChange={(e) => setAppName(e.target.value)}
                className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3.5 py-2 text-[#e8eef5] focus:outline-none focus:border-[#f7931a]"
              />
            </div>

            <div>
              <label className="block text-[#93a4b6] font-medium mb-1.5">
                زیرعنوان نمایشی:
              </label>
              <input
                type="text"
                value={appSubtitle}
                onChange={(e) => setAppSubtitle(e.target.value)}
                className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3.5 py-2 text-[#e8eef5] focus:outline-none focus:border-[#f7931a]"
              />
            </div>
          </div>

          <div>
            <label className="block text-[#93a4b6] font-medium mb-1.5">
              منطقه زمانی پیش‌فرض انتشار:
            </label>
            <select
              value={timezone}
              onChange={(e) => setTimezone(e.target.value)}
              className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3.5 py-2 text-[#e8eef5] focus:outline-none focus:border-[#f7931a] font-mono text-left dir-ltr"
            >
              <option value="Asia/Tehran">Asia/Tehran (GMT +3:30)</option>
              <option value="UTC">UTC (GMT +0:00)</option>
              <option value="Asia/Dubai">Asia/Dubai (GMT +4:00)</option>
            </select>
          </div>
        </div>

        {/* Nobitex API Settings */}
        <div className="bg-[#121a23] border border-[#22303f] rounded-xl p-5 space-y-4 text-xs">
          <h3 className="text-sm font-bold text-[#e8eef5] flex items-center gap-2 pb-2 border-b border-[#22303f]">
            <Zap className="w-4 h-4 text-emerald-400" />
            تنظیمات دریافت نرخ‌های نوبیتکس (Rate Limiting)
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-[#93a4b6] font-medium mb-1.5">
                فاصله زمانی به‌روزرسانی خودکار قیمت‌ها (ثانیه):
              </label>
              <input
                type="number"
                min="30"
                max="3600"
                value={marketInterval}
                onChange={(e) => setMarketInterval(e.target.value)}
                className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3.5 py-2 text-[#e8eef5] focus:outline-none font-mono"
              />
              <span className="text-[10px] text-[#64748b] mt-1 block">
                حداقل ۳۰ ثانیه جهت جلوگیری از مسدود شدن و دریافت خطای 429 Too Many Requests
              </span>
            </div>

            <div>
              <label className="block text-[#93a4b6] font-medium mb-1.5">
                آدرس سرور پایه نوبیتکس:
              </label>
              <input
                type="text"
                disabled
                value="https://apiv2.nobitex.ir"
                className="w-full bg-[#0e141b] border border-[#22303f] rounded-lg px-3.5 py-2 text-[#64748b] font-mono text-left dir-ltr cursor-not-allowed"
              />
            </div>
          </div>
        </div>

        {/* AI Model Settings */}
        <div className="bg-[#121a23] border border-[#22303f] rounded-xl p-5 space-y-4 text-xs">
          <h3 className="text-sm font-bold text-[#e8eef5] flex items-center gap-2 pb-2 border-b border-[#22303f]">
            <Cpu className="w-4 h-4 text-[#f7931a]" />
            موتور هوش مصنوعی استودیو (AI Provider)
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-[#93a4b6] font-medium mb-1.5">
                مدل پردازش محتوا:
              </label>
              <select
                value={aiModel}
                onChange={(e) => setAiModel(e.target.value)}
                className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3.5 py-2 text-[#e8eef5] focus:outline-none font-mono text-left dir-ltr"
              >
                <option value="gemini-2.5-flash">gemini-2.5-flash (توصیه شده - سریع و دقیق)</option>
                <option value="gemini-2.5-pro">gemini-2.5-pro (استدلال عمیق مهندسی)</option>
                <option value="miner-expert-v2">موتور تخصصی عیب‌یابی هش‌برد (آفلاین)</option>
              </select>
            </div>

            <div>
              <label className="block text-[#93a4b6] font-medium mb-1.5">
                درجه خلاقیت (Temperature):
              </label>
              <input
                type="number"
                step="0.1"
                min="0.1"
                max="1.0"
                value={aiTemp}
                onChange={(e) => setAiTemp(e.target.value)}
                className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3.5 py-2 text-[#e8eef5] focus:outline-none font-mono"
              />
              <span className="text-[10px] text-[#64748b] mt-1 block">
                مقدار 0.7 توازن بهینه بین دقت فنی و روانی متن را فراهم می‌آورد.
              </span>
            </div>
          </div>
        </div>

        {/* Security & Credentials info */}
        <div className="bg-[#121a23] border border-[#22303f] rounded-xl p-5 space-y-3 text-xs">
          <h3 className="text-sm font-bold text-[#e8eef5] flex items-center gap-2 pb-2 border-b border-[#22303f]">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            امنیت و مدیریت محرمانگی (Secret Store)
          </h3>

          <div className="bg-[#0e141b] rounded-lg p-3.5 border border-[#22303f] text-[#93a4b6] leading-relaxed">
            <p>
              کلیدهای Bot API و توکن‌های اتصال در فضای امن سرور ذخیره می‌شوند. طبق الزامات امنیتی v2.0.1، هیچ کلید یا توکنی در لاگ‌های ممیزی یا پاسخ‌های عمومی درج نمی‌گردد و ماژول <code className="text-[#f7931a] font-mono">redact</code> پیش از ثبت پیام‌ها، مقادیر حساس را سانسور می‌نماید.
            </p>
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={isSaving}
            className="px-6 py-2.5 bg-[#f7931a] hover:bg-[#ffa633] text-[#0b0f14] font-bold rounded-lg text-xs flex items-center gap-2 transition-colors cursor-pointer disabled:opacity-50 shadow-lg shadow-[#f7931a]/10"
          >
            <Save className="w-4 h-4" />
            <span>{isSaving ? 'در حال ذخیره‌سازی...' : 'ذخیره تنظیمات'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
