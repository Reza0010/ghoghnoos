import React from 'react';
import { FileText, Users, Video, Music, Sparkles, ArrowRight } from './icons';
import { useTranslation } from '../contexts/LanguageContext';

interface StudioCardProps {
  icon: React.FC<React.SVGProps<SVGSVGElement>>;
  title: string;
  description: string;
  onClick: () => void;
  color: string;
  hoverColor: string;
  t: (key: string) => string;
}

const StudioCard: React.FC<StudioCardProps> = ({ icon: Icon, title, description, onClick, color, hoverColor, t }) => {
  return (
    <button
      onClick={onClick}
      className={`group bg-white dark:bg-dark-surface p-6 rounded-2xl shadow-lg border-2 border-transparent rtl:text-right ltr:text-left w-full flex flex-col justify-between transition-all duration-300 hover:shadow-xl hover:-translate-y-1 ${hoverColor}`}
    >
      <div>
        <div className={`w-14 h-14 rounded-xl flex items-center justify-center bg-opacity-10 ${color.replace('text-', 'bg-')}`}>
            <Icon className={`w-8 h-8 ${color}`} />
        </div>
        <h3 className="mt-4 text-xl font-bold text-gray-800 dark:text-dark-text">{title}</h3>
        <p className="mt-2 text-sm text-gray-600 dark:text-dark-subtext leading-relaxed">{description}</p>
      </div>
      <div className="mt-6 flex items-center justify-end text-sm font-semibold text-dark-primary opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <span>{t('creativeHub.enterStudio')}</span>
        <ArrowRight className="w-4 h-4 rtl:mr-2 ltr:ml-2 rtl:scale-x-[-1]" />
      </div>
    </button>
  );
};

interface CreativeStudiosHubProps {
  setActiveView: (view: string) => void;
}

const CreativeStudiosHub: React.FC<CreativeStudiosHubProps> = ({ setActiveView }) => {
  const { t } = useTranslation();
  
  const studios = [
    { id: 'text-studio', title: t('creativeHub.studios.text.title'), description: t('creativeHub.studios.text.description'), icon: FileText, color: 'text-green-500', hoverColor: 'hover:border-green-500/50' },
    { id: 'face-fusion', title: t('creativeHub.studios.faceFusion.title'), description: t('creativeHub.studios.faceFusion.description'), icon: Users, color: 'text-blue-500', hoverColor: 'hover:border-blue-500/50' },
    { id: 'video-studio', title: t('creativeHub.studios.video.title'), description: t('creativeHub.studios.video.description'), icon: Video, color: 'text-red-500', hoverColor: 'hover:border-red-500/50' },
    { id: 'music-studio', title: t('creativeHub.studios.music.title'), description: t('creativeHub.studios.music.description'), icon: Music, color: 'text-purple-500', hoverColor: 'hover:border-purple-500/50' },
  ];

  return (
    <div className="p-6 h-full overflow-y-auto animate-fade-in">
      <div className="flex items-center gap-3 mb-2">
        <Sparkles className="w-8 h-8 text-dark-primary" />
        <h1 className="text-3xl font-bold text-gray-800 dark:text-dark-text">{t('creativeHub.title')}</h1>
      </div>
      <p className="text-gray-500 dark:text-dark-subtext mb-8">{t('creativeHub.description')}</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-4 gap-6">
        {studios.map((studio, index) => (
          <div key={studio.id} className="animate-slide-in-up" style={{ animationDelay: `${index * 100}ms` }}>
            <StudioCard
              title={studio.title}
              description={studio.description}
              icon={studio.icon}
              color={studio.color}
              hoverColor={studio.hoverColor}
              onClick={() => setActiveView(studio.id)}
              t={t}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default CreativeStudiosHub;