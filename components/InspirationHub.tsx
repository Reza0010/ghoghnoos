import React, { useState, useEffect } from 'react';
import { Prompt } from '../types';
import { Plus, Sparkles } from './icons';
import { getDynamicInspirations } from '../services/geminiService';

interface InspirationHubProps {
    prompts: Prompt[];
    onUsePrompt: (prompt: Prompt) => void;
}

const InspirationCard: React.FC<{ prompt: Omit<Prompt, 'id' | 'createdAt' | 'updatedAt'>, onUse: () => void }> = ({ prompt, onUse }) => {
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
                استفاده از این پرامپت
            </button>
        </div>
    );
};

const InspirationHub: React.FC<InspirationHubProps> = ({ prompts, onUsePrompt }) => {
    const [inspiredPrompts, setInspiredPrompts] = useState<Omit<Prompt, 'id' | 'createdAt' | 'updatedAt'>[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchInspirations = async () => {
            // Only fetch if prompts are available.
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
                } else {
                    // Don't show an error, just an empty state, which is handled below.
                }
            } catch (err) {
                console.error(err);
                setError('An unexpected error occurred while fetching ideas.');
            } finally {
                setIsLoading(false);
            }
        };

        fetchInspirations();
    }, [prompts]);

    const handleUse = (promptData: Omit<Prompt, 'id' | 'createdAt' | 'updatedAt'>) => {
        const now = new Date().toISOString();
        const newPrompt: Prompt = {
            ...promptData,
            rating: promptData.rating || 0, // ensure rating is not undefined
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
                    <p className="text-xl font-semibold">Asking the muses for inspiration...</p>
                    <p>Generating personalized ideas just for you.</p>
                </div>
            );
        }

        if (error) {
            return <div className="text-center text-dark-danger mt-20">{error}</div>;
        }

        if (prompts.length === 0) {
             return (
                <div className="text-center text-gray-500 dark:text-dark-subtext mt-20">
                    <p className="text-xl font-semibold">Your inspiration hub is ready!</p>
                    <p>Create your first prompt, and I'll generate personalized ideas here based on your style.</p>
                </div>
            );
        }

        if (inspiredPrompts.length === 0) {
             return (
                <div className="text-center text-gray-500 dark:text-dark-subtext mt-20">
                    <p className="text-xl font-semibold">Hmm, couldn't find any inspiration this time.</p>
                    <p>Try refreshing, or create more prompts to give me more context!</p>
                </div>
            );
        }

        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {inspiredPrompts.map((p, index) => (
                    <InspirationCard key={index} prompt={p} onUse={() => handleUse(p)} />
                ))}
            </div>
        );
    }

    return (
        <div className="p-6 h-full overflow-y-auto animate-fade-in" dir="rtl">
            <h1 className="text-3xl font-bold text-gray-800 dark:text-dark-text mb-2">مرکز الهام‌بخش پویا</h1>
            <p className="text-gray-500 dark:text-dark-subtext mb-6">ایده‌های جدید که هوش مصنوعی مخصوص شما تولید کرده است.</p>
            {renderContent()}
        </div>
    );
};

export default InspirationHub;
