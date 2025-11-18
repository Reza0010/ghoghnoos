import React from 'react';
import { Prompt, PromptType } from '../types';
import PromptCard from './PromptCard';
import { getPromptTypeConfig } from '../constants';
import { ArrowUpDown, Filter } from './icons';
import { useTranslation } from '../contexts/LanguageContext';

interface PromptListProps {
  prompts: Prompt[];
  view: string;
  onEdit: (prompt: Prompt) => void;
  onDelete: (id: string) => void;
  onRemix: (prompt: Prompt) => void;
  onViewHistory: (prompt: Prompt) => void;
  sortOption: string;
  setSortOption: (option: string) => void;
  ratingFilter: number;
  setRatingFilter: (rating: number) => void;
  searchQuery: string;
  isSelectionMode: boolean;
  toggleSelectionMode: () => void;
  selectedCount: number;
  onSelectPrompt: (id: string) => void;
  isSelected: (id: string) => boolean;
}

const PromptList: React.FC<PromptListProps> = ({ 
    prompts, 
    view, 
    onEdit, 
    onDelete, 
    onRemix,
    onViewHistory,
    sortOption,
    setSortOption,
    ratingFilter,
    setRatingFilter,
    searchQuery,
    isSelectionMode,
    toggleSelectionMode,
    selectedCount,
    onSelectPrompt,
    isSelected
}) => {
  const { t } = useTranslation();
  const PROMPT_TYPE_CONFIG = getPromptTypeConfig(t);
  const config = PROMPT_TYPE_CONFIG[view as PromptType];

  return (
    <div className="p-6 h-full overflow-y-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
        <div className="flex items-center gap-3">
          {config?.icon && <config.icon className={`w-8 h-8 ${config.textColor}`} />}
          <h1 className="text-3xl font-bold text-gray-800 dark:text-dark-text">
            {config?.label || t('promptList.allPromptsTitle')}
            {isSelectionMode && <span className="text-lg text-gray-500 dark:text-dark-subtext ml-3 rtl:mr-3">({t('bulkActions.selected', { count: selectedCount })})</span>}
          </h1>
        </div>
        
        <div className="flex items-center gap-4 w-full md:w-auto">
            {/* Select Button */}
            <button
                onClick={toggleSelectionMode}
                className={`px-4 py-2 text-sm font-semibold rounded-lg transition-colors ${isSelectionMode ? 'bg-dark-primary/20 text-dark-primary' : 'bg-gray-100 dark:bg-dark-surface'}`}
            >
                {isSelectionMode ? t('buttons.cancelSelection') : t('buttons.select')}
            </button>
            {/* Sort Dropdown */}
            <div className="relative w-full md:w-auto">
                <ArrowUpDown className="absolute top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-dark-subtext pointer-events-none rtl:right-3 ltr:left-3" />
                <select
                    value={sortOption}
                    onChange={(e) => setSortOption(e.target.value)}
                    className="w-full bg-gray-100 dark:bg-dark-surface border-transparent focus:border-dark-primary focus:ring-0 rounded-lg py-2 rtl:pr-10 ltr:pl-10 rtl:pl-4 ltr:pr-4 appearance-none text-sm"
                    aria-label={t('promptList.sortAriaLabel')}
                >
                    <option value="updatedAt-desc">{t('promptList.sort.latest')}</option>
                    <option value="updatedAt-asc">{t('promptList.sort.oldest')}</option>
                    <option value="title-asc">{t('promptList.sort.titleAsc')}</option>
                    <option value="title-desc">{t('promptList.sort.titleDesc')}</option>
                    <option value="rating-desc">{t('promptList.sort.ratingDesc')}</option>
                    <option value="rating-asc">{t('promptList.sort.ratingAsc')}</option>
                </select>
            </div>
            {/* Rating Filter Dropdown */}
            <div className="relative w-full md:w-auto">
                <Filter className="absolute top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-dark-subtext pointer-events-none rtl:right-3 ltr:left-3" />
                <select
                    value={ratingFilter}
                    onChange={(e) => setRatingFilter(Number(e.target.value))}
                    className="w-full bg-gray-100 dark:bg-dark-surface border-transparent focus:border-dark-primary focus:ring-0 rounded-lg py-2 rtl:pr-10 ltr:pl-10 rtl:pl-4 ltr:pr-4 appearance-none text-sm"
                    aria-label={t('promptList.filterAriaLabel')}
                >
                    <option value={0}>{t('promptList.filter.all')}</option>
                    <option value={5}>{t('promptList.filter.fiveStars')}</option>
                    <option value={4}>{t('promptList.filter.fourStars')}</option>
                    <option value={3}>{t('promptList.filter.threeStars')}</option>
                    <option value={-1}>{t('promptList.filter.unrated')}</option>
                </select>
            </div>
        </div>
      </div>
      {prompts.length === 0 ? (
        <div className="text-center text-gray-500 dark:text-dark-subtext mt-20">
          <p className="text-xl">{t('promptList.noResults.title')}</p>
          <p>{t('promptList.noResults.description')}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3 gap-6">
          {prompts.map(prompt => (
            <PromptCard 
              key={prompt.id} 
              prompt={prompt} 
              onEdit={onEdit} 
              onDelete={onDelete} 
              onRemix={onRemix} 
              onViewHistory={onViewHistory} 
              searchQuery={searchQuery}
              isSelectionMode={isSelectionMode}
              onSelect={() => onSelectPrompt(prompt.id)}
              isSelected={isSelected(prompt.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default PromptList;