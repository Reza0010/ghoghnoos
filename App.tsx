import React, { useState, useEffect } from 'react';
import { Prompt, UserSettings, AppState } from './types';
import { PromptForm } from './components/PromptForm';
import { PromptList } from './components/PromptList';
import Dashboard from './components/Dashboard';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import { ExperimentRunner } from './components/ExperimentRunner';
import { AIAssistant } from './components/AIAssistant';
import { InspirationHub } from './components/InspirationHub';
import { Settings } from './components/Settings';
import { ImageRemixStudio } from './components/ImageRemixStudio';
import { PromptStudio } from './components/PromptStudio';
import { PromptLab } from './components/PromptLab';
import { ToastProvider, useToast } from './components/ToastProvider';
import { useLocalStorage } from './hooks/useLocalStorage';
import { DEFAULT_SETTINGS, STORAGE_KEYS } from './constants';
import './index.css';

function AppContent() {
  // State management
  const [prompts, setPrompts] = useLocalStorage<Prompt[]>(STORAGE_KEYS.prompts, []);
  const [settings, setSettings] = useLocalStorage<UserSettings>(STORAGE_KEYS.settings, DEFAULT_SETTINGS);
  const [currentView, setCurrentView] = useState<AppState['currentView']>('dashboard');
  const [searchQuery, setSearchQuery] = useState('');
  const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const { success, error } = useToast();

  // Theme management
  useEffect(() => {
    const applyTheme = () => {
      const isDark = settings.theme === 'dark' || 
        (settings.theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
      
      document.documentElement.classList.toggle('dark', isDark);
    };

    applyTheme();

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => {
      if (settings.theme === 'system') {
        applyTheme();
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [settings.theme]);

  // Auto-save functionality
  useEffect(() => {
    if (settings.autoSave) {
      const interval = setInterval(() => {
        // Auto-save logic could go here
      }, 30000); // 30 seconds

      return () => clearInterval(interval);
    }
  }, [settings.autoSave]);

  // Handlers
  const handleThemeToggle = () => {
    const themes = ['light', 'dark', 'system'] as const;
    const currentIndex = themes.indexOf(settings.theme);
    const nextTheme = themes[(currentIndex + 1) % themes.length];
    
    setSettings({
      ...settings,
      theme: nextTheme
    });
  };

  const handleNewPrompt = () => {
    setEditingPrompt(null);
    setCurrentView('studio');
  };

  const handleEditPrompt = (prompt: Prompt) => {
    setEditingPrompt(prompt);
    setCurrentView('studio');
  };

  const handleSavePrompt = async (promptData: Omit<Prompt, 'id' | 'createdAt' | 'updatedAt'>) => {
    setIsLoading(true);
    
    try {
      if (editingPrompt) {
        // Update existing prompt
        setPrompts(prev => prev.map(p => 
          p.id === editingPrompt.id 
            ? { 
                ...p, 
                ...promptData, 
                updatedAt: new Date(),
                usageCount: p.usageCount // Preserve usage count
              }
            : p
        ));
        success('Prompt updated successfully!');
      } else {
        // Create new prompt
        const newPrompt: Prompt = {
          ...promptData,
          id: crypto.randomUUID(),
          createdAt: new Date(),
          updatedAt: new Date(),
          usageCount: 0,
          isFavorite: false,
        };
        setPrompts(prev => [...prev, newPrompt]);
        success('Prompt created successfully!');
      }
      
      setCurrentView('dashboard');
      setEditingPrompt(null);
    } catch (err) {
      error('Failed to save prompt', 'Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeletePrompt = async (id: string) => {
    try {
      setPrompts(prev => prev.filter(p => p.id !== id));
      success('Prompt deleted successfully!');
    } catch (err) {
      error('Failed to delete prompt', 'Please try again.');
    }
  };

  const handleToggleFavorite = (id: string) => {
    setPrompts(prev => prev.map(p => 
      p.id === id ? { ...p, isFavorite: !p.isFavorite } : p
    ));
  };

  const handleUsePrompt = (prompt: Prompt) => {
    // Increment usage count
    setPrompts(prev => prev.map(p => 
      p.id === prompt.id 
        ? { ...p, usageCount: p.usageCount + 1, lastUsed: new Date() }
        : p
    ));
    
    // Navigate to appropriate view based on prompt type
    if (prompt.type === 'image') {
      setCurrentView('image');
    } else {
      setCurrentView('lab');
    }
    
    // You could also pre-fill the prompt in the target view
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  const handleMenuToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleSidebarClose = () => {
    setSidebarOpen(false);
  };

  const handleViewChange = (view: AppState['currentView']) => {
    setCurrentView(view);
  };

  const handleImportData = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target?.result as string);
        if (data.prompts && Array.isArray(data.prompts)) {
          setPrompts(prev => [...prev, ...data.prompts]);
          success('Data imported successfully!', `Imported ${data.prompts.length} prompts`);
        }
      } catch (err) {
        error('Failed to import data', 'Please check the file format.');
      }
    };
    reader.readAsText(file);
  };

  const handleExportData = () => {
    try {
      const exportData = {
        prompts,
        settings,
        version: '1.0.0',
        exportDate: new Date().toISOString()
      };
      
      const dataStr = JSON.stringify(exportData, null, 2);
      const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
      
      const exportFileDefaultName = `prompt-studio-export-${new Date().toISOString().split('T')[0]}.json`;
      
      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
      
      success('Data exported successfully!');
    } catch (err) {
      error('Failed to export data', 'Please try again.');
    }
  };

  // Filter prompts based on search query
  const filteredPrompts = prompts.filter(prompt =>
    prompt.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    prompt.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
    prompt.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    prompt.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase())) ||
    prompt.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Render current view
  const renderContent = () => {
    const commonProps = {
      prompts: filteredPrompts,
      onEditPrompt: handleEditPrompt,
      onDeletePrompt: handleDeletePrompt,
      onToggleFavorite: handleToggleFavorite,
      onUsePrompt: handleUsePrompt,
    };

    switch (currentView) {
      case 'dashboard':
        return <Dashboard {...commonProps} />;
      
      case 'studio':
        return (
          <PromptStudio
            prompt={editingPrompt}
            onSave={handleSavePrompt}
            onCancel={() => setCurrentView('dashboard')}
            isLoading={isLoading}
          />
        );
      
      case 'lab':
        return <PromptLab prompts={prompts} />;
      
      case 'assistant':
        return <AIAssistant />;
      
      case 'image':
        return <ImageRemixStudio />;
      
      case 'inspiration':
        return (
          <InspirationHub 
            onUsePrompt={(template) => {
              // Convert template to prompt format and save
              const promptData = {
                title: template.name,
                content: template.template,
                description: template.description,
                type: 'text' as const,
                tags: template.tags,
                category: template.category,
              };
              handleSavePrompt(promptData);
            }}
          />
        );
      
      case 'settings':
        return (
          <Settings
            settings={settings}
            onSettingsChange={setSettings}
            onImport={handleImportData}
            onExport={handleExportData}
          />
        );
      
      default:
        return <Dashboard {...commonProps} />;
    }
  };

  const isDark = settings.theme === 'dark' || 
    (settings.theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
      <div className="flex h-screen">
        <Sidebar
          activeView={currentView}
          onViewChange={handleViewChange}
          isOpen={sidebarOpen}
          onClose={handleSidebarClose}
        />
        
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header
            onThemeToggle={handleThemeToggle}
            isDark={isDark}
            onNewPrompt={handleNewPrompt}
            onMenuToggle={handleMenuToggle}
            onSearch={handleSearch}
            currentView={currentView}
          />
          
          <main className="flex-1 overflow-auto">
            {renderContent()}
          </main>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <ToastProvider>
      <AppContent />
    </ToastProvider>
  );
}

export default App;