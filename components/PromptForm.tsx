
import React, { useState, useEffect, useRef } from 'react';
import { Prompt, PromptType } from '../types';
import { PROMPT_TYPE_CONFIG } from '../constants';
import { X, Wand2, Sparkles, Image as ImageIcon, Upload } from './icons';
import { getPromptEnhancements, generateImage } from '../services/geminiService';

interface PromptFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (prompt: Prompt) => void;
  editingPrompt: Prompt | null;
  initialType?: PromptType;
}

const PromptForm: React.FC<PromptFormProps> = ({ isOpen, onClose, onSave, editingPrompt, initialType }) => {
  const [prompt, setPrompt] = useState<Partial<Prompt>>({});
  const [currentTag, setCurrentTag] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isGeneratingImage, setIsGeneratingImage] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editingPrompt) {
      setPrompt(editingPrompt);
    } else {
      setPrompt({
        id: new Date().getTime().toString(),
        title: '',
        content: '',
        type: initialType || PromptType.Text,
        tags: [],
        rating: 0,
        createdAt: new Date().toISOString(),
      });
    }
  }, [editingPrompt, isOpen, initialType]);

  if (!isOpen) return null;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setPrompt(prev => ({ ...prev, [name]: value }));
  };

  const handleRatingChange = (newRating: number) => {
    setPrompt(prev => ({ ...prev, rating: newRating }));
  };

  const handleAddTag = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && currentTag.trim()) {
      e.preventDefault();
      if (!prompt.tags?.includes(currentTag.trim())) {
        setPrompt(prev => ({ ...prev, tags: [...(prev.tags || []), currentTag.trim()] }));
      }
      setCurrentTag('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setPrompt(prev => ({ ...prev, tags: (prev.tags || []).filter(tag => tag !== tagToRemove) }));
  };

  const handleEnhance = async () => {
    if (!prompt.content || !prompt.type) return;
    setIsLoading(true);
    try {
      const result = await getPromptEnhancements(prompt.content, prompt.type);
      if (result && result.improvements !== "AI analysis failed.") {
        setPrompt(prev => ({
          ...prev,
          content: result.improvements,
          tags: [...new Set([...(prev.tags || []), ...result.tags])]
        }));
      }
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleGenerateImage = async () => {
    if (!prompt.content) return;
    setIsGeneratingImage(true);
    try {
      const imageUrl = await generateImage(prompt.content);
      if (imageUrl) {
        setPrompt(prev => ({ ...prev, imageUrl }));
      }
    } finally {
      setIsGeneratingImage(false);
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
        const file = e.target.files[0];
        if (file.size > 4 * 1024 * 1024) { // 4MB limit for Gemini
            alert("حجم فایل باید کمتر از 4MB باشد.");
            return;
        }
        const reader = new FileReader();
        reader.onloadend = () => {
            setPrompt(prev => ({ ...prev, imageUrl: reader.result as string }));
        };
        reader.readAsDataURL(file);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({
      ...prompt,
      updatedAt: new Date().toISOString(),
    } as Prompt);
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-lg flex items-center justify-center p-4 z-40" onClick={onClose} dir="rtl">
      <div className="animate-fade-in bg-white dark:bg-dark-surface rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="flex justify-between items-center p-5 border-b border-gray-200 dark:border-dark-overlay">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-dark-text">
            {editingPrompt ? 'ویرایش پرامپت' : 'افزودن پرامپت جدید'}
          </h2>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-overlay">
            <X className="w-6 h-6 text-gray-500 dark:text-dark-subtext" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="flex-grow overflow-y-auto p-6 space-y-6">
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-dark-subtext mb-1">عنوان</label>
            <input type="text" name="title" id="title" value={prompt.title || ''} onChange={handleChange} required className="w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0" />
          </div>

          <div>
            <label htmlFor="content" className="block text-sm font-medium text-gray-700 dark:text-dark-subtext mb-1">محتوای پرامپت</label>
            <div className="relative">
              <textarea name="content" id="content" value={prompt.content || ''} onChange={handleChange} required rows={6} className="w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0 resize-none" />
              <button type="button" onClick={handleEnhance} disabled={isLoading} className="absolute bottom-3 left-3 flex items-center gap-2 text-xs bg-dark-secondary text-white font-semibold px-3 py-1.5 rounded-full hover:bg-opacity-90 transition-all duration-200 disabled:opacity-50">
                {isLoading ? <Sparkles className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
                بهبود با AI
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="type" className="block text-sm font-medium text-gray-700 dark:text-dark-subtext mb-1">نوع پرامپت</label>
              <select name="type" id="type" value={prompt.type} onChange={handleChange} className="w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0">
                {Object.values(PromptType).map(type => (
                  // FIX: Cast type to PromptType for correct indexing.
                  <option key={type} value={type}>{PROMPT_TYPE_CONFIG[type as PromptType].label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-dark-subtext mb-1">امتیاز</label>
              <div className="flex items-center gap-1">
                {[1, 2, 3, 4, 5].map(star => (
                  <button type="button" key={star} onClick={() => handleRatingChange(star)}>
                    <span className={`text-2xl ${prompt.rating && prompt.rating >= star ? 'text-dark-warn' : 'text-gray-300 dark:text-dark-overlay'}`}>★</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
          
          {prompt.type === 'image' && (
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-dark-subtext mb-2">پیش‌نمایش تصویر</h3>
              <div className="w-full aspect-square bg-gray-100 dark:bg-dark-bg rounded-lg flex items-center justify-center">
                {isGeneratingImage ? (
                   <div className="flex flex-col items-center text-dark-primary"><Sparkles className="w-10 h-10 animate-spin" /><p className="mt-2 text-sm">در حال ساخت تصویر...</p></div>
                ) : prompt.imageUrl ? (
                  <img src={prompt.imageUrl} alt="Generated preview" className="rounded-lg object-contain h-full w-full"/>
                ) : (
                  <div className="text-center text-gray-400 dark:text-dark-subtext">
                    <ImageIcon className="w-12 h-12 mx-auto" />
                    <p className="mt-2 text-sm">برای ساخت پیش‌نمایش، دکمه را بزنید</p>
                  </div>
                )}
              </div>
              <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <button type="button" onClick={() => fileInputRef.current?.click()} className="flex items-center justify-center gap-2 bg-dark-secondary/10 text-dark-secondary font-semibold px-4 py-2 rounded-lg hover:bg-opacity-90 transition-all duration-200">
                      <Upload className="w-5 h-5" />
                      {prompt.imageUrl ? 'جایگزینی تصویر' : 'آپلود تصویر'}
                  </button>
                  <input type="file" ref={fileInputRef} onChange={handleImageUpload} className="hidden" accept="image/png, image/jpeg, image/webp, image/heic, image/heif" />

                  <button type="button" onClick={handleGenerateImage} disabled={isGeneratingImage || !prompt.content} className="flex items-center justify-center gap-2 bg-dark-accent/10 text-dark-accent font-semibold px-4 py-2 rounded-lg hover:bg-opacity-90 transition-all duration-200 disabled:opacity-50">
                    <ImageIcon className="w-5 h-5"/>
                    ساخت تصویر از پرامپت
                  </button>
              </div>
            </div>
          )}

          <div>
            <label htmlFor="tags" className="block text-sm font-medium text-gray-700 dark:text-dark-subtext mb-1">تگ‌ها (با Enter جدا کنید)</label>
            <div className="flex flex-wrap gap-2 items-center p-2 bg-gray-100 dark:bg-dark-bg rounded-lg">
              {(prompt.tags || []).map(tag => (
                <div key={tag} className="flex items-center gap-1 bg-dark-primary/20 text-dark-primary text-sm font-semibold px-2 py-1 rounded-full">
                  <span>{tag}</span>
                  <button type="button" onClick={() => handleRemoveTag(tag)}><X className="w-4 h-4" /></button>
                </div>
              ))}
              <input
                type="text"
                id="tags"
                value={currentTag}
                onChange={(e) => setCurrentTag(e.target.value)}
                onKeyDown={handleAddTag}
                className="flex-grow bg-transparent focus:ring-0 border-none p-1"
                placeholder="تگ جدید..."
              />
            </div>
          </div>
        </form>
        <div className="p-5 border-t border-gray-200 dark:border-dark-overlay bg-gray-50 dark:bg-dark-surface/50 flex justify-end gap-3">
          <button type="button" onClick={onClose} className="px-6 py-2 rounded-full text-gray-700 dark:text-dark-subtext bg-gray-200 dark:bg-dark-overlay hover:opacity-90 transition">لغو</button>
          <button type="submit" onClick={handleSubmit} className="px-6 py-2 rounded-full text-white bg-dark-primary hover:opacity-90 font-semibold transition shadow-lg shadow-dark-primary/30">ذخیره</button>
        </div>
      </div>
    </div>
  );
};

export default PromptForm;
