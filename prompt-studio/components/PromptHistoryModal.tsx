import React, { useState } from 'react';
import { Prompt, PromptVersion } from '../types';
import { X, History } from './icons';
import { useTranslation } from '../contexts/LanguageContext';

const timeAgo = (dateString: string, t: (key: string, options?: any) => string) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    let interval = seconds / 31536000;
    if (interval > 1) return t('time.yearsAgo', { count: Math.floor(interval) });
    interval = seconds / 2592000;
    if (interval > 1) return t('time.monthsAgo', { count: Math.floor(interval) });
    interval = seconds / 86400;
    if (interval > 1) return t('time.daysAgo', { count: Math.floor(interval) });
    interval = seconds / 3600;
    if (interval > 1) return t('time.hoursAgo', { count: Math.floor(interval) });
    interval = seconds / 60;
    if (interval > 1) return t('time.minutesAgo', { count: Math.floor(interval) });
    return t('time.justNow');
};

const DiffViewer: React.FC<{ oldText: string; newText: string }> = ({ oldText, newText }) => {
    const oldLines = oldText.split('\n');
    const newLines = newText.split('\n');
    
    const maxLines = Math.max(oldLines.length, newLines.length);
    const diffLines = [];

    for (let i = 0; i < maxLines; i++) {
        const oldLine = oldLines[i];
        const newLine = newLines[i];

        if (oldLine !== undefined && newLine !== undefined) {
            if (oldLine !== newLine) {
                 diffLines.push({ type: 'removed', line: oldLine });
                 diffLines.push({ type: 'added', line: newLine });
            } else {
                 diffLines.push({ type: 'same', line: oldLine });
            }
        } else if (oldLine !== undefined) {
            diffLines.push({ type: 'removed', line: oldLine });
        } else if (newLine !== undefined) {
            diffLines.push({ type: 'added', line: newLine });
        }
    }

    return (
        <pre className="text-sm whitespace-pre-wrap font-mono bg-gray-100 dark:bg-dark-bg p-4 rounded-lg overflow-auto">
            {diffLines.map((item, index) => {
                let bgClass = '';
                let symbol = '';
                if (item.type === 'added') {
                    bgClass = 'bg-green-500/10 text-green-300';
                    symbol = '+ ';
                } else if (item.type === 'removed') {
                     bgClass = 'bg-red-500/10 text-red-300';
                     symbol = '- ';
                }
                return (
                    <div key={index} className={`${bgClass}`}>
                        <span className="select-none">{symbol}</span>
                        <span>{item.line}</span>
                    </div>
                )
            })}
        </pre>
    )
};

interface PromptHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  prompt: Prompt;
  onRestore: (promptId: string, version: PromptVersion) => void;
}

const PromptHistoryModal: React.FC<PromptHistoryModalProps> = ({ isOpen, onClose, prompt, onRestore }) => {
  const [selectedVersion, setSelectedVersion] = useState<PromptVersion | null>(null);
  const { t } = useTranslation();

  if (!isOpen) return null;
  
  const history = prompt.history || [];

  const handleRestore = () => {
    if (selectedVersion && window.confirm(t('history.restoreConfirm'))) {
        onRestore(prompt.id, selectedVersion);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-lg flex items-center justify-center p-4 z-50" onClick={onClose}>
      <div className="animate-fade-in bg-white dark:bg-dark-surface rounded-2xl shadow-2xl w-full max-w-5xl h-[90vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="flex justify-between items-center p-5 border-b border-gray-200 dark:border-dark-overlay flex-shrink-0">
          <div className="flex items-center gap-3">
            <History className="w-7 h-7 text-dark-primary" />
            <h2 className="text-2xl font-bold text-gray-800 dark:text-dark-text">{t('history.title')}: {prompt.title}</h2>
          </div>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-dark-overlay">
            <X className="w-6 h-6 text-gray-500 dark:text-dark-subtext" />
          </button>
        </div>
        
        <div className="flex-grow flex rtl:flex-row-reverse ltr:flex-row overflow-hidden">
            <div className="w-1/3 rtl:border-l ltr:border-r border-gray-200 dark:border-dark-overlay overflow-y-auto p-4 flex-shrink-0">
                <h3 className="font-semibold mb-3 text-lg">{t('history.versions')}</h3>
                <div className="space-y-2">
                    <button 
                        onClick={() => setSelectedVersion(null)}
                        className={`w-full rtl:text-right ltr:text-left p-3 rounded-lg border-2 ${!selectedVersion ? 'bg-dark-primary/10 border-dark-primary' : 'border-transparent hover:bg-gray-100 dark:hover:bg-dark-overlay'}`}
                    >
                       <p className="font-bold">{t('history.currentVersion')} <span className="text-xs font-normal bg-dark-accent/20 text-dark-accent px-2 py-0.5 rounded-full">{t('history.active')}</span></p>
                       <p className="text-xs text-gray-500 dark:text-dark-subtext mt-1">{timeAgo(prompt.updatedAt, t)}</p>
                    </button>

                    {history.map((version, index) => (
                        <button 
                            key={index}
                            onClick={() => setSelectedVersion(version)}
                            className={`w-full rtl:text-right ltr:text-left p-3 rounded-lg border-2 ${selectedVersion?.createdAt === version.createdAt ? 'bg-dark-primary/10 border-dark-primary' : 'border-transparent hover:bg-gray-100 dark:hover:bg-dark-overlay'}`}
                        >
                            <p className="font-semibold">{t('history.versionNumber', { number: history.length - index })}</p>
                            <p className="text-xs text-gray-500 dark:text-dark-subtext mt-1">{timeAgo(version.createdAt, t)}</p>
                            <p className="text-sm text-gray-600 dark:text-dark-subtext/80 truncate mt-2">{version.content}</p>
                        </button>
                    ))}
                </div>
            </div>
            <div className="w-2/3 overflow-y-auto p-6">
                {selectedVersion ? (
                     <div>
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="font-semibold text-xl">{t('history.compareTitle')}</h3>
                            <button 
                                onClick={handleRestore}
                                className="px-4 py-2 rounded-full text-white bg-dark-accent hover:opacity-90 font-semibold transition shadow-lg shadow-dark-accent/30"
                            >
                                {t('buttons.restoreVersion')}
                            </button>
                        </div>
                        <DiffViewer oldText={selectedVersion.content} newText={prompt.content} />
                    </div>
                ) : (
                    <div>
                        <h3 className="font-semibold text-xl mb-4">{t('history.currentContentTitle')}</h3>
                        <p className="whitespace-pre-wrap bg-gray-100 dark:bg-dark-bg p-4 rounded-lg">{prompt.content}</p>
                    </div>
                )}
            </div>
        </div>
      </div>
    </div>
  );
};

export default PromptHistoryModal;