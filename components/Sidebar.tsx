
import React from 'react';
import { NAV_STRUCTURE } from '../constants';

interface SidebarProps {
  activeView: string;
  setActiveView: (view: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeView, setActiveView }) => {
  return (
    <aside className="w-64 bg-gray-50 dark:bg-dark-surface text-gray-800 dark:text-dark-text flex flex-col h-screen p-4 border-l border-gray-200 dark:border-dark-overlay" dir="rtl">
      <div className="text-2xl font-bold text-dark-primary mb-10 text-center">
        <span role="img" aria-label="crystal ball" className="mr-2">🔮</span>
        استودیو پرامپت
      </div>
      <nav className="flex-grow">
        <ul>
          {NAV_STRUCTURE.map((section, sectionIndex) => (
            <React.Fragment key={section.title}>
              {sectionIndex > 0 && <hr className="my-3 border-gray-200 dark:border-dark-overlay/50" />}
              <li className="px-3 pt-2 pb-1 text-xs font-bold text-gray-400 dark:text-dark-subtext/60 uppercase tracking-wider">
                {section.title}
              </li>
              {section.items.map((item) => (
                <li key={item.id} className="mb-1">
                  <button
                    onClick={() => setActiveView(item.id)}
                    className={`w-full flex items-center p-3 rounded-lg transition-all duration-200 text-right ${
                      activeView === item.id
                        ? 'bg-dark-primary/20 text-dark-primary font-semibold'
                        : 'hover:bg-dark-primary/10'
                    }`}
                  >
                    <item.icon className="w-5 h-5 ml-3" />
                    {item.label}
                  </button>
                </li>
              ))}
            </React.Fragment>
          ))}
        </ul>
      </nav>
      <div className="text-center text-xs text-gray-500 dark:text-dark-subtext/50">
        نسخه 1.0.0
      </div>
    </aside>
  );
};

export default Sidebar;
