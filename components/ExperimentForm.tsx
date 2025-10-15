import React, { useState } from 'react';
import { PromptExperiment, PromptType } from '../types';
import { X, Plus, Beaker } from './icons';

interface ExperimentFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (experiment: Omit<PromptExperiment, 'id' | 'createdAt'>) => void;
}

const ExperimentForm: React.FC<ExperimentFormProps> = ({ isOpen, onClose, onSave }) => {
  const [title, setTitle] = useState('');
  const [goal, setGoal] = useState('');
  const [variations, setVariations] = useState(['', '']);

  if (!isOpen) return null;

  const handleVariationChange = (index: number, value: string) => {
    const newVariations = [...variations];
    newVariations[index] = value;
    setVariations(newVariations);
  };

  const addVariation = () => {
    setVariations([...variations, '']);
  };

  const removeVariation = (index: number) => {
    if (variations.length > 2) {
      setVariations(variations.filter((_, i) => i !== index));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim() && variations.every(v => v.trim())) {
      onSave({
        title,
        goal,
        promptType: PromptType.Image,
        status: 'running',
        variations: variations.map(content => ({
          id: new Date().getTime().toString() + Math.random(),
          content,
          isWinner: false,
        })),
      });
      // Reset form
      setTitle('');
      setGoal('');
      setVariations(['', '']);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-lg flex items-center justify-center p-4 z-40" onClick={onClose} dir="rtl">
      <div className="animate-fade-in bg-white dark:bg-dark-surface rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="flex justify-between items-center p-5 border-b border-gray-200 dark:border-dark-overlay">
           <div className="flex items-center gap-3">
              <Beaker className="w-7 h-7 text-dark-secondary" />
              <h2 className="text-2xl font-bold text-gray-800 dark:text-dark-text">ایجاد آزمایش جدید</h2>
           </div>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-overlay">
            <X className="w-6 h-6 text-gray-500 dark:text-dark-subtext" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="flex-grow overflow-y-auto p-6 space-y-6">
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-dark-subtext mb-1">عنوان آزمایش</label>
            <input type="text" name="title" id="title" value={title} onChange={(e) => setTitle(e.target.value)} required placeholder="مثلا: بهترین سبک هنری برای گربه فضانورد" className="w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0" />
          </div>
          <div>
            <label htmlFor="goal" className="block text-sm font-medium text-gray-700 dark:text-dark-subtext mb-1">هدف (اختیاری)</label>
            <input type="text" name="goal" id="goal" value={goal} onChange={(e) => setGoal(e.target.value)} placeholder="مثلا: پیدا کردن واقعی‌گرایانه‌ترین تصویر" className="w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0" />
          </div>
          <div>
            <h3 className="block text-sm font-medium text-gray-700 dark:text-dark-subtext mb-2">نسخه‌های پرامپت (حداقل ۲)</h3>
            <div className="space-y-4">
              {variations.map((content, index) => (
                <div key={index} className="flex items-center gap-3">
                  <textarea
                    value={content}
                    onChange={(e) => handleVariationChange(index, e.target.value)}
                    required
                    rows={3}
                    placeholder={`نسخه #${index + 1}`}
                    className="flex-grow bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0 resize-none"
                  />
                  <button type="button" onClick={() => removeVariation(index)} disabled={variations.length <= 2} className="p-2 rounded-full hover:bg-dark-danger/10 disabled:opacity-50 disabled:cursor-not-allowed">
                    <X className="w-5 h-5 text-dark-danger" />
                  </button>
                </div>
              ))}
            </div>
            <button type="button" onClick={addVariation} className="mt-4 flex items-center gap-2 text-sm font-semibold text-dark-primary hover:text-opacity-80 transition">
              <Plus className="w-4 h-4" />
              افزودن نسخه دیگر
            </button>
          </div>
           <p className="text-xs text-center text-gray-400 dark:text-dark-subtext/70">
              توجه: این قابلیت در حال حاضر فقط برای پرامپت‌های تصویر در دسترس است.
           </p>
        </form>
        <div className="p-5 border-t border-gray-200 dark:border-dark-overlay bg-gray-50 dark:bg-dark-surface/50 flex justify-end gap-3">
          <button type="button" onClick={onClose} className="px-6 py-2 rounded-full text-gray-700 dark:text-dark-subtext bg-gray-200 dark:bg-dark-overlay hover:opacity-90 transition">لغو</button>
          <button type="submit" onClick={handleSubmit} className="px-6 py-2 rounded-full text-white bg-dark-primary hover:opacity-90 font-semibold transition shadow-lg shadow-dark-primary/30">شروع آزمایش</button>
        </div>
      </div>
    </div>
  );
};

export default ExperimentForm;
