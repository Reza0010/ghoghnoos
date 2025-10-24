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
  Settings as SettingsIcon,
} from './components/icons';

type IconComponent = React.FC<React.SVGProps<SVGSVGElement>>;

export const PROMPT_TYPE_CONFIG: Record<PromptType, {
  label: string;
  icon: IconComponent;
  color: string;
  textColor: string;
  borderColor: string;
}> = {
  [PromptType.Image]: {
    label: 'پرامپت تصویر',
    icon: Image,
    color: 'bg-blue-500',
    textColor: 'text-blue-500',
    borderColor: 'border-blue-500',
  },
  [PromptType.Text]: {
    label: 'پرامپت متن',
    icon: FileText,
    color: 'bg-green-500',
    textColor: 'text-green-500',
    borderColor: 'border-green-500',
  },
  [PromptType.Video]: {
    label: 'پرامپت ویدیو',
    icon: Video,
    color: 'bg-red-500',
    textColor: 'text-red-500',
    borderColor: 'border-red-500',
  },
  [PromptType.Music]: {
    label: 'پرامپت موسیقی',
    icon: Music,
    color: 'bg-purple-500',
    textColor: 'text-purple-500',
    borderColor: 'border-purple-500',
  },
};

export const NAV_ITEMS: { id: string; label: string; icon: IconComponent }[] = [
  { id: 'dashboard', label: 'داشبورد', icon: LayoutDashboard },
  { id: 'all', label: 'همه پرامپت‌ها', icon: Folders },
  { id: 'image', label: 'تصویر', icon: Image },
  { id: 'text', label: 'متن', icon: FileText },
  { id: 'video', label: 'ویدیو', icon: Video },
  { id: 'music', label: 'موسیقی', icon: Music },
  { id: 'prompt-lab', label: 'آزمایشگاه پرامپت', icon: Beaker },
  { id: 'assistant', label: 'دستیار AI', icon: Bot },
  { id: 'inspiration', label: 'مرکز الهام‌بخش', icon: Sparkles },
  { id: 'settings', label: 'تنظیمات', icon: SettingsIcon },
];
