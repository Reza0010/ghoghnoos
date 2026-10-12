import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { OverviewPage } from './components/OverviewPage';
import { ChannelsPage } from './components/ChannelsPage';
import { QueuePage } from './components/QueuePage';
import { StudioPage } from './components/StudioPage';
import { MarketPage } from './components/MarketPage';
import { NewsPage } from './components/NewsPage';
import { MediaPage } from './components/MediaPage';
import { ReportsPage } from './components/ReportsPage';
import { SettingsPage } from './components/SettingsPage';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('overview');

  // Core Data States
  const [overviewData, setOverviewData] = useState<any>(null);
  const [channels, setChannels] = useState<any[]>([]);
  const [posts, setPosts] = useState<any[]>([]);
  const [marketData, setMarketData] = useState<any>(null);
  const [news, setNews] = useState<any[]>([]);
  const [drafts, setDrafts] = useState<any[]>([]);
  const [mediaAssets, setMediaAssets] = useState<any[]>([]);
  const [reports, setReports] = useState<any>(null);
  const [settings, setSettings] = useState<any>({
    app_name: 'MinerMedia AI',
    app_subtitle: 'Smart Mining & Crypto Channel Manager',
    version: '2.0.1'
  });
  const [logs, setLogs] = useState<any[]>([]);

  const [loading, setLoading] = useState<boolean>(true);
  const [refreshingMarket, setRefreshingMarket] = useState<boolean>(false);

  // Fetch all initial data
  const loadAllData = async () => {
    try {
      const [
        ovRes,
        chanRes,
        queueRes,
        mktRes,
        newsRes,
        draftsRes,
        mediaRes,
        repRes,
        settRes,
        logsRes
      ] = await Promise.all([
        fetch('/api/overview').then(r => r.json()).catch(() => null),
        fetch('/api/channels').then(r => r.json()).catch(() => []),
        fetch('/api/queue').then(r => r.json()).catch(() => []),
        fetch('/api/market').then(r => r.json()).catch(() => null),
        fetch('/api/news').then(r => r.json()).catch(() => []),
        fetch('/api/drafts').then(r => r.json()).catch(() => []),
        fetch('/api/media').then(r => r.json()).catch(() => []),
        fetch('/api/reports').then(r => r.json()).catch(() => null),
        fetch('/api/settings').then(r => r.json()).catch(() => null),
        fetch('/api/logs').then(r => r.json()).catch(() => [])
      ]);

      if (ovRes) setOverviewData(ovRes);
      if (chanRes) setChannels(chanRes);
      if (queueRes) setPosts(queueRes);
      if (mktRes) setMarketData(mktRes);
      if (newsRes) setNews(newsRes);
      if (draftsRes) setDrafts(draftsRes);
      if (mediaRes) setMediaAssets(mediaRes);
      if (repRes) setReports(repRes);
      if (settRes) setSettings(settRes);
      if (logsRes) setLogs(logsRes);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  // Refresh Market Handler
  const handleRefreshMarket = async () => {
    setRefreshingMarket(true);
    try {
      const res = await fetch('/api/market');
      if (res.ok) {
        const data = await res.json();
        setMarketData(data);
      }
    } finally {
      setRefreshingMarket(false);
    }
  };

  // Channels Handlers
  const handleAddChannel = async (channelData: any) => {
    const res = await fetch('/api/channels', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(channelData)
    });
    if (res.ok) {
      const newChan = await res.json();
      setChannels(prev => [...prev, newChan]);
    }
  };

  const handleToggleChannel = async (id: number, enabled: boolean) => {
    const res = await fetch(`/api/channels/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled })
    });
    if (res.ok) {
      setChannels(prev => prev.map(c => c.id === id ? { ...c, enabled } : c));
    }
  };

  const handleDeleteChannel = async (id: number) => {
    const res = await fetch(`/api/channels/${id}`, { method: 'DELETE' });
    if (res.ok) {
      setChannels(prev => prev.filter(c => c.id !== id));
    }
  };

  const handleTestChannel = async (id: number) => {
    const res = await fetch(`/api/channels/${id}/test`, { method: 'POST' });
    if (!res.ok) throw new Error('خطا در آزمون اتصال');
    const data = await res.json();
    setChannels(prev => prev.map(c => c.id === id ? { ...c, last_test_at: data.tested_at, last_test_ok: true } : c));
    return data;
  };

  // Queue Handlers
  const handleAddPost = async (postData: any) => {
    const res = await fetch('/api/queue', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(postData)
    });
    if (res.ok) {
      const newPost = await res.json();
      setPosts(prev => [newPost, ...prev]);
    }
  };

  const handleCancelPost = async (id: number) => {
    const res = await fetch(`/api/queue/${id}/cancel`, { method: 'POST' });
    if (res.ok) {
      setPosts(prev => prev.map(p => p.id === id ? { ...p, status: 'cancelled' } : p));
    }
  };

  const handleRetryPost = async (id: number) => {
    const res = await fetch(`/api/queue/${id}/retry`, { method: 'POST' });
    if (res.ok) {
      setPosts(prev => prev.map(p => p.id === id ? { ...p, status: 'pending', attempts: 0 } : p));
    }
  };

  const handlePublishNow = async (id: number) => {
    const res = await fetch(`/api/queue/${id}/publish-now`, { method: 'POST' });
    if (res.ok) {
      const updated = await res.json();
      setPosts(prev => prev.map(p => p.id === id ? updated : p));
    }
  };

  const handleViewAttempts = async (id: number) => {
    const res = await fetch(`/api/queue/${id}/attempts`);
    if (res.ok) return await res.json();
    return [];
  };

  // Studio Handlers
  const handleGenerateAI = async (params: any) => {
    const res = await fetch('/api/studio/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (res.ok) {
      const data = await res.json();
      if (data.draft) {
        setDrafts(prev => [data.draft, ...prev]);
      }
      return data;
    }
  };

  const handleSaveDraft = async (id: number, data: any) => {
    const res = await fetch(`/api/drafts/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (res.ok) {
      const updated = await res.json();
      setDrafts(prev => prev.map(d => d.id === id ? updated : d));
    }
  };

  const handleScheduleDraft = async (id: number, channelId: number, scheduledAt: string) => {
    const res = await fetch(`/api/drafts/${id}/schedule`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ channel_id: channelId, scheduled_at: scheduledAt })
    });
    if (res.ok) {
      const data = await res.json();
      if (data.post) {
        setPosts(prev => [data.post, ...prev]);
        setDrafts(prev => prev.map(d => d.id === id ? { ...d, status: 'scheduled' } : d));
      }
    }
  };

  // News Handlers
  const handleUpdateNewsStatus = async (id: number, status: string) => {
    const res = await fetch(`/api/news/${id}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    if (res.ok) {
      setNews(prev => prev.map(n => n.id === id ? { ...n, status } : n));
    }
  };

  const handleConvertNewsToDraft = async (id: number) => {
    const res = await fetch(`/api/news/${id}/convert-to-draft`, { method: 'POST' });
    if (res.ok) {
      const data = await res.json();
      if (data.draft) {
        setDrafts(prev => [data.draft, ...prev]);
        setNews(prev => prev.map(n => n.id === id ? { ...n, status: 'converted' } : n));
      }
    }
  };

  // Media Handlers
  const handleAddMedia = async (mediaData: any) => {
    const res = await fetch('/api/media', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(mediaData)
    });
    if (res.ok) {
      const newMedia = await res.json();
      setMediaAssets(prev => [newMedia, ...prev]);
    }
  };

  const handleDeleteMedia = async (id: number) => {
    const res = await fetch(`/api/media/${id}`, { method: 'DELETE' });
    if (res.ok) {
      setMediaAssets(prev => prev.filter(m => m.id !== id));
    }
  };

  // Settings Handlers
  const handleSaveSettings = async (newSettings: any) => {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newSettings)
    });
    if (res.ok) {
      const saved = await res.json();
      setSettings(saved);
    }
  };

  // Get current tab title
  const getTabTitle = () => {
    switch (currentTab) {
      case 'overview': return { title: 'نمای کلی سامانه', subtitle: 'خلاصه وضعیت کانال‌ها، صف انتشار و تابلوی نوبیتکس' };
      case 'channels': return { title: 'مدیریت کانال‌های تلگرام', subtitle: 'پیکربندی Bot API و دسترسی به کانال‌ها' };
      case 'queue': return { title: 'تقویم و صف انتشار', subtitle: 'مدیریت زمان‌بندی پست‌ها و بازیابی خطای شبکه' };
      case 'studio': return { title: 'استودیوی هوشمند تولید محتوا', subtitle: '۱۲ حوزه تخصصی ماینینگ، عیب‌یابی هش‌برد و تزریق قیمت' };
      case 'market': return { title: 'قیمت زنده ارزهای دیجیتال', subtitle: 'نرخ لحظه‌ای و نمودار تغییرات نوبیتکس (Nobitex Market)' };
      case 'news': return { title: 'پایگاه اخبار ماینینگ و بلاک‌چین', subtitle: 'پایش منابع معتبر، گردش کار تأیید و تبدیل به پست' };
      case 'media': return { title: 'کتابخانه رسانه و اسناد', subtitle: 'آرشیو تصاویر، شماتیک‌ها و کاتالوگ‌های فنی' };
      case 'reports': return { title: 'گزارش‌ها و آمار تحلیلی', subtitle: 'عملکرد کانال‌ها و بررسی سوابق تراکنش‌ها' };
      case 'settings': return { title: 'تنظیمات و APIها', subtitle: 'پیکربندی هوش مصنوعی، کنترل نرخ نوبیتکس و امنیت' };
      default: return { title: settings.app_name, subtitle: settings.app_subtitle };
    }
  };

  const { title, subtitle } = getTabTitle();
  const btcRate = marketData?.rates?.find((r: any) => r.symbol === 'BTC');

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#0b0f14] text-[#e8eef5]" dir="rtl">
      {/* Sidebar Navigation */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        appName={settings.app_name}
        version={settings.version || '2.0.1'}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <Header
          title={title}
          subtitle={subtitle}
          marketBtc={btcRate}
          onRefreshMarket={handleRefreshMarket}
          isRefreshing={refreshingMarket}
        />

        {/* Dynamic Page Container */}
        <main className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64 text-[#93a4b6] text-xs">
              در حال بارگذاری اطلاعات سامانه MinerMedia AI...
            </div>
          ) : (
            <>
              {currentTab === 'overview' && (
                <OverviewPage
                  data={overviewData}
                  onNavigate={setCurrentTab}
                  onRefresh={loadAllData}
                />
              )}
              {currentTab === 'channels' && (
                <ChannelsPage
                  channels={channels}
                  onAddChannel={handleAddChannel}
                  onToggleChannel={handleToggleChannel}
                  onDeleteChannel={handleDeleteChannel}
                  onTestChannel={handleTestChannel}
                />
              )}
              {currentTab === 'queue' && (
                <QueuePage
                  posts={posts}
                  channels={channels}
                  onAddPost={handleAddPost}
                  onCancelPost={handleCancelPost}
                  onRetryPost={handleRetryPost}
                  onPublishNow={handlePublishNow}
                  onViewAttempts={handleViewAttempts}
                />
              )}
              {currentTab === 'studio' && (
                <StudioPage
                  drafts={drafts}
                  channels={channels}
                  onGenerate={handleGenerateAI}
                  onSaveDraft={handleSaveDraft}
                  onScheduleDraft={handleScheduleDraft}
                />
              )}
              {currentTab === 'market' && (
                <MarketPage
                  marketData={marketData}
                  onRefresh={handleRefreshMarket}
                  isRefreshing={refreshingMarket}
                />
              )}
              {currentTab === 'news' && (
                <NewsPage
                  news={news}
                  onUpdateStatus={handleUpdateNewsStatus}
                  onConvertToDraft={handleConvertNewsToDraft}
                  onNavigateToStudio={() => setCurrentTab('studio')}
                />
              )}
              {currentTab === 'media' && (
                <MediaPage
                  assets={mediaAssets}
                  onAddMedia={handleAddMedia}
                  onDeleteMedia={handleDeleteMedia}
                />
              )}
              {currentTab === 'reports' && (
                <ReportsPage
                  reports={reports}
                  logs={logs}
                />
              )}
              {currentTab === 'settings' && (
                <SettingsPage
                  settings={settings}
                  onSaveSettings={handleSaveSettings}
                />
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
