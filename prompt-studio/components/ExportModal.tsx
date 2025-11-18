import React, { useState, useMemo } from 'react';
import { Prompt, PromptType } from '../types';
import { X, FileDown } from './icons';
import { useTranslation } from '../contexts/LanguageContext';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  prompts: Prompt[];
  onExport: (promptsToExport: Prompt[]) => void;
}

const ExportModal: React.FC<ExportModalProps> = ({ isOpen, onClose, prompts, onExport }) => {
    const { t } = useTranslation();
    const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
    const [selectedTags, setSelectedTags] = useState<string[]>([]);
    const [selectedRating, setSelectedRating] = useState(0);

    const allTags = useMemo(() => [...new Set(prompts.flatMap(p => p.tags || []))], [prompts]);

    const filteredPrompts = useMemo(() => {
        return prompts.filter(p => {
            const typeMatch = selectedTypes.length === 0 || selectedTypes.includes(p.type);
            const tagMatch = selectedTags.length === 0 || selectedTags.some(tag => (p.tags || []).includes(tag));
            const ratingMatch = selectedRating === 0 || (p.rating && p.rating >= selectedRating);
            return typeMatch && tagMatch && ratingMatch;
        });
    }, [prompts, selectedTypes, selectedTags, selectedRating]);

    const handleTypeChange = (type: string) => {
        setSelectedTypes(prev => prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]);
    };
    
    const handleTagChange = (tag: string) => {
        setSelectedTags(prev => prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]);
    };
    
    if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-lg flex items-center justify-center p-4 z-50" onClick={onClose}>
      <div className="animate-fade-in bg-white dark:bg-dark-surface rounded-2xl shadow-2xl w-full max-w-lg flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="flex justify-between items-center p-5 border-b border-gray-200 dark:border-dark-overlay">
          <div className="flex items-center gap-3">
            <FileDown className="w-7 h-7 text-dark-primary" />
            <h2 className="text-2xl font-bold text-gray-800 dark:text-dark-text">{t('exportModal.title')}</h2>
          </div>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-overlay">
            <X className="w-6 h-6 text-gray-500 dark:text-dark-subtext" />
          </button>
        </div>
        <div className="p-6 space-y-6 overflow-y-auto max-h-[60vh]">
            <p className="text-sm text-gray-600 dark:text-dark-subtext">{t('exportModal.description')}</p>
            <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-dark-subtext mb-2">{t('exportModal.filterByType')}</label>
                <div className="flex flex-wrap gap-2">
                    {Object.values(PromptType).map(type => (
                        <button key={type} onClick={() => handleTypeChange(type)} className={`px-3 py-1.5 text-sm rounded-full border-2 transition-colors ${selectedTypes.includes(type) ? 'bg-dark-primary/20 border-dark-primary' : 'bg-gray-100 dark:bg-dark-bg border-transparent'}`}>
                            {t(`promptType.${type}`)}
                        </button>
                    ))}
                </div>
            </div>
            <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-dark-subtext mb-2">{t('exportModal.filterByTags')}</label>
                 <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto bg-gray-100 dark:bg-dark-bg p-2 rounded-lg">
                    {allTags.length > 0 ? allTags.map(tag => (
                        <button key={tag} onClick={() => handleTagChange(tag)} className={`px-2 py-1 text-xs rounded-full border transition-colors ${selectedTags.includes(tag) ? 'bg-dark-primary/20 border-dark-primary' : 'bg-white dark:bg-dark-surface border-gray-200 dark:border-dark-overlay'}`}>
                           #{tag}
                        </button>
                    )) : <p className="text-xs text-gray-400 p-2">{t('exportModal.allTags')}</p>}
                </div>
            </div>
            <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-dark-subtext mb-2">{t('exportModal.filterByRating')}</label>
                <select value={selectedRating} onChange={(e) => setSelectedRating(Number(e.target.value))} className="w-full bg-gray-100 dark:bg-dark-bg rounded-lg border-transparent focus:border-dark-primary focus:ring-0">
                    <option value={0}>{t('exportModal.allRatings')}</option>
                    <option value={5}>{t('promptList.filter.fiveStars')}</option>
                    <option value={4}>{t('promptList.filter.fourStars')}</option>
                    <option value={3}>{t('promptList.filter.threeStars')}</option>
                </select>
            </div>
        </div>
        <div className="p-5 border-t border-gray-200 dark:border-dark-overlay bg-gray-50 dark:bg-dark-surface/50 flex justify-between items-center">
            <p className="text-sm font-semibold">{t('bulkActions.selected', { count: filteredPrompts.length })}</p>
            <div className="flex gap-3">
                <button type="button" onClick={onClose} className="px-6 py-2 rounded-full text-gray-700 dark:text-dark-subtext bg-gray-200 dark:bg-dark-overlay hover:opacity-90 transition">{t('buttons.cancel')}</button>
                <button type="button" onClick={() => onExport(filteredPrompts)} disabled={filteredPrompts.length === 0} className="px-6 py-2 rounded-full text-white bg-dark-primary hover:opacity-90 font-semibold transition shadow-lg shadow-dark-primary/30 disabled:opacity-50 disabled:cursor-not-allowed">{t('buttons.export')}</button>
            </div>
        </div>
      </div>
    </div>
  );
};

export default ExportModal;