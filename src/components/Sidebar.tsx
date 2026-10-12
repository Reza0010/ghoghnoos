import React from 'react';
import {
  LayoutDashboard,
  Radio,
  CalendarClock,
  Sparkles,
  TrendingUp,
  Newspaper,
  Image as ImageIcon,
  BarChart3,
  Settings,
  Cpu
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  appName: string;
  version: string;
}

export const NAV_ITEMS = [
  { id: 'overview', title: 'نمای کلی', icon: LayoutDashboard },
  { id: 'channels', title: 'مدیریت کانال‌ها', icon: Radio },
  { id: 'queue', title: 'تقویم و صف انتشار', icon: CalendarClock },
  { id: 'studio', title: 'استودیوی تولید محتوا', icon: Sparkles },
  { id: 'market', title: 'قیمت ارزهای دیجیتال', icon: TrendingUp },
  { id: 'news', title: 'اخبار ماینینگ', icon: Newspaper },
  { id: 'media', title: 'کتابخانه رسانه', icon: ImageIcon },
  { id: 'reports', title: 'گزارش‌ها و آمار', icon: BarChart3 },
  { id: 'settings', title: 'تنظیمات و APIها', icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  appName,
  version
}) => {
  return (
    <aside className="w-64 bg-[#0e141b] border-l border-[#22303f] flex flex-col justify-between shrink-0 select-none">
      <div>
        {/* Brand Header */}
        <div className="p-5 border-b border-[#22303f]/60">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-[#f7931a]/15 border border-[#f7931a]/40 flex items-center justify-center text-[#f7931a]">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-base font-extrabold text-[#f7931a] tracking-tight">{appName}</h1>
              <p className="text-[10px] text-[#64748b] font-medium">Smart Mining & Crypto Manager</p>
            </div>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-3 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all text-right ${
                  isActive
                    ? 'bg-[#f7931a]/15 text-[#f7931a] font-semibold border-r-2 border-[#f7931a]'
                    : 'text-[#93a4b6] hover:bg-[#17212d] hover:text-[#e8eef5]'
                }`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-[#f7931a]' : 'text-[#64748b]'}`} />
                <span>{item.title}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-[#22303f]/50">
        <div className="bg-[#121a23] rounded-lg p-3 border border-[#22303f]/60 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-[#93a4b6] text-[11px]">موتور زمان‌بند فعال</span>
          </div>
          <span className="text-[#64748b] text-[11px] font-mono">v{version}</span>
        </div>
      </div>
    </aside>
  );
};
