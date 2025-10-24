import React, { useState, useMemo, useCallback } from 'react';
import useLocalStorage from '../hooks/useLocalStorage';
import { Prompt, PromptType, PromptVariation } from '../types';
import Sidebar from './Sidebar';
import Header from './Header';
import PromptList from './PromptList';
import Dashboard from './Dashboard';
import AIAssistant from './AIAssistant';
import PromptForm from './PromptForm';
import ImageRemixStudio from './ImageRemixStudio';
import InspirationHub from './InspirationHub';
import PromptLab from './PromptLab';
import Settings from './Settings';
import { NAV_ITEMS } from '../constants';
import { useToast } from './ToastProvider';
import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

// Sample data for initial load
const initialPrompts: Prompt[] = [
    {
        id: "1",
        title: "ربات آینده‌نگر",
        content: "A photorealistic image of a sleek, humanoid robot standing in a neon-lit futuristic city street at night. Rain is falling, reflecting the city lights on the wet pavement. The robot is looking thoughtfully into the distance. 8K, cinematic lighting, hyper-detailed.",
        type: PromptType.Image,
        tags: ["futuristic", "robot", "neon", "photorealistic"],
        createdAt: "2023-10-26T10:00:00Z",
        updatedAt: "2023-10-26T10:00:00Z",
        summary: "A photorealistic image of a sleek, humanoid robot in a neon-lit futuristic city.",
        rating: 5,
        imageUrl: "https://storage.googleapis.com/maker-me/prompts%2F995a55a4-e1b6-4598-a1a7-f58be318856c",
    },
    {
        id: "2",
        title: "داستان کوتاه علمی-تخیلی",
        content: "Write a short story about a lone astronaut who discovers a mysterious, glowing plant on an unexplored planet. The plant seems to communicate through light patterns. The story should build a sense of wonder and suspense.",
        type: PromptType.Text,
        tags: ["sci-fi", "story", "space", "mystery"],
        createdAt: "2023-10-25T14:30:00Z",
        updatedAt: "2023-10-27T11:00:00Z",
        summary: "A short story about an astronaut discovering a communicating plant on a new planet.",
        rating: 4,
    }
];

interface PromptStudioProps {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const PromptStudio: React.FC<PromptStudioProps> = ({ theme, toggleTheme }) => {
  const [prompts, setPrompts] = useLocalStorage<Prompt[]>('prompts', initialPrompts);
  const [activeView, setActiveView] = useState(NAV_ITEMS[0].id);
  const [searchQuery, setSearchQuery] = useState('');
  const { showToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Sync active view with current path
    const path = (location.pathname || '/').replace(/^\//, '');
    const candidate = path || 'dashboard';
    const exists = NAV_ITEMS.some(n => n.id === candidate);
    setActiveView(exists ? candidate : 'dashboard');
  }, [location.pathname]);

  const handleSetActiveView = useCallback((view: string) => {
    setActiveView(view);
    navigate(`/${view}`);
  }, [navigate]);

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null);
  
  const [isRemixOpen, setIsRemixOpen] = useState(false);
  const [remixingPrompt, setRemixingPrompt] = useState<Prompt | null>(null);

  const handleAddPrompt = useCallback(() => {
    setEditingPrompt(null);
    setIsFormOpen(true);
  }, []);

  const handleEditPrompt = useCallback((prompt: Prompt) => {
    setEditingPrompt(prompt);
    setIsFormOpen(true);
  }, []);
  
  const handleRemixPrompt = useCallback((prompt: Prompt) => {
    setRemixingPrompt(prompt);
    setIsRemixOpen(true);
  }, []);

  const handleDeletePrompt = useCallback((id: string) => {
    if (window.confirm('آیا از حذف این پرامپت مطمئن هستید؟')) {
      setPrompts(prevPrompts => prevPrompts.filter(p => p.id !== id));
    }
  }, [setPrompts]);

  const handleSavePrompt = useCallback((promptToSave: Prompt) => {
    setPrompts(prevPrompts => {
        const exists = prevPrompts.some(p => p.id === promptToSave.id);
        if (exists) {
            return prevPrompts.map(p => (p.id === promptToSave.id ? promptToSave : p));
        } else {
            return [promptToSave, ...prevPrompts];
        }
    });
    setIsFormOpen(false); // Close form after save
    showToast('پرامپت ذخیره شد', { type: 'success' });
  }, [setPrompts]);
  
  const handleSavePromptFromLab = useCallback((title: string, variation: PromptVariation) => {
    const now = new Date().toISOString();
    const newPrompt: Prompt = {
        id: new Date().getTime().toString(),
        title: `${title} (Winner)`,
        content: variation.content,
        imageUrl: variation.outputUrl,
        type: PromptType.Image,
        tags: ['ab-test-winner', 'prompt-lab'],
        createdAt: now,
        updatedAt: now,
        rating: 0,
    };
    handleSavePrompt(newPrompt);
    showToast('پرامپت برنده با موفقیت ذخیره شد', { type: 'success' });
    setActiveView('image'); // Switch view to see the new prompt
  }, [handleSavePrompt]);

  const filteredPrompts = useMemo(() => {
    const nonLabViews = ['all', 'dashboard', 'assistant', 'inspiration', 'prompt-lab'];
    return prompts
      .filter(prompt => {
        if (nonLabViews.includes(activeView)) return true;
        return prompt.type === activeView;
      })
      .filter(prompt =>
        prompt.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        prompt.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
        prompt.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
  }, [prompts, activeView, searchQuery]);
  
  const handleExport = useCallback(() => {
    const dataStr = JSON.stringify(prompts, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = 'prompt_studio_export.json';
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  }, [prompts]);
  
  const handleImport = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
      if (event.target.files && event.target.files[0]) {
          const fileReader = new FileReader();
          fileReader.onload = (e) => {
              try {
                  const result = e.target?.result;
                  if (typeof result === 'string') {
                      const importedPrompts = JSON.parse(result) as Prompt[];
                      // Basic validation
                      if (Array.isArray(importedPrompts) && importedPrompts.every(p => p.id && p.title && p.content)) {
                          setPrompts(importedPrompts);
                          setActiveView('dashboard');
                          showToast('پرامپت‌ها با موفقیت وارد شدند', { type: 'success' });
                      } else {
                          throw new Error('Invalid file format');
                      }
                  }
              } catch (error) {
                  showToast('خطا در ورود فایل. لطفا از فایل JSON معتبر استفاده کنید', { type: 'error' });
              }
          };
          fileReader.readAsText(event.target.files[0]);
      }
  }, [setPrompts]);

  const renderContent = useCallback(() => {
    switch (activeView) {
      case 'dashboard':
        return <Dashboard prompts={prompts} onImport={handleImport} onExport={handleExport} />;
      case 'assistant':
        return <AIAssistant />;
      case 'inspiration':
        return <InspirationHub prompts={prompts} onUsePrompt={handleSavePrompt} />;
      case 'prompt-lab':
        return <PromptLab onSaveWinner={handleSavePromptFromLab} />;
      case 'settings':
        return <Settings prompts={prompts} setPrompts={setPrompts as unknown as (value: unknown[]) => void} />;
      case 'all':
      case 'image':
      case 'text':
      case 'video':
      case 'music':
        return (
          <PromptList
            prompts={filteredPrompts}
            view={activeView}
            onEdit={handleEditPrompt}
            onDelete={handleDeletePrompt}
            onRemix={handleRemixPrompt}
          />
        );
      default:
        return null;
    }
  }, [activeView, prompts, filteredPrompts, handleSavePromptFromLab, handleExport, handleImport, handleEditPrompt, handleDeletePrompt, handleRemixPrompt, handleSavePrompt]);

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-dark-bg text-gray-900 dark:text-dark-text overflow-hidden">
      <main className="flex-1 flex flex-col overflow-hidden">
        <Header 
          theme={theme}
          toggleTheme={toggleTheme}
          onAddPrompt={handleAddPrompt}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
        />
        <div className="flex-1 overflow-y-auto">
          {renderContent()}
        </div>
      </main>
      <Sidebar activeView={activeView} setActiveView={handleSetActiveView} />

      <PromptForm 
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        onSave={handleSavePrompt}
        editingPrompt={editingPrompt}
      />
      
      <ImageRemixStudio
        isOpen={isRemixOpen}
        onClose={() => setIsRemixOpen(false)}
        prompt={remixingPrompt}
        onSave={handleSavePrompt}
      />
    </div>
  );
};

export default PromptStudio;