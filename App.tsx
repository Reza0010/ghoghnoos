import React from 'react';
import useLocalStorage from './hooks/useLocalStorage';
import PromptStudio from './components/PromptStudio';
import Settings from './components/Settings';

function App() {
  const [theme, setTheme] = useLocalStorage<'light' | 'dark'>('theme', 'dark');
  const [view, setView] = React.useState<'main' | 'settings'>('main');

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
      <nav>
        <button onClick={() => setView('main')}>Main</button>
        <button onClick={() => setView('settings')}>Settings</button>
      </nav>
      {view === 'main' ? (
        <PromptStudio theme={theme} toggleTheme={toggleTheme} />
      ) : (
        <Settings />
      )}
    </div>
  );
}

export default App;
