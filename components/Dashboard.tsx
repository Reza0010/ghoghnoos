import React from 'react';
import { Prompt } from '../types';
import { PromptCard } from './PromptCard';
import { 
  FileText, 
  Image, 
  TrendingUp, 
  Clock, 
  Star, 
  Zap,
  BarChart,
  Heart
} from './icons';

interface DashboardProps {
  prompts: Prompt[];
  onEditPrompt: (prompt: Prompt) => void;
  onDeletePrompt: (id: string) => void;
  onToggleFavorite: (id: string) => void;
  onUsePrompt: (prompt: Prompt) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  prompts,
  onEditPrompt,
  onDeletePrompt,
  onToggleFavorite,
  onUsePrompt,
}) => {
  const recentPrompts = prompts
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    .slice(0, 6);

  const favoritePrompts = prompts.filter(p => p.isFavorite);
  const textPrompts = prompts.filter(p => p.type === 'text');
  const imagePrompts = prompts.filter(p => p.type === 'image');
  const totalUsage = prompts.reduce((sum, p) => sum + p.usageCount, 0);

  const stats = [
    {
      title: 'Total Prompts',
      value: prompts.length,
      icon: FileText,
      color: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
      change: '+12%',
      changeType: 'positive' as const
    },
    {
      title: 'Text Prompts',
      value: textPrompts.length,
      icon: FileText,
      color: 'text-green-600 dark:text-green-400',
      bgColor: 'bg-green-50 dark:bg-green-900/20',
      change: '+8%',
      changeType: 'positive' as const
    },
    {
      title: 'Image Prompts',
      value: imagePrompts.length,
      icon: Image,
      color: 'text-purple-600 dark:text-purple-400',
      bgColor: 'bg-purple-50 dark:bg-purple-900/20',
      change: '+15%',
      changeType: 'positive' as const
    },
    {
      title: 'Favorites',
      value: favoritePrompts.length,
      icon: Heart,
      color: 'text-red-600 dark:text-red-400',
      bgColor: 'bg-red-50 dark:bg-red-900/20',
      change: '+5%',
      changeType: 'positive' as const
    },
    {
      title: 'Total Usage',
      value: totalUsage,
      icon: TrendingUp,
      color: 'text-orange-600 dark:text-orange-400',
      bgColor: 'bg-orange-50 dark:bg-orange-900/20',
      change: '+23%',
      changeType: 'positive' as const
    },
    {
      title: 'Categories',
      value: new Set(prompts.map(p => p.category)).size,
      icon: BarChart,
      color: 'text-indigo-600 dark:text-indigo-400',
      bgColor: 'bg-indigo-50 dark:bg-indigo-900/20',
      change: '+2%',
      changeType: 'positive' as const
    }
  ];

  return (
    <div className="main-content">
      <div className="space-y-8">
        {/* Header */}
        <div className="fade-in">
          <div className="flex items-center space-x-3 mb-2">
            <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-primary-500 to-purple-600 rounded-xl">
              <Zap size={20} className="text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                Dashboard
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Welcome back! Here's what's happening with your prompts.
              </p>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6 slide-up">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div
                key={stat.title}
                className="card hover:shadow-lg transition-all duration-300"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="card-body">
                  <div className="flex items-center justify-between mb-4">
                    <div className={`p-3 rounded-xl ${stat.bgColor}`}>
                      <Icon size={20} className={stat.color} />
                    </div>
                    <div className={`text-xs font-medium px-2 py-1 rounded-full ${
                      stat.changeType === 'positive' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                        : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                    }`}>
                      {stat.change}
                    </div>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                      {stat.value.toLocaleString()}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {stat.title}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Quick Actions */}
        <div className="card slide-up" style={{ animationDelay: '600ms' }}>
          <div className="card-header">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Quick Actions
            </h2>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <button className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors group">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg group-hover:bg-blue-200 dark:group-hover:bg-blue-900/50 transition-colors">
                  <FileText size={20} className="text-blue-600 dark:text-blue-400" />
                </div>
                <div className="text-left">
                  <p className="font-medium text-gray-900 dark:text-white">New Text Prompt</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Create a text-based prompt</p>
                </div>
              </button>

              <button className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors group">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg group-hover:bg-purple-200 dark:group-hover:bg-purple-900/50 transition-colors">
                  <Image size={20} className="text-purple-600 dark:text-purple-400" />
                </div>
                <div className="text-left">
                  <p className="font-medium text-gray-900 dark:text-white">New Image Prompt</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Create an image generation prompt</p>
                </div>
              </button>

              <button className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors group">
                <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg group-hover:bg-green-200 dark:group-hover:bg-green-900/50 transition-colors">
                  <Zap size={20} className="text-green-600 dark:text-green-400" />
                </div>
                <div className="text-left">
                  <p className="font-medium text-gray-900 dark:text-white">Run Experiment</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Test prompts in the lab</p>
                </div>
              </button>

              <button className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors group">
                <div className="p-2 bg-orange-100 dark:bg-orange-900/30 rounded-lg group-hover:bg-orange-200 dark:group-hover:bg-orange-900/50 transition-colors">
                  <Star size={20} className="text-orange-600 dark:text-orange-400" />
                </div>
                <div className="text-left">
                  <p className="font-medium text-gray-900 dark:text-white">Browse Templates</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Explore inspiration hub</p>
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Recent Prompts */}
        <div className="slide-up" style={{ animationDelay: '800ms' }}>
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-2">
              <Clock size={20} className="text-gray-600 dark:text-gray-400" />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Recent Prompts
              </h2>
            </div>
            <button className="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium text-sm">
              View All
            </button>
          </div>

          {recentPrompts.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {recentPrompts.map((prompt, index) => (
                <div
                  key={prompt.id}
                  className="fade-in"
                  style={{ animationDelay: `${1000 + index * 100}ms` }}
                >
                  <PromptCard
                    prompt={prompt}
                    onEdit={onEditPrompt}
                    onDelete={onDeletePrompt}
                    onToggleFavorite={onToggleFavorite}
                    onUse={onUsePrompt}
                  />
                </div>
              ))}
            </div>
          ) : (
            <div className="card">
              <div className="card-body text-center py-12">
                <div className="flex items-center justify-center w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full mx-auto mb-4">
                  <FileText size={24} className="text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  No prompts yet
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  Create your first prompt to get started with Prompt Studio.
                </p>
                <button className="btn btn-primary">
                  <FileText size={16} />
                  <span className="ml-2">Create Your First Prompt</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;