import React from 'react';
import { Prompt, PromptCardProps } from '../types';
import { 
  Edit, 
  Trash, 
  Heart, 
  Copy, 
  Play, 
  Clock,
  Tag,
  FileText,
  Image as ImageIcon
} from './icons';
import { PROMPT_TYPE_CONFIG } from '../constants';
import { formatDistanceToNow } from 'date-fns';

export const PromptCard: React.FC<PromptCardProps> = ({
  prompt,
  onEdit,
  onDelete,
  onToggleFavorite,
  onUse,
}) => {
  const typeConfig = PROMPT_TYPE_CONFIG[prompt.type];
  const TypeIcon = typeConfig.icon;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(prompt.content);
      // You could add a toast notification here
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const truncateText = (text: string, maxLength: number = 120) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <div className="prompt-card group">
      <div className="prompt-card-header">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <div className={`p-1.5 rounded-lg ${typeConfig.bgColor}`}>
              <TypeIcon size={16} className={typeConfig.color} />
            </div>
            <span className={`text-xs font-medium px-2 py-1 rounded-full ${typeConfig.bgColor} ${typeConfig.color}`}>
              {typeConfig.label}
            </span>
            {prompt.isFavorite && (
              <Heart size={14} className="text-red-500 fill-current" />
            )}
          </div>
          <h3 className="font-semibold text-gray-900 dark:text-white text-lg mb-1 line-clamp-2">
            {prompt.title}
          </h3>
          {prompt.description && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              {truncateText(prompt.description, 80)}
            </p>
          )}
        </div>
        
        <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => onToggleFavorite(prompt.id)}
            className="btn btn-ghost btn-sm"
            title={prompt.isFavorite ? 'Remove from favorites' : 'Add to favorites'}
          >
            <Heart 
              size={16} 
              className={prompt.isFavorite ? 'text-red-500 fill-current' : 'text-gray-400'} 
            />
          </button>
          <button
            onClick={handleCopy}
            className="btn btn-ghost btn-sm"
            title="Copy prompt"
          >
            <Copy size={16} />
          </button>
          <button
            onClick={() => onEdit(prompt)}
            className="btn btn-ghost btn-sm"
            title="Edit prompt"
          >
            <Edit size={16} />
          </button>
          <button
            onClick={() => onDelete(prompt.id)}
            className="btn btn-ghost btn-sm text-red-600 hover:text-red-700"
            title="Delete prompt"
          >
            <Trash size={16} />
          </button>
        </div>
      </div>

      <div className="prompt-card-body">
        <p className="text-gray-700 dark:text-gray-300 text-sm mb-4 line-clamp-3">
          {truncateText(prompt.content)}
        </p>

        {/* Tags */}
        {prompt.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-4">
            {prompt.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="tag tag-gray text-xs"
              >
                {tag}
              </span>
            ))}
            {prompt.tags.length > 3 && (
              <span className="tag tag-gray text-xs">
                +{prompt.tags.length - 3} more
              </span>
            )}
          </div>
        )}

        {/* Category */}
        {prompt.category && (
          <div className="flex items-center space-x-1 mb-3">
            <Tag size={12} className="text-gray-400" />
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {prompt.category}
            </span>
          </div>
        )}
      </div>

      <div className="prompt-card-footer">
        <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
          <div className="flex items-center space-x-1">
            <Clock size={12} />
            <span>
              {formatDistanceToNow(new Date(prompt.updatedAt), { addSuffix: true })}
            </span>
          </div>
          <div className="flex items-center space-x-1">
            <Play size={12} />
            <span>{prompt.usageCount} uses</span>
          </div>
        </div>

        <button
          onClick={() => onUse(prompt)}
          className="btn btn-primary btn-sm"
        >
          <Play size={14} />
          <span className="ml-1">Use</span>
        </button>
      </div>
    </div>
  );
};