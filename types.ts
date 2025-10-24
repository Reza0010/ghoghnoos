export enum PromptType {
  Image = 'image',
  Text = 'text',
  Video = 'video',
  Music = 'music',
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
