import React from 'react';
import { Prompt, PromptType } from '../types';
import PromptCard from './PromptCard';
import { PROMPT_TYPE_CONFIG } from '../constants';

interface PromptListProps {
  prompts: Prompt[];
  view: string;
  onEdit: (prompt: Prompt) => void;
  onDelete: (id: string) => void;
  onRemix: (prompt: Prompt) => void;
}

const PromptList: React.FC<PromptListProps> = ({ prompts, view, onEdit, onDelete, onRemix }) => {
  // FIX: Cast view to PromptType (which is a keyof PROMPT_TYPE_CONFIG) to ensure type safety.
  const config = PROMPT_TYPE_CONFIG[view as PromptType];

  return (
    <div className="p-6 h-full overflow-y-auto" dir="rtl">
      <div className="flex items-center gap-3 mb-6">
        {config?.icon && <config.icon className={`w-8 h-8 ${config.textColor}`} />}
        <h1 className="text-3xl font-bold text-gray-800 dark:text-dark-text">
          {config?.label || 'همه پرامپت‌ها'}
        </h1>
      </div>
      {prompts.length === 0 ? (
        <div className="text-center text-gray-500 dark:text-dark-subtext mt-20">
          <p className="text-xl">هیچ پرامپتی یافت نشد.</p>
          <p>یک پرامپت جدید اضافه کنید تا شروع کنید!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3 gap-6">
          {prompts.map(prompt => (
            <PromptCard key={prompt.id} prompt={prompt} onEdit={onEdit} onDelete={onDelete} onRemix={onRemix}/>
          ))}
        </div>
      )}
    </div>
  );
};

export default PromptList;