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
  WandSparkles,
  BookOpen,
  Globe,
  Repeat,
  Upload,
  X,
} from './icons';
import { useTranslation } from '../contexts/LanguageContext';

interface TextStudioProps {
  onSave: (prompt: Prompt) => void;
}

type Tool = 'writer' | 'summarizer' | 'rephraser' | 'translator';

const TONES = ['Formal', 'Friendly', 'Persuasive', 'Simple', 'Creative'];
const LANGUAGES = ['English', 'Spanish', 'French', 'German', 'Persian', 'Japanese'];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB for PDF/DOCX, 1MB for text

const TextStudio: React.FC<TextStudioProps> = ({ onSave }) => {
  const { t } = useTranslation();
  
  const toolConfig: Record<Tool, {
    label: string;
    icon: React.FC<React.SVGProps<SVGSVGElement>>;
    placeholder: string;
    buttonText: string;
  }> = {
    writer: { label: t('textStudio.tools.writer.label'), icon: WandSparkles, placeholder: t('textStudio.tools.writer.placeholder'), buttonText: t('textStudio.tools.writer.button') },
    summarizer: { label: t('textStudio.tools.summarizer.label'), icon: BookOpen, placeholder: t('textStudio.tools.summarizer.placeholder'), buttonText: t('textStudio.tools.summarizer.button') },
    rephraser: { label: t('textStudio.tools.rephraser.label'), icon: Repeat, placeholder: t('textStudio.tools.rephraser.placeholder'), buttonText: t('textStudio.tools.rephraser.button') },
    translator: { label: t('textStudio.tools.translator.label'), icon: Globe, placeholder: t('textStudio.tools.translator.placeholder'), buttonText: t('textStudio.tools.translator.button') }
  };

  const [activeTool, setActiveTool] = useState<Tool>('writer');
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isParsing, setIsParsing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    pdfjsLib.GlobalWorkerOptions.workerSrc = `https://aistudiocdn.com/pdfjs-dist@^4.6.439/build/pdf.worker.mjs`;
  }, []);

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
        case 'writer': result = await generateCreativeText(inputText); break;
        case 'summarizer': result = await summarizeText(inputText); break;
        case 'rephraser': result = await rephraseText(inputText, rephraseTone); break;
        case 'translator': result = await translateText(inputText, translateLang); break;
      }
      setOutputText(result);
    } catch (err: any) {
        setError(err.message || t('textStudio.unexpectedError'));
    } finally {
        setIsLoading(false);
    }
  };
  
  const handleSaveAsPrompt = () => {
    if (!outputText.trim()) return;
    const now = new Date().toISOString();
    const newPrompt: Prompt = {
        id: new Date().getTime().toString(),
        title: t('textStudio.saveTitle', { prompt: inputText.substring(0, 30) }),
        content: outputText,
        type: PromptType.Text,
        tags: ['text-studio', activeTool],
        createdAt: now,
        updatedAt: now,
        rating: 0,
        summary: outputText.substring(0, 120) + (outputText.length > 120 ? '...' : '')
    };
    onSave(newPrompt);
    alert(t('textStudio.saveSuccess'));
  };

  const handleCopy = () => {
    if (!outputText) return;
    navigator.clipboard.writeText(outputText);
    alert(t('textStudio.copySuccess'));
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const extension = file.name.split('.').pop()?.toLowerCase();
    const isTextFile = ['txt', 'md'].includes(extension || '');
    if (file.size > (isTextFile ? 1 * 1024 * 1024 : MAX_FILE_SIZE)) {
        alert(t('textStudio.fileSizeError'));
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
                    textPromises.push(pdf.getPage(i).then(page => page.getTextContent()));
                }
                const textContents = await Promise.all(textPromises);
                content = textContents.map(tc => tc.items.map(item => ('str' in item ? item.str : '')).join(' ')).join('\n');
                break;
            case 'docx':
            case 'doc':
                content = (await mammoth.extractRawText({ arrayBuffer })).value;
                break;
            case 'txt':
            case 'md':
                content = await new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = (e) => resolve(e.target?.result as string);
                    reader.onerror = reject;
                    reader.readAsText(file);
                });
                break;
            default:
                throw new Error(t('textStudio.unsupportedFormatError'));
        }
        setInputText(content);
    } catch (err: any) {
        setError(err.message || t('textStudio.fileParseError'));
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
    <div className="p-6 h-full overflow-y-auto animate-fade-in">
      <div className="flex items-center gap-3 mb-2">
        <FileText className="w-8 h-8 text-dark-primary" />
        <h1 className="text-3xl font-bold text-gray-800 dark:text-dark-text">{t('textStudio.title')}</h1>
      </div>
      <p className="text-gray-500 dark:text-dark-subtext mb-6">{t('textStudio.description')}</p>
      
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
        <div className="bg-white dark:bg-dark-surface p-6 rounded-2xl shadow-lg flex flex-col">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-dark-text">{t('textStudio.input')}</h2>
                {showUploadButton && (
                    <>
                        <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept=".txt,.md,.pdf,.doc,.docx" />
                        <button onClick={handleUploadClick} className="flex items-center gap-2 text-sm font-semibold text-dark-primary hover:text-opacity-80 transition">
                            <Upload className="w-4 h-4" />
                            <span>{t('buttons.uploadFile')}</span>
                        </button>
                    </>
                )}
            </div>
            <div className="relative w-full flex-grow">
                <textarea
                    value={inputText}
                    onChange={(e) => { setInputText(e.target.value); if(fileName) handleClearInput(); }}
                    placeholder={currentTool.placeholder}
                    className="w-full h-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0 resize-none p-3 text-sm"
                    disabled={isParsing}
                />
                {(fileName || isParsing) && (
                    <div className="absolute inset-0 bg-dark-surface/80 rounded-lg flex items-center justify-center">
                         <div className="text-center text-white">
                            {isParsing ? <Sparkles className="w-8 h-8 animate-spin mx-auto" /> : <FileText className="w-8 h-8 mx-auto" />}
                            <p className="mt-2 text-sm">{isParsing ? t('textStudio.parsingFile') : fileName}</p>
                            {!isParsing && 
                                <button onClick={handleClearInput} className="mt-2 text-xs bg-dark-danger/50 px-2 py-1 rounded-full hover:bg-dark-danger/80">
                                    {t('buttons.clear')}
                                </button>
                            }
                         </div>
                    </div>
                )}
            </div>
            {activeTool === 'rephraser' && (
                <div className="mt-4">
                    <label className="text-sm font-medium text-gray-700 dark:text-dark-subtext">{t('textStudio.toneLabel')}:</label>
                    <select value={rephraseTone} onChange={(e) => setRephraseTone(e.target.value)} className="mt-1 w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0">
                        {TONES.map(tone => <option key={tone} value={tone}>{t(`textStudio.tones.${tone.toLowerCase()}`)}</option>)}
                    </select>
                </div>
            )}
            {activeTool === 'translator' && (
                 <div className="mt-4">
                    <label className="text-sm font-medium text-gray-700 dark:text-dark-subtext">{t('textStudio.translateToLabel')}:</label>
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
                {isLoading ? t('textStudio.processing') : currentTool.buttonText}
            </button>
        </div>

        <div className="bg-white dark:bg-dark-surface p-6 rounded-2xl shadow-lg flex flex-col">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-dark-text">{t('textStudio.output')}</h2>
                {outputText && !isLoading && (
                    <div className="flex gap-2">
                        <button onClick={handleCopy} title={t('buttons.copy')} className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-overlay transition-colors">
                            <Copy className="w-5 h-5 text-gray-500 dark:text-dark-subtext" />
                        </button>
                        <button onClick={handleSaveAsPrompt} title={t('buttons.saveAsPrompt')} className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-overlay transition-colors">
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
                        <p className="font-semibold">{t('textStudio.errorTitle')}</p>
                        <p className="text-sm">{error}</p>
                    </div>
                ) : outputText ? (
                    outputText
                ) : (
                    <div className="flex items-center justify-center h-full text-gray-400 dark:text-dark-subtext">
                        <p>{t('textStudio.resultPlaceholder')}</p>
                    </div>
                )}
            </div>
        </div>
      </div>
    </div>
  );
};

export default TextStudio;