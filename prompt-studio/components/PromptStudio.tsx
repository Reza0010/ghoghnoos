import React, { useState, useMemo, useCallback } from 'react';
import useLocalStorage from '../hooks/useLocalStorage';
import { Prompt, PromptType, PromptVariation, PromptVersion, ImportMode } from '../types';
import Sidebar from './Sidebar';
import Header from './Header';
import PromptList from './PromptList';
import Dashboard from './Dashboard';
import AIAssistant from './AIAssistant';
import PromptForm from './PromptForm';
import PromptHistoryModal from './PromptHistoryModal';
import ImageRemixStudio from './ImageRemixStudio';
import InspirationHub from './InspirationHub';
import PromptLab from './PromptLab';
import FaceFusion from './FaceFusion';
import VideoStudio from './VideoStudio';
import TextStudio from './TextStudio';
import MusicStudio from './MusicStudio';
import PromptChainStudio from './PromptChainStudio';
import CreativeStudiosHub from './CreativeStudiosHub';
import ImportModal from './ImportModal';
import ExportModal from './ExportModal';
import BulkActionBar from './BulkActionBar';
import { getNavStructure } from '../constants';
import { useTranslation } from '../contexts/LanguageContext';
import { getSemanticSearchFilters } from '../services/geminiService';

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
        history: [],
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
        history: [],
    }
];

interface PromptStudioProps {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const PromptStudio: React.FC<PromptStudioProps> = ({ theme, toggleTheme }) => {
  const { t } = useTranslation();
  const NAV_STRUCTURE = getNavStructure(t);

  const [prompts, setPrompts] = useLocalStorage<Prompt[]>('prompts', initialPrompts);
  const [activeView, setActiveView] = useState(NAV_STRUCTURE[0].items[0].id);
  
  // Search and Filter State
  const [searchQuery, setSearchQuery] = useState('');
  const [searchIn, setSearchIn] = useState({ title: true, content: true, tags: true });
  const [isAiSearching, setIsAiSearching] = useState(false);
  const [sortOption, setSortOption] = useState('updatedAt-desc');
  const [ratingFilter, setRatingFilter] = useState(0);

  // Modal/Form State
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null);
  const [initialPromptType, setInitialPromptType] = useState<PromptType>(PromptType.Text);
  
  const [isRemixOpen, setIsRemixOpen] = useState(false);
  const [remixingPrompt, setRemixingPrompt] = useState<Prompt | null>(null);

  const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false);
  const [historyPrompt, setHistoryPrompt] = useState<Prompt | null>(null);

  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  
  // Bulk Action State
  const [isSelectionMode, setIsSelectionMode] = useState(false);
  const [selectedPrompts, setSelectedPrompts] = useState<string[]>([]);

  const handleAddPrompt = useCallback((type: PromptType) => {
    setEditingPrompt(null);
    setInitialPromptType(type);
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
    if (window.confirm(t('fileHandlers.deleteConfirm'))) {
      setPrompts(prevPrompts => prevPrompts.filter(p => p.id !== id));
    }
  }, [setPrompts, t]);

  const handleSavePrompt = useCallback((promptToSave: Prompt) => {
    setPrompts(prevPrompts => {
        const existingPrompt = prevPrompts.find(p => p.id === promptToSave.id);
        if (existingPrompt) {
            if (existingPrompt.content !== promptToSave.content) {
                const newVersion: PromptVersion = {
                    content: existingPrompt.content,
                    summary: existingPrompt.summary,
                    createdAt: existingPrompt.updatedAt,
                };
                promptToSave.history = [newVersion, ...(existingPrompt.history || [])];
            } else {
                promptToSave.history = existingPrompt.history || [];
            }
            return prevPrompts.map(p => (p.id === promptToSave.id ? promptToSave : p));
        } else {
            promptToSave.history = [];
            return [promptToSave, ...prevPrompts];
        }
    });
    setIsFormOpen(false);
  }, [setPrompts]);

  const handleViewHistory = useCallback((prompt: Prompt) => {
    setHistoryPrompt(prompt);
    setIsHistoryModalOpen(true);
  }, []);

  const handleRestoreVersion = useCallback((promptId: string, version: PromptVersion) => {
      setPrompts(prev => prev.map(p => {
          if (p.id === promptId) {
              const currentVersion: PromptVersion = {
                  content: p.content,
                  summary: p.summary,
                  createdAt: p.updatedAt,
              };
              return {
                  ...p,
                  content: version.content,
                  summary: version.summary,
                  updatedAt: new Date().toISOString(),
                  history: [currentVersion, ...(p.history || [])],
              };
          }
          return p;
      }));
      setIsHistoryModalOpen(false);
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
        history: [],
    };
    handleSavePrompt(newPrompt);
    alert('پرامپت برنده با موفقیت ذخیره شد!');
    setActiveView('image');
  }, [handleSavePrompt, setActiveView]);

  const handleAiSearch = async () => {
      if (!searchQuery.trim()) return;
      setIsAiSearching(true);
      alert(t('search.aiSearchLoading'));
      try {
          const filters = await getSemanticSearchFilters(searchQuery);
          setSearchQuery(prev => filters.keywords || prev); // Use keywords from AI
          if (filters.tags && filters.tags.length > 0) {
              const tagQuery = filters.tags.join(' ');
              setSearchQuery(prev => `${tagQuery} ${filters.keywords || ''}`.trim());
          }
          setRatingFilter(filters.ratingFilter);
          setSortOption(filters.sortOption);
      } catch (error) {
          console.error("AI Search failed:", error);
          alert(t('search.aiSearchError'));
      } finally {
          setIsAiSearching(false);
      }
  };
  
  const handleExport = useCallback((promptsToExport: Prompt[]) => {
    const dataStr = JSON.stringify(promptsToExport, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = 'prompt_studio_export.json';
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    setIsExportModalOpen(false);
  }, []);
  
  const handleImport = useCallback((importedPrompts: Prompt[], mode: ImportMode) => {
    if (mode === 'replace') {
      setPrompts(importedPrompts);
    } else { // 'merge'
      setPrompts(prev => {
        const existingIds = new Set(prev.map(p => p.id));
        const newPrompts = importedPrompts.filter(p => !existingIds.has(p.id));
        // A more advanced merge could update existing prompts, but for now we only add new ones.
        return [...prev, ...newPrompts];
      });
    }
    setIsImportModalOpen(false);
    setActiveView('dashboard');
    alert(t('fileHandlers.importSuccess'));
  }, [setPrompts, t]);
  
  // --- Bulk Action Handlers ---
  const toggleSelectionMode = useCallback(() => {
    setIsSelectionMode(prev => !prev);
    setSelectedPrompts([]);
  }, []);

  const handleSelectPrompt = useCallback((id: string) => {
    setSelectedPrompts(prev =>
      prev.includes(id) ? prev.filter(pId => pId !== id) : [...prev, id]
    );
  }, []);
  
  const handleBulkDelete = useCallback(() => {
    if (window.confirm(t('bulkActions.deleteConfirm', { count: selectedPrompts.length }))) {
      setPrompts(prev => prev.filter(p => !selectedPrompts.includes(p.id)));
      toggleSelectionMode();
    }
  }, [selectedPrompts.length, setPrompts, t, toggleSelectionMode]);
  
  const handleBulkAddTags = useCallback(() => {
    const tagsToAdd = window.prompt(t('bulkActions.enterTags'));
    if (tagsToAdd) {
      const newTags = tagsToAdd.split(',').map(tag => tag.trim()).filter(Boolean);
      setPrompts(prev => prev.map(p => 
        selectedPrompts.includes(p.id) 
          ? { ...p, tags: [...new Set([...(p.tags || []), ...newTags])] } 
          : p
      ));
      toggleSelectionMode();
    }
  }, [selectedPrompts, setPrompts, t, toggleSelectionMode]);
  
  const handleBulkChangeRating = useCallback(() => {
    const newRatingStr = window.prompt(t('bulkActions.enterRating'));
    if (newRatingStr) {
      const newRating = parseInt(newRatingStr, 10);
      if (!isNaN(newRating) && newRating >= 0 && newRating <= 5) {
        setPrompts(prev => prev.map(p =>
          selectedPrompts.includes(p.id) ? { ...p, rating: newRating } : p
        ));
        toggleSelectionMode();
      } else {
        alert(t('bulkActions.invalidRating'));
      }
    }
  }, [selectedPrompts, setPrompts, t, toggleSelectionMode]);

  const handleBulkExport = useCallback(() => {
    const promptsToExport = prompts.filter(p => selectedPrompts.includes(p.id));
    handleExport(promptsToExport);
    toggleSelectionMode();
  }, [prompts, selectedPrompts, handleExport, toggleSelectionMode]);

  const filteredPrompts = useMemo(() => {
    const lowerCaseQuery = searchQuery.toLowerCase();
    const queryParts = lowerCaseQuery.split(' ').filter(p => p.length > 0);

    return [...prompts]
      .filter(prompt => {
        // 1. Filter by view
        if (activeView === 'all' || activeView === 'dashboard') return true;
        return prompt.type === activeView;
      })
      .filter(prompt => {
        // 2. Filter by advanced search query
        if (!searchQuery) return true;
        
        const searchableText = [];
        if (searchIn.title) searchableText.push(prompt.title.toLowerCase());
        if (searchIn.content) searchableText.push(prompt.content.toLowerCase());
        if (searchIn.tags) searchableText.push(...(prompt.tags || []).map(t => t.toLowerCase()));

        const combinedText = searchableText.join(' ');
        return queryParts.every(part => combinedText.includes(part));
      })
      .filter(prompt => { 
        // 3. Filter by rating
        if (ratingFilter === 0) return true;
        if (ratingFilter === -1) return !prompt.rating || prompt.rating === 0;
        return prompt.rating && prompt.rating >= ratingFilter;
      })
      .sort((a, b) => { // 4. Sort
        switch (sortOption) {
            case 'updatedAt-asc':
                return new Date(a.updatedAt).getTime() - new Date(b.updatedAt).getTime();
            case 'title-asc':
                return a.title.localeCompare(b.title);
            case 'title-desc':
                return b.title.localeCompare(a.title);
            case 'rating-desc':
                return (b.rating || 0) - (a.rating || 0);
            case 'rating-asc':
                return (a.rating || 0) - (b.rating || 0);
            case 'updatedAt-desc':
            default:
                return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
        }
    });
  }, [prompts, activeView, searchQuery, ratingFilter, sortOption, searchIn]);
  
  const renderContent = useCallback(() => {
    switch (activeView) {
      case 'dashboard':
        return <Dashboard prompts={prompts} onImport={() => setIsImportModalOpen(true)} onExport={() => setIsExportModalOpen(true)} setActiveView={setActiveView} setSearchQuery={setSearchQuery} />;
      case 'creative-studios':
        return <CreativeStudiosHub setActiveView={setActiveView} />;
      case 'assistant':
        return <AIAssistant />;
      case 'inspiration':
        return <InspirationHub prompts={prompts} onUsePrompt={handleSavePrompt} />;
      case 'prompt-lab':
        return <PromptLab onSaveWinner={handleSavePromptFromLab} />;
      case 'face-fusion':
        return <FaceFusion onSave={handleSavePrompt} />;
      case 'video-studio':
        return <VideoStudio onSave={handleSavePrompt} />;
      case 'text-studio':
        return <TextStudio onSave={handleSavePrompt} />;
      case 'music-studio':
        return <MusicStudio onSave={handleSavePrompt} />;
      case 'prompt-chains':
        return <PromptChainStudio />;
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
            onViewHistory={handleViewHistory}
            sortOption={sortOption}
            setSortOption={setSortOption}
            ratingFilter={ratingFilter}
            setRatingFilter={setRatingFilter}
            searchQuery={searchQuery}
            isSelectionMode={isSelectionMode}
            toggleSelectionMode={toggleSelectionMode}
            selectedCount={selectedPrompts.length}
            onSelectPrompt={handleSelectPrompt}
            isSelected={(id) => selectedPrompts.includes(id)}
          />
        );
      default:
        return null;
    }
  }, [activeView, prompts, filteredPrompts, handleSavePromptFromLab, handleEditPrompt, handleDeletePrompt, handleRemixPrompt, handleViewHistory, handleSavePrompt, setActiveView, sortOption, ratingFilter, searchQuery, setSearchQuery, isSelectionMode, toggleSelectionMode, selectedPrompts.length, handleSelectPrompt]);

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-dark-bg text-gray-900 dark:text-dark-text overflow-hidden">
      <main className="flex-1 flex flex-col overflow-hidden">
        <Header 
          theme={theme}
          toggleTheme={toggleTheme}
          onAddPrompt={handleAddPrompt}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          onAiSearch={handleAiSearch}
          isAiSearching={isAiSearching}
          searchIn={searchIn}
          setSearchIn={setSearchIn}
        />
        <div className="flex-1 overflow-y-auto">
          {renderContent()}
        </div>
      </main>
      <Sidebar activeView={activeView} setActiveView={setActiveView} />

      <PromptForm 
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        onSave={handleSavePrompt}
        editingPrompt={editingPrompt}
        initialType={initialPromptType}
      />
      
      {isSelectionMode && selectedPrompts.length > 0 && (
          <BulkActionBar 
              selectedCount={selectedPrompts.length}
              onDelete={handleBulkDelete}
              onAddTags={handleBulkAddTags}
              onChangeRating={handleBulkChangeRating}
              onExport={handleBulkExport}
              onCancel={toggleSelectionMode}
          />
      )}

      {historyPrompt && (
        <PromptHistoryModal
            isOpen={isHistoryModalOpen}
            onClose={() => setIsHistoryModalOpen(false)}
            prompt={historyPrompt}
            onRestore={handleRestoreVersion}
        />
      )}
      
      <ImageRemixStudio
        isOpen={isRemixOpen}
        onClose={() => setIsRemixOpen(false)}
        prompt={remixingPrompt}
        onSave={handleSavePrompt}
      />

      <ImportModal 
        isOpen={isImportModalOpen}
        onClose={() => setIsImportModalOpen(false)}
        onImport={handleImport}
      />

      <ExportModal 
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        prompts={prompts}
        onExport={handleExport}
      />
    </div>
  );
};

export default PromptStudio;