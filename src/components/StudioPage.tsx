import React, { useState } from 'react';
import {
  Sparkles,
  Zap,
  CheckCircle2,
  CalendarClock,
  Save,
  AlertTriangle,
  Cpu,
  Layers,
  Hash,
  Send,
  RefreshCw,
  FileCheck
} from 'lucide-react';

export const CONTENT_CATEGORIES = [
  { id: 'repair_tutorial', name: 'آموزش تعمیرات ماینر', icon: '🔧' },
  { id: 'hashboard_debug', name: 'عیب‌یابی هش‌برد', icon: '🔍' },
  { id: 'controlboard_repair', name: 'تعمیر کنترل‌برد', icon: '🎛️' },
  { id: 'psu_repair', name: 'تعمیر پاور و PSU', icon: '⚡' },
  { id: 'antminer_errors', name: 'خطاهای رایج Antminer', icon: '🐜' },
  { id: 'whatsminer_errors', name: 'خطای رایج WhatsMiner', icon: '⚙️' },
  { id: 'mining_industry', name: 'اخبار صنعت ماینینگ', icon: '🏭' },
  { id: 'bitcoin_network', name: 'اخبار بیت‌کوین و شبکه', icon: '⛓️' },
  { id: 'coin_market', name: 'قیمت و اخبار ارزهای ماینینگ', icon: '💰' },
  { id: 'tools_tutorial', name: 'آموزش تجهیزات تعمیرگاهی', icon: '🛠️' },
  { id: 'safety_tips', name: 'نکات ایمنی تعمیرات', icon: '⚠️' },
  { id: 'services_intro', name: 'معرفی خدمات و ابزارها', icon: '📢' },
];

export const CONTENT_TYPES = [
  { id: 'short_post', name: 'پست آموزشی کوتاه (۱۲۰ تا ۲۰۰ کلمه)' },
  { id: 'tutorial', name: 'آموزش تخصصی مرحله‌به‌مرحله' },
  { id: 'news_flash', name: 'خبر فوری با تاریخ و منبع' },
  { id: 'news_analysis', name: 'تحلیل خبر و پیامدها' },
  { id: 'part_intro', name: 'معرفی قطعه و کاربرد' },
  { id: 'troubleshooting', name: 'نکات عیب‌یابی و ترفندها' },
  { id: 'comparison', name: 'مقایسه فنی دو مدل' },
  { id: 'image_post', name: 'پست همراه تصویر یا دیاگرام' },
  { id: 'caption_hashtag', name: 'کپشن و هشتگ اختصاصی' },
  { id: 'series', name: 'مجموعه پست‌های دنباله‌دار' },
];

interface StudioPageProps {
  drafts: any[];
  channels: any[];
  onGenerate: (params: any) => Promise<any>;
  onSaveDraft: (id: number, data: any) => Promise<void>;
  onScheduleDraft: (id: number, channelId: number, scheduledAt: string) => Promise<void>;
}

export const StudioPage: React.FC<StudioPageProps> = ({
  drafts,
  channels,
  onGenerate,
  onSaveDraft,
  onScheduleDraft
}) => {
  const [category, setCategory] = useState('hashboard_debug');
  const [ctype, setCtype] = useState('tutorial');
  const [topic, setTopic] = useState('');
  const [keywords, setKeywords] = useState('');
  const [includeMarket, setIncludeMarket] = useState(true);
  const [targetChannelId, setTargetChannelId] = useState(channels[0]?.id?.toString() || '1');
  const [isGenerating, setIsGenerating] = useState(false);

  // Active Draft in Editor
  const [activeDraft, setActiveDraft] = useState<any>(drafts[0] || null);
  const [editedTitle, setEditedTitle] = useState(activeDraft?.title || '');
  const [editedBody, setEditedBody] = useState(activeDraft?.body || '');
  const [editedHashtags, setEditedHashtags] = useState(activeDraft?.hashtags || '');

  // Schedule Drawer
  const [showScheduleBox, setShowScheduleBox] = useState(false);
  const [schedTime, setSchedTime] = useState('');

  const handleSelectDraft = (d: any) => {
    setActiveDraft(d);
    setEditedTitle(d.title);
    setEditedBody(d.body);
    setEditedHashtags(d.hashtags);
  };

  const handleGenerateClick = async () => {
    setIsGenerating(true);
    try {
      const res = await onGenerate({
        category,
        ctype,
        topic,
        keywords,
        include_market: includeMarket,
        target_channel_id: Number(targetChannelId)
      });
      if (res && res.draft) {
        handleSelectDraft(res.draft);
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSave = async () => {
    if (!activeDraft) return;
    await onSaveDraft(activeDraft.id, {
      title: editedTitle,
      body: editedBody,
      hashtags: editedHashtags,
      status: 'review'
    });
  };

  const handleSchedule = async () => {
    if (!activeDraft) return;
    await onScheduleDraft(activeDraft.id, Number(targetChannelId), schedTime || new Date(Date.now() + 3600000).toISOString());
    setShowScheduleBox(false);
  };

  return (
    <div className="space-y-6">
      {/* Studio Header Banner */}
      <div className="bg-[#121a23] border border-[#22303f] p-5 rounded-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-[#e8eef5] flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-[#f7931a]" />
              استودیوی تولید محتوای هوشمند ماینینگ و الکترونیک صنعتی
            </h2>
            <p className="text-xs text-[#93a4b6] mt-1">
              مبتنی بر قوانین تخصصی: عدم اختراع ولتاژ و شماره پایه، تزریق نرخ‌های واقعی نوبیتکس، و درج هشدارهای ایمنی.
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="bg-[#17212d] border border-[#22303f] px-3 py-1.5 rounded-lg text-[#93a4b6] flex items-center gap-1.5 font-mono">
              <Cpu className="w-3.5 h-3.5 text-[#f7931a]" />
              مدل: Gemini 2.5 Flash
            </span>
          </div>
        </div>
      </div>

      {/* Main Grid: Parameters on Right, Editor on Left */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Parameters Column (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-[#121a23] border border-[#22303f] rounded-xl p-5 space-y-4 text-xs">
            <h3 className="font-bold text-[#e8eef5] text-sm flex items-center gap-2">
              <Layers className="w-4 h-4 text-[#f7931a]" />
              پارامترهای تولید پست
            </h3>

            <div>
              <label className="block text-[#93a4b6] font-medium mb-1.5">
                دسته‌بندی تخصصی (۱۲ حوزه):
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3 py-2 text-[#e8eef5] focus:outline-none focus:border-[#f7931a]"
              >
                {CONTENT_CATEGORIES.map(c => (
                  <option key={c.id} value={c.id}>
                    {c.icon} {c.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[#93a4b6] font-medium mb-1.5">
                قالب و فرمت خروجی (۱۰ نوع):
              </label>
              <select
                value={ctype}
                onChange={(e) => setCtype(e.target.value)}
                className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3 py-2 text-[#e8eef5] focus:outline-none focus:border-[#f7931a]"
              >
                {CONTENT_TYPES.map(t => (
                  <option key={t.id} value={t.id}>
                    {t.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[#93a4b6] font-medium mb-1.5">
                موضوع یا سؤال اصلی (اختیاری):
              </label>
              <input
                type="text"
                placeholder="مثال: روش تست مقاومت صفر اهم در هش‌برد S19j Pro"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3 py-2 text-[#e8eef5] focus:outline-none focus:border-[#f7931a]"
              />
            </div>

            <div>
              <label className="block text-[#93a4b6] font-medium mb-1.5">
                کلیدواژه‌ها یا قطعات خاص:
              </label>
              <input
                type="text"
                placeholder="BM1398, LDO 1.8V, اسیلوسکوپ, خازن تانتالیوم"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3 py-2 text-[#e8eef5] focus:outline-none focus:border-[#f7931a]"
              />
            </div>

            <div className="flex items-center gap-2 pt-1">
              <input
                type="checkbox"
                id="inc_market"
                checked={includeMarket}
                onChange={(e) => setIncludeMarket(e.target.checked)}
                className="rounded border-[#22303f] text-[#f7931a] focus:ring-0"
              />
              <label htmlFor="inc_market" className="text-[#93a4b6] cursor-pointer">
                تزریق نرخ‌های لحظه‌ای نوبیتکس در انتهای پست
              </label>
            </div>

            <button
              onClick={handleGenerateClick}
              disabled={isGenerating}
              className="w-full mt-2 py-3 bg-[#f7931a] hover:bg-[#ffa633] text-[#0b0f14] font-bold rounded-lg flex items-center justify-center gap-2 transition-colors cursor-pointer disabled:opacity-50 text-xs shadow-lg shadow-[#f7931a]/10"
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  در حال استخراج و نگارش با هوش مصنوعی...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  تولید پیش‌نویس با موتور AI
                </>
              )}
            </button>
          </div>

          {/* Drafts History List */}
          <div className="bg-[#121a23] border border-[#22303f] rounded-xl p-4 text-xs">
            <h4 className="font-bold text-[#e8eef5] mb-3 flex items-center justify-between">
              <span>پیش‌نویس‌های اخیر ({drafts.length})</span>
              <FileCheck className="w-3.5 h-3.5 text-[#93a4b6]" />
            </h4>
            <div className="space-y-2 max-h-56 overflow-y-auto">
              {drafts.map(d => (
                <div
                  key={d.id}
                  onClick={() => handleSelectDraft(d)}
                  className={`p-2.5 rounded-lg border transition-all cursor-pointer ${
                    activeDraft?.id === d.id
                      ? 'bg-[#17212d] border-[#f7931a]/60 text-[#e8eef5]'
                      : 'bg-[#0e141b] border-[#22303f] text-[#93a4b6] hover:border-slate-600'
                  }`}
                >
                  <div className="font-semibold line-clamp-1">{d.title}</div>
                  <div className="flex items-center justify-between text-[10px] text-[#64748b] mt-1">
                    <span>{d.meta?.category_name || d.category}</span>
                    <span className="capitalize">{d.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Editor Column (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="bg-[#121a23] border border-[#22303f] rounded-xl p-5 flex flex-col justify-between space-y-4">
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[#22303f]">
                <div>
                  <h3 className="text-sm font-bold text-[#e8eef5]">ویرایشگر و پیش‌نمایش خروجی</h3>
                  <span className="text-[11px] text-[#64748b]">
                    طراحی شده متناسب با پیام‌های کانال تلگرام
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-[10px] bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2 py-0.5 rounded-full flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" />
                    نیازمند بازبینی و تأیید فنی
                  </span>
                </div>
              </div>

              {/* Title Input */}
              <div>
                <label className="block text-xs font-medium text-[#93a4b6] mb-1">
                  عنوان مطلب:
                </label>
                <input
                  type="text"
                  value={editedTitle}
                  onChange={(e) => setEditedTitle(e.target.value)}
                  placeholder="عنوان پست..."
                  className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3.5 py-2 text-sm font-bold text-[#e8eef5] focus:outline-none focus:border-[#f7931a]"
                />
              </div>

              {/* Body Textarea */}
              <div>
                <label className="block text-xs font-medium text-[#93a4b6] mb-1">
                  متن اصلی (فارسی روان و حرفه‌ای):
                </label>
                <textarea
                  rows={10}
                  value={editedBody}
                  onChange={(e) => setEditedBody(e.target.value)}
                  placeholder="محتوای تولید شده در اینجا ظاهر می‌شود..."
                  className="w-full bg-[#0e141b] border border-[#22303f] rounded-lg p-3.5 text-xs text-[#e8eef5] focus:outline-none focus:border-[#f7931a] font-sans leading-relaxed resize-y"
                />
              </div>

              {/* Hashtags */}
              <div>
                <label className="block text-xs font-medium text-[#93a4b6] mb-1 flex items-center gap-1">
                  <Hash className="w-3 h-3 text-[#f7931a]" />
                  هشتگ‌های تخصصی:
                </label>
                <input
                  type="text"
                  value={editedHashtags}
                  onChange={(e) => setEditedHashtags(e.target.value)}
                  placeholder="#ماینینگ #تعمیرات_هشبرد ..."
                  className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3.5 py-2 text-xs text-[#f7931a] focus:outline-none focus:border-[#f7931a] font-sans"
                />
              </div>
            </div>

            {/* Bottom Actions */}
            <div className="pt-4 border-t border-[#22303f] flex flex-wrap items-center justify-between gap-3 text-xs">
              <button
                onClick={handleSave}
                className="bg-[#17212d] hover:bg-[#22303f] text-[#e8eef5] border border-[#22303f] px-4 py-2 rounded-lg font-medium flex items-center gap-1.5 transition-colors cursor-pointer"
              >
                <Save className="w-4 h-4 text-emerald-400" />
                ذخیره پیش‌نویس
              </button>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowScheduleBox(!showScheduleBox)}
                  className="bg-[#f7931a] hover:bg-[#ffa633] text-[#0b0f14] font-bold px-4 py-2 rounded-lg flex items-center gap-1.5 transition-colors cursor-pointer"
                >
                  <CalendarClock className="w-4 h-4" />
                  تأیید و زمان‌بندی انتشار
                </button>
              </div>
            </div>

            {/* Inline Schedule Box */}
            {showScheduleBox && (
              <div className="p-4 bg-[#17212d] border border-[#f7931a]/40 rounded-xl space-y-3 text-xs">
                <div className="font-bold text-[#e8eef5]">تنظیم انتشار در تلگرام:</div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-[#93a4b6] block mb-1">کانال:</label>
                    <select
                      value={targetChannelId}
                      onChange={(e) => setTargetChannelId(e.target.value)}
                      className="w-full bg-[#0e141b] border border-[#22303f] rounded p-2 text-[#e8eef5]"
                    >
                      {channels.map(c => (
                        <option key={c.id} value={c.id.toString()}>{c.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="text-[#93a4b6] block mb-1">زمان انتشار:</label>
                    <input
                      type="datetime-local"
                      value={schedTime}
                      onChange={(e) => setSchedTime(e.target.value)}
                      className="w-full bg-[#0e141b] border border-[#22303f] rounded p-2 text-[#e8eef5]"
                    />
                  </div>
                </div>
                <div className="flex justify-end gap-2 pt-1">
                  <button
                    onClick={() => setShowScheduleBox(false)}
                    className="px-3 py-1.5 bg-[#0e141b] text-[#93a4b6] rounded"
                  >
                    انصراف
                  </button>
                  <button
                    onClick={handleSchedule}
                    className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded"
                  >
                    افزودن به تقویم صف
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
