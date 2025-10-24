import React, { useState } from 'react';
import { PromptTemplate } from '../types';
import { INSPIRATION_PROMPTS, BUILT_IN_TEMPLATES } from '../constants';
import { 
  Lightbulb, 
  Copy, 
  Play, 
  Star, 
  Filter, 
  Search,
  ArrowRight,
  Tag
} from './icons';

interface InspirationHubProps {
  onUsePrompt: (template: PromptTemplate) => void;
}

export const InspirationHub: React.FC<InspirationHubProps> = ({ onUsePrompt }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [activeTab, setActiveTab] = useState<'inspiration' | 'templates'>('inspiration');

  // Get unique categories and difficulties
  const categories = Array.from(new Set(INSPIRATION_PROMPTS.map(p => p.category)));
  const difficulties = Array.from(new Set(INSPIRATION_PROMPTS.map(p => p.difficulty)));

  // Filter inspiration prompts
  const filteredInspirationPrompts = INSPIRATION_PROMPTS.filter(prompt => {
    const matchesSearch = searchQuery === '' || 
      prompt.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      prompt.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      prompt.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      prompt.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesCategory = selectedCategory === '' || prompt.category === selectedCategory;
    const matchesDifficulty = selectedDifficulty === '' || prompt.difficulty === selectedDifficulty;

    return matchesSearch && matchesCategory && matchesDifficulty;
  });

  // Filter templates
  const filteredTemplates = BUILT_IN_TEMPLATES.filter(template => {
    const matchesSearch = searchQuery === '' || 
      template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.template.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesCategory = selectedCategory === '' || template.category === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  const handleCopyPrompt = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content);
    } catch (err) {
      console.error('Failed to copy prompt:', err);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300';
      case 'advanced': return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    }
  };

  return (
    <div className="main-content">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center space-x-3 mb-8">
          <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-orange-500 to-pink-600 rounded-xl">
            <Lightbulb size={20} className="text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Inspiration Hub
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Discover expertly crafted prompts and templates to spark your creativity
            </p>
          </div>
        </div>

        {/* Tabs */}
        <div className="tabs mb-6">
          <button
            onClick={() => setActiveTab('inspiration')}
            className={`tab ${activeTab === 'inspiration' ? 'active' : ''}`}
          >
            <Star size={16} />
            <span className="ml-2">Inspiration Prompts</span>
          </button>
          <button
            onClick={() => setActiveTab('templates')}
            className={`tab ${activeTab === 'templates' ? 'active' : ''}`}
          >
            <Copy size={16} />
            <span className="ml-2">Templates</span>
          </button>
        </div>

        {/* Filters */}
        <div className="card mb-6">
          <div className="card-body">
            <div className="flex flex-col lg:flex-row gap-4">
              {/* Search */}
              <div className="flex-1">
                <div className="relative">
                  <Search className="search-icon" size={16} />
                  <input
                    type="text"
                    placeholder="Search prompts and templates..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="search-input"
                  />
                </div>
              </div>

              {/* Category Filter */}
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="select w-auto"
              >
                <option value="">All Categories</option>
                {categories.map(category => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>

              {/* Difficulty Filter (only for inspiration prompts) */}
              {activeTab === 'inspiration' && (
                <select
                  value={selectedDifficulty}
                  onChange={(e) => setSelectedDifficulty(e.target.value)}
                  className="select w-auto"
                >
                  <option value="">All Levels</option>
                  {difficulties.map(difficulty => (
                    <option key={difficulty} value={difficulty}>
                      {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>
        </div>

        {/* Content */}
        {activeTab === 'inspiration' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredInspirationPrompts.map((prompt, index) => (
              <div
                key={prompt.id}
                className="card hover:shadow-lg transition-all duration-300 fade-in"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="card-header">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 dark:text-white text-lg mb-2">
                        {prompt.title}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                        {prompt.description}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 mb-3">
                    <span className={`px-2 py-1 text-xs rounded-full ${getDifficultyColor(prompt.difficulty)}`}>
                      {prompt.difficulty}
                    </span>
                    <span className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full">
                      {prompt.category}
                    </span>
                  </div>
                </div>

                <div className="card-body">
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                      Use Case:
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {prompt.useCase}
                    </p>
                  </div>

                  <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg mb-4">
                    <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-3">
                      {prompt.content}
                    </p>
                  </div>

                  {prompt.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-4">
                      {prompt.tags.slice(0, 3).map(tag => (
                        <span
                          key={tag}
                          className="px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded"
                        >
                          {tag}
                        </span>
                      ))}
                      {prompt.tags.length > 3 && (
                        <span className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded">
                          +{prompt.tags.length - 3}
                        </span>
                      )}
                    </div>
                  )}
                </div>

                <div className="card-footer">
                  <div className="flex items-center justify-between">
                    {prompt.author && (
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        by {prompt.author}
                      </span>
                    )}
                    
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleCopyPrompt(prompt.content)}
                        className="btn btn-ghost btn-sm"
                        title="Copy prompt"
                      >
                        <Copy size={14} />
                      </button>
                      <button
                        onClick={() => onUsePrompt({
                          id: prompt.id,
                          name: prompt.title,
                          description: prompt.description,
                          template: prompt.content,
                          variables: [],
                          category: prompt.category,
                          tags: prompt.tags,
                          isBuiltIn: true
                        })}
                        className="btn btn-primary btn-sm"
                      >
                        <Play size={14} />
                        <span className="ml-1">Use</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredTemplates.map((template, index) => (
              <div
                key={template.id}
                className="card hover:shadow-lg transition-all duration-300 fade-in"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="card-header">
                  <h3 className="font-semibold text-gray-900 dark:text-white text-lg mb-2">
                    {template.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    {template.description}
                  </p>
                  <span className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full">
                    {template.category}
                  </span>
                </div>

                <div className="card-body">
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                      Template:
                    </h4>
                    <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <p className="text-sm text-gray-700 dark:text-gray-300 font-mono">
                        {template.template}
                      </p>
                    </div>
                  </div>

                  {template.variables.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                        Variables:
                      </h4>
                      <div className="flex flex-wrap gap-1">
                        {template.variables.map(variable => (
                          <span
                            key={variable}
                            className="px-2 py-1 text-xs bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 rounded font-mono"
                          >
                            {`{{${variable}}}`}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {template.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {template.tags.map(tag => (
                        <span
                          key={tag}
                          className="px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="card-footer">
                  <div className="flex justify-end space-x-2">
                    <button
                      onClick={() => handleCopyPrompt(template.template)}
                      className="btn btn-ghost btn-sm"
                      title="Copy template"
                    >
                      <Copy size={14} />
                    </button>
                    <button
                      onClick={() => onUsePrompt(template)}
                      className="btn btn-primary btn-sm"
                    >
                      <ArrowRight size={14} />
                      <span className="ml-1">Use Template</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {(activeTab === 'inspiration' ? filteredInspirationPrompts : filteredTemplates).length === 0 && (
          <div className="card">
            <div className="card-body text-center py-12">
              <Lightbulb size={48} className="mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No {activeTab === 'inspiration' ? 'prompts' : 'templates'} found
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Try adjusting your search or filters to find what you're looking for.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};