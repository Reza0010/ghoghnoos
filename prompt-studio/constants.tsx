import React from 'react';
import { PromptType } from './types';
import {
  LayoutDashboard,
  Folders,
  Image,
  FileText,
  Video,
  Music,
  Bot,
  Sparkles,
  Beaker,
  Users,
  Link,
} from './components/icons';
import { TFunction } from './contexts/LanguageContext';

type IconComponent = React.FC<React.SVGProps<SVGSVGElement>>;

export const getPromptTypeConfig = (t: TFunction) => ({
  [PromptType.Image]: {
    label: t('promptType.image'),
    icon: Image,
    color: 'bg-blue-500',
    textColor: 'text-blue-500',
    borderColor: 'border-blue-500',
  },
  [PromptType.Text]: {
    label: t('promptType.text'),
    icon: FileText,
    color: 'bg-green-500',
    textColor: 'text-green-500',
    borderColor: 'border-green-500',
  },
  [PromptType.Video]: {
    label: t('promptType.video'),
    icon: Video,
    color: 'bg-red-500',
    textColor: 'text-red-500',
    borderColor: 'border-red-500',
  },
  [PromptType.Music]: {
    label: t('promptType.music'),
    icon: Music,
    color: 'bg-purple-500',
    textColor: 'text-purple-500',
    borderColor: 'border-purple-500',
  },
});

interface NavItem {
    id: string;
    label: string;
    icon: IconComponent;
}

interface NavSection {
    title: string;
    items: NavItem[];
}

export const getNavStructure = (t: TFunction): NavSection[] => [
  {
    title: t('nav.workspace'),
    items: [
      { id: 'dashboard', label: t('nav.dashboard'), icon: LayoutDashboard },
      { id: 'all', label: t('nav.allPrompts'), icon: Folders },
    ],
  },
  {
    title: t('nav.yourLibrary'),
    items: [
      { id: 'image', label: t('nav.image'), icon: Image },
      { id: 'text', label: t('nav.text'), icon: FileText },
      { id: 'video', label: t('nav.video'), icon: Video },
      { id: 'music', label: t('nav.music'), icon: Music },
    ],
  },
  {
    title: t('nav.studio'),
    items: [
        { id: 'creative-studios', label: t('nav.creativeStudios'), icon: Sparkles },
    ],
  },
  {
    title: t('nav.advancedTools'),
    items: [
      { id: 'prompt-chains', label: t('nav.promptChains'), icon: Link },
      { id: 'prompt-lab', label: t('nav.promptLab'), icon: Beaker },
      { id: 'inspiration', label: t('nav.inspiration'), icon: Sparkles },
      { id: 'assistant', label: t('nav.assistant'), icon: Bot },
    ],
  },
];