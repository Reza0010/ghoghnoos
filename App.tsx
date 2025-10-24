import React from 'react';
import useLocalStorage from './hooks/useLocalStorage';
import PromptStudio from './components/PromptStudio';
import { ToastProvider } from './components/ToastProvider';

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
    <div className={`theme-${theme}`}>
      <ToastProvider>
        <PromptStudio theme={theme} toggleTheme={toggleTheme} />
      </ToastProvider>
    </div>
  );
}

export default App;
