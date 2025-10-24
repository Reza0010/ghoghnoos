import React, { useState } from 'react';
import { Prompt, PromptType } from '../types';
import { generateMusic } from '../services/geminiService';
import { Music, Sparkles, Download, Plus } from './icons';

interface MusicStudioProps {
  onSave: (prompt: Prompt) => void;
}

const GENRES = ['سینمایی', 'کلاسیک', 'جاز', 'الکترونیک', 'راک', 'Lo-fi', 'امبینت'];
const MOODS = ['شاد', 'غمگین', 'حماسی', 'آرامش‌بخش', 'مرموز', 'انرژی‌بخش', 'رمانتیک'];

const MusicStudio: React.FC<MusicStudioProps> = ({ onSave }) => {
    const [promptText, setPromptText] = useState('');
    const [genre, setGenre] = useState(GENRES[0]);
    const [mood, setMood] = useState(MOODS[0]);
    const [duration, setDuration] = useState(60);
    
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [resultAudioUrl, setResultAudioUrl] = useState<string | null>(null);
    
    const handleGenerate = async () => {
        setIsLoading(true);
        setError(null);
        setResultAudioUrl(null);

        try {
            const fullPrompt = `یک قطعه موسیقی در ژانر ${genre} با حال و هوای ${mood} بساز. توضیحات: ${promptText}`;
            const result = await generateMusic(fullPrompt, duration);

            if (result) {
                setResultAudioUrl(result);
            } else {
                // This will be triggered by the placeholder function
                setError('قابلیت تولید موسیقی هنوز فعال نشده است. این رابط کاربری برای ادغام با مدل‌های آینده آماده شده است.');
            }
        } catch (err: any) {
            setError(err.message || 'یک خطای غیرمنتظره رخ داد.');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };
    
    const handleSave = () => {
        // We don't save if there's no audio URL, but this is for future use.
        if (!resultAudioUrl) {
            alert("هنوز موسیقی برای ذخیره تولید نشده است.");
            return;
        };
        const now = new Date().toISOString();
        const newPrompt: Prompt = {
            id: new Date().getTime().toString(),
            title: `موسیقی: ${promptText.substring(0, 30)}...`,
            content: `Prompt: ${promptText}\nGenre: ${genre}\nMood: ${mood}\nDuration: ${duration}s`,
            type: PromptType.Music,
            tags: ['music-studio', 'ai-generated', genre, mood],
            createdAt: now,
            updatedAt: now,
            rating: 0,
            // We wouldn't save the temporary audio URL in a real app,
            // but we might save a permanent reference if the API provided one.
        };
        onSave(newPrompt);
        alert('پرامپت موسیقی با موفقیت ذخیره شد!');
    };

    return (
        <div className="p-6 h-full overflow-y-auto animate-fade-in" dir="rtl">
            <div className="flex items-center gap-3 mb-2">
                <Music className="w-8 h-8 text-dark-primary" />
                <h1 className="text-3xl font-bold text-gray-800 dark:text-dark-text">استودیوی موسیقی AI</h1>
            </div>
            <p className="text-gray-500 dark:text-dark-subtext mb-6">ایده‌های خود را به موسیقی تبدیل کنید. (آماده برای مدل‌های آینده)</p>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Input Column */}
                <div className="bg-white dark:bg-dark-surface p-6 rounded-2xl shadow-lg space-y-6">
                    <div>
                        <h2 className="text-xl font-semibold mb-3">۱. ایده اصلی خود را توصیف کنید</h2>
                        <textarea
                            value={promptText}
                            onChange={(e) => setPromptText(e.target.value)}
                            rows={6}
                            placeholder="مثلا: یک قطعه پیانوی آرام و احساسی با صدای پس‌زمینه بارش باران، مناسب برای تمرکز..."
                            className="w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0 resize-none p-3"
                        />
                    </div>
                    <div>
                         <h2 className="text-xl font-semibold mb-3">۲. جزئیات را انتخاب کنید</h2>
                         <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-dark-subtext mb-1">ژانر</label>
                                <select value={genre} onChange={(e) => setGenre(e.target.value)} className="w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0">
                                    {GENRES.map(g => <option key={g} value={g}>{g}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-dark-subtext mb-1">حال و هوا</label>
                                <select value={mood} onChange={(e) => setMood(e.target.value)} className="w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0">
                                    {MOODS.map(m => <option key={m} value={m}>{m}</option>)}
                                </select>
                            </div>
                         </div>
                         <div className="mt-4">
                             <label htmlFor="duration" className="block text-sm font-medium text-gray-700 dark:text-dark-subtext mb-1">مدت زمان (ثانیه): {duration}</label>
                            <input
                                id="duration"
                                type="range"
                                min="15"
                                max="180"
                                step="15"
                                value={duration}
                                onChange={(e) => setDuration(Number(e.target.value))}
                                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-dark-overlay"
                            />
                         </div>
                    </div>
                     <button
                        onClick={handleGenerate}
                        disabled={isLoading || !promptText.trim()}
                        className="w-full flex items-center justify-center gap-2 bg-dark-primary text-white font-bold px-4 py-3 rounded-full hover:bg-opacity-90 transition-all duration-200 shadow-lg shadow-dark-primary/30 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Sparkles className={`w-6 h-6 ${isLoading ? 'animate-spin' : ''}`} />
                        {isLoading ? 'در حال ساخت...' : 'موسیقی را بساز!'}
                    </button>
                </div>
                 {/* Output Column */}
                 <div className="bg-white dark:bg-dark-surface p-6 rounded-2xl shadow-lg flex flex-col items-center justify-center">
                    <div className="w-full min-h-[150px] bg-gray-100 dark:bg-dark-bg rounded-lg flex items-center justify-center mb-4 p-4">
                         {isLoading ? (
                            <div className="flex flex-col items-center text-dark-primary">
                                <Sparkles className="w-12 h-12 animate-spin" />
                                <p className="mt-4 font-semibold">ارتباط با ارکستر هوش مصنوعی...</p>
                            </div>
                        ) : error ? (
                             <div className="text-center text-dark-warn p-4">
                                <p className="font-semibold">توجه!</p>
                                <p className="text-sm">{error}</p>
                            </div>
                        ) : resultAudioUrl ? (
                            <audio src={resultAudioUrl} controls className="w-full" />
                        ) : (
                            <div className="text-center text-gray-400 dark:text-dark-subtext">
                                <Music className="w-16 h-16 mx-auto" />
                                <p className="mt-2 font-semibold">نتیجه اینجا پخش می‌شود</p>
                            </div>
                        )}
                    </div>
                     {resultAudioUrl && !isLoading && (
                        <div className="w-full grid grid-cols-2 gap-4 animate-fade-in">
                            <a href={resultAudioUrl} download={`prompt-studio-music-${Date.now()}.mp3`} className="w-full flex items-center justify-center gap-2 bg-dark-secondary/10 text-dark-secondary font-semibold px-4 py-2 rounded-lg hover:bg-opacity-90 transition-all duration-200">
                                <Download className="w-5 h-5"/>
                                دانلود
                            </a>
                            <button onClick={handleSave} className="w-full flex items-center justify-center gap-2 bg-dark-accent/10 text-dark-accent font-semibold px-4 py-2 rounded-lg hover:bg-opacity-90 transition-all duration-200">
                                <Plus className="w-5 h-5" />
                                ذخیره پرامپت
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default MusicStudio;