
import React, { useState, useRef, useEffect } from 'react';
import { Sun, Moon, Plus, Search, ChevronDown } from './icons';
import { PromptType } from '../types';
import { PROMPT_TYPE_CONFIG } from '../constants';

interface HeaderProps {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  onAddPrompt: (type: PromptType) => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
}

const Header: React.FC<HeaderProps> = ({ theme, toggleTheme, onAddPrompt, searchQuery, setSearchQuery }) => {
  const [isAddMenuOpen, setIsAddMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsAddMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [menuRef]);

  const handleAddClick = (type: PromptType) => {
    onAddPrompt(type);
    setIsAddMenuOpen(false);
  };
  
  return (
    <header className="p-4 bg-gray-100/80 dark:bg-dark-bg/80 backdrop-blur-sm border-b border-gray-200 dark:border-dark-overlay flex items-center justify-between" dir="rtl">
      <div className="relative flex-grow max-w-lg">
        <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-dark-subtext" />
        <input
          type="text"
          placeholder="جستجو در پرامپت‌ها..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full bg-gray-200 dark:bg-dark-surface border-transparent focus:border-dark-primary focus:ring-0 rounded-full py-2 pr-10 pl-4 transition"
        />
      </div>
      <div className="flex items-center gap-4">
        <button
          onClick={toggleTheme}
          className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-surface transition-colors"
        >
          {theme === 'dark' ? <Sun className="w-6 h-6 text-dark-warn" /> : <Moon className="w-6 h-6 text-dark-secondary" />}
        </button>
         <div className="relative" ref={menuRef}>
          <button
            onClick={() => setIsAddMenuOpen(prev => !prev)}
            className="flex items-center gap-2 bg-dark-primary text-white font-semibold px-4 py-2 rounded-full hover:bg-opacity-90 transition-all duration-200 shadow-lg shadow-dark-primary/30"
          >
            <Plus className="w-5 h-5" />
            ایجاد جدید
            <ChevronDown className={`w-4 h-4 transition-transform ${isAddMenuOpen ? 'rotate-180' : ''}`} />
          </button>
          {isAddMenuOpen && (
            <div className="absolute left-0 mt-2 w-56 origin-top-left bg-white dark:bg-dark-surface rounded-lg shadow-2xl z-20 animate-fade-in p-2">
              <div className="py-1">
                {Object.values(PromptType).map(type => {
                  // FIX: Cast type to PromptType for correct indexing.
                  const config = PROMPT_TYPE_CONFIG[type as PromptType];
                  return (
                    <button
                      key={type}
                      onClick={() => handleAddClick(type)}
                      className="w-full text-right flex items-center gap-3 px-4 py-2 text-sm text-gray-700 dark:text-dark-text hover:bg-gray-100 dark:hover:bg-dark-overlay rounded-md transition-colors"
                    >
                      <config.icon className={`w-5 h-5 ${config.textColor}`} />
                      {config.label}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
