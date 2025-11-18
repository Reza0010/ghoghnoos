import React from 'react';
import useLocalStorage from './hooks/useLocalStorage';
import PromptStudio from './components/PromptStudio';
import { LanguageProvider, useTranslation } from './contexts/LanguageContext';

const LanguageEffects = () => {
  const { language } = useTranslation();

  React.useEffect(() => {
    const root = window.document.documentElement;
    root.lang = language;
    root.dir = language === 'fa' ? 'rtl' : 'ltr';
    
    const body = window.document.body;
    if (language === 'fa') {
        body.classList.add('font-fa');
        body.classList.remove('font-en');
    } else {
        body.classList.add('font-en');
        body.classList.remove('font-fa');
    }
  }, [language]);

  return null;
};

function App() {
  const [theme, setTheme] = useLocalStorage<'light' | 'dark'>('theme', 'dark');

  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'dark' ? 'light' : 'dark'));
  };

  React.useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove(theme === 'dark' ? 'light' : 'dark');
    root.classList.add(theme);
  }, [theme]);

  return (
    <LanguageProvider>
      <LanguageEffects />
      <div className={`theme-${theme}`}>
        <PromptStudio theme={theme} toggleTheme={toggleTheme} />
      </div>
    </LanguageProvider>
  );
}

export default App;