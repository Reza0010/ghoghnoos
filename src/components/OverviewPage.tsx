import React from 'react';
import {
  Radio,
  CalendarClock,
  Send,
  Newspaper,
  Sparkles,
  TrendingUp,
  ArrowUpRight,
  Clock,
  CheckCircle2,
  AlertTriangle,
  FileText
} from 'lucide-react';

interface OverviewPageProps {
  data: any;
  onNavigate: (tab: string) => void;
  onRefresh: () => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ data, onNavigate, onRefresh }) => {
  if (!data) {
    return (
      <div className="flex items-center justify-center h-64 text-[#93a4b6]">
        در حال دریافت داده‌های سامانه...
      </div>
    );
  }

  const statCards = [
    {
      title: 'کانال‌های متصل',
      value: `${data.activeChannelsCount || 0} / ${data.totalChannelsCount || 0}`,
      subtitle: 'کانال‌های فعال تلگرام',
      icon: Radio,
      tab: 'channels',
      color: 'text-sky-400',
      bgColor: 'bg-sky-500/10'
    },
    {
      title: 'صف انتشار معلق',
      value: data.pendingPostsCount || 0,
      subtitle: 'پست‌های زمان‌بندی شده',
      icon: CalendarClock,
      tab: 'queue',
      color: 'text-[#f7931a]',
      bgColor: 'bg-[#f7931a]/10'
    },
    {
      title: 'پست‌های ارسال شده',
      value: data.sentPostsCount || 0,
      subtitle: 'موفق در Bot API',
      icon: Send,
      tab: 'queue',
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10'
    },
    {
      title: 'اخبار جدید',
      value: data.unreviewedNewsCount || 0,
      subtitle: 'نیازمند بازبینی و تأیید',
      icon: Newspaper,
      tab: 'news',
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10'
    },
    {
      title: 'پیش‌نویس‌های استودیو',
      value: data.draftsCount || 0,
      subtitle: 'محتوای تخصصی ماینینگ',
      icon: Sparkles,
      tab: 'studio',
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-l from-[#17212d] to-[#121a23] border border-[#22303f] rounded-2xl p-6 relative overflow-hidden">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 bg-[#f7931a]/15 text-[#f7931a] text-xs px-3 py-1 rounded-full font-medium mb-3 border border-[#f7931a]/30">
            <span>نسخه ۲.۰.۱ پایدار — پایش نوبیتکس و اتوماسیون محتوا</span>
          </div>
          <h2 className="text-xl font-bold text-[#e8eef5] mb-2">
            داشبورد مدیریت کانال‌های ماینینگ و ارز دیجیتال
          </h2>
          <p className="text-sm text-[#93a4b6] leading-relaxed">
            مدیریت چندکاناله تلگرام، دریافت قیمت لحظه‌ای نوبیتکس، تولید محتوای هوشمند با اصول عیب‌یابی هش‌برد و پاور، و صف انتشار بدون قطعی با مانیتورینگ وضعیت خطاها.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <button
              onClick={() => onNavigate('studio')}
              className="bg-[#f7931a] hover:bg-[#ffa633] text-[#0b0f14] font-bold text-xs px-4 py-2.5 rounded-lg flex items-center gap-2 transition-colors cursor-pointer"
            >
              <Sparkles className="w-4 h-4" />
              تولید محتوا در استودیو AI
            </button>
            <button
              onClick={() => onNavigate('queue')}
              className="bg-[#17212d] hover:bg-[#22303f] text-[#e8eef5] text-xs px-4 py-2.5 rounded-lg border border-[#22303f] flex items-center gap-2 transition-colors cursor-pointer"
            >
              <CalendarClock className="w-4 h-4 text-[#f7931a]" />
              مشاهده تقویم و صف انتشار
            </button>
            <button
              onClick={() => onNavigate('market')}
              className="bg-[#17212d] hover:bg-[#22303f] text-[#e8eef5] text-xs px-4 py-2.5 rounded-lg border border-[#22303f] flex items-center gap-2 transition-colors cursor-pointer"
            >
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              تابلوی قیمت نوبیتکس
            </button>
          </div>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {statCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <div
              key={i}
              onClick={() => onNavigate(card.tab)}
              className="bg-[#121a23] hover:bg-[#17212d] border border-[#22303f] rounded-xl p-4 transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs text-[#93a4b6] font-medium">{card.title}</span>
                <div className={`p-2 rounded-lg ${card.bgColor} ${card.color}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div className="text-2xl font-bold font-mono text-[#e8eef5] mb-1">
                {card.value}
              </div>
              <div className="text-[11px] text-[#64748b] flex items-center justify-between">
                <span>{card.subtitle}</span>
                <ArrowUpRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity text-[#f7931a]" />
              </div>
            </div>
          );
        })}
      </div>

      {/* Two Column Layout: Upcoming Queue & Live Market */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upcoming Posts in Queue */}
        <div className="bg-[#121a23] border border-[#22303f] rounded-xl p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <CalendarClock className="w-4 h-4 text-[#f7931a]" />
                <h3 className="text-sm font-bold text-[#e8eef5]">پست‌های آینده در صف انتشار</h3>
              </div>
              <button
                onClick={() => onNavigate('queue')}
                className="text-xs text-[#f7931a] hover:underline"
              >
                مشاهده همه
              </button>
            </div>

            <div className="space-y-3">
              {data.recentQueue && data.recentQueue.length > 0 ? (
                data.recentQueue.map((post: any) => (
                  <div
                    key={post.id}
                    className="p-3 bg-[#17212d] border border-[#22303f]/70 rounded-lg text-xs space-y-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-[#e8eef5] line-clamp-1">
                        {post.title || post.body.substring(0, 45) + '...'}
                      </span>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                        post.status === 'sent'
                          ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                          : post.status === 'pending'
                          ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                          : 'bg-slate-700/50 text-slate-300'
                      }`}>
                        {post.status === 'sent' ? 'ارسال شده' : post.status === 'pending' ? 'در انتظار' : post.status}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-[11px] text-[#64748b]">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(post.scheduled_at).toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' })}
                      </span>
                      <span>نوع: {post.content_type === 'text' ? 'متنی' : post.content_type === 'photo' ? 'تصویر' : post.content_type}</span>
                      <span>کانال #{post.channel_id}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-xs text-[#64748b] text-center py-6">
                  پستی در صف انتظار وجود ندارد.
                </div>
              )}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#22303f]/50">
            <button
              onClick={() => onNavigate('queue')}
              className="w-full py-2 bg-[#17212d] hover:bg-[#22303f] text-[#e8eef5] rounded-lg text-xs transition-colors"
            >
              + افزودن زمان‌بندی جدید
            </button>
          </div>
        </div>

        {/* Live Market Snapshot */}
        <div className="bg-[#121a23] border border-[#22303f] rounded-xl p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-bold text-[#e8eef5]">نرخ‌های زنده نوبیتکس (تومان و تتر)</h3>
              </div>
              <button
                onClick={() => onNavigate('market')}
                className="text-xs text-[#f7931a] hover:underline"
              >
                جدول کامل و نمودار
              </button>
            </div>

            <div className="space-y-2">
              {data.marketSnapshot && data.marketSnapshot.map((rate: any) => (
                <div
                  key={rate.symbol}
                  className="p-2.5 bg-[#17212d] border border-[#22303f]/70 rounded-lg flex items-center justify-between text-xs"
                >
                  <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded bg-[#22303f] flex items-center justify-center font-bold font-mono text-[#f7931a] text-[11px]">
                      {rate.symbol}
                    </div>
                    <div>
                      <div className="font-semibold text-[#e8eef5]">{rate.name}</div>
                      <div className="text-[10px] text-[#64748b] font-mono">${rate.price_usdt.toLocaleString()}</div>
                    </div>
                  </div>

                  <div className="text-left font-mono">
                    <div className="font-bold text-[#e8eef5]">
                      {rate.price_toman.toLocaleString('fa-IR')} ت
                    </div>
                    <div className={`text-[10px] ${rate.change_24h >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {rate.change_24h >= 0 ? '+' : ''}{rate.change_24h}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#22303f]/50 flex items-center justify-between text-[11px] text-[#64748b]">
            <span>منبع: وب‌سرویس رسمی نوبیتکس (apiv2)</span>
            <span className="text-emerald-400">کش هوشمند فعال</span>
          </div>
        </div>
      </div>

      {/* System Activity Logs */}
      <div className="bg-[#121a23] border border-[#22303f] rounded-xl p-5">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-[#93a4b6]" />
            <h3 className="text-sm font-bold text-[#e8eef5]">آخرین رخدادها و لاگ‌های سیستم</h3>
          </div>
          <span className="text-[11px] text-[#64748b]">ردیابی بدون نشت کلید و توکن</span>
        </div>

        <div className="divide-y divide-[#22303f]/50 font-mono text-xs">
          {data.recentLogs && data.recentLogs.map((log: any) => (
            <div key={log.id} className="py-2.5 flex items-start gap-3">
              <span className={`text-[10px] px-1.5 py-0.5 rounded uppercase font-bold shrink-0 ${
                log.level === 'SUCCESS' ? 'bg-emerald-500/15 text-emerald-400' :
                log.level === 'WARN' ? 'bg-amber-500/15 text-amber-400' :
                log.level === 'ERROR' ? 'bg-rose-500/15 text-rose-400' :
                'bg-sky-500/15 text-sky-400'
              }`}>
                {log.category || log.level}
              </span>
              <span className="text-[#e8eef5] text-xs font-sans flex-1">
                {log.message}
              </span>
              <span className="text-[10px] text-[#64748b] shrink-0 font-sans">
                {new Date(log.ts).toLocaleTimeString('fa-IR')}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
