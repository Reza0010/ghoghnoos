import React from 'react';
import { Home, Box, Wrench, FileText, Sun, Moon } from 'lucide-react';

interface SidebarProps {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ theme, toggleTheme }) => {
  return (
    <aside className="w-20 bg-white dark:bg-gray-800 p-4 flex flex-col items-center justify-between">
      <div>
        <div className="mb-8">
          <a href="#" className="text-blue-500">
            <Home size={28} />
          </a>
        </div>
        <nav className="flex flex-col space-y-6">
          <a href="#" className="hover:text-blue-500">
            <Box size={24} />
          </a>
          <a href="#" className="hover:text-blue-500">
            <Wrench size={24} />
          </a>
          <a href="#" className="hover:text-blue-500">
            <FileText size={24} />
          </a>
        </nav>
      </div>
      <button onClick={toggleTheme} className="p-2 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700">
        {theme === 'dark' ? <Sun size={24} /> : <Moon size={24} />}
      </button>
    </aside>
  );
};

export default Sidebar;
