import React, { useState, useEffect } from 'react';
import { PromptExperiment, PromptVariation } from '../types';
import { generateImage } from '../services/geminiService';
import { ArrowRight, Sparkles, Star, Download } from './icons';
import { useTranslation } from '../contexts/LanguageContext';

interface ExperimentRunnerProps {
    experiment: PromptExperiment;
    onUpdateExperiment: (updatedExperiment: PromptExperiment) => void;
    onSaveWinner: (title: string, variation: PromptVariation) => void;
    onBack: () => void;
}

const ExperimentRunner: React.FC<ExperimentRunnerProps> = ({ experiment, onUpdateExperiment, onSaveWinner, onBack }) => {
    const [internalExperiment, setInternalExperiment] = useState(experiment);
    const [isGenerating, setIsGenerating] = useState(false);
    const { t } = useTranslation();

    useEffect(() => {
        const generateOutputs = async () => {
            const variationsToGenerate = internalExperiment.variations.filter(v => !v.outputUrl);
            if (variationsToGenerate.length === 0) return;

            setIsGenerating(true);
            const generationPromises = variationsToGenerate.map(v => generateImage(v.content));
            
            try {
                const results = await Promise.all(generationPromises);

                const updatedVariations = internalExperiment.variations.map(v => {
                    const index = variationsToGenerate.findIndex(vg => vg.id === v.id);
                    if (index > -1 && results[index]) {
                        return { ...v, outputUrl: results[index]! };
                    }
                    return v;
                });
                
                const updatedExperiment = { ...internalExperiment, variations: updatedVariations };
                setInternalExperiment(updatedExperiment);
                onUpdateExperiment(updatedExperiment);
            } catch (error) {
                console.error("Failed to generate one or more images:", error);
            } finally {
                setIsGenerating(false);
            }
        };

        if (internalExperiment.status === 'running') {
            generateOutputs();
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [internalExperiment.status]);

    const handleSelectWinner = (winnerId: string) => {
        const finalExperiment = {
            ...internalExperiment,
            status: 'completed' as const,
            variations: internalExperiment.variations.map(v => ({
                ...v,
                isWinner: v.id === winnerId,
            }))
        };
        setInternalExperiment(finalExperiment);
        onUpdateExperiment(finalExperiment);
    };

    return (
        <div className="p-6 h-full overflow-y-auto animate-fade-in">
            <div className="mb-6">
                <button onClick={onBack} className="flex items-center gap-2 text-sm font-semibold text-dark-primary mb-4">
                    <ArrowRight className="w-5 h-5 rtl:scale-x-[-1]" />
                    {t('experimentRunner.backButton')}
                </button>
                <h1 className="text-3xl font-bold text-gray-800 dark:text-dark-text">{experiment.title}</h1>
                {experiment.goal && <p className="text-gray-500 dark:text-dark-subtext">{t('experimentRunner.goalPrefix')}: {experiment.goal}</p>}
                {isGenerating && (
                    <div className="mt-4 flex items-center gap-2 text-dark-warn">
                        <Sparkles className="w-5 h-5 animate-spin" />
                        <span>{t('experimentRunner.generatingMessage')}</span>
                    </div>
                )}
            </div>

            <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6`}>
                {internalExperiment.variations.map((variation, index) => (
                    <div key={variation.id} className={`bg-white dark:bg-dark-surface rounded-2xl shadow-lg flex flex-col transition-all duration-300 ${variation.isWinner ? 'ring-4 ring-offset-2 ring-offset-dark-bg ring-yellow-400' : 'hover:shadow-xl'}`}>
                        <div className="p-4 border-b border-gray-200 dark:border-dark-overlay">
                            <h3 className="font-semibold">{t('experimentRunner.variationTitle', { number: index + 1 })}</h3>
                            <p className="text-sm font-mono bg-gray-100 dark:bg-dark-bg p-2 rounded-md mt-2">{variation.content}</p>
                        </div>
                        <div className="p-4 flex-grow flex flex-col items-center justify-center">
                            <div className="w-full aspect-square bg-gray-100 dark:bg-dark-bg rounded-lg flex items-center justify-center">
                                {!variation.outputUrl ? (
                                    <div className="text-center text-dark-primary">
                                        <Sparkles className="w-10 h-10 animate-spin" />
                                        <p className="mt-2 text-sm">{t('experimentRunner.generating')}</p>
                                    </div>
                                ) : (
                                    <img src={variation.outputUrl} alt="Generated output" className="rounded-lg object-contain h-full w-full" />
                                )}
                            </div>
                        </div>
                        <div className="p-4 border-t border-gray-200 dark:border-dark-overlay">
                            {internalExperiment.status === 'running' && variation.outputUrl && (
                                <button
                                    onClick={() => handleSelectWinner(variation.id)}
                                    className="w-full flex items-center justify-center gap-2 bg-yellow-400/10 text-yellow-500 font-semibold px-4 py-2 rounded-lg hover:bg-yellow-400/20 transition-all duration-200"
                                >
                                    <Star className="w-5 h-5" />
                                    {t('experimentRunner.selectWinnerButton')}
                                </button>
                            )}
                            {internalExperiment.status === 'completed' && variation.isWinner && (
                                <div className="text-center animate-fade-in">
                                    <div className="flex items-center justify-center gap-2 font-bold text-yellow-500">
                                        <Star className="w-6 h-6 fill-current" />
                                        <span>{t('experimentRunner.winner')}</span>
                                    </div>
                                    <button
                                        onClick={() => onSaveWinner(experiment.title, variation)}
                                        className="mt-3 w-full flex items-center justify-center gap-2 bg-dark-accent/10 text-dark-accent font-semibold px-4 py-2 rounded-lg hover:bg-dark-accent/20 transition-all duration-200"
                                    >
                                        <Download className="w-5 h-5" />
                                        {t('experimentRunner.saveWinnerButton')}
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ExperimentRunner;