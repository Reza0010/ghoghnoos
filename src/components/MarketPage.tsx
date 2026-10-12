import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  RefreshCw,
  Zap,
  ArrowUp,
  ArrowDown,
  Clock,
  ExternalLink,
  ShieldCheck,
  BarChart2
} from 'lucide-react';

interface MarketPageProps {
  marketData: any;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const MarketPage: React.FC<MarketPageProps> = ({
  marketData,
  onRefresh,
  isRefreshing
}) => {
  const [currencyUnit, setCurrencyUnit] = useState<'toman' | 'rls' | 'usdt'>('toman');
  const [selectedSymbol, setSelectedSymbol] = useState('BTC');
  const [historyCandles, setHistoryCandles] = useState<any>(null);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const rates = marketData?.rates || [];

  // Fetch candle history for chart
  useEffect(() => {
    let active = true;
    const fetchHistory = async () => {
      setLoadingHistory(true);
      try {
        const res = await fetch(`/api/market/udf/history?symbol=${selectedSymbol}IRT&resolution=60`);
        if (res.ok) {
          const json = await res.json();
          if (active) setHistoryCandles(json);
        }
      } catch (err) {
        console.warn('Failed to load history candles:', err);
      } finally {
        if (active) setLoadingHistory(false);
      }
    };
    fetchHistory();
    return () => { active = false; };
  }, [selectedSymbol]);

  const activeRate = rates.find((r: any) => r.symbol === selectedSymbol) || rates[0];

  const formatPrice = (rate: any) => {
    if (!rate) return '—';
    if (currencyUnit === 'toman') {
      return `${rate.price_toman.toLocaleString('fa-IR')} تومان`;
    }
    if (currencyUnit === 'rls') {
      return `${rate.price_rls.toLocaleString('fa-IR')} ریال`;
    }
    return `$${rate.price_usdt.toLocaleString('en-US')}`;
  };

  return (
    <div className="space-y-6">
      {/* Top Banner and Controls */}
      <div className="bg-[#121a23] border border-[#22303f] p-5 rounded-xl flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-400" />
            <h2 className="text-base font-bold text-[#e8eef5]">
              تابلوی زنده قیمت‌های صرافی نوبیتکس (Nobitex Market)
            </h2>
          </div>
          <p className="text-xs text-[#93a4b6] mt-1">
            داده‌های مستقیم از وب‌سرویس عمومی <span className="font-mono text-[#f7931a]">apiv2.nobitex.ir</span> بر اساس استاندارد OpenAPI.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Currency Toggle */}
          <div className="bg-[#17212d] border border-[#22303f] rounded-lg p-1 flex items-center text-xs">
            <button
              onClick={() => setCurrencyUnit('toman')}
              className={`px-3 py-1 rounded-md transition-all cursor-pointer ${
                currencyUnit === 'toman' ? 'bg-[#f7931a] text-[#0b0f14] font-bold' : 'text-[#93a4b6] hover:text-[#e8eef5]'
              }`}
            >
              تومان
            </button>
            <button
              onClick={() => setCurrencyUnit('rls')}
              className={`px-3 py-1 rounded-md transition-all cursor-pointer ${
                currencyUnit === 'rls' ? 'bg-[#f7931a] text-[#0b0f14] font-bold' : 'text-[#93a4b6] hover:text-[#e8eef5]'
              }`}
            >
              ریال
            </button>
            <button
              onClick={() => setCurrencyUnit('usdt')}
              className={`px-3 py-1 rounded-md transition-all cursor-pointer ${
                currencyUnit === 'usdt' ? 'bg-[#f7931a] text-[#0b0f14] font-bold' : 'text-[#93a4b6] hover:text-[#e8eef5]'
              }`}
            >
              تتر (USDT)
            </button>
          </div>

          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="bg-[#17212d] hover:bg-[#22303f] text-[#e8eef5] border border-[#22303f] px-3.5 py-1.5 rounded-lg text-xs flex items-center gap-2 transition-colors cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-[#f7931a] ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>به‌روزرسانی</span>
          </button>
        </div>
      </div>

      {/* Selected Coin Spotlight & Interactive Mini-Chart */}
      {activeRate && (
        <div className="bg-[#121a23] border border-[#22303f] rounded-xl p-6">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-[#17212d] border border-[#f7931a]/40 flex items-center justify-center font-black font-mono text-[#f7931a] text-lg">
                {activeRate.symbol}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-bold text-[#e8eef5]">{activeRate.name}</h3>
                  {activeRate.is_mining && (
                    <span className="text-[10px] bg-amber-500/15 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded-full font-medium">
                      ارز قابل استخراج با ASIC / GPU
                    </span>
                  )}
                </div>
                <div className="text-xs text-[#64748b] font-mono mt-0.5">
                  نماد در نوبیتکس: {activeRate.symbol}IRT / {activeRate.symbol}USDT
                </div>
              </div>
            </div>

            <div className="text-left font-mono">
              <div className="text-2xl font-bold text-[#e8eef5]">{formatPrice(activeRate)}</div>
              <div className={`text-xs font-semibold flex items-center justify-end gap-1 mt-1 ${
                activeRate.change_24h >= 0 ? 'text-emerald-400' : 'text-rose-400'
              }`}>
                {activeRate.change_24h >= 0 ? <ArrowUp className="w-3.5 h-3.5" /> : <ArrowDown className="w-3.5 h-3.5" />}
                <span>{activeRate.change_24h >= 0 ? '+' : ''}{activeRate.change_24h}% (تغییر ۲۴ ساعته)</span>
              </div>
            </div>
          </div>

          {/* Sparkline / Candle Chart Visualizer */}
          <div className="bg-[#0e141b] border border-[#22303f]/60 rounded-xl p-4">
            <div className="flex items-center justify-between mb-2 text-xs text-[#93a4b6]">
              <div className="flex items-center gap-2">
                <BarChart2 className="w-4 h-4 text-[#f7931a]" />
                <span>نمودار نوسانات قیمت ۳۰ دوره گذشته (تایم‌فریم ۱ ساعته)</span>
              </div>
              <span className="text-[11px] text-[#64748b]">منبع داده: UDF History نوبیتکس</span>
            </div>

            {historyCandles && historyCandles.c && historyCandles.c.length > 0 ? (
              <div className="h-44 w-full flex items-end gap-1.5 pt-4 px-2">
                {historyCandles.c.map((closeVal: number, idx: number) => {
                  const min = Math.min(...historyCandles.l);
                  const max = Math.max(...historyCandles.h);
                  const range = max - min || 1;
                  const heightPercent = Math.max(12, Math.min(100, Math.round(((closeVal - min) / range) * 90) + 10));
                  const isUp = closeVal >= (historyCandles.o[idx] || closeVal);

                  return (
                    <div
                      key={idx}
                      className="flex-1 flex flex-col items-center justify-end h-full group relative"
                    >
                      <div
                        style={{ height: `${heightPercent}%` }}
                        className={`w-full rounded-t transition-all ${
                          isUp ? 'bg-emerald-500/80 hover:bg-emerald-400' : 'bg-rose-500/80 hover:bg-rose-400'
                        }`}
                      ></div>
                      {/* Tooltip on hover */}
                      <div className="absolute bottom-full mb-2 hidden group-hover:block bg-[#17212d] border border-[#22303f] text-[#e8eef5] text-[10px] font-mono px-2 py-1 rounded shadow-lg z-20 whitespace-nowrap">
                        {closeVal.toLocaleString()} {currencyUnit === 'usdt' ? '$' : 'ت'}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="h-44 flex items-center justify-center text-xs text-[#64748b]">
                {loadingHistory ? 'در حال بارگذاری کندل‌ها...' : 'داده تاریخی در دسترس نیست.'}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Full Watchlist Table */}
      <div className="bg-[#121a23] border border-[#22303f] rounded-xl overflow-hidden">
        <div className="p-4 border-b border-[#22303f] flex items-center justify-between">
          <h3 className="text-sm font-bold text-[#e8eef5]">لیست کامل ارزهای منتخب ماینینگ و پایه</h3>
          <span className="text-xs text-[#64748b]">کلیک روی هر سطر برای نمایش نمودار اختصاصی</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-right text-xs">
            <thead className="bg-[#17212d] text-[#93a4b6] border-b border-[#22303f]">
              <tr>
                <th className="py-3 px-4">نماد و ارز</th>
                <th className="py-3 px-4">قیمت فعلی</th>
                <th className="py-3 px-4">تغییر ۲۴ ساعته</th>
                <th className="py-3 px-4">بالاترین / پایین‌ترین ۲۴س</th>
                <th className="py-3 px-4">حجم معاملات</th>
                <th className="py-3 px-4">دسته‌بندی</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#22303f]/50">
              {rates.map((rate: any) => {
                const isSelected = rate.symbol === selectedSymbol;
                return (
                  <tr
                    key={rate.symbol}
                    onClick={() => setSelectedSymbol(rate.symbol)}
                    className={`cursor-pointer transition-colors ${
                      isSelected ? 'bg-[#f7931a]/10 hover:bg-[#f7931a]/15' : 'hover:bg-[#17212d]'
                    }`}
                  >
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-2.5">
                        <span className="w-7 h-7 rounded bg-[#17212d] border border-[#22303f] flex items-center justify-center font-bold font-mono text-[#f7931a] text-[11px]">
                          {rate.symbol}
                        </span>
                        <div>
                          <div className="font-bold text-[#e8eef5]">{rate.name}</div>
                          <div className="text-[10px] text-[#64748b] font-mono">{rate.symbol}</div>
                        </div>
                      </div>
                    </td>

                    <td className="py-3.5 px-4 font-mono font-bold text-[#e8eef5]">
                      {formatPrice(rate)}
                    </td>

                    <td className="py-3.5 px-4 font-mono">
                      <span className={`inline-flex items-center gap-0.5 px-2 py-0.5 rounded text-[11px] font-semibold ${
                        rate.change_24h >= 0 ? 'bg-emerald-500/15 text-emerald-400' : 'bg-rose-500/15 text-rose-400'
                      }`}>
                        {rate.change_24h >= 0 ? '+' : ''}{rate.change_24h}%
                      </span>
                    </td>

                    <td className="py-3.5 px-4 font-mono text-[11px] text-[#93a4b6]">
                      <div>بالا: {rate.high_24h?.toLocaleString()}</div>
                      <div>پایین: {rate.low_24h?.toLocaleString()}</div>
                    </td>

                    <td className="py-3.5 px-4 font-mono text-[11px] text-[#93a4b6]">
                      {rate.volume?.toLocaleString()} {rate.symbol}
                    </td>

                    <td className="py-3.5 px-4">
                      {rate.is_mining ? (
                        <span className="text-[10px] bg-amber-500/10 text-amber-400 px-2 py-0.5 rounded border border-amber-500/20">
                          ماینینگ
                        </span>
                      ) : (
                        <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded">
                          پایه / استیبل
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
