export enum PromptType {
  Image = 'image',
  Text = 'text',
  Video = 'video',
  Music = 'music',
}

export interface PromptVersion {
  content: string;
  summary?: string;
  createdAt: string; // The date this version was created (from the prompt's updatedAt)
}

export interface Prompt {
  id: string;
  title: string;
  content: string;
  type: PromptType;
  tags: string[];
  createdAt: string;
  updatedAt: string;
  summary?: string;
  rating?: number;
  imageUrl?: string;
  history?: PromptVersion[];
}

export interface ChatMessage {
  role: 'user' | 'model';
  text: string;
}

export interface GeminiContent {
  role: 'user' | 'model';
  parts: Array<{ text: string }>;
}

export interface PromptVariation {
    id: string;
    content: string;
    outputUrl?: string;
    isWinner: boolean;
}

export interface PromptExperiment {
    id: string;
    title: string;
    goal: string;
    promptType: PromptType;
    status: 'running' | 'completed';
    variations: PromptVariation[];
    createdAt: string;
}

export type SocialPlatform = 'instagram' | 'telegram' | 'twitter';

export type Language = 'en' | 'fa';

export type ImportMode = 'merge' | 'replace';
