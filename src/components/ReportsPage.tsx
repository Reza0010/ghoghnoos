import React, { useState } from 'react';
import {
  BarChart3,
  CheckCircle2,
  AlertTriangle,
  Radio,
  FileText,
  Activity,
  Layers,
  Sparkles
} from 'lucide-react';

interface ReportsPageProps {
  reports: any;
  logs: any[];
}

export const ReportsPage: React.FC<ReportsPageProps> = ({ reports, logs }) => {
  const [logFilter, setLogFilter] = useState<string>('all');

  const channelStats = reports?.channelStats || [];
  const dailyCounts = reports?.dailyCounts || [];

  const filteredLogs = logs.filter(l => logFilter === 'all' || l.level === logFilter || l.category === logFilter);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-[#121a23] border border-[#22303f] p-5 rounded-xl">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-[#f7931a]" />
          <h2 className="text-base font-bold text-[#e8eef5]">
            گزارش‌های عملکرد، نرخ تحویل تلگرام و تحلیل داده‌ها
          </h2>
        </div>
        <p className="text-xs text-[#93a4b6] mt-1">
          تمام آمار و ارقام مستقیماً از سوابق تراکنش‌ها و پایگاه‌داده استخراج شده و فاقد هرگونه داده ساختگی است.
        </p>
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-[#121a23] border border-[#22303f] rounded-xl p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-[#93a4b6]">مجموع پست‌های ارسالی</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-bold font-mono text-[#e8eef5]">
            {channelStats.reduce((acc: number, c: any) => acc + c.sent_posts, 0)}
          </div>
          <span className="text-[11px] text-emerald-400 mt-1 block">تحویل موفق در کانال‌های مقصد</span>
        </div>

        <div className="bg-[#121a23] border border-[#22303f] rounded-xl p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-[#93a4b6]">پیش‌نویس‌های تولیدی هوش مصنوعی</span>
            <Sparkles className="w-4 h-4 text-[#f7931a]" />
          </div>
          <div className="text-3xl font-bold font-mono text-[#e8eef5]">
            {reports?.totalDrafts || 0}
          </div>
          <span className="text-[11px] text-[#f7931a] mt-1 block">تولید شده در ۱۲ حوزه تخصصی</span>
        </div>

        <div className="bg-[#121a23] border border-[#22303f] rounded-xl p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-[#93a4b6]">رسانه‌های آرشیو شده</span>
            <Layers className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-3xl font-bold font-mono text-[#e8eef5]">
            {reports?.totalMedia || 0}
          </div>
          <span className="text-[11px] text-purple-400 mt-1 block">تصاویر، شماتیک‌ها و ویدیوها</span>
        </div>
      </div>

      {/* Weekly Activity Chart */}
      <div className="bg-[#121a23] border border-[#22303f] rounded-xl p-5">
        <h3 className="text-sm font-bold text-[#e8eef5] mb-4 flex items-center gap-2">
          <Activity className="w-4 h-4 text-[#f7931a]" />
          تعداد پست‌های ارسالی در طول هفته (شنبه تا جمعه)
        </h3>

        <div className="h-44 flex items-end gap-4 pt-4 px-4 border-b border-[#22303f]">
          {dailyCounts.map((d: any, idx: number) => {
            const max = Math.max(...dailyCounts.map((x: any) => x.sent)) || 1;
            const heightPct = Math.round((d.sent / max) * 100);

            return (
              <div key={idx} className="flex-1 flex flex-col items-center gap-2 h-full justify-end">
                <span className="text-[11px] font-mono font-bold text-[#f7931a]">{d.sent}</span>
                <div
                  style={{ height: `${Math.max(15, heightPct)}%` }}
                  className="w-full bg-[#f7931a]/80 hover:bg-[#f7931a] rounded-t-md transition-all cursor-pointer"
                ></div>
                <span className="text-xs text-[#93a4b6] mt-1">{d.day}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Channel Performance Table */}
      <div className="bg-[#121a23] border border-[#22303f] rounded-xl overflow-hidden">
        <div className="p-4 border-b border-[#22303f]">
          <h3 className="text-sm font-bold text-[#e8eef5] flex items-center gap-2">
            <Radio className="w-4 h-4 text-sky-400" />
            عملکرد تفکیکی هر کانال تلگرام
          </h3>
        </div>

        <table className="w-full text-right text-xs">
          <thead className="bg-[#17212d] text-[#93a4b6] border-b border-[#22303f]">
            <tr>
              <th className="py-3 px-4">نام کانال</th>
              <th className="py-3 px-4">نام مستعار</th>
              <th className="py-3 px-4">کل پست‌ها</th>
              <th className="py-3 px-4">ارسال موفق</th>
              <th className="py-3 px-4">درصد موفقیت</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#22303f]/50">
            {channelStats.map((c: any) => (
              <tr key={c.channel_id} className="hover:bg-[#17212d]">
                <td className="py-3.5 px-4 font-bold text-[#e8eef5]">{c.name}</td>
                <td className="py-3.5 px-4 text-[#f7931a] font-mono">{c.alias}</td>
                <td className="py-3.5 px-4 font-mono text-[#e8eef5]">{c.total_posts}</td>
                <td className="py-3.5 px-4 font-mono text-emerald-400">{c.sent_posts}</td>
                <td className="py-3.5 px-4 font-mono">
                  <span className="bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded text-[11px] font-bold">
                    {c.success_rate}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Audit Log Stream */}
      <div className="bg-[#121a23] border border-[#22303f] rounded-xl p-5 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-[#93a4b6]" />
            <h3 className="text-sm font-bold text-[#e8eef5]">لاگ‌های ممیزی و حسابرسی سیستم</h3>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="text-[#93a4b6]">فیلتر سطح:</span>
            <select
              value={logFilter}
              onChange={(e) => setLogFilter(e.target.value)}
              className="bg-[#17212d] border border-[#22303f] text-[#e8eef5] rounded-lg px-2.5 py-1 text-xs focus:outline-none"
            >
              <option value="all">همه دسته‌ها</option>
              <option value="SUCCESS">موفقیت‌ها (SUCCESS)</option>
              <option value="INFO">اطلاعات (INFO)</option>
              <option value="WARN">هشدارها (WARN)</option>
              <option value="ERROR">خطاها (ERROR)</option>
            </select>
          </div>
        </div>

        <div className="bg-[#0e141b] rounded-xl border border-[#22303f] divide-y divide-[#22303f]/50 font-mono text-xs max-h-72 overflow-y-auto">
          {filteredLogs.map(l => (
            <div key={l.id} className="p-3 flex items-start gap-3">
              <span className={`text-[10px] px-1.5 py-0.5 rounded uppercase font-bold shrink-0 ${
                l.level === 'SUCCESS' ? 'bg-emerald-500/15 text-emerald-400' :
                l.level === 'WARN' ? 'bg-amber-500/15 text-amber-400' :
                l.level === 'ERROR' ? 'bg-rose-500/15 text-rose-400' :
                'bg-sky-500/15 text-sky-400'
              }`}>
                {l.category || l.level}
              </span>
              <span className="text-[#e8eef5] text-xs font-sans flex-1">
                {l.message}
              </span>
              <span className="text-[10px] text-[#64748b] shrink-0 font-sans">
                {new Date(l.ts).toLocaleString('fa-IR')}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
