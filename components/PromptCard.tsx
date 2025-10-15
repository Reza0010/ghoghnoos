import React from 'react';
import { Prompt } from '../types';
import { PROMPT_TYPE_CONFIG } from '../constants';
import { Star, Edit, Trash, Wand2, Copy } from './icons';

interface PromptCardProps {
  prompt: Prompt;
  onEdit: (prompt: Prompt) => void;
  onDelete: (id: string) => void;
  onRemix: (prompt: Prompt) => void;
}

const PromptCard: React.FC<PromptCardProps> = ({ prompt, onEdit, onDelete, onRemix }) => {
  const config = PROMPT_TYPE_CONFIG[prompt.type];

  const handleCopy = () => {
    navigator.clipboard.writeText(prompt.content);
    // In a real app, you might want to show a toast notification here.
  };

  return (
    <div className="bg-white dark:bg-dark-surface rounded-2xl shadow-lg flex flex-col transition-all duration-300 hover:shadow-xl hover:-translate-y-1 animate-fade-in">
      {prompt.imageUrl && (
        <div className="relative h-48 w-full">
          <img src={prompt.imageUrl} alt={prompt.title} className="w-full h-full object-cover rounded-t-2xl" />
          <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-t from-black/60 to-transparent"></div>
          <div className={`absolute top-3 right-3 flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-semibold text-white ${config.color}`}>
            <config.icon className="w-4 h-4" />
            <span>{config.label}</span>
          </div>
        </div>
      )}
      <div className="p-5 flex flex-col flex-grow">
        {!prompt.imageUrl && (
            <div className={`self-start flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-semibold ${config.textColor} ${config.color}/10 mb-3`}>
                <config.icon className="w-4 h-4" />
                <span>{config.label}</span>
            </div>
        )}
        <div className="flex justify-between items-start">
            <h3 className={`text-xl font-bold ${prompt.imageUrl ? 'text-white -mt-16' : 'text-gray-800 dark:text-dark-text'}`}>{prompt.title}</h3>
            {prompt.rating && prompt.rating > 0 && (
                <div className="flex items-center gap-1 flex-shrink-0 ml-2">
                    {[...Array(5)].map((_, i) => (
                        <Star key={i} className={`w-5 h-5 ${i < (prompt.rating || 0) ? 'text-dark-warn fill-current' : 'text-gray-300 dark:text-dark-overlay'}`} />
                    ))}
                </div>
            )}
        </div>
        <p className="mt-2 text-sm text-gray-600 dark:text-dark-subtext flex-grow leading-relaxed">{prompt.summary || prompt.content.substring(0, 120) + (prompt.content.length > 120 ? '...' : '')}</p>
        <div className="mt-4 flex flex-wrap gap-2">
            {prompt.tags.map(tag => (
                <span key={tag} className="px-2 py-1 bg-dark-primary/10 text-dark-primary text-xs font-semibold rounded-full">
                    #{tag}
                </span>
            ))}
        </div>
      </div>
      <div className="p-3 border-t border-gray-100 dark:border-dark-overlay bg-gray-50/50 dark:bg-dark-surface/50 rounded-b-2xl flex items-center justify-end gap-2">
        <button onClick={handleCopy} title="کپی کردن پرامپت" className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-overlay transition-colors">
            <Copy className="w-5 h-5 text-gray-500 dark:text-dark-subtext" />
        </button>
        {prompt.type === 'image' && prompt.imageUrl && (
            <button onClick={() => onRemix(prompt)} title="ریمیکس تصویر" className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-overlay transition-colors">
                <Wand2 className="w-5 h-5 text-dark-secondary" />
            </button>
        )}
        <button onClick={() => onEdit(prompt)} title="ویرایش" className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-overlay transition-colors">
            <Edit className="w-5 h-5 text-dark-accent" />
        </button>
        <button onClick={() => onDelete(prompt.id)} title="حذف" className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-overlay transition-colors">
            <Trash className="w-5 h-5 text-dark-danger" />
        </button>
      </div>
    </div>
  );
};

export default PromptCard;