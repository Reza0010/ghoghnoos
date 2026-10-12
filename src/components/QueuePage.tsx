import React, { useState } from 'react';
import {
  CalendarClock,
  Plus,
  Send,
  XCircle,
  RotateCcw,
  CheckCircle2,
  Clock,
  AlertTriangle,
  FileText,
  Image as ImageIcon,
  Video,
  FileCode,
  Layers,
  History
} from 'lucide-react';

interface ScheduledPost {
  id: number;
  group_uuid: string;
  channel_id: number;
  content_type: 'text' | 'photo' | 'video' | 'audio' | 'document' | 'album';
  title?: string;
  body: string;
  media_path: string;
  scheduled_at: string;
  timezone: string;
  status: 'draft' | 'pending' | 'processing' | 'sent' | 'failed' | 'unknown' | 'cancelled';
  attempts: number;
  max_attempts: number;
  created_at: string;
  telegram_message_id?: number;
  source: string;
  split_long_text?: boolean;
}

interface QueuePageProps {
  posts: ScheduledPost[];
  channels: any[];
  onAddPost: (post: any) => Promise<void>;
  onCancelPost: (id: number) => Promise<void>;
  onRetryPost: (id: number) => Promise<void>;
  onPublishNow: (id: number) => Promise<void>;
  onViewAttempts: (id: number) => Promise<any[]>;
}

export const QueuePage: React.FC<QueuePageProps> = ({
  posts,
  channels,
  onAddPost,
  onCancelPost,
  onRetryPost,
  onPublishNow,
  onViewAttempts
}) => {
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterChannel, setFilterChannel] = useState<string>('all');
  const [showAddModal, setShowAddModal] = useState(false);

  // Attempt History Modal
  const [historyModal, setHistoryModal] = useState<{ open: boolean; postId?: number; attempts: any[] }>({
    open: false,
    attempts: []
  });

  // Form State
  const [channelId, setChannelId] = useState(channels[0]?.id?.toString() || '1');
  const [contentType, setContentType] = useState<'text' | 'photo' | 'video' | 'document'>('text');
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [mediaPath, setMediaPath] = useState('');
  const [scheduledAt, setScheduledAt] = useState('');
  const [splitLongText, setSplitLongText] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const filteredPosts = posts.filter(p => {
    if (filterStatus !== 'all' && p.status !== filterStatus) return false;
    if (filterChannel !== 'all' && p.channel_id.toString() !== filterChannel) return false;
    return true;
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!body.trim()) return;
    setIsSubmitting(true);
    try {
      await onAddPost({
        channel_id: Number(channelId),
        content_type: contentType,
        title,
        body,
        media_path: mediaPath,
        scheduled_at: scheduledAt ? new Date(scheduledAt).toISOString() : new Date(Date.now() + 3600000).toISOString(),
        split_long_text: splitLongText
      });
      setShowAddModal(false);
      setTitle('');
      setBody('');
      setMediaPath('');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleShowAttempts = async (id: number) => {
    try {
      const attempts = await onViewAttempts(id);
      setHistoryModal({ open: true, postId: id, attempts: attempts || [] });
    } catch {
      setHistoryModal({ open: true, postId: id, attempts: [] });
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'photo': return <ImageIcon className="w-4 h-4 text-sky-400" />;
      case 'video': return <Video className="w-4 h-4 text-purple-400" />;
      case 'document': return <FileCode className="w-4 h-4 text-amber-400" />;
      default: return <FileText className="w-4 h-4 text-emerald-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'sent':
        return <span className="bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-2.5 py-0.5 rounded-full text-[11px] font-medium flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> ارسال شده</span>;
      case 'pending':
        return <span className="bg-amber-500/15 text-amber-400 border border-amber-500/30 px-2.5 py-0.5 rounded-full text-[11px] font-medium flex items-center gap-1"><Clock className="w-3 h-3" /> در انتظار ارسال</span>;
      case 'processing':
        return <span className="bg-sky-500/15 text-sky-400 border border-sky-500/30 px-2.5 py-0.5 rounded-full text-[11px] font-medium flex items-center gap-1"><RotateCcw className="w-3 h-3 animate-spin" /> در حال پردازش</span>;
      case 'cancelled':
        return <span className="bg-slate-700/50 text-slate-400 border border-slate-700 px-2.5 py-0.5 rounded-full text-[11px] font-medium flex items-center gap-1"><XCircle className="w-3 h-3" /> لغو شده</span>;
      case 'failed':
        return <span className="bg-rose-500/15 text-rose-400 border border-rose-500/30 px-2.5 py-0.5 rounded-full text-[11px] font-medium flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> ناموفق</span>;
      default:
        return <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded text-[11px]">{status}</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Filter and Action Bar */}
      <div className="bg-[#121a23] border border-[#22303f] p-4 rounded-xl flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 text-xs text-[#93a4b6]">
            <span>فیلتر وضعیت:</span>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="bg-[#17212d] border border-[#22303f] text-[#e8eef5] rounded-lg px-2.5 py-1.5 text-xs focus:outline-none"
            >
              <option value="all">همه وضعیت‌ها</option>
              <option value="pending">در انتظار زمان‌بندی</option>
              <option value="sent">ارسال شده‌ها</option>
              <option value="draft">پیش‌نویس‌ها</option>
              <option value="cancelled">لغو شده‌ها</option>
              <option value="failed">خطا داده‌ها</option>
            </select>
          </div>

          <div className="flex items-center gap-2 text-xs text-[#93a4b6]">
            <span>کانال مقصد:</span>
            <select
              value={filterChannel}
              onChange={(e) => setFilterChannel(e.target.value)}
              className="bg-[#17212d] border border-[#22303f] text-[#e8eef5] rounded-lg px-2.5 py-1.5 text-xs focus:outline-none"
            >
              <option value="all">همه کانال‌ها</option>
              {channels.map(c => (
                <option key={c.id} value={c.id.toString()}>{c.name}</option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="bg-[#f7931a] hover:bg-[#ffa633] text-[#0b0f14] font-bold text-xs px-4 py-2 rounded-lg flex items-center gap-2 transition-colors cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          زمان‌بندی پست جدید
        </button>
      </div>

      {/* Posts Table / Cards */}
      <div className="space-y-3">
        {filteredPosts.length > 0 ? (
          filteredPosts.map((post) => {
            const chan = channels.find(c => c.id === post.channel_id);
            return (
              <div
                key={post.id}
                className="bg-[#121a23] hover:bg-[#17212d]/70 border border-[#22303f] rounded-xl p-5 transition-all space-y-3"
              >
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2.5">
                    <div className="p-2 bg-[#17212d] rounded-lg border border-[#22303f]">
                      {getTypeIcon(post.content_type)}
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-[#e8eef5]">
                        {post.title || 'پست متنی بدون عنوان'}
                      </h3>
                      <div className="flex items-center gap-3 text-[11px] text-[#64748b] mt-0.5">
                        <span className="text-[#f7931a]">کانال: {chan?.name || `#${post.channel_id}`}</span>
                        <span>•</span>
                        <span>زمان‌بندی: {new Date(post.scheduled_at).toLocaleDateString('fa-IR')} {new Date(post.scheduled_at).toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' })}</span>
                        {post.telegram_message_id && (
                          <>
                            <span>•</span>
                            <span className="font-mono text-emerald-400">شناسه تلگرام: #{post.telegram_message_id}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {getStatusBadge(post.status)}
                    <span className="text-[11px] font-mono text-[#64748b] bg-[#17212d] px-2 py-0.5 rounded">
                      تلاش: {post.attempts}/{post.max_attempts}
                    </span>
                  </div>
                </div>

                {/* Body Preview */}
                <div className="bg-[#0e141b] rounded-lg p-3 text-xs text-[#93a4b6] font-sans leading-relaxed border border-[#22303f]/50 whitespace-pre-line line-clamp-3">
                  {post.body}
                </div>

                {/* Actions Footer */}
                <div className="pt-2 flex flex-wrap items-center justify-between gap-3 text-xs">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleShowAttempts(post.id)}
                      className="text-[#93a4b6] hover:text-[#e8eef5] flex items-center gap-1.5 py-1 px-2.5 rounded bg-[#17212d] border border-[#22303f] transition-colors"
                    >
                      <History className="w-3.5 h-3.5 text-[#f7931a]" />
                      تاریخچه تلاش‌ها
                    </button>
                    {post.split_long_text && (
                      <span className="text-[10px] text-sky-400 bg-sky-500/10 px-2 py-0.5 rounded border border-sky-500/20">
                        تفکیک خودکار متن بلند فعال
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    {post.status === 'pending' && (
                      <>
                        <button
                          onClick={() => onPublishNow(post.id)}
                          className="bg-emerald-600 hover:bg-emerald-500 text-white font-medium px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors cursor-pointer"
                        >
                          <Send className="w-3.5 h-3.5" />
                          ارسال فوری
                        </button>
                        <button
                          onClick={() => onCancelPost(post.id)}
                          className="bg-slate-800 hover:bg-slate-700 text-rose-300 font-medium px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
                        >
                          لغو زمان‌بندی
                        </button>
                      </>
                    )}
                    {(post.status === 'cancelled' || post.status === 'failed') && (
                      <button
                        onClick={() => onRetryPost(post.id)}
                        className="bg-[#f7931a]/15 hover:bg-[#f7931a]/25 text-[#f7931a] border border-[#f7931a]/30 font-medium px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors cursor-pointer"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                        بازنشانی به صف
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          <div className="bg-[#121a23] border border-[#22303f] rounded-xl p-12 text-center text-xs text-[#64748b]">
            هیچ پستی با فیلترهای انتخابی یافت نشد.
          </div>
        )}
      </div>

      {/* Add Scheduled Post Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#121a23] border border-[#22303f] rounded-2xl w-full max-w-xl p-6 relative max-h-[90vh] overflow-y-auto">
            <h3 className="text-base font-bold text-[#e8eef5] mb-4 flex items-center gap-2">
              <Plus className="w-5 h-5 text-[#f7931a]" />
              زمان‌بندی پست جدید در کانال
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-medium text-[#93a4b6] mb-1.5">
                    کانال مقصد:
                  </label>
                  <select
                    value={channelId}
                    onChange={(e) => setChannelId(e.target.value)}
                    className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3 py-2 text-[#e8eef5] focus:outline-none focus:border-[#f7931a]"
                  >
                    {channels.map(c => (
                      <option key={c.id} value={c.id.toString()}>{c.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block font-medium text-[#93a4b6] mb-1.5">
                    نوع محتوا:
                  </label>
                  <select
                    value={contentType}
                    onChange={(e: any) => setContentType(e.target.value)}
                    className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3 py-2 text-[#e8eef5] focus:outline-none focus:border-[#f7931a]"
                  >
                    <option value="text">متنی ساده</option>
                    <option value="photo">تصویر + کپشن</option>
                    <option value="video">ویدیو کلیپ</option>
                    <option value="document">فایل / سند PDF</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-medium text-[#93a4b6] mb-1.5">
                  عنوان پست:
                </label>
                <input
                  type="text"
                  placeholder="مثال: آموزش رفع خطای سنسور دمای WhatsMiner"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3.5 py-2 text-[#e8eef5] focus:outline-none focus:border-[#f7931a]"
                />
              </div>

              <div>
                <label className="block font-medium text-[#93a4b6] mb-1.5">
                  متن اصلی پست (کپشن):
                </label>
                <textarea
                  required
                  rows={5}
                  placeholder="متن پست را وارد کنید..."
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3.5 py-2 text-[#e8eef5] focus:outline-none focus:border-[#f7931a] font-sans"
                />
              </div>

              {contentType !== 'text' && (
                <div>
                  <label className="block font-medium text-[#93a4b6] mb-1.5">
                    مسیر یا لینک فایل رسانه:
                  </label>
                  <input
                    type="text"
                    placeholder="/assets/demo/hashboard_s19.jpg"
                    value={mediaPath}
                    onChange={(e) => setMediaPath(e.target.value)}
                    className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3.5 py-2 text-[#e8eef5] focus:outline-none focus:border-[#f7931a] font-mono text-left dir-ltr"
                  />
                </div>
              )}

              <div>
                <label className="block font-medium text-[#93a4b6] mb-1.5">
                  تاریخ و زمان انتشار (تهران):
                </label>
                <input
                  type="datetime-local"
                  value={scheduledAt}
                  onChange={(e) => setScheduledAt(e.target.value)}
                  className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3.5 py-2 text-[#e8eef5] focus:outline-none focus:border-[#f7931a]"
                />
              </div>

              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="split_long"
                  checked={splitLongText}
                  onChange={(e) => setSplitLongText(e.target.checked)}
                  className="rounded border-[#22303f] text-[#f7931a] focus:ring-0"
                />
                <label htmlFor="split_long" className="text-xs text-[#93a4b6] cursor-pointer">
                  سیاست تفکیک صریح: در صورت طولانی بودن متن، تصویر و متن به صورت دو پیام پیوسته ارسال گردند.
                </label>
              </div>

              <div className="pt-3 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-[#17212d] hover:bg-[#22303f] text-[#93a4b6] rounded-lg cursor-pointer"
                >
                  انصراف
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2 bg-[#f7931a] hover:bg-[#ffa633] text-[#0b0f14] font-bold rounded-lg cursor-pointer disabled:opacity-50"
                >
                  {isSubmitting ? 'در حال ثبت...' : 'ثبت در صف'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Attempt History Modal */}
      {historyModal.open && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#121a23] border border-[#22303f] rounded-2xl w-full max-w-lg p-6 relative">
            <h3 className="text-base font-bold text-[#e8eef5] mb-3 flex items-center gap-2">
              <History className="w-5 h-5 text-[#f7931a]" />
              تاریخچه تلاش‌های ارسال پست #{historyModal.postId}
            </h3>

            <div className="space-y-2.5 max-h-80 overflow-y-auto my-4 text-xs">
              {historyModal.attempts && historyModal.attempts.length > 0 ? (
                historyModal.attempts.map((a: any) => (
                  <div key={a.id} className="p-3 bg-[#17212d] border border-[#22303f] rounded-lg">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-[#e8eef5]">تلاش شماره {a.attempt_no}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono ${
                        a.outcome === 'OK' ? 'bg-emerald-500/15 text-emerald-400' : 'bg-rose-500/15 text-rose-400'
                      }`}>
                        {a.outcome}
                      </span>
                    </div>
                    <p className="text-[#93a4b6] text-xs">{a.detail}</p>
                    <div className="mt-2 text-[10px] text-[#64748b] flex items-center justify-between font-mono">
                      <span>{new Date(a.started_at).toLocaleString('fa-IR')}</span>
                      <span>مدت زمان: {a.duration_ms}ms</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-6 text-[#64748b]">
                  هنوز تلاشی برای این پست ثبت نشده است (در صف انتظار است).
                </div>
              )}
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setHistoryModal({ open: false, attempts: [] })}
                className="px-4 py-2 bg-[#17212d] hover:bg-[#22303f] text-[#e8eef5] rounded-lg text-xs"
              >
                بستن
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
