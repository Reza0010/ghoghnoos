import React, { useState, useEffect } from 'react';
import { Prompt } from '../types';
import { Plus, Sparkles } from './icons';
import { getDynamicInspirations } from '../services/geminiService';
import { useTranslation } from '../contexts/LanguageContext';

interface InspirationHubProps {
    prompts: Prompt[];
    onUsePrompt: (prompt: Prompt) => void;
}

const InspirationCard: React.FC<{ prompt: Omit<Prompt, 'id' | 'createdAt' | 'updatedAt'>, onUse: () => void, t: (key: string) => string }> = ({ prompt, onUse, t }) => {
    return (
        <div className="bg-white dark:bg-dark-surface rounded-xl shadow-lg p-5 flex flex-col justify-between animate-fade-in">
            <div>
                <h3 className="font-bold text-lg text-gray-800 dark:text-dark-text">{prompt.title}</h3>
                <p className="text-sm text-gray-600 dark:text-dark-subtext mt-2 h-24 overflow-hidden">{prompt.content}</p>
                <div className="mt-3 flex flex-wrap gap-2">
                    {(prompt.tags || []).map(tag => (
                        <span key={tag} className="px-2 py-1 bg-dark-primary/10 text-dark-primary text-xs font-semibold rounded-full">
                            #{tag}
                        </span>
                    ))}
                </div>
            </div>
            <button 
                onClick={onUse}
                className="mt-4 w-full flex items-center justify-center gap-2 bg-dark-accent/10 text-dark-accent font-semibold px-4 py-2 rounded-lg hover:bg-opacity-90 transition-all duration-200"
            >
                <Plus className="w-5 h-5"/>
                {t('inspiration.usePromptButton')}
            </button>
        </div>
    );
};

const InspirationHub: React.FC<InspirationHubProps> = ({ prompts, onUsePrompt }) => {
    const [inspiredPrompts, setInspiredPrompts] = useState<Omit<Prompt, 'id' | 'createdAt' | 'updatedAt'>[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { t } = useTranslation();

    useEffect(() => {
        const fetchInspirations = async () => {
            if (prompts.length === 0) {
                setIsLoading(false);
                return;
            }
            
            setIsLoading(true);
            setError(null);
            try {
                const newPrompts = await getDynamicInspirations(prompts);
                if (newPrompts && newPrompts.length > 0) {
                    setInspiredPrompts(newPrompts);
                }
            } catch (err) {
                console.error(err);
                setError(t('inspiration.error'));
            } finally {
                setIsLoading(false);
            }
        };

        fetchInspirations();
    }, [prompts, t]);

    const handleUse = (promptData: Omit<Prompt, 'id' | 'createdAt' | 'updatedAt'>) => {
        const now = new Date().toISOString();
        const newPrompt: Prompt = {
            ...promptData,
            rating: promptData.rating || 0,
            id: new Date().getTime().toString(),
            createdAt: now,
            updatedAt: now,
        };
        onUsePrompt(newPrompt);
    };
    
    const renderContent = () => {
        if (isLoading) {
            return (
                <div className="text-center text-gray-500 dark:text-dark-subtext mt-20 flex flex-col items-center">
                    <Sparkles className="w-16 h-16 text-dark-secondary animate-spin mb-4" />
                    <p className="text-xl font-semibold">{t('inspiration.loading.title')}</p>
                    <p>{t('inspiration.loading.description')}</p>
                </div>
            );
        }

        if (error) {
            return <div className="text-center text-dark-danger mt-20">{error}</div>;
        }

        if (prompts.length === 0) {
             return (
                <div className="text-center text-gray-500 dark:text-dark-subtext mt-20">
                    <p className="text-xl font-semibold">{t('inspiration.empty.title')}</p>
                    <p>{t('inspiration.empty.description')}</p>
                </div>
            );
        }

        if (inspiredPrompts.length === 0) {
             return (
                <div className="text-center text-gray-500 dark:text-dark-subtext mt-20">
                    <p className="text-xl font-semibold">{t('inspiration.noResults.title')}</p>
                    <p>{t('inspiration.noResults.description')}</p>
                </div>
            );
        }

        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {inspiredPrompts.map((p, index) => (
                    <InspirationCard key={index} prompt={p} onUse={() => handleUse(p)} t={t} />
                ))}
            </div>
        );
    }

    return (
        <div className="p-6 h-full overflow-y-auto animate-fade-in">
            <h1 className="text-3xl font-bold text-gray-800 dark:text-dark-text mb-2">{t('inspiration.title')}</h1>
            <p className="text-gray-500 dark:text-dark-subtext mb-6">{t('inspiration.description')}</p>
            {renderContent()}
        </div>
    );
};

export default InspirationHub;