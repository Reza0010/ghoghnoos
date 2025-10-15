
import React from 'react';
import { Sun, Moon, Plus, Search } from './icons';

interface HeaderProps {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  onAddPrompt: () => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
}

const Header: React.FC<HeaderProps> = ({ theme, toggleTheme, onAddPrompt, searchQuery, setSearchQuery }) => {
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
        <button
          onClick={onAddPrompt}
          className="flex items-center gap-2 bg-dark-primary text-white font-semibold px-4 py-2 rounded-full hover:bg-opacity-90 transition-all duration-200 shadow-lg shadow-dark-primary/30"
        >
          <Plus className="w-5 h-5" />
          افزودن پرامپت
        </button>
      </div>
    </header>
  );
};

export default Header;
