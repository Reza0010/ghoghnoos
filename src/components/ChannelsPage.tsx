import React, { useState } from 'react';
import {
  Radio,
  Plus,
  CheckCircle2,
  XCircle,
  Trash2,
  Shield,
  Send,
  RefreshCw,
  ExternalLink,
  AlertCircle
} from 'lucide-react';

interface Channel {
  id: number;
  name: string;
  chat_id: string;
  alias: string;
  enabled: boolean;
  token_key: string;
  created_at: string;
  last_test_at?: string;
  last_test_ok?: boolean;
  last_error?: string;
}

interface ChannelsPageProps {
  channels: Channel[];
  onAddChannel: (channel: Partial<Channel>) => Promise<void>;
  onToggleChannel: (id: number, enabled: boolean) => Promise<void>;
  onDeleteChannel: (id: number) => Promise<void>;
  onTestChannel: (id: number) => Promise<any>;
}

export const ChannelsPage: React.FC<ChannelsPageProps> = ({
  channels,
  onAddChannel,
  onToggleChannel,
  onDeleteChannel,
  onTestChannel
}) => {
  const [showAddModal, setShowAddModal] = useState(false);
  const [testingId, setTestingId] = useState<number | null>(null);
  const [testResult, setTestResult] = useState<{ id: number; ok: boolean; msg: string } | null>(null);

  // Form State
  const [name, setName] = useState('');
  const [chatId, setChatId] = useState('');
  const [alias, setAlias] = useState('');
  const [tokenKey, setTokenKey] = useState('default');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !chatId.trim()) return;
    setIsSubmitting(true);
    try {
      await onAddChannel({
        name,
        chat_id: chatId.startsWith('@') || chatId.startsWith('-100') ? chatId : `@${chatId}`,
        alias: alias || name,
        token_key: tokenKey
      });
      setShowAddModal(false);
      setName('');
      setChatId('');
      setAlias('');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTest = async (id: number) => {
    setTestingId(id);
    setTestResult(null);
    try {
      const res = await onTestChannel(id);
      setTestResult({
        id,
        ok: true,
        msg: `اتصال ربات به کانال با موفقیت تأیید شد. دسترسی ارسال پیام فعال است.`
      });
    } catch (err: any) {
      setTestResult({
        id,
        ok: false,
        msg: `خطا در برقراری ارتباط با Bot API: ${err.message || 'عدم دسترسی ربات به عنوان ادمین'}`
      });
    } finally {
      setTestingId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-[#121a23] border border-[#22303f] p-5 rounded-xl">
        <div>
          <h2 className="text-base font-bold text-[#e8eef5] flex items-center gap-2">
            <Radio className="w-5 h-5 text-[#f7931a]" />
            مدیریت کانال‌های تلگرام و دسترسی Bot API
          </h2>
          <p className="text-xs text-[#93a4b6] mt-1">
            ربات باید در کانال‌های مقصد به عنوان مدیر (Administrator) با دسترسی ارسال پیام اضافه شده باشد.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-[#f7931a] hover:bg-[#ffa633] text-[#0b0f14] font-bold text-xs px-4 py-2.5 rounded-lg flex items-center gap-2 transition-colors shrink-0 cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          افزودن کانال جدید
        </button>
      </div>

      {/* Test Result Alert */}
      {testResult && (
        <div className={`p-4 rounded-xl border flex items-start gap-3 text-xs ${
          testResult.ok
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
            : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
        }`}>
          {testResult.ok ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
          ) : (
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          )}
          <div className="flex-1">
            <div className="font-semibold">{testResult.ok ? 'تست موفقیت‌آمیز' : 'خطای اتصال'}</div>
            <div className="mt-0.5 opacity-90">{testResult.msg}</div>
          </div>
          <button
            onClick={() => setTestResult(null)}
            className="text-slate-400 hover:text-white"
          >
            ×
          </button>
        </div>
      )}

      {/* Channels List Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {channels.map((chan) => (
          <div
            key={chan.id}
            className={`bg-[#121a23] border rounded-xl p-5 flex flex-col justify-between transition-all ${
              chan.enabled ? 'border-[#22303f] hover:border-[#f7931a]/40' : 'border-rose-950/40 opacity-70'
            }`}
          >
            <div>
              <div className="flex items-start justify-between gap-2 mb-3">
                <div>
                  <span className="text-[11px] font-mono text-[#f7931a] bg-[#f7931a]/10 px-2 py-0.5 rounded">
                    {chan.alias}
                  </span>
                  <h3 className="text-sm font-bold text-[#e8eef5] mt-1.5 line-clamp-1">
                    {chan.name}
                  </h3>
                </div>

                <div className="flex items-center gap-1">
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                    chan.enabled
                      ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                      : 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                  }`}>
                    {chan.enabled ? 'فعال' : 'غیرفعال'}
                  </span>
                </div>
              </div>

              <div className="space-y-2 text-xs py-2 border-y border-[#22303f]/50 my-3">
                <div className="flex items-center justify-between text-[#93a4b6]">
                  <span>شناسه تلگرام (Chat ID):</span>
                  <span className="font-mono text-[#e8eef5] dir-ltr text-left font-semibold">
                    {chan.chat_id}
                  </span>
                </div>
                <div className="flex items-center justify-between text-[#93a4b6]">
                  <span>کلید توکن ربات:</span>
                  <span className="font-mono text-[#64748b] text-[11px] flex items-center gap-1">
                    <Shield className="w-3 h-3 text-[#f7931a]" />
                    {chan.token_key}
                  </span>
                </div>
                <div className="flex items-center justify-between text-[#93a4b6]">
                  <span>آخرین آزمون اتصال:</span>
                  <span className="text-[11px]">
                    {chan.last_test_at
                      ? new Date(chan.last_test_at).toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' })
                      : 'انجام نشده'}
                  </span>
                </div>
              </div>
            </div>

            <div className="pt-2 flex items-center justify-between gap-2">
              <button
                onClick={() => handleTest(chan.id)}
                disabled={testingId === chan.id}
                className="flex-1 bg-[#17212d] hover:bg-[#22303f] text-[#e8eef5] py-2 px-3 rounded-lg text-xs font-medium flex items-center justify-center gap-1.5 transition-colors cursor-pointer border border-[#22303f]"
              >
                <RefreshCw className={`w-3.5 h-3.5 text-[#f7931a] ${testingId === chan.id ? 'animate-spin' : ''}`} />
                <span>{testingId === chan.id ? 'در حال آزمون...' : 'آزمون اتصال'}</span>
              </button>

              <button
                onClick={() => onToggleChannel(chan.id, !chan.enabled)}
                className={`py-2 px-3 rounded-lg text-xs font-medium transition-colors cursor-pointer ${
                  chan.enabled
                    ? 'bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20'
                    : 'bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20'
                }`}
                title={chan.enabled ? 'غیرفعال‌سازی موقت' : 'فعال‌سازی'}
              >
                {chan.enabled ? 'تعلیق' : 'فعال'}
              </button>

              <button
                onClick={() => onDeleteChannel(chan.id)}
                className="p-2 bg-[#17212d] hover:bg-rose-500/20 text-[#64748b] hover:text-rose-400 rounded-lg transition-colors cursor-pointer border border-[#22303f]"
                title="حذف کانال"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Add Channel Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#121a23] border border-[#22303f] rounded-2xl w-full max-w-md p-6 relative">
            <h3 className="text-base font-bold text-[#e8eef5] mb-4 flex items-center gap-2">
              <Plus className="w-5 h-5 text-[#f7931a]" />
              افزودن کانال تلگرام جدید
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-[#93a4b6] mb-1.5">
                  نام نمایشی کانال:
                </label>
                <input
                  type="text"
                  required
                  placeholder="مثال: کانال تخصصی تعمیرات ماینر"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3.5 py-2 text-xs text-[#e8eef5] focus:outline-none focus:border-[#f7931a]"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-[#93a4b6] mb-1.5">
                  آیدی عمومی یا شناسه عددی (Chat ID):
                </label>
                <input
                  type="text"
                  required
                  placeholder="مثال: @MinerRepair_IR یا -100123456789"
                  value={chatId}
                  onChange={(e) => setChatId(e.target.value)}
                  className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3.5 py-2 text-xs text-[#e8eef5] dir-ltr text-left focus:outline-none focus:border-[#f7931a] font-mono"
                />
                <span className="text-[10px] text-[#64748b] mt-1 block">
                  ربات باید ادمین با دسترسی Post Messages باشد.
                </span>
              </div>

              <div>
                <label className="block text-xs font-medium text-[#93a4b6] mb-1.5">
                  نام مستعار کوتاه (جهت نمایش در تب‌ها):
                </label>
                <input
                  type="text"
                  placeholder="مثال: تعمیرات ۱"
                  value={alias}
                  onChange={(e) => setAlias(e.target.value)}
                  className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3.5 py-2 text-xs text-[#e8eef5] focus:outline-none focus:border-[#f7931a]"
                />
              </div>

              <div className="pt-2 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-[#17212d] hover:bg-[#22303f] text-[#93a4b6] rounded-lg text-xs cursor-pointer"
                >
                  انصراف
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2 bg-[#f7931a] hover:bg-[#ffa633] text-[#0b0f14] font-bold rounded-lg text-xs cursor-pointer disabled:opacity-50"
                >
                  {isSubmitting ? 'در حال ثبت...' : 'ثبت و اتصال کانال'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
