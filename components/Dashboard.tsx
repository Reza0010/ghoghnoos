
import React from 'react';
import { PieChart, Pie, Cell, Legend, ResponsiveContainer, Tooltip } from 'recharts';
import { Prompt, PromptType } from '../types';
import { PROMPT_TYPE_CONFIG } from '../constants';
import { Download, Upload, Star } from './icons';

interface DashboardProps {
  prompts: Prompt[];
  onImport: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onExport: () => void;
}

const timeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    let interval = seconds / 31536000;
    if (interval > 1) return `${Math.floor(interval)} سال پیش`;
    interval = seconds / 2592000;
    if (interval > 1) return `${Math.floor(interval)} ماه پیش`;
    interval = seconds / 86400;
    if (interval > 1) return `${Math.floor(interval)} روز پیش`;
    interval = seconds / 3600;
    if (interval > 1) return `${Math.floor(interval)} ساعت پیش`;
    interval = seconds / 60;
    if (interval > 1) return `${Math.floor(interval)} دقیقه پیش`;
    return 'همین الان';
};


const Dashboard: React.FC<DashboardProps> = ({ prompts, onImport, onExport }) => {

  // --- Data Processing ---

  const totalPrompts = prompts.length;
  const promptsWithRatings = prompts.filter(p => p.rating && p.rating > 0);
  const averageRating = promptsWithRatings.length > 0
    ? (promptsWithRatings.reduce((acc, p) => acc + (p.rating || 0), 0) / promptsWithRatings.length).toFixed(1)
    : 'N/A';
  const totalTags = new Set(prompts.flatMap(p => p.tags)).size;

  const promptTypeData = Object.values(PromptType).map(type => {
    const config = PROMPT_TYPE_CONFIG[type as PromptType];
    return {
      name: config.label.split(' ')[1],
      value: prompts.filter(p => p.type === type).length,
      color: PROMPT_TYPE_CONFIG[type as PromptType].borderColor.replace('border-', '#').replace('-500', ''),
    };
  }).filter(d => d.value > 0);

  const ratingData = [1, 2, 3, 4, 5].map(star => ({
    name: `${star} ستاره`,
    value: prompts.filter(p => p.rating === star).length
  })).filter(d => d.value > 0);
  const RATING_COLORS = ['#f7768e', '#e0af68', '#73daca', '#7aa2f7', '#bb9af7']; // 1 to 5 stars

  const recentPrompts = [...prompts]
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    .slice(0, 5);
    
  // FIX: Explicitly typed the accumulator in the reduce function to ensure `tagFrequency` is a `Record<string, number>`, which resolves downstream type errors.
  const tagFrequency = prompts.flatMap(p => p.tags).reduce((acc: Record<string, number>, tag) => {
    acc[tag] = (acc[tag] || 0) + 1;
    return acc;
  }, {});

  const sortedTags = Object.entries(tagFrequency).sort((a, b) => b[1] - a[1]).slice(0, 20);
  const maxFreq = sortedTags.length > 0 ? sortedTags[0][1] : 1;

  // --- Rendering Helpers ---

  const RADIAN = Math.PI / 180;
  // FIX: Replaced `any` with an explicit object type for recharts props to resolve arithmetic operation errors.
  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }: { cx: number; cy: number; midAngle: number; innerRadius: number; outerRadius: number; percent: number; }) => {
    if (percent < 0.05) return null; // Don't render label for small slices
    
    const radius = innerRadius + (outerRadius - innerRadius) * 0.6;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central" fontSize="14" fontWeight="bold">
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };
  
  // FIX: Replaced `any` with an explicit type for recharts tooltip props for type safety.
  const CustomTooltip = ({ active, payload }: { active?: boolean, payload?: Array<{ name: string, value: number }> }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-dark-overlay p-3 rounded-lg border border-dark-surface text-sm">
          <p className="label">{`${payload[0].name} : ${payload[0].value}`}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="p-6 h-full overflow-y-auto animate-fade-in" dir="rtl">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-dark-text mb-6">داشبورد پیشرفته</h1>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white dark:bg-dark-surface p-5 rounded-2xl shadow-lg animate-slide-in-up">
          <h3 className="text-md font-semibold text-gray-500 dark:text-dark-subtext">تعداد کل پرامپت‌ها</h3>
          <p className="text-4xl font-bold text-dark-primary mt-2">{totalPrompts}</p>
        </div>
        <div className="bg-white dark:bg-dark-surface p-5 rounded-2xl shadow-lg animate-slide-in-up" style={{animationDelay: '100ms'}}>
          <h3 className="text-md font-semibold text-gray-500 dark:text-dark-subtext">میانگین امتیاز</h3>
          <div className="flex items-center gap-2">
            <p className="text-4xl font-bold text-dark-warn mt-2">{averageRating}</p>
            {averageRating !== 'N/A' && <Star className="w-8 h-8 text-dark-warn mt-2" />}
          </div>
        </div>
        <div className="bg-white dark:bg-dark-surface p-5 rounded-2xl shadow-lg animate-slide-in-up" style={{animationDelay: '200ms'}}>
          <h3 className="text-md font-semibold text-gray-500 dark:text-dark-subtext">تعداد کل تگ‌ها</h3>
          <p className="text-4xl font-bold text-dark-accent mt-2">{totalTags}</p>
        </div>
        <div className="bg-white dark:bg-dark-surface p-5 rounded-2xl shadow-lg animate-slide-in-up flex flex-col justify-center" style={{animationDelay: '300ms'}}>
           <h3 className="text-md font-semibold text-gray-500 dark:text-dark-subtext mb-2">مدیریت داده‌ها</h3>
           <div className="flex gap-2">
              <label htmlFor="import-file" className="flex-1 flex items-center justify-center gap-2 bg-dark-accent/10 text-dark-accent font-semibold px-3 py-2 rounded-lg hover:bg-opacity-90 transition-all duration-200 cursor-pointer">
                  <Upload className="w-4 h-4" />
                  ورود
              </label>
              <input type="file" id="import-file" className="hidden" accept=".json" onChange={onImport} />
              <button onClick={onExport} className="flex-1 flex items-center justify-center gap-2 bg-dark-secondary/10 text-dark-secondary font-semibold px-3 py-2 rounded-lg hover:bg-opacity-90 transition-all duration-200">
                  <Download className="w-4 h-4" />
                  خروج
              </button>
           </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
           <div className="bg-white dark:bg-dark-surface p-6 rounded-2xl shadow-lg h-80">
                <h2 className="text-xl font-bold text-gray-700 dark:text-dark-text mb-4">توزیع نوع پرامپت</h2>
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie data={promptTypeData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={100} labelLine={false} label={renderCustomizedLabel} paddingAngle={5}>
                            {promptTypeData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                        </Pie>
                        <Tooltip content={<CustomTooltip />} />
                        <Legend wrapperStyle={{fontSize: '14px'}}/>
                    </PieChart>
                </ResponsiveContainer>
            </div>
             <div className="bg-white dark:bg-dark-surface p-6 rounded-2xl shadow-lg h-80">
                <h2 className="text-xl font-bold text-gray-700 dark:text-dark-text mb-4">توزیع امتیازات</h2>
                 <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie data={ratingData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={100} labelLine={false} label={renderCustomizedLabel} paddingAngle={5}>
                             {ratingData.map((entry, index) => <Cell key={`cell-${index}`} fill={RATING_COLORS[parseInt(entry.name) - 1]} />)}
                        </Pie>
                        <Tooltip content={<CustomTooltip />} />
                        <Legend wrapperStyle={{fontSize: '14px'}}/>
                    </PieChart>
                </ResponsiveContainer>
            </div>
        </div>
        <div className="lg:col-span-1 space-y-6">
            <div className="bg-white dark:bg-dark-surface p-6 rounded-2xl shadow-lg">
                <h2 className="text-xl font-bold text-gray-700 dark:text-dark-text mb-4">فعالیت‌های اخیر</h2>
                <div className="space-y-4">
                    {recentPrompts.map(prompt => {
                        const config = PROMPT_TYPE_CONFIG[prompt.type];
                        return (
                             <div key={prompt.id} className="flex items-center gap-3">
                                <div className={`w-10 h-10 rounded-lg ${config.color} flex-shrink-0 flex items-center justify-center`}>
                                    <config.icon className="w-5 h-5 text-white" />
                                </div>
                                <div>
                                    <p className="font-semibold text-sm truncate">{prompt.title}</p>
                                    <p className="text-xs text-gray-400 dark:text-dark-subtext/70">{timeAgo(prompt.updatedAt)}</p>
                                </div>
                            </div>
                        )
                    })}
                </div>
            </div>
            <div className="bg-white dark:bg-dark-surface p-6 rounded-2xl shadow-lg">
                <h2 className="text-xl font-bold text-gray-700 dark:text-dark-text mb-4">ابر تگ‌ها</h2>
                <div className="flex flex-wrap gap-2 justify-center">
                    {sortedTags.map(([tag, freq]) => {
                        const ratio = maxFreq > 1 ? (freq - 1) / (maxFreq - 1) : 0;
                        const fontSize = 12 + ratio * (24 - 12);
                        const opacity = 0.6 + ratio * 0.4;
                        return (
                            <span key={tag} className="text-dark-primary cursor-pointer hover:text-dark-accent transition-colors" style={{fontSize: `${fontSize}px`, opacity: opacity}}>
                                {tag}
                            </span>
                        )
                    })}
                </div>
            </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
