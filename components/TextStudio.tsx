import React, { useState, useRef, useEffect } from 'react';
import * as pdfjsLib from 'pdfjs-dist';
import mammoth from 'mammoth';
import { Prompt, PromptType } from '../types';
import {
  generateCreativeText,
  summarizeText,
  rephraseText,
  translateText,
} from '../services/geminiService';
import {
  FileText,
  Sparkles,
  Copy,
  Plus,
  Wand2,
  BookOpen,
  Globe,
  Repeat,
  Upload,
  X,
} from './icons';

interface TextStudioProps {
  onSave: (prompt: Prompt) => void;
}

type Tool = 'writer' | 'summarizer' | 'rephraser' | 'translator';

const TONES = ['رسمی', 'دوستانه', 'متقاعد کننده', 'ساده', 'خلاقانه'];
const LANGUAGES = ['English', 'Spanish', 'French', 'German', 'Persian', 'Japanese'];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB for PDF/DOCX, 1MB for text

const toolConfig: Record<Tool, {
    label: string;
    icon: React.FC<React.SVGProps<SVGSVGElement>>;
    placeholder: string;
    buttonText: string;
}> = {
    writer: {
        label: 'نویسنده خلاق',
        icon: Wand2,
        placeholder: 'یک پرامپت برای نوشتن وارد کنید. مثلا: داستانی کوتاه درباره یک ساعت‌ساز که می‌تواند زمان را کنترل کند بنویس...',
        buttonText: 'بنویس'
    },
    summarizer: {
        label: 'خلاصه‌ساز',
        icon: BookOpen,
        placeholder: 'متن طولانی خود را برای خلاصه شدن اینجا وارد کنید یا یک فایل متنی آپلود کنید...',
        buttonText: 'خلاصه کن'
    },
    rephraser: {
        label: 'بازنویس',
        icon: Repeat,
        placeholder: 'متنی که می‌خواهید بازنویسی شود را اینجا وارد کنید یا یک فایل متنی آپلود کنید...',
        buttonText: 'بازنویسی کن'
    },
    translator: {
        label: 'مترجم',
        icon: Globe,
        placeholder: 'متن خود را برای ترجمه اینجا وارد کنید یا یک فایل متنی آپلود کنید...',
        buttonText: 'ترجمه کن'
    }
};

const TextStudio: React.FC<TextStudioProps> = ({ onSave }) => {
  const [activeTool, setActiveTool] = useState<Tool>('writer');
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isParsing, setIsParsing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Set worker source for pdf.js
    pdfjsLib.GlobalWorkerOptions.workerSrc = `https://aistudiocdn.com/pdfjs-dist@^4.6.439/build/pdf.worker.mjs`;
  }, []);

  // Tool-specific options
  const [rephraseTone, setRephraseTone] = useState(TONES[0]);
  const [translateLang, setTranslateLang] = useState(LANGUAGES[0]);
  
  const handleGenerate = async () => {
    if (!inputText.trim()) return;
    setIsLoading(true);
    setError(null);
    setOutputText('');

    try {
      let result = '';
      switch (activeTool) {
        case 'writer':
          result = await generateCreativeText(inputText);
          break;
        case 'summarizer':
          result = await summarizeText(inputText);
          break;
        case 'rephraser':
          result = await rephraseText(inputText, rephraseTone);
          break;
        case 'translator':
          result = await translateText(inputText, translateLang);
          break;
      }
      setOutputText(result);
    } catch (err: any) {
        setError(err.message || 'یک خطای غیرمنتظره رخ داد.');
    } finally {
        setIsLoading(false);
    }
  };
  
  const handleSaveAsPrompt = () => {
    if (!outputText.trim()) return;
    const now = new Date().toISOString();
    const newPrompt: Prompt = {
        id: new Date().getTime().toString(),
        title: `متن تولید شده: ${inputText.substring(0, 30)}...`,
        content: outputText,
        type: PromptType.Text,
        tags: ['text-studio', activeTool],
        createdAt: now,
        updatedAt: now,
        rating: 0,
        summary: outputText.substring(0, 120) + (outputText.length > 120 ? '...' : '')
    };
    onSave(newPrompt);
    alert('متن با موفقیت به عنوان پرامپت جدید ذخیره شد!');
  };

  const handleCopy = () => {
    if (!outputText) return;
    navigator.clipboard.writeText(outputText);
    alert('متن کپی شد!');
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const extension = file.name.split('.').pop()?.toLowerCase();
    const isTextFile = ['txt', 'md'].includes(extension || '');
    if (file.size > (isTextFile ? 1 * 1024 * 1024 : MAX_FILE_SIZE)) {
        alert(`حجم فایل بیش از حد مجاز است.`);
        return;
    }

    setIsParsing(true);
    setError(null);
    setInputText('');
    setFileName(file.name);

    try {
        let content = '';
        const arrayBuffer = await file.arrayBuffer();

        switch (extension) {
            case 'pdf':
                const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
                const textPromises = [];
                for (let i = 1; i <= pdf.numPages; i++) {
                    const page = await pdf.getPage(i);
                    textPromises.push(page.getTextContent());
                }
                const textContents = await Promise.all(textPromises);
                content = textContents.map(tc => tc.items.map(item => ('str' in item ? item.str : '')).join(' ')).join('\n');
                break;
            case 'docx':
            case 'doc':
                const result = await mammoth.extractRawText({ arrayBuffer });
                content = result.value;
                break;
            case 'txt':
            case 'md':
                const reader = new FileReader();
                content = await new Promise((resolve, reject) => {
                    reader.onload = (e) => resolve(e.target?.result as string);
                    reader.onerror = reject;
                    reader.readAsText(file);
                });
                break;
            default:
                throw new Error('فرمت فایل پشتیبانی نمی‌شود.');
        }
        setInputText(content);
    } catch (err: any) {
        setError(err.message || 'خطا در پردازش فایل.');
        setFileName(null);
    } finally {
        setIsParsing(false);
    }

    if (event.target) event.target.value = '';
  };

  const handleUploadClick = () => fileInputRef.current?.click();

  const handleClearInput = () => {
      setInputText('');
      setFileName(null);
      setOutputText('');
      setError(null);
      if(fileInputRef.current) fileInputRef.current.value = '';
  };

  const currentTool = toolConfig[activeTool];
  const showUploadButton = ['summarizer', 'rephraser', 'translator'].includes(activeTool);

  return (
    <div className="p-6 h-full overflow-y-auto animate-fade-in" dir="rtl">
      <div className="flex items-center gap-3 mb-2">
        <FileText className="w-8 h-8 text-dark-primary" />
        <h1 className="text-3xl font-bold text-gray-800 dark:text-dark-text">استودیوی متن AI</h1>
      </div>
      <p className="text-gray-500 dark:text-dark-subtext mb-6">محتوای متنی خود را با ابزارهای هوشمند بنویسید، ویرایش و بهینه کنید.</p>
      
      <div className="mb-6 border-b border-gray-200 dark:border-dark-overlay">
        <nav className="-mb-px flex gap-8" aria-label="Tabs">
          {Object.keys(toolConfig).map((toolKey) => {
              const tool = toolKey as Tool;
              return (
                 <button 
                    key={tool} 
                    onClick={() => setActiveTool(tool)} 
                    className={`whitespace-nowrap flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                        activeTool === tool
                        ? 'border-dark-primary text-dark-primary'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-dark-subtext dark:hover:text-dark-text dark:hover:border-dark-overlay'
                    }`}
                 >
                    <toolConfig[tool].icon className="w-5 h-5"/>
                    {toolConfig[tool].label}
                 </button>
              )
          })}
        </nav>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Panel */}
        <div className="bg-white dark:bg-dark-surface p-6 rounded-2xl shadow-lg flex flex-col">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-dark-text">ورودی</h2>
                {showUploadButton && (
                    <>
                        <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept=".txt,.md,.pdf,.doc,.docx" />
                        <button onClick={handleUploadClick} className="flex items-center gap-2 text-sm font-semibold text-dark-primary hover:text-opacity-80 transition">
                            <Upload className="w-4 h-4" />
                            <span>آپلود فایل</span>
                        </button>
                    </>
                )}
            </div>
            <div className="relative w-full flex-grow">
                <textarea
                    value={inputText}
                    onChange={(e) => {
                        setInputText(e.target.value);
                        if(fileName) handleClearInput();
                    }}
                    placeholder={currentTool.placeholder}
                    className="w-full h-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0 resize-none p-3 text-sm"
                    disabled={isParsing}
                />
                {(fileName || isParsing) && (
                    <div className="absolute inset-0 bg-dark-surface/80 rounded-lg flex items-center justify-center">
                         <div className="text-center text-white">
                            {isParsing ? <Sparkles className="w-8 h-8 animate-spin mx-auto" /> : <FileText className="w-8 h-8 mx-auto" />}
                            <p className="mt-2 text-sm">{isParsing ? 'در حال پردازش فایل...' : fileName}</p>
                            {!isParsing && 
                                <button onClick={handleClearInput} className="mt-2 text-xs bg-dark-danger/50 px-2 py-1 rounded-full hover:bg-dark-danger/80">
                                    پاک کردن
                                </button>
                            }
                         </div>
                    </div>
                )}
            </div>
            {activeTool === 'rephraser' && (
                <div className="mt-4">
                    <label className="text-sm font-medium text-gray-700 dark:text-dark-subtext">انتخاب لحن:</label>
                    <select value={rephraseTone} onChange={(e) => setRephraseTone(e.target.value)} className="mt-1 w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0">
                        {TONES.map(tone => <option key={tone} value={tone}>{tone}</option>)}
                    </select>
                </div>
            )}
            {activeTool === 'translator' && (
                 <div className="mt-4">
                    <label className="text-sm font-medium text-gray-700 dark:text-dark-subtext">ترجمه به:</label>
                    <select value={translateLang} onChange={(e) => setTranslateLang(e.target.value)} className="mt-1 w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0">
                        {LANGUAGES.map(lang => <option key={lang} value={lang}>{lang}</option>)}
                    </select>
                </div>
            )}
             <button
                onClick={handleGenerate}
                disabled={isLoading || isParsing || !inputText.trim()}
                className="mt-4 w-full flex items-center justify-center gap-2 bg-dark-primary text-white font-bold px-4 py-3 rounded-full hover:bg-opacity-90 transition-all duration-200 shadow-lg shadow-dark-primary/30 disabled:opacity-50 disabled:cursor-not-allowed"
            >
                <Sparkles className={`w-6 h-6 ${isLoading ? 'animate-spin' : ''}`} />
                {isLoading ? 'در حال پردازش...' : currentTool.buttonText}
            </button>
        </div>

        {/* Output Panel */}
        <div className="bg-white dark:bg-dark-surface p-6 rounded-2xl shadow-lg flex flex-col">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-dark-text">خروجی</h2>
                {outputText && !isLoading && (
                    <div className="flex gap-2">
                        <button onClick={handleCopy} title="کپی کردن" className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-overlay transition-colors">
                            <Copy className="w-5 h-5 text-gray-500 dark:text-dark-subtext" />
                        </button>
                        <button onClick={handleSaveAsPrompt} title="ذخیره به عنوان پرامپت" className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-overlay transition-colors">
                            <Plus className="w-5 h-5 text-dark-accent" />
                        </button>
                    </div>
                )}
            </div>
            <div className="w-full flex-grow bg-gray-100 dark:bg-dark-bg rounded-lg p-3 text-sm whitespace-pre-wrap overflow-y-auto">
                {isLoading ? (
                     <div className="flex items-center justify-center h-full text-dark-primary">
                         <Sparkles className="w-8 h-8 animate-spin" />
                    </div>
                ) : error ? (
                    <div className="text-center text-dark-danger p-4">
                        <p className="font-semibold">خطا!</p>
                        <p className="text-sm">{error}</p>
                    </div>
                ) : outputText ? (
                    outputText
                ) : (
                    <div className="flex items-center justify-center h-full text-gray-400 dark:text-dark-subtext">
                        <p>نتیجه اینجا نمایش داده می‌شود.</p>
                    </div>
                )}
            </div>
        </div>
      </div>
    </div>
  );
};

export default TextStudio;