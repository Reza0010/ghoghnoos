import React, { useState } from 'react';
import { SocialPlatform } from '../types';
import { generateCreativeText, generateImage } from '../services/geminiService';
import { Instagram, Telegram, Twitter, Link, Sparkles, Copy, Download, ArrowRight } from './icons';
import { useTranslation } from '../contexts/LanguageContext';

type Stage = 'platform' | 'idea' | 'generating' | 'result';

const PromptChainStudio: React.FC = () => {
    const { t } = useTranslation();

    const platformConfig: Record<SocialPlatform, {
        label: string;
        icon: React.FC<React.SVGProps<SVGSVGElement>>;
        color: string;
        description: string;
        aspectRatio: '1:1' | '16:9';
    }> = {
        instagram: { label: t('promptChain.platforms.instagram.label'), icon: Instagram, color: 'text-[#E1306C]', description: t('promptChain.platforms.instagram.description'), aspectRatio: '1:1' },
        telegram: { label: t('promptChain.platforms.telegram.label'), icon: Telegram, color: 'text-[#24A1DE]', description: t('promptChain.platforms.telegram.description'), aspectRatio: '16:9' },
        twitter: { label: t('promptChain.platforms.twitter.label'), icon: Twitter, color: 'dark:text-white text-black', description: t('promptChain.platforms.twitter.description'), aspectRatio: '16:9' },
    };

    const [stage, setStage] = useState<Stage>('platform');
    const [platform, setPlatform] = useState<SocialPlatform | null>(null);
    const [idea, setIdea] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [progressMessage, setProgressMessage] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [generatedCaption, setGeneratedCaption] = useState('');
    const [generatedImageUrl, setGeneratedImageUrl] = useState('');

    const handlePlatformSelect = (selectedPlatform: SocialPlatform) => {
        setPlatform(selectedPlatform);
        setStage('idea');
    };

    const handleGenerate = async () => {
        if (!idea.trim() || !platform) return;
        
        setIsLoading(true);
        setStage('generating');
        setError(null);

        try {
            setProgressMessage(t('promptChain.generating.caption'));
            const captionPrompt = t('promptChain.internalPrompts.caption', { platform: platformConfig[platform].label, idea });
            const caption = await generateCreativeText(captionPrompt);
            setGeneratedCaption(caption);

            setProgressMessage(t('promptChain.generating.image'));
            const imagePrompt = t('promptChain.internalPrompts.image', { idea, caption });
            const imageUrl = await generateImage(imagePrompt, platformConfig[platform].aspectRatio);
            if (!imageUrl) throw new Error(t('promptChain.errors.imageGenerationFailed'));
            
            setGeneratedImageUrl(imageUrl);
            setStage('result');
        } catch (err: any) {
            setError(err.message || t('promptChain.errors.unexpected'));
            setStage('idea');
        } finally {
            setIsLoading(false);
        }
    };
    
    const handleStartOver = () => {
        setStage('platform');
        setPlatform(null);
        setIdea('');
        setGeneratedCaption('');
        setGeneratedImageUrl('');
        setError(null);
    };

    const handleCopyCaption = () => {
        navigator.clipboard.writeText(generatedCaption);
        alert(t('promptChain.copySuccess'));
    };

    const renderContent = () => {
        switch (stage) {
            case 'platform':
                return (
                    <div className="text-center">
                        <h2 className="text-2xl font-bold mb-2">{t('promptChain.platformStage.title')}</h2>
                        <p className="text-gray-500 dark:text-dark-subtext mb-8">{t('promptChain.platformStage.description')}</p>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
                            {Object.keys(platformConfig).map(key => {
                                const p = platformConfig[key as SocialPlatform];
                                return (
                                    <button key={key} onClick={() => handlePlatformSelect(key as SocialPlatform)} className="bg-white dark:bg-dark-surface p-6 rounded-2xl shadow-lg rtl:text-right ltr:text-left w-full flex flex-col justify-between transition-all duration-300 hover:shadow-xl hover:-translate-y-1 border-2 border-transparent hover:border-dark-primary/50">
                                        <p.icon className={`w-10 h-10 mb-4 ${p.color}`} />
                                        <h3 className="text-xl font-bold text-gray-800 dark:text-dark-text">{p.label}</h3>
                                        <p className="mt-2 text-sm text-gray-600 dark:text-dark-subtext flex-grow">{p.description}</p>
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                );
            case 'idea':
                if (!platform) return null;
                const currentPlatform = platformConfig[platform];
                return (
                    <div className="text-center max-w-2xl mx-auto animate-fade-in">
                        <div className="flex items-center justify-center gap-3 mb-4">
                           <currentPlatform.icon className={`w-8 h-8 ${currentPlatform.color}`} />
                           <h2 className="text-2xl font-bold">{t('promptChain.ideaStage.title')}</h2>
                        </div>
                        <p className="text-gray-500 dark:text-dark-subtext mb-6">{t('promptChain.ideaStage.description')}</p>
                        <textarea
                            value={idea}
                            onChange={(e) => setIdea(e.target.value)}
                            rows={5}
                            className="w-full bg-white dark:bg-dark-surface rounded-lg border-gray-300 dark:border-dark-overlay focus:border-dark-primary focus:ring-dark-primary resize-none p-4 text-center text-lg"
                            placeholder={t('promptChain.ideaStage.placeholder')}
                        />
                         {error && <p className="text-dark-danger mt-4">{error}</p>}
                        <div className="flex items-center justify-center gap-4 mt-6">
                            <button onClick={() => setStage('platform')} className="px-6 py-3 rounded-full text-gray-700 dark:text-dark-subtext bg-gray-200 dark:bg-dark-overlay hover:opacity-90 transition">{t('buttons.previousStep')}</button>
                            <button onClick={handleGenerate} disabled={!idea.trim()} className="px-8 py-3 rounded-full text-white bg-dark-primary hover:opacity-90 font-semibold transition shadow-lg shadow-dark-primary/30 disabled:opacity-50">
                                {t('buttons.generatePost')}
                            </button>
                        </div>
                    </div>
                );
             case 'generating':
                return (
                    <div className="text-center flex flex-col items-center justify-center">
                        <Sparkles className="w-16 h-16 text-dark-primary animate-spin" />
                        <p className="mt-4 font-semibold text-xl">{progressMessage}</p>
                        <p className="text-gray-500 dark:text-dark-subtext">{t('promptChain.generating.waitMessage')}</p>
                    </div>
                );
            case 'result':
                return (
                    <div className="animate-fade-in">
                        <h2 className="text-2xl font-bold mb-4 text-center">{t('promptChain.resultStage.title')}</h2>
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-5xl mx-auto">
                            <div className="bg-white dark:bg-dark-surface rounded-2xl shadow-lg flex flex-col p-4">
                               <img src={generatedImageUrl} alt="Generated for post" className="w-full h-auto object-contain rounded-lg" />
                            </div>
                             <div className="bg-white dark:bg-dark-surface rounded-2xl shadow-lg flex flex-col p-6">
                                <h3 className="font-semibold mb-2">{t('promptChain.resultStage.captionTitle')}:</h3>
                                <div className="flex-grow bg-gray-100 dark:bg-dark-bg rounded-lg p-4 text-sm whitespace-pre-wrap overflow-y-auto">
                                    {generatedCaption}
                                </div>
                                <div className="mt-4 grid grid-cols-2 gap-3">
                                    <button onClick={handleCopyCaption} className="flex items-center justify-center gap-2 bg-dark-secondary/10 text-dark-secondary font-semibold px-4 py-2 rounded-lg hover:bg-opacity-90 transition-all duration-200">
                                        <Copy className="w-5 h-5"/>
                                        {t('buttons.copyText')}
                                    </button>
                                     <a href={generatedImageUrl} download={`prompt-studio-post.png`} className="flex items-center justify-center gap-2 bg-dark-accent/10 text-dark-accent font-semibold px-4 py-2 rounded-lg hover:bg-opacity-90 transition-all duration-200">
                                        <Download className="w-5 h-5"/>
                                        {t('buttons.downloadImage')}
                                    </a>
                                </div>
                            </div>
                        </div>
                        <div className="text-center mt-6">
                            <button onClick={handleStartOver} className="px-8 py-3 rounded-full text-white bg-dark-primary hover:opacity-90 font-semibold transition shadow-lg shadow-dark-primary/30">
                                {t('buttons.createAnotherPost')}
                            </button>
                        </div>
                    </div>
                );
        }
    };

    return (
        <div className="p-6 h-full flex flex-col items-center justify-center animate-fade-in">
            <div className="flex items-center gap-3 mb-2">
                <Link className="w-8 h-8 text-dark-primary" />
                <h1 className="text-3xl font-bold text-gray-800 dark:text-dark-text">{t('promptChain.title')}</h1>
            </div>
             <p className="text-gray-500 dark:text-dark-subtext mb-8">{t('promptChain.description')}</p>
             <div className="w-full flex-grow flex items-center justify-center">
                {renderContent()}
             </div>
        </div>
    );
};

export default PromptChainStudio;