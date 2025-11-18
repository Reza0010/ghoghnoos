import React from 'react';
import { Prompt } from '../types';
import { getPromptTypeConfig } from '../constants';
import { Star, FilePenLine, Trash2, WandSparkles, Copy, History, StarFill, CheckSquare, Square } from './icons';
import { useTranslation } from '../contexts/LanguageContext';

interface HighlightProps {
  text: string;
  query: string;
}

const Highlight: React.FC<HighlightProps> = ({ text, query }) => {
  if (!query) {
    return <>{text}</>;
  }
  const parts = text.split(new RegExp(`(${query.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')})`, 'gi'));
  return (
    <>
      {parts.map((part, i) =>
        part.toLowerCase() === query.toLowerCase() ? (
          <mark key={i} className="bg-yellow-300/70 dark:bg-yellow-500/50 rounded px-0.5 py-0">
            {part}
          </mark>
        ) : (
          part
        )
      )}
    </>
  );
};

interface PromptCardProps {
  prompt: Prompt;
  onEdit: (prompt: Prompt) => void;
  onDelete: (id: string) => void;
  onRemix: (prompt: Prompt) => void;
  onViewHistory: (prompt: Prompt) => void;
  searchQuery: string;
  isSelectionMode: boolean;
  onSelect: () => void;
  isSelected: boolean;
}

const PromptCard: React.FC<PromptCardProps> = ({ prompt, onEdit, onDelete, onRemix, onViewHistory, searchQuery, isSelectionMode, onSelect, isSelected }) => {
  const { t } = useTranslation();
  const PROMPT_TYPE_CONFIG = getPromptTypeConfig(t);
  const config = PROMPT_TYPE_CONFIG[prompt.type];

  const handleCopy = () => {
    navigator.clipboard.writeText(prompt.content);
  };
  
  const displayContent = prompt.summary || prompt.content.substring(0, 120) + (prompt.content.length > 120 ? '...' : '');

  const commonCardProps = {
    className: `group relative rounded-2xl flex flex-col transition-all duration-300 animate-fade-in ${isSelectionMode ? 'cursor-pointer' : ''} ${isSelected ? 'ring-4 ring-offset-2 ring-offset-dark-bg ring-dark-primary' : 'shadow-lg'}`,
    onClick: isSelectionMode ? onSelect : undefined,
  };

  const selectionOverlay = isSelectionMode && (
    <div className={`absolute top-4 rtl:left-4 ltr:right-4 z-30 transition-opacity duration-200 ${isSelected ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`}>
        {isSelected ? (
            <CheckSquare className="w-8 h-8 text-white bg-dark-primary rounded-md p-1" />
        ) : (
            <Square className="w-8 h-8 text-white bg-black/40 rounded-md p-1 backdrop-blur-sm" />
        )}
    </div>
  );

  // Card for Image Prompts
  if (prompt.imageUrl) {
    return (
      <div {...commonCardProps} style={{
        aspectRatio: '1 / 1',
        backgroundColor: 'rgb(209 213 219)', // bg-gray-300
      }}>
        <div className="absolute inset-0 overflow-hidden rounded-2xl">
            {selectionOverlay}
            <img src={prompt.imageUrl} alt={prompt.title} className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent"></div>
            
            <div className="relative p-5 text-white h-full flex flex-col justify-end">
                {prompt.rating && prompt.rating > 0 && (
                    <div className="absolute top-5 rtl:left-5 ltr:right-5 flex items-center gap-1">
                        {[...Array(5)].map((_, i) => (
                            i < (prompt.rating || 0) 
                            ? <StarFill key={i} className="w-5 h-5 text-dark-warn" /> 
                            : <Star key={i} className="w-5 h-5 text-gray-300/50" />
                        ))}
                    </div>
                )}
                <h3 className="text-xl font-bold">
                    <Highlight text={prompt.title} query={searchQuery} />
                </h3>
                <div className="mt-2 flex flex-wrap gap-2">
                    {(prompt.tags || []).slice(0, 3).map(tag => (
                        <span key={tag} className="px-2 py-0.5 bg-white/20 text-white text-xs font-semibold rounded-full backdrop-blur-sm">
                            #<Highlight text={tag} query={searchQuery} />
                        </span>
                    ))}
                </div>
            </div>
            
            <div className="absolute bottom-0 left-0 right-0 p-3 bg-black/20 backdrop-blur-sm transform translate-y-full group-hover:translate-y-0 transition-transform duration-300 flex items-center justify-end gap-2 z-20">
                <button onClick={(e) => { e.stopPropagation(); handleCopy(); }} title={t('promptCard.copy')} className="p-2 rounded-full text-white hover:bg-white/20 transition-colors">
                    <Copy className="w-5 h-5" />
                </button>
                <button onClick={(e) => { e.stopPropagation(); onRemix(prompt); }} title={t('promptCard.remix')} className="p-2 rounded-full text-white hover:bg-white/20 transition-colors">
                    <WandSparkles className="w-5 h-5" />
                </button>
                <button onClick={(e) => { e.stopPropagation(); onViewHistory(prompt); }} title={t('promptCard.history')} className="p-2 rounded-full text-white hover:bg-white/20 transition-colors">
                    <History className="w-5 h-5" />
                </button>
                <button onClick={(e) => { e.stopPropagation(); onEdit(prompt); }} title={t('promptCard.edit')} className="p-2 rounded-full text-white hover:bg-white/20 transition-colors">
                    <FilePenLine className="w-5 h-5" />
                </button>
                <button onClick={(e) => { e.stopPropagation(); onDelete(prompt.id); }} title={t('promptCard.delete')} className="p-2 rounded-full text-white hover:bg-white/20 transition-colors">
                    <Trash2 className="w-5 h-5" />
                </button>
            </div>
        </div>
      </div>
    );
  }

  // Card for Text, Video, Music Prompts
  const gradientMap: { [key: string]: string } = {
    'bg-green-500': 'from-green-500/20',
    'bg-red-500': 'from-red-500/20',
    'bg-purple-500': 'from-purple-500/20',
  };
  const gradientFrom = gradientMap[config.color] || 'from-gray-500/20';

  return (
    <div {...commonCardProps} className={`${commonCardProps.className} bg-white dark:bg-dark-surface hover:-translate-y-1 min-h-[350px] overflow-hidden`}>
      {selectionOverlay}
      <div className={`absolute inset-0 bg-gradient-to-br ${gradientFrom} to-transparent opacity-30 group-hover:opacity-50 transition-opacity`}></div>
      <div className="relative p-5 flex flex-col flex-grow z-10">
        <div className="flex justify-between items-start mb-3">
            <div className={`self-start flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-semibold ${config.textColor} bg-white dark:bg-dark-surface shadow-sm`}>
                <config.icon className="w-4 h-4" />
                <span>{config.label}</span>
            </div>
            {prompt.rating && prompt.rating > 0 && (
                <div className="flex items-center gap-1 flex-shrink-0">
                    {[...Array(5)].map((_, i) => (
                        i < (prompt.rating || 0) 
                        ? <StarFill key={i} className="w-5 h-5 text-dark-warn" />
                        : <Star key={i} className="w-5 h-5 text-gray-300 dark:text-dark-overlay" />
                    ))}
                </div>
            )}
        </div>
        
        <h3 className="text-xl font-bold text-gray-800 dark:text-dark-text">
            <Highlight text={prompt.title} query={searchQuery} />
        </h3>
        
        <p className="mt-2 text-sm text-gray-600 dark:text-dark-subtext flex-grow leading-relaxed">
            <Highlight text={displayContent} query={searchQuery} />
        </p>
        
        <div className="mt-4 flex flex-wrap gap-2">
            {(prompt.tags || []).map(tag => (
                <span key={tag} className="px-2 py-1 bg-dark-primary/10 text-dark-primary text-xs font-semibold rounded-full">
                    #<Highlight text={tag} query={searchQuery} />
                </span>
            ))}
        </div>
      </div>
      
      <div className="absolute bottom-0 left-0 right-0 p-3 bg-white/60 dark:bg-dark-surface/60 backdrop-blur-sm transform translate-y-full group-hover:translate-y-0 transition-transform duration-300 flex items-center justify-end gap-2 z-20 border-t border-gray-200/50 dark:border-dark-overlay/50">
        <button onClick={(e) => { e.stopPropagation(); handleCopy(); }} title={t('promptCard.copy')} className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-overlay transition-colors">
            <Copy className="w-5 h-5 text-gray-500 dark:text-dark-subtext" />
        </button>
        <button onClick={(e) => { e.stopPropagation(); onViewHistory(prompt); }} title={t('promptCard.history')} className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-overlay transition-colors">
            <History className="w-5 h-5 text-gray-500 dark:text-dark-subtext" />
        </button>
        <button onClick={(e) => { e.stopPropagation(); onEdit(prompt); }} title={t('promptCard.edit')} className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-overlay transition-colors">
            <FilePenLine className="w-5 h-5 text-dark-accent" />
        </button>
        <button onClick={(e) => { e.stopPropagation(); onDelete(prompt.id); }} title={t('promptCard.delete')} className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-overlay transition-colors">
            <Trash2 className="w-5 h-5 text-dark-danger" />
        </button>
      </div>
    </div>
  );
};

export default PromptCard;