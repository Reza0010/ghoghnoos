// Core Types
export interface Prompt {
  id: string;
  title: string;
  content: string;
  description?: string;
  type: 'text' | 'image';
  tags: string[];
  category: string;
  isFavorite: boolean;
  createdAt: Date;
  updatedAt: Date;
  usageCount: number;
  lastUsed?: Date;
}

export interface ExperimentResult {
  id: string;
  promptId: string;
  model: string;
  temperature: number;
  maxTokens?: number;
  response: string;
  timestamp: Date;
  executionTime: number;
  tokenUsage?: {
    prompt: number;
    completion: number;
    total: number;
  };
}

export interface AIModel {
  id: string;
  name: string;
  provider: 'openai' | 'gemini' | 'claude' | 'local';
  type: 'text' | 'image' | 'multimodal';
  maxTokens: number;
  supportedFeatures: string[];
}

export interface APIConfiguration {
  openaiKey?: string;
  geminiKey?: string;
  claudeKey?: string;
  defaultModel: string;
  defaultTemperature: number;
  defaultMaxTokens: number;
}

export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  language: 'en' | 'fa';
  autoSave: boolean;
  showLineNumbers: boolean;
  fontSize: 'sm' | 'md' | 'lg';
  apiConfig: APIConfiguration;
  shortcuts: Record<string, string>;
}

export interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  template: string;
  variables: string[];
  category: string;
  tags: string[];
  isBuiltIn: boolean;
}

export interface ImageGenerationResult {
  id: string;
  promptId: string;
  prompt: string;
  imageUrl: string;
  model: string;
  parameters: {
    width: number;
    height: number;
    steps: number;
    guidance: number;
    seed?: number;
  };
  timestamp: Date;
}

export interface PromptComparison {
  id: string;
  name: string;
  prompts: {
    promptId: string;
    title: string;
    content: string;
  }[];
  model: string;
  parameters: {
    temperature: number;
    maxTokens: number;
  };
  results: {
    promptId: string;
    response: string;
    executionTime: number;
    timestamp: Date;
  }[];
  createdAt: Date;
}

export interface InspirationPrompt {
  id: string;
  title: string;
  content: string;
  description: string;
  category: string;
  tags: string[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  useCase: string;
  example?: string;
  author?: string;
}

export interface AppState {
  prompts: Prompt[];
  experiments: ExperimentResult[];
  templates: PromptTemplate[];
  comparisons: PromptComparison[];
  imageResults: ImageGenerationResult[];
  settings: UserSettings;
  currentView: 'dashboard' | 'studio' | 'lab' | 'assistant' | 'image' | 'inspiration' | 'settings';
  isLoading: boolean;
  error?: string;
}

// UI Component Props
export interface PromptCardProps {
  prompt: Prompt;
  onEdit: (prompt: Prompt) => void;
  onDelete: (id: string) => void;
  onToggleFavorite: (id: string) => void;
  onUse: (prompt: Prompt) => void;
}

export interface ExperimentFormProps {
  prompt: Prompt;
  onRun: (config: ExperimentConfig) => void;
  isLoading: boolean;
}

export interface ExperimentConfig {
  model: string;
  temperature: number;
  maxTokens: number;
  prompt: string;
}

// Utility Types
export type SortOption = 'newest' | 'oldest' | 'alphabetical' | 'mostUsed' | 'lastUsed';
export type FilterOption = 'all' | 'favorites' | 'text' | 'image' | 'recent';

export interface SearchFilters {
  query: string;
  tags: string[];
  category: string;
  type: 'all' | 'text' | 'image';
  sortBy: SortOption;
  showFavorites: boolean;
}

// API Response Types
export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface GenerationResponse {
  text?: string;
  imageUrl?: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  model: string;
  executionTime: number;
}

// Storage Types
export interface StorageData {
  prompts: Prompt[];
  experiments: ExperimentResult[];
  templates: PromptTemplate[];
  comparisons: PromptComparison[];
  imageResults: ImageGenerationResult[];
  settings: UserSettings;
  version: string;
  exportDate: Date;
}

// Event Types
export interface PromptEvent {
  type: 'create' | 'update' | 'delete' | 'use';
  promptId: string;
  timestamp: Date;
  details?: any;
}

// Theme Types
export interface ThemeColors {
  primary: string;
  secondary: string;
  background: string;
  surface: string;
  text: string;
  textSecondary: string;
  border: string;
  accent: string;
}

export interface Theme {
  name: string;
  colors: ThemeColors;
  isDark: boolean;
}

// Legacy types for backward compatibility
export enum PromptType {
  Image = 'image',
  Text = 'text',
  Video = 'video',
  Music = 'music',
}

export interface ChatMessage {
  role: 'user' | 'model';
  text: string;
}

export interface GeminiContent {
  role: 'user' | 'model';
  parts: { text: string }[];
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
  promptType: PromptType.Image;
  variations: PromptVariation[];
  createdAt: string;
  status: 'running' | 'completed';
}