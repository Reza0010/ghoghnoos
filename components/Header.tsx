import React, { useState } from 'react';
import { Sun, Moon, Plus, Search, Menu, Settings, Zap } from './icons';

interface HeaderProps {
  onThemeToggle: () => void;
  isDark: boolean;
  onNewPrompt: () => void;
  onMenuToggle: () => void;
  onSearch: (query: string) => void;
  currentView: string;
}

export const Header: React.FC<HeaderProps> = ({ 
  onThemeToggle, 
  isDark, 
  onNewPrompt, 
  onMenuToggle,
  onSearch,
  currentView 
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    onSearch(query);
  };

  const getViewTitle = () => {
    switch (currentView) {
      case 'dashboard': return 'Dashboard';
      case 'studio': return 'Prompt Studio';
      case 'lab': return 'Prompt Lab';
      case 'assistant': return 'AI Assistant';
      case 'image': return 'Image Studio';
      case 'inspiration': return 'Inspiration Hub';
      case 'settings': return 'Settings';
      default: return 'Prompt Studio';
    }
  };

  return (
    <header className="header">
      <div className="flex items-center space-x-4">
        {/* Mobile Menu Toggle */}
        <button
          onClick={onMenuToggle}
          className="md:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          <Menu size={20} />
        </button>

        {/* Logo and Title */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-br from-primary-500 to-purple-600 rounded-lg">
            <Zap size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              Prompt Studio
            </h1>
            <p className="text-xs text-gray-500 dark:text-gray-400 hidden sm:block">
              {getViewTitle()}
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center space-x-3">
        {/* Search */}
        <div className="relative hidden sm:block">
          <Search className="search-icon" size={16} />
          <input
            type="text"
            placeholder="Search prompts..."
            value={searchQuery}
            onChange={handleSearchChange}
            className="search-input w-64"
          />
        </div>

        {/* Quick Actions */}
        <div className="flex items-center space-x-2">
          {/* New Prompt Button */}
          <button
            onClick={onNewPrompt}
            className="btn btn-primary btn-sm hidden sm:flex"
          >
            <Plus size={16} />
            <span className="ml-2">New Prompt</span>
          </button>

          {/* Mobile New Prompt Button */}
          <button
            onClick={onNewPrompt}
            className="btn btn-primary btn-sm sm:hidden"
          >
            <Plus size={16} />
          </button>

          {/* Theme Toggle */}
          <button
            onClick={onThemeToggle}
            className="btn btn-ghost btn-sm"
            title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDark ? <Sun size={16} /> : <Moon size={16} />}
          </button>

          {/* Settings (Mobile) */}
          <button
            className="btn btn-ghost btn-sm md:hidden"
            title="Settings"
          >
            <Settings size={16} />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;