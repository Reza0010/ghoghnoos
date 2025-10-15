import React, { useState } from 'react';
import useLocalStorage from '../hooks/useLocalStorage';
import { PromptExperiment, PromptType, PromptVariation } from '../types';
import ExperimentForm from './ExperimentForm';
import ExperimentRunner from './ExperimentRunner';
import { Plus, Beaker, Trash } from './icons';

interface PromptLabProps {
  onSaveWinner: (title: string, variation: PromptVariation) => void;
}

const PromptLab: React.FC<PromptLabProps> = ({ onSaveWinner }) => {
    const [experiments, setExperiments] = useLocalStorage<PromptExperiment[]>('prompt_experiments', []);
    const [runningExperiment, setRunningExperiment] = useState<PromptExperiment | null>(null);
    const [isFormOpen, setIsFormOpen] = useState(false);

    const handleSaveExperiment = (newExperiment: Omit<PromptExperiment, 'id' | 'createdAt'>) => {
        const experimentWithMeta: PromptExperiment = {
            ...newExperiment,
            id: new Date().getTime().toString(),
            createdAt: new Date().toISOString(),
        }
        setExperiments(prev => [experimentWithMeta, ...prev]);
        setIsFormOpen(false);
    };

    const handleDeleteExperiment = (id: string) => {
        if (window.confirm('Are you sure you want to delete this experiment and all its data?')) {
            setExperiments(prev => prev.filter(exp => exp.id !== id));
        }
    };
    
    const handleUpdateExperiment = (updatedExperiment: PromptExperiment) => {
        setExperiments(prev => prev.map(exp => exp.id === updatedExperiment.id ? updatedExperiment : exp));
    };

    if (runningExperiment) {
        return <ExperimentRunner
                    experiment={runningExperiment}
                    onUpdateExperiment={handleUpdateExperiment}
                    onSaveWinner={onSaveWinner}
                    onBack={() => setRunningExperiment(null)}
                />
    }

    return (
        <div className="p-6 h-full overflow-y-auto animate-fade-in" dir="rtl">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-3xl font-bold text-gray-800 dark:text-dark-text">آزمایشگاه پرامپت</h1>
                    <p className="text-gray-500 dark:text-dark-subtext">آزمایش‌های A/B برای یافتن بهترین پرامپت‌ها اجرا کنید.</p>
                </div>
                <button
                  onClick={() => setIsFormOpen(true)}
                  className="flex items-center gap-2 bg-dark-primary text-white font-semibold px-4 py-2 rounded-full hover:bg-opacity-90 transition-all duration-200 shadow-lg shadow-dark-primary/30"
                >
                  <Plus className="w-5 h-5" />
                  ایجاد آزمایش جدید
                </button>
            </div>

            {experiments.length === 0 ? (
                <div className="text-center text-gray-500 dark:text-dark-subtext mt-20 border-2 border-dashed border-gray-300 dark:border-dark-overlay rounded-2xl p-10">
                    <Beaker className="w-16 h-16 mx-auto text-gray-400 dark:text-dark-overlay" />
                    <h2 className="mt-4 text-xl font-semibold">آزمایشگاه شما خالی است</h2>
                    <p className="mt-2">اولین آزمایش A/B خود را برای مقایسه نسخه‌های مختلف پرامپت ایجاد کنید.</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {experiments.map(exp => (
                        <div key={exp.id} className="bg-white dark:bg-dark-surface rounded-xl shadow-md p-4 flex items-center justify-between transition-shadow hover:shadow-lg">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 bg-dark-secondary/10 flex items-center justify-center rounded-lg">
                                    <Beaker className="w-6 h-6 text-dark-secondary" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-lg text-gray-800 dark:text-dark-text">{exp.title}</h3>
                                    <p className="text-sm text-gray-500 dark:text-dark-subtext">{exp.variations.length} نسخه</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
                                    exp.status === 'completed' 
                                    ? 'bg-dark-accent/10 text-dark-accent' 
                                    : 'bg-dark-warn/10 text-dark-warn'
                                }`}>
                                    {exp.status === 'completed' ? 'تکمیل شده' : 'در حال اجرا'}
                                </span>
                                <button onClick={() => setRunningExperiment(exp)} className="px-4 py-2 text-sm font-semibold text-dark-primary bg-dark-primary/10 rounded-lg hover:bg-dark-primary/20 transition">
                                    {exp.status === 'completed' ? 'مشاهده نتایج' : 'اجرا'}
                                </button>
                                <button onClick={() => handleDeleteExperiment(exp.id)} className="p-2 rounded-full hover:bg-dark-danger/10">
                                    <Trash className="w-5 h-5 text-dark-danger" />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <ExperimentForm
                isOpen={isFormOpen}
                onClose={() => setIsFormOpen(false)}
                onSave={handleSaveExperiment}
            />
        </div>
    );
}

export default PromptLab;
