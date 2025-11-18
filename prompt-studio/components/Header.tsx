import React, { useState, useRef, useEffect } from 'react';
import { Sun, Moon, Plus, Search, ChevronDown, Globe, Filter, Sparkles } from './icons';
import { PromptType } from '../types';
import { getPromptTypeConfig } from '../constants';
import { useTranslation } from '../contexts/LanguageContext';

interface HeaderProps {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  onAddPrompt: (type: PromptType) => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  onAiSearch: () => void;
  isAiSearching: boolean;
  searchIn: { title: boolean, content: boolean, tags: boolean };
  setSearchIn: React.Dispatch<React.SetStateAction<{ title: boolean, content: boolean, tags: boolean }>>;
}

const Header: React.FC<HeaderProps> = ({ 
    theme, toggleTheme, onAddPrompt, searchQuery, setSearchQuery, 
    onAiSearch, isAiSearching, searchIn, setSearchIn 
}) => {
  const [isAddMenuOpen, setIsAddMenuOpen] = useState(false);
  const [isFilterMenuOpen, setIsFilterMenuOpen] = useState(false);
  const addMenuRef = useRef<HTMLDivElement>(null);
  const filterMenuRef = useRef<HTMLDivElement>(null);

  const { language, setLanguage, t } = useTranslation();
  const PROMPT_TYPE_CONFIG = getPromptTypeConfig(t);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (addMenuRef.current && !addMenuRef.current.contains(event.target as Node)) {
        setIsAddMenuOpen(false);
      }
      if (filterMenuRef.current && !filterMenuRef.current.contains(event.target as Node)) {
        setIsFilterMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleAddClick = (type: PromptType) => {
    onAddPrompt(type);
    setIsAddMenuOpen(false);
  };
  
  const toggleLanguage = () => {
    setLanguage(language === 'fa' ? 'en' : 'fa');
  };

  const handleSearchInChange = (field: 'title' | 'content' | 'tags') => {
    setSearchIn(prev => ({ ...prev, [field]: !prev[field] }));
  };

  return (
    <header className="relative z-30 p-4 bg-gray-100/80 dark:bg-dark-bg/80 backdrop-blur-sm border-b border-gray-200 dark:border-dark-overlay flex items-center justify-between">
      <div className="relative flex-grow max-w-2xl flex items-center gap-2">
        {/* Advanced Filter */}
        <div className="relative" ref={filterMenuRef}>
          <button
            onClick={() => setIsFilterMenuOpen(prev => !prev)}
            className="p-3 rounded-full bg-gray-200 dark:bg-dark-surface hover:bg-gray-300 dark:hover:bg-dark-overlay transition-colors"
            title={t('search.searchIn')}
          >
            <Filter className="w-5 h-5 text-gray-500 dark:text-dark-subtext" />
          </button>
          {isFilterMenuOpen && (
            <div className="absolute rtl:right-0 ltr:left-0 top-full mt-2 w-48 bg-white dark:bg-dark-surface rounded-lg shadow-2xl z-20 animate-fade-in p-2">
              <div className="px-2 py-1 text-xs font-bold text-gray-400 dark:text-dark-subtext/60">{t('search.searchIn')}</div>
              {(['title', 'content', 'tags'] as const).map(field => (
                <label key={field} className="flex items-center gap-2 p-2 rounded-md hover:bg-gray-100 dark:hover:bg-dark-overlay cursor-pointer">
                  <input
                    type="checkbox"
                    checked={searchIn[field]}
                    onChange={() => handleSearchInChange(field)}
                    className="h-4 w-4 rounded border-gray-300 dark:border-dark-overlay text-dark-primary focus:ring-dark-primary bg-gray-200 dark:bg-dark-bg"
                  />
                  <span className="text-sm">{t(`search.${field}`)}</span>
                </label>
              ))}
            </div>
          )}
        </div>
        {/* Search Input */}
        <div className="relative flex-grow">
          <Search className="absolute top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-dark-subtext rtl:right-4 ltr:left-4 pointer-events-none" />
          <input
            type="text"
            placeholder={t('header.searchPlaceholder')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-gray-200 dark:bg-dark-surface border-transparent focus:border-dark-primary focus:ring-0 rounded-full py-3 rtl:pr-12 ltr:pl-12 rtl:pl-20 ltr:pr-20 transition"
          />
          <button
            onClick={onAiSearch}
            disabled={isAiSearching || !searchQuery}
            className="absolute top-1/2 -translate-y-1/2 rtl:left-3 ltr:right-3 p-2 rounded-full bg-dark-secondary/20 hover:bg-dark-secondary/30 transition-colors disabled:opacity-50"
            title={t('search.aiSearchTooltip')}
          >
            <Sparkles className={`w-5 h-5 text-dark-secondary ${isAiSearching ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>
      <div className="flex items-center gap-2 sm:gap-4">
        <button
          onClick={toggleLanguage}
          className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-surface transition-colors flex items-center gap-1.5"
          aria-label="Toggle language"
        >
          <Globe className="w-5 h-5 text-dark-primary" />
          <span className="font-semibold text-sm text-gray-700 dark:text-dark-subtext">{language.toUpperCase()}</span>
        </button>
        <button
          onClick={toggleTheme}
          className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-surface transition-colors"
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? <Sun className="w-6 h-6 text-dark-warn" /> : <Moon className="w-6 h-6 text-dark-secondary" />}
        </button>
         <div className="relative" ref={addMenuRef}>
          <button
            onClick={() => setIsAddMenuOpen(prev => !prev)}
            className="flex items-center gap-2 bg-dark-primary text-white font-semibold px-4 py-2 rounded-full hover:bg-opacity-90 transition-all duration-200 shadow-lg shadow-dark-primary/30"
          >
            <Plus className="w-5 h-5" />
            {t('header.createNewLabel')}
            <ChevronDown className={`w-4 h-4 transition-transform ${isAddMenuOpen ? 'rotate-180' : ''}`} />
          </button>
          {isAddMenuOpen && (
            <div className="absolute rtl:left-0 ltr:right-0 mt-2 w-56 rtl:origin-top-left ltr:origin-top-right bg-white dark:bg-dark-surface rounded-lg shadow-2xl z-20 animate-fade-in p-2">
              <div className="py-1">
                {Object.values(PromptType).map(type => {
                  const config = PROMPT_TYPE_CONFIG[type as PromptType];
                  return (
                    <button
                      key={type}
                      onClick={() => handleAddClick(type)}
                      className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 dark:text-dark-text hover:bg-gray-100 dark:hover:bg-dark-overlay rounded-md transition-colors"
                    >
                      <config.icon className={`w-5 h-5 ${config.textColor} flex-shrink-0`} />
                      <span className="flex-grow rtl:text-right ltr:text-left">{config.label}</span>
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