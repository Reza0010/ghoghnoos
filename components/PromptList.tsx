import React, { useState } from 'react';
import { Prompt, SortOption, FilterOption } from '../types';
import { PromptCard } from './PromptCard';
import { 
  Search, 
  Filter, 
  Grid3X3, 
  List, 
  SortAsc,
  FileText,
  Image as ImageIcon,
  Heart,
  Clock
} from './icons';

interface PromptListProps {
  prompts: Prompt[];
  onEdit: (prompt: Prompt) => void;
  onDelete: (id: string) => void;
  onToggleFavorite: (id: string) => void;
  onUse: (prompt: Prompt) => void;
}

export const PromptList: React.FC<PromptListProps> = ({
  prompts,
  onEdit,
  onDelete,
  onToggleFavorite,
  onUse,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<SortOption>('newest');
  const [filterBy, setFilterBy] = useState<FilterOption>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedCategory, setSelectedCategory] = useState<string>('');

  // Get unique categories
  const categories = Array.from(new Set(prompts.map(p => p.category))).filter(Boolean);

  // Filter prompts
  const filteredPrompts = prompts.filter(prompt => {
    // Search filter
    const matchesSearch = searchQuery === '' || 
      prompt.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      prompt.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      prompt.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      prompt.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));

    // Type filter
    const matchesFilter = filterBy === 'all' || 
      (filterBy === 'favorites' && prompt.isFavorite) ||
      (filterBy === 'text' && prompt.type === 'text') ||
      (filterBy === 'image' && prompt.type === 'image') ||
      (filterBy === 'recent' && new Date(prompt.updatedAt).getTime() > Date.now() - 7 * 24 * 60 * 60 * 1000);

    // Category filter
    const matchesCategory = selectedCategory === '' || prompt.category === selectedCategory;

    return matchesSearch && matchesFilter && matchesCategory;
  });

  // Sort prompts
  const sortedPrompts = [...filteredPrompts].sort((a, b) => {
    switch (sortBy) {
      case 'newest':
        return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
      case 'oldest':
        return new Date(a.updatedAt).getTime() - new Date(b.updatedAt).getTime();
      case 'alphabetical':
        return a.title.localeCompare(b.title);
      case 'mostUsed':
        return b.usageCount - a.usageCount;
      case 'lastUsed':
        return (b.lastUsed?.getTime() || 0) - (a.lastUsed?.getTime() || 0);
      default:
        return 0;
    }
  });

  const filterOptions = [
    { value: 'all', label: 'All Prompts', icon: FileText },
    { value: 'favorites', label: 'Favorites', icon: Heart },
    { value: 'text', label: 'Text Prompts', icon: FileText },
    { value: 'image', label: 'Image Prompts', icon: ImageIcon },
    { value: 'recent', label: 'Recent', icon: Clock },
  ];

  const sortOptions = [
    { value: 'newest', label: 'Newest First' },
    { value: 'oldest', label: 'Oldest First' },
    { value: 'alphabetical', label: 'Alphabetical' },
    { value: 'mostUsed', label: 'Most Used' },
    { value: 'lastUsed', label: 'Recently Used' },
  ];

  return (
    <div className="main-content">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              All Prompts
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              {sortedPrompts.length} of {prompts.length} prompts
            </p>
          </div>

          {/* View Toggle */}
          <div className="flex items-center space-x-2 mt-4 sm:mt-0">
            <button
              onClick={() => setViewMode('grid')}
              className={`btn btn-sm ${viewMode === 'grid' ? 'btn-primary' : 'btn-ghost'}`}
            >
              <Grid3X3 size={16} />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`btn btn-sm ${viewMode === 'list' ? 'btn-primary' : 'btn-ghost'}`}
            >
              <List size={16} />
            </button>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="card mb-6">
          <div className="card-body">
            <div className="flex flex-col lg:flex-row gap-4">
              {/* Search */}
              <div className="flex-1">
                <div className="relative">
                  <Search className="search-icon" size={16} />
                  <input
                    type="text"
                    placeholder="Search prompts..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="search-input"
                  />
                </div>
              </div>

              {/* Filter by Type */}
              <div className="flex flex-wrap gap-2">
                {filterOptions.map(option => {
                  const Icon = option.icon;
                  return (
                    <button
                      key={option.value}
                      onClick={() => setFilterBy(option.value as FilterOption)}
                      className={`btn btn-sm ${
                        filterBy === option.value ? 'btn-primary' : 'btn-ghost'
                      }`}
                    >
                      <Icon size={14} />
                      <span className="ml-1 hidden sm:inline">{option.label}</span>
                    </button>
                  );
                })}
              </div>

              {/* Category Filter */}
              {categories.length > 0 && (
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
              )}

              {/* Sort */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortOption)}
                className="select w-auto"
              >
                {sortOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Prompts Grid/List */}
        {sortedPrompts.length === 0 ? (
          <div className="card">
            <div className="card-body text-center py-12">
              <div className="flex items-center justify-center w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full mx-auto mb-4">
                <FileText size={24} className="text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                {searchQuery || filterBy !== 'all' || selectedCategory ? 'No matching prompts' : 'No prompts yet'}
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                {searchQuery || filterBy !== 'all' || selectedCategory
                  ? 'Try adjusting your search or filters.'
                  : 'Create your first prompt to get started.'
                }
              </p>
              {!searchQuery && filterBy === 'all' && !selectedCategory && (
                <button className="btn btn-primary">
                  <FileText size={16} />
                  <span className="ml-2">Create Your First Prompt</span>
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className={
            viewMode === 'grid' 
              ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6'
              : 'space-y-4'
          }>
            {sortedPrompts.map((prompt, index) => (
              <div
                key={prompt.id}
                className="fade-in"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <PromptCard
                  prompt={prompt}
                  onEdit={onEdit}
                  onDelete={onDelete}
                  onToggleFavorite={onToggleFavorite}
                  onUse={onUse}
                />
              </div>
            ))}
          </div>
        )}

        {/* Load More (if needed for pagination) */}
        {sortedPrompts.length > 0 && sortedPrompts.length < prompts.length && (
          <div className="text-center mt-8">
            <button className="btn btn-secondary">
              Load More Prompts
            </button>
          </div>
        )}
      </div>
    </div>
  );
};