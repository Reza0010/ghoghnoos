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

interface NavItem {
    id: string;
    label: string;
    icon: IconComponent;
}

interface NavSection {
    title: string;
    items: NavItem[];
}

export const NAV_STRUCTURE: NavSection[] = [
  {
    title: 'فضای کاری',
    items: [
      { id: 'dashboard', label: 'داشبورد', icon: LayoutDashboard },
      { id: 'all', label: 'همه پرامپت‌ها', icon: Folders },
    ],
  },
  {
    title: 'کتابخانه شما',
    items: [
      { id: 'image', label: 'تصویر', icon: Image },
      { id: 'text', label: 'متن', icon: FileText },
      { id: 'video', label: 'ویدیو', icon: Video },
      { id: 'music', label: 'موسیقی', icon: Music },
    ],
  },
  {
    title: 'استودیو',
    items: [
        { id: 'creative-studios', label: 'استودیو خلاقیت', icon: Sparkles },
    ],
  },
  {
    title: 'ابزارهای پیشرفته',
    items: [
      { id: 'prompt-chains', label: 'زنجیره پرامپت', icon: Link },
      { id: 'prompt-lab', label: 'آزمایشگاه پرامپت', icon: Beaker },
      { id: 'inspiration', label: 'مرکز الهام‌بخش', icon: Sparkles },
      { id: 'assistant', label: 'دستیار AI', icon: Bot },
    ],
  },
];