import React from 'react';
import { RefreshCw, Radio, ShieldCheck, Zap } from 'lucide-react';

interface HeaderProps {
  title: string;
  subtitle?: string;
  marketBtc?: { price_toman: number; change_24h: number };
  onRefreshMarket?: () => void;
  isRefreshing?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  marketBtc,
  onRefreshMarket,
  isRefreshing
}) => {
  return (
    <header className="h-16 border-b border-[#22303f] bg-[#0e141b]/80 backdrop-blur px-6 flex items-center justify-between shrink-0">
      <div>
        <h2 className="text-lg font-bold text-[#e8eef5]">{title}</h2>
        {subtitle && <p className="text-xs text-[#93a4b6]">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {/* Live BTC Ticker */}
        {marketBtc && (
          <div className="hidden sm:flex items-center gap-2 bg-[#121a23] border border-[#22303f] px-3 py-1.5 rounded-lg text-xs">
            <span className="text-[#f7931a] font-semibold flex items-center gap-1">
              <Zap className="w-3.5 h-3.5" />
              BTC/IRT:
            </span>
            <span className="font-mono text-[#e8eef5]">
              {(marketBtc.price_toman).toLocaleString('fa-IR')} ت
            </span>
            <span className={`font-mono text-[11px] ${marketBtc.change_24h >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
              {marketBtc.change_24h >= 0 ? '+' : ''}{marketBtc.change_24h}%
            </span>
          </div>
        )}

        {/* Telegram Bot Status Badge */}
        <div className="flex items-center gap-1.5 bg-[#121a23] border border-[#22303f] px-2.5 py-1.5 rounded-lg text-xs text-[#93a4b6]">
          <Radio className="w-3.5 h-3.5 text-emerald-400" />
          <span className="hidden md:inline">ربات تلگرام:</span>
          <span className="text-emerald-400 font-medium">آماده ارسال</span>
        </div>

        {/* Refresh Market Button */}
        {onRefreshMarket && (
          <button
            onClick={onRefreshMarket}
            disabled={isRefreshing}
            className="flex items-center gap-1.5 bg-[#17212d] hover:bg-[#22303f] text-[#e8eef5] border border-[#22303f] px-3 py-1.5 rounded-lg text-xs transition-colors cursor-pointer disabled:opacity-50"
            title="به‌روزرسانی نرخ‌های نوبیتکس"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-[#f7931a] ${isRefreshing ? 'animate-spin' : ''}`} />
            <span className="hidden lg:inline">نوبیتکس</span>
          </button>
        )}
      </div>
    </header>
  );
};
