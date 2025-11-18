import React, { useState, useRef } from 'react';
import { Prompt, ImportMode } from '../types';
import { X, FileUp } from './icons';
import { useTranslation } from '../contexts/LanguageContext';

interface ImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onImport: (prompts: Prompt[], mode: ImportMode) => void;
}

const ImportModal: React.FC<ImportModalProps> = ({ isOpen, onClose, onImport }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [importMode, setImportMode] = useState<ImportMode>('merge');
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { t } = useTranslation();

  if (!isOpen) return null;

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      if (file.type === 'application/json') {
        setSelectedFile(file);
        setError(null);
      } else {
        setError('Please select a valid .json file.');
      }
    }
  };

  const handleImportClick = () => {
    if (!selectedFile) return;

    const fileReader = new FileReader();
    fileReader.onload = (e) => {
      try {
        const result = e.target?.result;
        if (typeof result === 'string') {
          const importedPrompts = JSON.parse(result) as Prompt[];
          if (Array.isArray(importedPrompts) && importedPrompts.every(p => p.id && p.title && p.content && p.type)) {
            onImport(importedPrompts, importMode);
          } else {
            throw new Error('Invalid file format');
          }
        }
      } catch (err) {
        setError(t('importModal.invalidFile'));
      }
    };
    fileReader.readAsText(selectedFile);
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-lg flex items-center justify-center p-4 z-50" onClick={onClose}>
      <div className="animate-fade-in bg-white dark:bg-dark-surface rounded-2xl shadow-2xl w-full max-w-lg flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="flex justify-between items-center p-5 border-b border-gray-200 dark:border-dark-overlay">
          <div className="flex items-center gap-3">
            <FileUp className="w-7 h-7 text-dark-primary" />
            <h2 className="text-2xl font-bold text-gray-800 dark:text-dark-text">{t('importModal.title')}</h2>
          </div>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-overlay">
            <X className="w-6 h-6 text-gray-500 dark:text-dark-subtext" />
          </button>
        </div>
        <div className="p-6 space-y-6">
            <p className="text-sm text-gray-600 dark:text-dark-subtext">{t('importModal.description')}</p>
            <div>
                <button onClick={() => fileInputRef.current?.click()} className="w-full text-center p-6 border-2 border-dashed border-gray-300 dark:border-dark-overlay rounded-lg hover:bg-gray-50 dark:hover:bg-dark-overlay/20 transition">
                    <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept=".json" />
                    <p>{selectedFile ? t('importModal.fileSelected', { name: selectedFile.name }) : t('importModal.selectFile')}</p>
                </button>
                {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
            </div>
             <div>
              <h3 className="block text-sm font-medium text-gray-700 dark:text-dark-subtext mb-2">{t('importModal.importMode')}</h3>
              <div className="space-y-3">
                  <label className={`flex items-start p-4 rounded-lg border-2 cursor-pointer ${importMode === 'merge' ? 'border-dark-primary bg-dark-primary/5' : 'border-gray-300 dark:border-dark-overlay'}`}>
                    <input type="radio" name="import-mode" value="merge" checked={importMode === 'merge'} onChange={() => setImportMode('merge')} className="mt-1 h-4 w-4 text-dark-primary focus:ring-dark-primary border-gray-300 dark:border-dark-overlay bg-transparent"/>
                    <div className="rtl:mr-3 ltr:ml-3">
                        <span className="font-semibold">{t('importModal.merge')}</span>
                        <p className="text-xs text-gray-500 dark:text-dark-subtext">{t('importModal.mergeDescription')}</p>
                    </div>
                  </label>
                  <label className={`flex items-start p-4 rounded-lg border-2 cursor-pointer ${importMode === 'replace' ? 'border-dark-danger bg-dark-danger/5' : 'border-gray-300 dark:border-dark-overlay'}`}>
                    <input type="radio" name="import-mode" value="replace" checked={importMode === 'replace'} onChange={() => setImportMode('replace')} className="mt-1 h-4 w-4 text-dark-danger focus:ring-dark-danger border-gray-300 dark:border-dark-overlay bg-transparent"/>
                    <div className="rtl:mr-3 ltr:ml-3">
                        <span className="font-semibold text-dark-danger">{t('importModal.replace')}</span>
                        <p className="text-xs text-gray-500 dark:text-dark-subtext">{t('importModal.replaceDescription')}</p>
                    </div>
                  </label>
              </div>
            </div>
        </div>
        <div className="p-5 border-t border-gray-200 dark:border-dark-overlay bg-gray-50 dark:bg-dark-surface/50 flex justify-end gap-3">
          <button type="button" onClick={onClose} className="px-6 py-2 rounded-full text-gray-700 dark:text-dark-subtext bg-gray-200 dark:bg-dark-overlay hover:opacity-90 transition">{t('buttons.cancel')}</button>
          <button type="button" onClick={handleImportClick} disabled={!selectedFile} className="px-6 py-2 rounded-full text-white bg-dark-primary hover:opacity-90 font-semibold transition shadow-lg shadow-dark-primary/30 disabled:opacity-50 disabled:cursor-not-allowed">{t('buttons.import')}</button>
        </div>
      </div>
    </div>
  );
};

export default ImportModal;
