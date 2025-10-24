
import React, { useState, useEffect, useRef } from 'react';
import { GoogleGenAI } from "@google/genai";
import { Prompt, PromptType } from '../types';
import { Video, Sparkles, Download, Plus, Upload, X } from './icons';

const MAX_FILE_SIZE = 4 * 1024 * 1024; // 4MB

const blobToBase64 = (blob: Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result as string);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
};

// @ts-ignore
declare global {
    interface Window {
        aistudio: {
            hasSelectedApiKey: () => Promise<boolean>;
            openSelectKey: () => Promise<void>;
        };
    }
}

const loadingMessages = [
    "در حال آماده‌سازی استودیو...",
    "در حال تماس با هوش مصنوعی...",
    "هوش مصنوعی در حال ایده‌پردازی است...",
    "در حال ساخت فریم‌های اولیه...",
    "در حال رندر کردن ویدیو...",
    "این فرآیند ممکن است چند دقیقه طول بکشد...",
    "در حال نهایی‌سازی جزئیات..."
];

interface VideoStudioProps {
  onSave: (prompt: Prompt) => void;
}

const VideoStudio: React.FC<VideoStudioProps> = ({ onSave }) => {
    const [apiKeySelected, setApiKeySelected] = useState(false);
    const [promptText, setPromptText] = useState('');
    const [startImage, setStartImage] = useState<string | null>(null);
    const [aspectRatio, setAspectRatio] = useState<'16:9' | '9:16'>('16:9');
    const [resolution, setResolution] = useState<'720p' | '1080p'>('720p');
    
    const [isLoading, setIsLoading] = useState(false);
    const [loadingMessage, setLoadingMessage] = useState(loadingMessages[0]);
    const [error, setError] = useState<string | null>(null);
    const [resultVideoUrl, setResultVideoUrl] = useState<string | null>(null);
    
    const loadingIntervalRef = useRef<number | null>(null);

    useEffect(() => {
        const checkApiKey = async () => {
            if (window.aistudio && await window.aistudio.hasSelectedApiKey()) {
                setApiKeySelected(true);
            }
        };
        checkApiKey();
    }, []);

    useEffect(() => {
        if (isLoading) {
            loadingIntervalRef.current = window.setInterval(() => {
                setLoadingMessage(prev => {
                    const currentIndex = loadingMessages.indexOf(prev);
                    return loadingMessages[(currentIndex + 1) % loadingMessages.length];
                });
            }, 3000);
        } else if (loadingIntervalRef.current) {
            clearInterval(loadingIntervalRef.current);
            loadingIntervalRef.current = null;
        }
        return () => {
            if (loadingIntervalRef.current) clearInterval(loadingIntervalRef.current);
        };
    }, [isLoading]);

    const handleSelectKey = async () => {
        await window.aistudio.openSelectKey();
        // Assume success to avoid race condition
        setApiKeySelected(true);
    };

    const handleImageChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files[0]) {
            const file = event.target.files[0];
            if (file.size > MAX_FILE_SIZE) {
                alert(`حجم فایل ${file.name} باید کمتر از 4MB باشد.`);
                return;
            }
            try {
                const base64 = await blobToBase64(file);
                setStartImage(base64);
            } catch (err) {
                 console.error("Error converting file to base64:", err);
            }
        }
    };

    const handleGenerate = async () => {
        setIsLoading(true);
        setError(null);
        setResultVideoUrl(null);
        setLoadingMessage(loadingMessages[0]);

        try {
            const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
            const imagePayload = startImage ? {
                imageBytes: startImage.split(',')[1],
                mimeType: startImage.match(/data:(.*);base64/)?.[1] || 'image/png'
            } : undefined;

            let operation = await ai.models.generateVideos({
                model: 'veo-3.1-fast-generate-preview',
                prompt: promptText,
                image: imagePayload,
                config: {
                    numberOfVideos: 1,
                    resolution,
                    aspectRatio,
                }
            });

            while (!operation.done) {
                await new Promise(resolve => setTimeout(resolve, 10000));
                operation = await ai.operations.getVideosOperation({ operation });
            }

            const downloadLink = operation.response?.generatedVideos?.[0]?.video?.uri;
            if (downloadLink) {
                const response = await fetch(`${downloadLink}&key=${process.env.API_KEY}`);
                const videoBlob = await response.blob();
                const objectUrl = URL.createObjectURL(videoBlob);
                setResultVideoUrl(objectUrl);
            } else {
                throw new Error("لینک دانلود ویدیو یافت نشد.");
            }
        } catch (err: any) {
            console.error(err);
            const errorMessage = err.message || 'یک خطای غیرمنتظره رخ داد.';
            if (errorMessage.includes("Requested entity was not found.")) {
                setError("کلید API نامعتبر است. لطفا یک کلید جدید انتخاب کنید.");
                setApiKeySelected(false); // Reset key state
            } else {
                setError(errorMessage);
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handleSave = () => {
        if (!resultVideoUrl) return;
        const now = new Date().toISOString();
        const newPrompt: Prompt = {
            id: new Date().getTime().toString(),
            title: `ویدیو: ${promptText.substring(0, 30)}...`,
            content: promptText,
            type: PromptType.Video,
            tags: ['video-studio', 'ai-generated', aspectRatio, resolution],
            createdAt: now,
            updatedAt: now,
            rating: 0,
            // We don't save the video URL as it's temporary
        };
        onSave(newPrompt);
        alert('پرامپت ویدیو با موفقیت ذخیره شد!');
    };
    
    if (!apiKeySelected) {
        return (
            <div className="p-6 h-full flex flex-col items-center justify-center text-center animate-fade-in" dir="rtl">
                <Video className="w-16 h-16 text-dark-primary mb-4" />
                <h1 className="text-2xl font-bold mb-2">به استودیوی ویدیو خوش آمدید</h1>
                <p className="max-w-md mb-4 text-gray-500 dark:text-dark-subtext">برای استفاده از این قابلیت (که از مدل Veo استفاده می‌کند)، باید یک کلید API را انتخاب کرده و صورتحساب را فعال کنید.</p>
                <p className="text-xs max-w-md mb-6 text-gray-400 dark:text-dark-subtext/70">
                    برای اطلاعات بیشتر در مورد قیمت‌گذاری، به <a href="https://ai.google.dev/gemini-api/docs/billing" target="_blank" rel="noopener noreferrer" className="underline text-dark-primary">مستندات صورتحساب</a> مراجعه کنید.
                </p>
                <button onClick={handleSelectKey} className="bg-dark-primary text-white font-semibold px-6 py-3 rounded-full hover:bg-opacity-90 transition-all shadow-lg shadow-dark-primary/30">
                    انتخاب کلید API
                </button>
            </div>
        )
    }

    return (
        <div className="p-6 h-full overflow-y-auto animate-fade-in" dir="rtl">
            <div className="flex items-center gap-3 mb-2">
                <Video className="w-8 h-8 text-dark-primary" />
                <h1 className="text-3xl font-bold text-gray-800 dark:text-dark-text">استودیوی ویدیو AI</h1>
            </div>
            <p className="text-gray-500 dark:text-dark-subtext mb-6">ایده‌های خود را با قدرت مدل Veo به ویدیوهای شگفت‌انگیز تبدیل کنید.</p>

             <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Input Column */}
                <div className="bg-white dark:bg-dark-surface p-6 rounded-2xl shadow-lg space-y-6">
                    <div>
                        <h2 className="text-xl font-semibold mb-3">۱. پرامپت خود را بنویسید</h2>
                        <textarea
                            value={promptText}
                            onChange={(e) => setPromptText(e.target.value)}
                            rows={6}
                            placeholder="مثلا: یک ربات آینده‌نگر در حال اسکیت‌بورد سواری در یک شهر نئونی..."
                            className="w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0 resize-none p-3"
                        />
                    </div>
                    <div>
                        <h2 className="text-xl font-semibold mb-3">۲. تصویر اولیه (اختیاری)</h2>
                         {startImage ? (
                            <div className="relative group aspect-video">
                                <img src={startImage} alt="Uploaded" className="w-full h-full object-contain rounded-lg bg-gray-100 dark:bg-dark-bg" />
                                <button onClick={() => setStartImage(null)} className="absolute top-2 right-2 bg-black/50 text-white rounded-full p-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <X className="w-5 h-5" />
                                </button>
                            </div>
                        ) : (
                            <label className="aspect-video border-2 border-dashed border-gray-300 dark:border-dark-overlay rounded-lg flex flex-col items-center justify-center cursor-pointer hover:bg-gray-50 dark:hover:bg-dark-overlay/20 transition-colors">
                                <Upload className="w-10 h-10 text-gray-400 dark:text-dark-subtext" />
                                <span className="mt-2 text-sm text-center text-gray-500 dark:text-dark-subtext">برای آپلود کلیک کنید</span>
                                <input type="file" accept="image/png, image/jpeg, image/webp" className="hidden" onChange={handleImageChange} />
                            </label>
                        )}
                    </div>
                    <div>
                         <h2 className="text-xl font-semibold mb-3">۳. تنظیمات</h2>
                         <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-dark-subtext mb-1">نسبت تصویر</label>
                                <select value={aspectRatio} onChange={(e) => setAspectRatio(e.target.value as any)} className="w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0">
                                    <option value="16:9">۱۶:۹ (افقی)</option>
                                    <option value="9:16">۹:۱۶ (عمودی)</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-dark-subtext mb-1">کیفیت</label>
                                <select value={resolution} onChange={(e) => setResolution(e.target.value as any)} className="w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0">
                                    <option value="720p">720p</option>
                                    <option value="1080p">1080p</option>
                                </select>
                            </div>
                         </div>
                    </div>
                     <button
                        onClick={handleGenerate}
                        disabled={isLoading || !promptText.trim()}
                        className="w-full flex items-center justify-center gap-2 bg-dark-primary text-white font-bold px-4 py-3 rounded-full hover:bg-opacity-90 transition-all duration-200 shadow-lg shadow-dark-primary/30 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Sparkles className={`w-6 h-6 ${isLoading ? 'animate-spin' : ''}`} />
                        {isLoading ? 'در حال ساخت ویدیو...' : 'ویدیو را بساز!'}
                    </button>
                </div>
                 {/* Output Column */}
                 <div className="bg-white dark:bg-dark-surface p-6 rounded-2xl shadow-lg flex flex-col items-center justify-center">
                    <div className="w-full aspect-video bg-gray-100 dark:bg-dark-bg rounded-lg flex items-center justify-center mb-4">
                         {isLoading ? (
                            <div className="flex flex-col items-center text-dark-primary p-4 text-center">
                                <Sparkles className="w-12 h-12 animate-spin" />
                                <p className="mt-4 font-semibold">{loadingMessage}</p>
                            </div>
                        ) : error ? (
                             <div className="text-center text-dark-danger p-4">
                                <p className="font-semibold">خطا!</p>
                                <p className="text-sm">{error}</p>
                            </div>
                        ) : resultVideoUrl ? (
                            <video src={resultVideoUrl} controls autoPlay loop className="rounded-lg w-full h-full" />
                        ) : (
                            <div className="text-center text-gray-400 dark:text-dark-subtext">
                                <Video className="w-16 h-16 mx-auto" />
                                <p className="mt-2 font-semibold">نتیجه اینجا نمایش داده می‌شود</p>
                            </div>
                        )}
                    </div>
                     {resultVideoUrl && !isLoading && (
                        <div className="w-full grid grid-cols-2 gap-4 animate-fade-in">
                            <a href={resultVideoUrl} download={`prompt-studio-video-${Date.now()}.mp4`} className="w-full flex items-center justify-center gap-2 bg-dark-secondary/10 text-dark-secondary font-semibold px-4 py-2 rounded-lg hover:bg-opacity-90 transition-all duration-200">
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

export default VideoStudio;
