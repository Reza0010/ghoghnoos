
import React, { useState } from 'react';
import { Prompt, PromptType } from '../types';
import { fuseFaces } from '../services/geminiService';
import { Users, Upload, X, Sparkles, Download, Plus, Image as ImageIcon } from './icons';

interface FaceFusionProps {
  onSave: (prompt: Prompt) => void;
}

const MAX_FUSION_IMAGES = 3;
const MAX_FILE_SIZE = 4 * 1024 * 1024; // 4MB

const blobToBase64 = (blob: Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result as string);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
};

type Mode = 'fusion' | 'style';

const FaceFusion: React.FC<FaceFusionProps> = ({ onSave }) => {
    const [mode, setMode] = useState<Mode>('fusion');
    
    // State for Fusion mode
    const [sourceImages, setSourceImages] = useState<string[]>([]);
    
    // State for Style Transfer mode
    const [contentImage, setContentImage] = useState<string | null>(null);
    const [styleImage, setStyleImage] = useState<string | null>(null);

    const [promptText, setPromptText] = useState('');
    const [resultImage, setResultImage] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleModeChange = (newMode: Mode) => {
        if (mode === newMode) return;
        setMode(newMode);
        // Reset all inputs to avoid confusion
        setSourceImages([]);
        setContentImage(null);
        setStyleImage(null);
        setPromptText('');
        setResultImage(null);
        setError(null);
        setIsLoading(false);
    };

    const handleFusionFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        if (!event.target.files) return;

        const files = Array.from(event.target.files);
        const newImages: string[] = [];

        for (const file of files) {
            if (sourceImages.length + newImages.length >= MAX_FUSION_IMAGES) {
                alert(`شما فقط می‌توانید تا ${MAX_FUSION_IMAGES} تصویر آپلود کنید.`);
                break;
            }
            const currentFile = file as File;
            if (currentFile.size > MAX_FILE_SIZE) {
                alert(`حجم فایل ${currentFile.name} باید کمتر از 4MB باشد.`);
                continue;
            }
            try {
                const base64 = await blobToBase64(currentFile);
                newImages.push(base64);
            } catch (err) {
                console.error("Error converting file to base64:", err);
            }
        }
        setSourceImages(prev => [...prev, ...newImages]);
    };
    
    const handleSingleFileChange = async (event: React.ChangeEvent<HTMLInputElement>, setImage: (b64: string) => void) => {
        if (event.target.files && event.target.files[0]) {
            const file = event.target.files[0];
            if (file.size > MAX_FILE_SIZE) {
                alert(`حجم فایل ${file.name} باید کمتر از 4MB باشد.`);
                return;
            }
            try {
                const base64 = await blobToBase64(file);
                setImage(base64);
            } catch (err) {
                 console.error("Error converting file to base64:", err);
            }
        }
    };
    
    const handleRemoveFusionImage = (index: number) => {
        setSourceImages(prev => prev.filter((_, i) => i !== index));
    };

    const handleGenerate = async () => {
        setIsLoading(true);
        setError(null);
        setResultImage(null);

        try {
            let result: string | null = null;
            if (mode === 'fusion') {
                if (sourceImages.length === 0 || !promptText.trim()) {
                    setError("لطفا تصاویر را آپلود کرده و پرامپت را بنویسید.");
                    setIsLoading(false);
                    return;
                }
                result = await fuseFaces(sourceImages, promptText);
            } else { // mode === 'style'
                if (!contentImage || !styleImage) {
                    setError("لطفا هم تصویر محتوا و هم تصویر استایل را آپلود کنید.");
                    setIsLoading(false);
                    return;
                }
                const styleTransferPrompt = `Apply the artistic style, color palette, and texture of the second image (the style image) to the first image (the content image). ${promptText}`;
                result = await fuseFaces([contentImage, styleImage], styleTransferPrompt);
            }

            if (result) {
                setResultImage(result);
            } else {
                setError('عملیات با شکست مواجه شد. لطفا دوباره تلاش کنید.');
            }
        } catch (err) {
            setError('یک خطای غیرمنتظره رخ داد. لطفا کنسول را بررسی کنید.');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };
    
    const handleSaveAsNew = () => {
        if (!resultImage) return;
        const now = new Date().toISOString();
        const promptData = mode === 'fusion' ? {
            title: `ترکیب چهره: ${promptText.substring(0, 20)}...`,
            content: `Prompt: ${promptText}\n\nFused from ${sourceImages.length} source images.`,
            tags: ['face-fusion', 'ai-generated'],
        } : {
            title: `انتقال استایل: ${promptText.substring(0, 20) || 'بدون عنوان'}`,
            content: `Style Transfer. Additional instructions: ${promptText || 'None'}`,
            tags: ['style-transfer', 'ai-generated'],
        };
        
        const newPrompt: Prompt = {
            id: new Date().getTime().toString(),
            ...promptData,
            type: PromptType.Image,
            createdAt: now,
            updatedAt: now,
            rating: 0,
            imageUrl: resultImage,
        };

        onSave(newPrompt);
        alert('پرامپت جدید با موفقیت ذخیره شد!');
    };
    
    const isGenerateDisabled = mode === 'fusion'
        ? (isLoading || sourceImages.length === 0 || !promptText.trim())
        : (isLoading || !contentImage || !styleImage);

    return (
        <div className="p-6 h-full overflow-y-auto animate-fade-in" dir="rtl">
            <div className="flex items-center gap-3 mb-2">
                <Users className="w-8 h-8 text-dark-primary" />
                <h1 className="text-3xl font-bold text-gray-800 dark:text-dark-text">چهره‌ساز AI</h1>
            </div>
            <p className="text-gray-500 dark:text-dark-subtext mb-6">چهره‌ها را ترکیب کنید یا استایل‌های هنری را به تصاویر خود منتقل کنید.</p>
            
            <div className="mb-6 flex justify-center">
                <div className="bg-gray-200 dark:bg-dark-overlay p-1 rounded-full flex items-center gap-1">
                    <button onClick={() => handleModeChange('fusion')} className={`px-6 py-2 rounded-full text-sm font-semibold transition-colors ${mode === 'fusion' ? 'bg-white dark:bg-dark-surface text-dark-primary' : 'text-gray-500 dark:text-dark-subtext'}`}>ترکیب خلاق</button>
                    <button onClick={() => handleModeChange('style')} className={`px-6 py-2 rounded-full text-sm font-semibold transition-colors ${mode === 'style' ? 'bg-white dark:bg-dark-surface text-dark-primary' : 'text-gray-500 dark:text-dark-subtext'}`}>انتقال استایل</button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Input Column */}
                <div className="bg-white dark:bg-dark-surface p-6 rounded-2xl shadow-lg space-y-6">
                    {mode === 'fusion' ? (
                        <>
                            <div>
                                <h2 className="text-xl font-semibold mb-3">۱. آپلود تصاویر چهره (تا {MAX_FUSION_IMAGES} عدد)</h2>
                                <div className="grid grid-cols-3 gap-4">
                                    {sourceImages.map((src, index) => (
                                        <div key={index} className="relative group aspect-square">
                                            <img src={src} alt={`Source ${index + 1}`} className="w-full h-full object-cover rounded-lg" />
                                            <button onClick={() => handleRemoveFusionImage(index)} className="absolute top-1 right-1 bg-black/50 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <X className="w-4 h-4" />
                                            </button>
                                        </div>
                                    ))}
                                    {sourceImages.length < MAX_FUSION_IMAGES && (
                                        <label className="aspect-square border-2 border-dashed border-gray-300 dark:border-dark-overlay rounded-lg flex flex-col items-center justify-center cursor-pointer hover:bg-gray-50 dark:hover:bg-dark-overlay/20 transition-colors">
                                            <Upload className="w-8 h-8 text-gray-400 dark:text-dark-subtext" />
                                            <span className="mt-2 text-xs text-center text-gray-500 dark:text-dark-subtext">افزودن تصویر</span>
                                            <input type="file" multiple accept="image/png, image/jpeg, image/webp" className="hidden" onChange={handleFusionFileChange} />
                                        </label>
                                    )}
                                </div>
                            </div>
                            <div>
                                <h2 className="text-xl font-semibold mb-3">۲. پرامپت خود را بنویسید</h2>
                                <textarea
                                    value={promptText}
                                    onChange={(e) => setPromptText(e.target.value)}
                                    rows={5}
                                    placeholder="مثال: شخصیتی بساز که چشمان تصویر اول و لبخند تصویر دوم را داشته باشد، به سبک یک جنگجوی فانتزی."
                                    className="w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0 resize-none p-3"
                                />
                            </div>
                        </>
                    ) : (
                        <>
                            <div>
                                <h2 className="text-xl font-semibold mb-3">۱. آپلود تصویر محتوا</h2>
                                <p className="text-sm text-gray-500 dark:text-dark-subtext mb-3 -mt-2">چهره یا شیئی که می‌خواهید استایل را روی آن اعمال کنید.</p>
                                <ImageUploadBox image={contentImage} onImageSelect={(b64) => setContentImage(b64)} onImageRemove={() => setContentImage(null)} />
                            </div>
                             <div>
                                <h2 className="text-xl font-semibold mb-3">۲. آپلود تصویر استایل</h2>
                                <p className="text-sm text-gray-500 dark:text-dark-subtext mb-3 -mt-2">نقاشی، بافت یا تصویری که می‌خواهید استایل آن را منتقل کنید.</p>
                                <ImageUploadBox image={styleImage} onImageSelect={(b64) => setStyleImage(b64)} onImageRemove={() => setStyleImage(null)} />
                            </div>
                             <div>
                                <h2 className="text-xl font-semibold mb-3">۳. توضیحات بیشتر (اختیاری)</h2>
                                <textarea
                                    value={promptText}
                                    onChange={(e) => setPromptText(e.target.value)}
                                    rows={3}
                                    placeholder="مثال: با تاکید بر رنگ‌های آبی و چرخش‌های قلم‌مو."
                                    className="w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0 resize-none p-3"
                                />
                            </div>
                        </>
                    )}
                     <button
                        onClick={handleGenerate}
                        disabled={isGenerateDisabled}
                        className="w-full flex items-center justify-center gap-2 bg-dark-primary text-white font-bold px-4 py-3 rounded-full hover:bg-opacity-90 transition-all duration-200 shadow-lg shadow-dark-primary/30 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Sparkles className={`w-6 h-6 ${isLoading ? 'animate-spin' : ''}`} />
                        {isLoading ? 'در حال ساخت...' : (mode === 'fusion' ? 'ترکیب کن!' : 'انتقال استایل!')}
                    </button>
                </div>
                {/* Output Column */}
                 <div className="bg-white dark:bg-dark-surface p-6 rounded-2xl shadow-lg flex flex-col items-center justify-center">
                    <div className="w-full aspect-square bg-gray-100 dark:bg-dark-bg rounded-lg flex items-center justify-center mb-4">
                         {isLoading ? (
                            <div className="flex flex-col items-center text-dark-primary">
                                <Sparkles className="w-12 h-12 animate-spin" />
                                <p className="mt-4 font-semibold">در حال پردازش جادویی...</p>
                            </div>
                        ) : error ? (
                             <div className="text-center text-dark-danger p-4">
                                <p className="font-semibold">خطا!</p>
                                <p className="text-sm">{error}</p>
                            </div>
                        ) : resultImage ? (
                            <img src={resultImage} alt="Generated Result" className="rounded-lg object-contain h-full w-full"/>
                        ) : (
                            <div className="text-center text-gray-400 dark:text-dark-subtext">
                                <Users className="w-16 h-16 mx-auto" />
                                <p className="mt-2 font-semibold">نتیجه اینجا نمایش داده می‌شود</p>
                            </div>
                        )}
                    </div>
                     {resultImage && !isLoading && (
                        <div className="w-full grid grid-cols-2 gap-4 animate-fade-in">
                            <a href={resultImage} download={`ai-generated-${Date.now()}.png`} className="w-full flex items-center justify-center gap-2 bg-dark-secondary/10 text-dark-secondary font-semibold px-4 py-2 rounded-lg hover:bg-opacity-90 transition-all duration-200">
                                <Download className="w-5 h-5"/>
                                دانلود
                            </a>
                            <button onClick={handleSaveAsNew} className="w-full flex items-center justify-center gap-2 bg-dark-accent/10 text-dark-accent font-semibold px-4 py-2 rounded-lg hover:bg-opacity-90 transition-all duration-200">
                                <Plus className="w-5 h-5" />
                                ذخیره به عنوان پرامپت
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

// Helper component for single image upload box in Style Transfer mode
const ImageUploadBox: React.FC<{
    image: string | null;
    onImageSelect: (base64: string) => void;
    onImageRemove: () => void;
}> = ({ image, onImageSelect, onImageRemove }) => {
    
    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files[0]) {
            const file = event.target.files[0];
            if (file.size > MAX_FILE_SIZE) {
                alert(`حجم فایل ${file.name} باید کمتر از 4MB باشد.`);
                return;
            }
            try {
                const base64 = await blobToBase64(file);
                onImageSelect(base64);
            } catch (err) {
                 console.error("Error converting file to base64:", err);
            }
        }
    };

    if (image) {
        return (
            <div className="relative group aspect-video">
                <img src={image} alt="Uploaded" className="w-full h-full object-contain rounded-lg bg-gray-100 dark:bg-dark-bg" />
                <button onClick={onImageRemove} className="absolute top-2 right-2 bg-black/50 text-white rounded-full p-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                    <X className="w-5 h-5" />
                </button>
            </div>
        );
    }

    return (
        <label className="aspect-video border-2 border-dashed border-gray-300 dark:border-dark-overlay rounded-lg flex flex-col items-center justify-center cursor-pointer hover:bg-gray-50 dark:hover:bg-dark-overlay/20 transition-colors">
            <ImageIcon className="w-10 h-10 text-gray-400 dark:text-dark-subtext" />
            <span className="mt-2 text-sm text-center text-gray-500 dark:text-dark-subtext">برای آپلود کلیک کنید</span>
            <input type="file" accept="image/png, image/jpeg, image/webp" className="hidden" onChange={handleFileChange} />
        </label>
    );
};

export default FaceFusion;
