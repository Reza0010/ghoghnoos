import React, { useState, useEffect } from 'react';
import { Prompt } from '../types';
import { 
  Save, 
  X, 
  FileText, 
  Image as ImageIcon, 
  Tag, 
  Folder, 
  Eye,
  Play,
  Wand2,
  Copy
} from './icons';
import { DEFAULT_PROMPT_CATEGORIES } from '../constants';

interface PromptStudioProps {
  prompt?: Prompt | null;
  onSave: (prompt: Omit<Prompt, 'id' | 'createdAt' | 'updatedAt'>) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export const PromptStudio: React.FC<PromptStudioProps> = ({
  prompt,
  onSave,
  onCancel,
  isLoading = false,
}) => {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    description: '',
    type: 'text' as 'text' | 'image',
    tags: [] as string[],
    category: '',
  });

  const [newTag, setNewTag] = useState('');
  const [showPreview, setShowPreview] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Initialize form data when prompt changes
  useEffect(() => {
    if (prompt) {
      setFormData({
        title: prompt.title,
        content: prompt.content,
        description: prompt.description || '',
        type: prompt.type,
        tags: [...prompt.tags],
        category: prompt.category,
      });
    } else {
      setFormData({
        title: '',
        content: '',
        description: '',
        type: 'text',
        tags: [],
        category: DEFAULT_PROMPT_CATEGORIES[0],
      });
    }
  }, [prompt]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }

    if (!formData.content.trim()) {
      newErrors.content = 'Prompt content is required';
    }

    if (!formData.category.trim()) {
      newErrors.category = 'Category is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    onSave({
      ...formData,
      title: formData.title.trim(),
      content: formData.content.trim(),
      description: formData.description.trim(),
      category: formData.category.trim(),
    });
  };

  const handleAddTag = () => {
    const tag = newTag.trim();
    if (tag && !formData.tags.includes(tag)) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tag]
      }));
      setNewTag('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAddTag();
    }
  };

  const handleCopyContent = async () => {
    try {
      await navigator.clipboard.writeText(formData.content);
      // Could add toast notification here
    } catch (err) {
      console.error('Failed to copy content:', err);
    }
  };

  const getCharacterCount = () => {
    return formData.content.length;
  };

  const getWordCount = () => {
    return formData.content.trim().split(/\s+/).filter(word => word.length > 0).length;
  };

  return (
    <div className="main-content">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {prompt ? 'Edit Prompt' : 'Create New Prompt'}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              {prompt ? 'Update your existing prompt' : 'Design and craft your AI prompt'}
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              type="button"
              onClick={() => setShowPreview(!showPreview)}
              className="btn btn-secondary btn-sm"
            >
              <Eye size={16} />
              <span className="ml-2">{showPreview ? 'Hide' : 'Preview'}</span>
            </button>
            
            <button
              type="button"
              onClick={onCancel}
              className="btn btn-ghost btn-sm"
            >
              <X size={16} />
              <span className="ml-2">Cancel</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Form */}
          <div className="lg:col-span-2">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Basic Information */}
              <div className="card">
                <div className="card-header">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Basic Information
                  </h2>
                </div>
                <div className="card-body space-y-4">
                  {/* Title */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Title *
                    </label>
                    <input
                      type="text"
                      value={formData.title}
                      onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                      className={`input ${errors.title ? 'border-red-500' : ''}`}
                      placeholder="Enter a descriptive title for your prompt"
                    />
                    {errors.title && (
                      <p className="text-red-500 text-sm mt-1">{errors.title}</p>
                    )}
                  </div>

                  {/* Description */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Description
                    </label>
                    <input
                      type="text"
                      value={formData.description}
                      onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                      className="input"
                      placeholder="Brief description of what this prompt does"
                    />
                  </div>

                  {/* Type */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Type *
                    </label>
                    <div className="flex space-x-4">
                      <label className="flex items-center">
                        <input
                          type="radio"
                          name="type"
                          value="text"
                          checked={formData.type === 'text'}
                          onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value as 'text' | 'image' }))}
                          className="mr-2"
                        />
                        <FileText size={16} className="mr-2" />
                        Text Prompt
                      </label>
                      <label className="flex items-center">
                        <input
                          type="radio"
                          name="type"
                          value="image"
                          checked={formData.type === 'image'}
                          onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value as 'text' | 'image' }))}
                          className="mr-2"
                        />
                        <ImageIcon size={16} className="mr-2" />
                        Image Prompt
                      </label>
                    </div>
                  </div>

                  {/* Category */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Category *
                    </label>
                    <select
                      value={formData.category}
                      onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                      className={`select ${errors.category ? 'border-red-500' : ''}`}
                    >
                      <option value="">Select a category</option>
                      {DEFAULT_PROMPT_CATEGORIES.map(category => (
                        <option key={category} value={category}>
                          {category}
                        </option>
                      ))}
                    </select>
                    {errors.category && (
                      <p className="text-red-500 text-sm mt-1">{errors.category}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Prompt Content */}
              <div className="card">
                <div className="card-header">
                  <div className="flex items-center justify-between">
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Prompt Content
                    </h2>
                    <div className="flex items-center space-x-4">
                      <button
                        type="button"
                        onClick={handleCopyContent}
                        className="btn btn-ghost btn-sm"
                        title="Copy content"
                      >
                        <Copy size={16} />
                      </button>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {getWordCount()} words, {getCharacterCount()} characters
                      </div>
                    </div>
                  </div>
                </div>
                <div className="card-body">
                  <textarea
                    value={formData.content}
                    onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
                    className={`textarea min-h-[300px] ${errors.content ? 'border-red-500' : ''}`}
                    placeholder={formData.type === 'image' 
                      ? "Describe the image you want to generate in detail. Include style, composition, colors, lighting, and any specific elements..."
                      : "Enter your prompt here. Be specific and clear about what you want the AI to do..."
                    }
                  />
                  {errors.content && (
                    <p className="text-red-500 text-sm mt-1">{errors.content}</p>
                  )}
                </div>
              </div>

              {/* Tags */}
              <div className="card">
                <div className="card-header">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Tags
                  </h2>
                </div>
                <div className="card-body">
                  <div className="flex flex-wrap gap-2 mb-4">
                    {formData.tags.map(tag => (
                      <span
                        key={tag}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-300"
                      >
                        {tag}
                        <button
                          type="button"
                          onClick={() => handleRemoveTag(tag)}
                          className="ml-2 text-primary-600 hover:text-primary-800 dark:text-primary-400 dark:hover:text-primary-200"
                        >
                          <X size={14} />
                        </button>
                      </span>
                    ))}
                  </div>
                  
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                      onKeyPress={handleKeyPress}
                      className="input flex-1"
                      placeholder="Add a tag and press Enter"
                    />
                    <button
                      type="button"
                      onClick={handleAddTag}
                      className="btn btn-secondary btn-sm"
                    >
                      <Tag size={16} />
                    </button>
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={onCancel}
                  className="btn btn-secondary"
                  disabled={isLoading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <div className="loading-spinner" />
                  ) : (
                    <Save size={16} />
                  )}
                  <span className="ml-2">
                    {isLoading ? 'Saving...' : (prompt ? 'Update Prompt' : 'Create Prompt')}
                  </span>
                </button>
              </div>
            </form>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Preview */}
            {showPreview && (
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Preview
                  </h3>
                </div>
                <div className="card-body">
                  <div className="space-y-3">
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        {formData.title || 'Untitled Prompt'}
                      </h4>
                      {formData.description && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          {formData.description}
                        </p>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-2 text-sm">
                      <span className={`px-2 py-1 rounded text-xs ${
                        formData.type === 'text' 
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                          : 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300'
                      }`}>
                        {formData.type === 'text' ? 'Text' : 'Image'}
                      </span>
                      {formData.category && (
                        <span className="text-gray-500 dark:text-gray-400">
                          {formData.category}
                        </span>
                      )}
                    </div>

                    <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                        {formData.content || 'Your prompt content will appear here...'}
                      </p>
                    </div>

                    {formData.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {formData.tags.map(tag => (
                          <span
                            key={tag}
                            className="px-2 py-1 text-xs bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Tips */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Tips for Great Prompts
                </h3>
              </div>
              <div className="card-body">
                <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <li className="flex items-start space-x-2">
                    <span className="text-primary-500 mt-1">•</span>
                    <span>Be specific and clear about what you want</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-primary-500 mt-1">•</span>
                    <span>Include context and background information</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-primary-500 mt-1">•</span>
                    <span>Use examples when helpful</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-primary-500 mt-1">•</span>
                    <span>Specify the desired format or style</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-primary-500 mt-1">•</span>
                    <span>Test and iterate to improve results</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Quick Actions
                </h3>
              </div>
              <div className="card-body space-y-2">
                <button
                  type="button"
                  className="w-full btn btn-ghost btn-sm justify-start"
                >
                  <Wand2 size={16} />
                  <span className="ml-2">AI Enhance</span>
                </button>
                <button
                  type="button"
                  className="w-full btn btn-ghost btn-sm justify-start"
                >
                  <Play size={16} />
                  <span className="ml-2">Test Prompt</span>
                </button>
                <button
                  type="button"
                  className="w-full btn btn-ghost btn-sm justify-start"
                >
                  <Folder size={16} />
                  <span className="ml-2">Save as Template</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};