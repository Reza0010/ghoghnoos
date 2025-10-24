import React, { useEffect, useMemo, useState } from 'react';
import useLocalStorage from '../hooks/useLocalStorage';
import { useToast } from './ToastProvider';

interface SettingsProps {
  prompts: unknown[];
  setPrompts: (value: unknown[]) => void;
}

const TEXT_MODELS = [
  'gemini-2.5-flash',
  'gemini-1.5-flash',
  'gemini-2.0-flash-lite',
];

const IMAGE_MODELS = [
  'imagen-4.0-generate-001',
];

const Settings: React.FC<SettingsProps> = ({ prompts, setPrompts }) => {
  const { showToast } = useToast();
  const [apiKey, setApiKey] = useLocalStorage<string>('geminiApiKey', '');
  const [defaultTextModel, setDefaultTextModel] = useLocalStorage<string>('defaultTextModel', TEXT_MODELS[0]);
  const [defaultImageModel, setDefaultImageModel] = useLocalStorage<string>('defaultImageModel', IMAGE_MODELS[0]);
  const [defaultTemperature, setDefaultTemperature] = useLocalStorage<number>('defaultTemperature', 0.7);

  const promptsCount = useMemo(() => Array.isArray(prompts) ? prompts.length : 0, [prompts]);

  const handleSave = () => {
    showToast('تنظیمات ذخیره شد', { type: 'success' });
  };

  const handleBackup = () => {
    try {
      const data = window.localStorage.getItem('prompts') || '[]';
      const uri = 'data:application/json;charset=utf-8,' + encodeURIComponent(data);
      const link = document.createElement('a');
      link.setAttribute('href', uri);
      link.setAttribute('download', 'prompt_studio_backup.json');
      link.click();
      showToast('پشتیبان‌گیری انجام شد', { type: 'success' });
    } catch {
      showToast('خطا در پشتیبان‌گیری', { type: 'error' });
    }
  };

  const handleRestore: React.ChangeEventHandler<HTMLInputElement> = (event) => {
    if (!event.target.files || !event.target.files[0]) return;
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const json = JSON.parse(String(reader.result || '[]'));
        if (Array.isArray(json)) {
          window.localStorage.setItem('prompts', JSON.stringify(json));
          setPrompts(json);
          showToast('بازیابی انجام شد', { type: 'success' });
        } else {
          throw new Error('invalid format');
        }
      } catch {
        showToast('فایل نامعتبر است', { type: 'error' });
      }
    };
    reader.readAsText(file);
  };

  const handleClearAll = () => {
    if (!window.confirm('همه داده‌ها حذف شوند؟ این عملیات غیرقابل بازگشت است.')) return;
    try {
      window.localStorage.clear();
      setPrompts([]);
      showToast('همه داده‌ها پاک شد', { type: 'success' });
    } catch {
      showToast('خطا در حذف داده‌ها', { type: 'error' });
    }
  };

  return (
    <div className="p-6 h-full overflow-y-auto animate-fade-in" dir="rtl">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-dark-text mb-2">تنظیمات</h1>
      <p className="text-gray-500 dark:text-dark-subtext mb-6">کلید API و تنظیمات پیش‌فرض مدل‌ها را مدیریت کنید. همچنین از داده‌ها پشتیبان بگیرید.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-dark-surface rounded-2xl shadow-lg p-6 space-y-4">
          <h2 className="text-xl font-bold">اتصال API</h2>
          <label className="block text-sm font-medium mb-1">کلید API سرویس Gemini</label>
          <input
            type="password"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            placeholder="کلید خود را وارد کنید"
            className="w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0"
          />
          <button onClick={handleSave} className="mt-2 px-4 py-2 rounded-full text-white bg-dark-primary hover:opacity-90 font-semibold transition">ذخیره</button>
          {apiKey ? <p className="text-xs text-green-500">کلید ثبت شده است</p> : <p className="text-xs text-red-500">کلید ثبت نشده</p>}
        </div>

        <div className="bg-white dark:bg-dark-surface rounded-2xl shadow-lg p-6 space-y-4">
          <h2 className="text-xl font-bold">تنظیمات پیش‌فرض مدل</h2>
          <div>
            <label className="block text-sm font-medium mb-1">مدل متنی</label>
            <select value={defaultTextModel} onChange={e => setDefaultTextModel(e.target.value)} className="w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0">
              {TEXT_MODELS.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">مدل تصویری</label>
            <select value={defaultImageModel} onChange={e => setDefaultImageModel(e.target.value)} className="w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0">
              {IMAGE_MODELS.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Temperature پیش‌فرض: <span className="font-semibold">{defaultTemperature.toFixed(2)}</span></label>
            <input type="range" min={0} max={1} step={0.01} value={defaultTemperature} onChange={e => setDefaultTemperature(parseFloat(e.target.value))} className="w-full" />
          </div>
          <button onClick={handleSave} className="px-4 py-2 rounded-full text-white bg-dark-primary hover:opacity-90 font-semibold transition">ذخیره</button>
        </div>

        <div className="bg-white dark:bg-dark-surface rounded-2xl shadow-lg p-6 space-y-4 lg:col-span-2">
          <h2 className="text-xl font-bold">پشتیبان‌گیری و بازیابی</h2>
          <p className="text-sm text-gray-500 dark:text-dark-subtext">تعداد پرامپت‌های ذخیره‌شده: {promptsCount}</p>
          <div className="flex flex-wrap gap-3">
            <button onClick={handleBackup} className="px-4 py-2 rounded-lg text-dark-accent bg-dark-accent/10 hover:bg-dark-accent/20 font-semibold transition">دانلود پشتیبان</button>
            <label className="px-4 py-2 rounded-lg text-dark-secondary bg-dark-secondary/10 hover:bg-dark-secondary/20 font-semibold transition cursor-pointer">
              بارگذاری پشتیبان
              <input type="file" accept=".json" onChange={handleRestore} className="hidden" />
            </label>
            <button onClick={handleClearAll} className="px-4 py-2 rounded-lg text-dark-danger bg-dark-danger/10 hover:bg-dark-danger/20 font-semibold transition">حذف همه داده‌ها</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
