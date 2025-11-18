import React, { useState } from 'react';
import { Prompt } from '../types';
import { X, WandSparkles, Sparkles, Download } from './icons';
import { editImage } from '../services/geminiService';
import { useTranslation } from '../contexts/LanguageContext';

interface ImageRemixStudioProps {
  isOpen: boolean;
  onClose: () => void;
  prompt: Prompt | null;
  onSave: (newPrompt: Prompt) => void;
}

const ImageRemixStudio: React.FC<ImageRemixStudioProps> = ({ isOpen, onClose, prompt, onSave }) => {
  const [instruction, setInstruction] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [remixedImageUrl, setRemixedImageUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { t } = useTranslation();

  if (!isOpen || !prompt || !prompt.imageUrl) return null;

  const handleRemix = async () => {
    if (!instruction || !prompt.imageUrl) return;
    setIsLoading(true);
    setRemixedImageUrl(null);
    setError(null);
    try {
      const result = await editImage(prompt.imageUrl, instruction);
      if (result) {
        setRemixedImageUrl(result);
      } else {
        setError(t('imageRemix.editFailedError'));
      }
    } catch (err) {
      setError(t('imageRemix.unexpectedError'));
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveAsNew = () => {
    if (!remixedImageUrl) return;
    const now = new Date().toISOString();
    const newPrompt: Prompt = {
      ...prompt,
      id: new Date().getTime().toString(),
      title: `${prompt.title} (${t('imageRemix.remixSuffix')})`,
      content: `${prompt.content}\n\n---\n${t('imageRemix.remixInstructionPrefix')}: ${instruction}`,
      imageUrl: remixedImageUrl,
      createdAt: now,
      updatedAt: now,
    };
    onSave(newPrompt);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-lg flex items-center justify-center p-4 z-50" onClick={onClose}>
      <div className="animate-fade-in bg-white dark:bg-dark-surface rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="flex justify-between items-center p-5 border-b border-gray-200 dark:border-dark-overlay">
          <div className="flex items-center gap-3">
            <WandSparkles className="w-7 h-7 text-dark-secondary" />
            <h2 className="text-2xl font-bold text-gray-800 dark:text-dark-text">{t('imageRemix.title')}</h2>
          </div>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-overlay">
            <X className="w-6 h-6 text-gray-500 dark:text-dark-subtext" />
          </button>
        </div>

        <div className="flex-grow overflow-y-auto p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex flex-col items-center">
            <h3 className="text-lg font-semibold mb-3">{t('imageRemix.originalImage')}</h3>
            <div className="w-full aspect-square bg-gray-200 dark:bg-dark-bg rounded-lg shadow-md flex items-center justify-center">
                <img src={prompt.imageUrl} alt="Original" className="rounded-lg w-full h-full object-contain" />
            </div>
          </div>
          <div className="flex flex-col items-center">
            <h3 className="text-lg font-semibold mb-3">{t('imageRemix.remixResult')}</h3>
            <div className="w-full aspect-square bg-gray-100 dark:bg-dark-bg rounded-lg shadow-md flex items-center justify-center">
              {isLoading ? (
                <div className="flex flex-col items-center text-dark-primary">
                  <Sparkles className="w-12 h-12 animate-spin" />
                  <p className="mt-4">{t('imageRemix.loadingMessage')}</p>
                </div>
              ) : remixedImageUrl ? (
                <img src={remixedImageUrl} alt="Remixed" className="rounded-lg w-full h-full object-contain" />
              ) : (
                <p className="text-gray-400 dark:text-dark-overlay">{t('imageRemix.resultPlaceholder')}</p>
              )}
            </div>
          </div>
        </div>
        
        {error && <p className="text-center text-sm text-dark-danger px-6 pb-4">{error}</p>}

        <div className="p-5 border-t border-gray-200 dark:border-dark-overlay bg-gray-50 dark:bg-dark-surface/50 space-y-4">
            <div>
                <label htmlFor="instruction" className="block text-sm font-medium text-gray-700 dark:text-dark-subtext mb-1">{t('imageRemix.instructionLabel')}:</label>
                <div className="flex gap-3">
                    <input 
                        type="text" 
                        id="instruction" 
                        value={instruction}
                        onChange={(e) => setInstruction(e.target.value)}
                        placeholder={t('imageRemix.instructionPlaceholder')}
                        className="w-full bg-white dark:bg-dark-bg rounded-lg border-gray-300 dark:border-dark-overlay focus:border-dark-secondary focus:ring-dark-secondary"
                        disabled={isLoading}
                    />
                    <button 
                        onClick={handleRemix} 
                        disabled={isLoading || !instruction}
                        className="flex items-center justify-center gap-2 px-6 py-2 text-sm font-semibold text-white bg-dark-secondary rounded-lg hover:bg-opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-dark-secondary/30"
                    >
                       <WandSparkles className={`w-5 h-5 ${isLoading ? 'animate-pulse' : ''}`} />
                       {isLoading ? '...' : t('buttons.remix')}
                    </button>
                </div>
            </div>
            {remixedImageUrl && !isLoading && (
                 <div className="flex justify-end gap-3 animate-fade-in">
                    <button onClick={onClose} className="px-6 py-2 rounded-full text-gray-700 dark:text-dark-subtext bg-gray-200 dark:bg-dark-overlay hover:opacity-90 transition">{t('buttons.close')}</button>
                    <button 
                        onClick={handleSaveAsNew} 
                        className="flex items-center gap-2 px-6 py-2 rounded-full text-white bg-dark-accent hover:opacity-90 font-semibold transition shadow-lg shadow-dark-accent/30"
                    >
                       <Download className="w-5 h-5" />
                       {t('buttons.saveAsNew')}
                    </button>
                </div>
            )}
        </div>
      </div>
    </div>
  );
};

export default ImageRemixStudio;