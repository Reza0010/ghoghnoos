import React from 'react';
import { FileText, Users, Video, Music, Sparkles, ArrowRight } from './icons';

interface StudioCardProps {
  icon: React.FC<React.SVGProps<SVGSVGElement>>;
  title: string;
  description: string;
  onClick: () => void;
  color: string;
  hoverColor: string;
}

const StudioCard: React.FC<StudioCardProps> = ({ icon: Icon, title, description, onClick, color, hoverColor }) => {
  return (
    <button
      onClick={onClick}
      className={`group bg-white dark:bg-dark-surface p-6 rounded-2xl shadow-lg border-2 border-transparent text-right w-full flex flex-col justify-between transition-all duration-300 hover:shadow-xl hover:-translate-y-1 ${hoverColor}`}
    >
      <div>
        <div className={`w-14 h-14 rounded-xl flex items-center justify-center bg-opacity-10 ${color.replace('text-', 'bg-')}`}>
            <Icon className={`w-8 h-8 ${color}`} />
        </div>
        <h3 className="mt-4 text-xl font-bold text-gray-800 dark:text-dark-text">{title}</h3>
        <p className="mt-2 text-sm text-gray-600 dark:text-dark-subtext leading-relaxed">{description}</p>
      </div>
      <div className="mt-6 flex items-center justify-end text-sm font-semibold text-dark-primary opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <span>ورود به استودیو</span>
        <ArrowRight className="w-4 h-4 mr-2 transform -rotate-180" />
      </div>
    </button>
  );
};

interface CreativeStudiosHubProps {
  setActiveView: (view: string) => void;
}

const CreativeStudiosHub: React.FC<CreativeStudiosHubProps> = ({ setActiveView }) => {
  const studios = [
    { id: 'text-studio', title: 'استودیوی متن', description: 'محتوای متنی خود را با ابزارهای هوشمند بنویسید، ویرایش و بهینه کنید.', icon: FileText, color: 'text-green-500', hoverColor: 'hover:border-green-500/50' },
    { id: 'face-fusion', title: 'چهره‌ساز', description: 'چهره‌ها را ترکیب کنید یا استایل‌های هنری را به تصاویر خود منتقل کنید.', icon: Users, color: 'text-blue-500', hoverColor: 'hover:border-blue-500/50' },
    { id: 'video-studio', title: 'استودیوی ویدیو', description: 'ایده‌های خود را با قدرت مدل Veo به ویدیوهای شگفت‌انگیز تبدیل کنید.', icon: Video, color: 'text-red-500', hoverColor: 'hover:border-red-500/50' },
    { id: 'music-studio', title: 'استودیوی موسیقی', description: 'ایده‌های متنی خود را به قطعات موسیقی منحصربه‌فرد تبدیل کنید.', icon: Music, color: 'text-purple-500', hoverColor: 'hover:border-purple-500/50' },
  ];

  return (
    <div className="p-6 h-full overflow-y-auto animate-fade-in" dir="rtl">
      <div className="flex items-center gap-3 mb-2">
        <Sparkles className="w-8 h-8 text-dark-primary" />
        <h1 className="text-3xl font-bold text-gray-800 dark:text-dark-text">استودیو خلاقیت</h1>
      </div>
      <p className="text-gray-500 dark:text-dark-subtext mb-8">ابزار مناسب برای پروژه بعدی خود را انتخاب کنید.</p>
      
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
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default CreativeStudiosHub;