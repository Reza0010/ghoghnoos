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

// For Gemini API history
export interface GeminiContent {
  role: 'user' | 'model';
  parts: { text: string }[];
}

// --- A/B Testing Types ---

export interface PromptVariation {
  id: string;
  content: string;
  outputUrl?: string; // for image prompts
  isWinner: boolean;
}

export interface PromptExperiment {
  id: string;
  title: string;
  goal: string;
  promptType: PromptType.Image; // For now, only support image
  variations: PromptVariation[];
  createdAt: string;
  status: 'running' | 'completed';
}
