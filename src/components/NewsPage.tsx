import React, { useState } from 'react';
import {
  Newspaper,
  CheckCircle2,
  XCircle,
  Sparkles,
  ExternalLink,
  Filter,
  Clock,
  Layers,
  ArrowRight
} from 'lucide-react';

interface NewsItem {
  id: number;
  guid: string;
  title: string;
  link: string;
  source: string;
  topic: string;
  published_at: string;
  fetched_at: string;
  summary: string;
  status: 'new' | 'reviewed' | 'approved' | 'rejected' | 'converted';
}

interface NewsPageProps {
  news: NewsItem[];
  onUpdateStatus: (id: number, status: string) => Promise<void>;
  onConvertToDraft: (id: number) => Promise<void>;
  onNavigateToStudio: () => void;
}

export const NewsPage: React.FC<NewsPageProps> = ({
  news,
  onUpdateStatus,
  onConvertToDraft,
  onNavigateToStudio
}) => {
  const [selectedTopic, setSelectedTopic] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [convertingId, setConvertingId] = useState<number | null>(null);

  const topics = [
    { id: 'all', name: 'همه موضوعات' },
    { id: 'hardware', name: 'سخت‌افزار و قطعات' },
    { id: 'mining', name: 'صنعت ماینینگ و استخراج' },
    { id: 'bitcoin', name: 'بیت‌کوین و بلاک‌چین' },
    { id: 'energy', name: 'انرژی و تعرفه برق' },
    { id: 'regulation', name: 'قوانین و مقررات' },
  ];

  const filteredNews = news.filter(item => {
    if (selectedTopic !== 'all' && item.topic !== selectedTopic) return false;
    if (selectedStatus !== 'all' && item.status !== selectedStatus) return false;
    return true;
  });

  const handleConvert = async (id: number) => {
    setConvertingId(id);
    try {
      await onConvertToDraft(id);
      onNavigateToStudio();
    } finally {
      setConvertingId(null);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return <span className="text-[10px] bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded-full font-medium">تأیید شده</span>;
      case 'converted':
        return <span className="text-[10px] bg-purple-500/15 text-purple-400 border border-purple-500/30 px-2 py-0.5 rounded-full font-medium">تبدیل به پیش‌نویس</span>;
      case 'rejected':
        return <span className="text-[10px] bg-rose-500/15 text-rose-400 border border-rose-500/30 px-2 py-0.5 rounded-full font-medium">رد شده</span>;
      default:
        return <span className="text-[10px] bg-amber-500/15 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded-full font-medium">جدید (بررسی نشده)</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner and Topic Filter Tabs */}
      <div className="bg-[#121a23] border border-[#22303f] p-5 rounded-xl space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Newspaper className="w-5 h-5 text-purple-400" />
              <h2 className="text-base font-bold text-[#e8eef5]">
                جریان اخبار تخصصی ماینینگ و بلاک‌چین (RSS Aggregator)
              </h2>
            </div>
            <p className="text-xs text-[#93a4b6] mt-1">
              گردش کار الزامی تأیید خبر: انتشار اخبار پیش از تأیید ناظر ممنوع است تا از اطلاعات کذب و تاریخ‌گذشته جلوگیری شود.
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="text-[#93a4b6]">فیلتر وضعیت:</span>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="bg-[#17212d] border border-[#22303f] rounded-lg px-2.5 py-1.5 text-[#e8eef5] text-xs focus:outline-none"
            >
              <option value="all">همه</option>
              <option value="new">جدید (بررسی نشده)</option>
              <option value="approved">تأیید شده‌ها</option>
              <option value="converted">تبدیل شده به پست</option>
              <option value="rejected">رد شده‌ها</option>
            </select>
          </div>
        </div>

        {/* Topic Pills */}
        <div className="flex flex-wrap gap-2 pt-2 border-t border-[#22303f]/50">
          {topics.map(t => (
            <button
              key={t.id}
              onClick={() => setSelectedTopic(t.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                selectedTopic === t.id
                  ? 'bg-[#f7931a] text-[#0b0f14] font-bold shadow'
                  : 'bg-[#17212d] text-[#93a4b6] hover:text-[#e8eef5] border border-[#22303f]'
              }`}
            >
              {t.name}
            </button>
          ))}
        </div>
      </div>

      {/* News Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {filteredNews.length > 0 ? (
          filteredNews.map((item) => (
            <div
              key={item.id}
              className="bg-[#121a23] border border-[#22303f] hover:border-[#22303f]/90 rounded-xl p-5 flex flex-col justify-between transition-all space-y-4"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-[11px] font-mono font-semibold text-[#f7931a] bg-[#f7931a]/10 px-2.5 py-0.5 rounded">
                    {item.source}
                  </span>
                  {getStatusBadge(item.status)}
                </div>

                <h3 className="text-sm font-bold text-[#e8eef5] leading-snug line-clamp-2">
                  {item.title}
                </h3>

                <p className="text-xs text-[#93a4b6] mt-2.5 leading-relaxed line-clamp-3">
                  {item.summary}
                </p>
              </div>

              <div className="pt-3 border-t border-[#22303f]/60 space-y-3">
                <div className="flex items-center justify-between text-[11px] text-[#64748b]">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(item.published_at).toLocaleDateString('fa-IR')}
                  </span>
                  {item.link && (
                    <a
                      href={item.link}
                      target="_blank"
                      rel="noreferrer"
                      className="text-[#93a4b6] hover:text-[#f7931a] flex items-center gap-1 transition-colors"
                    >
                      <span>مشاهده در منبع اصلی</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between gap-2 pt-1">
                  <div className="flex items-center gap-1.5">
                    {item.status !== 'approved' && item.status !== 'converted' && (
                      <button
                        onClick={() => onUpdateStatus(item.id, 'approved')}
                        className="bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 px-2.5 py-1.5 rounded-lg text-xs flex items-center gap-1 transition-colors cursor-pointer"
                        title="تأیید خبر برای انتشار"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>تأیید خبر</span>
                      </button>
                    )}
                    {item.status !== 'rejected' && (
                      <button
                        onClick={() => onUpdateStatus(item.id, 'rejected')}
                        className="bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 px-2.5 py-1.5 rounded-lg text-xs flex items-center gap-1 transition-colors cursor-pointer"
                        title="رد خبر"
                      >
                        <XCircle className="w-3.5 h-3.5" />
                        <span>رد</span>
                      </button>
                    )}
                  </div>

                  <button
                    onClick={() => handleConvert(item.id)}
                    disabled={convertingId === item.id}
                    className="bg-[#f7931a] hover:bg-[#ffa633] text-[#0b0f14] font-bold px-3 py-1.5 rounded-lg text-xs flex items-center gap-1.5 transition-colors cursor-pointer disabled:opacity-50"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>تبدیل به پست تلگرام</span>
                  </button>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-2 bg-[#121a23] border border-[#22303f] rounded-xl p-12 text-center text-xs text-[#64748b]">
            هیچ خبری مطابق فیلترهای انتخابی یافت نشد.
          </div>
        )}
      </div>
    </div>
  );
};
