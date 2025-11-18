import React from 'react';
import { getNavStructure } from '../constants';
import { useTranslation } from '../contexts/LanguageContext';

interface SidebarProps {
  activeView: string;
  setActiveView: (view: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeView, setActiveView }) => {
  const { t } = useTranslation();
  const NAV_STRUCTURE = getNavStructure(t);

  return (
    <aside className="w-64 bg-gray-50 dark:bg-dark-surface text-gray-800 dark:text-dark-text flex flex-col h-screen p-4 rtl:border-l ltr:border-r border-gray-200 dark:border-dark-overlay">
      <div className="text-2xl font-bold text-dark-primary mb-10 text-center">
        <span role="img" aria-label="crystal ball" className="mr-2">🔮</span>
        {t('sidebar.title')}
      </div>
      <nav className="flex-grow overflow-y-auto">
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
                    className={`w-full flex items-center p-3 rounded-lg transition-all duration-200 rtl:text-right ltr:text-left ${
                      activeView === item.id
                        ? 'bg-dark-primary/20 text-dark-primary font-semibold'
                        : 'hover:bg-dark-primary/10'
                    }`}
                  >
                    <item.icon className="w-5 h-5 rtl:ml-3 ltr:mr-3" />
                    {item.label}
                  </button>
                </li>
              ))}
            </React.Fragment>
          ))}
        </ul>
      </nav>
      <div className="text-center text-xs text-gray-500 dark:text-dark-subtext/50">
        {t('sidebar.version')} 1.0.0
      </div>
    </aside>
  );
};

export default Sidebar;