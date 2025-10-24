import React from 'react';
import { AIModel, UserSettings, PromptTemplate, InspirationPrompt } from './types';
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
  Palette,
  Lightbulb,
} from './components/icons';

type IconComponent = React.FC<React.SVGProps<SVGSVGElement>>;

// API Configuration
export const GEMINI_API_KEY = process.env.GEMINI_API_KEY || '';
export const GEMINI_MODEL = 'gemini-1.5-flash-latest';

// Available AI Models
export const AI_MODELS: AIModel[] = [
  {
    id: 'gemini-1.5-flash',
    name: 'Gemini 1.5 Flash',
    provider: 'gemini',
    type: 'multimodal',
    maxTokens: 8192,
    supportedFeatures: ['text', 'image', 'vision']
  },
  {
    id: 'gemini-1.5-pro',
    name: 'Gemini 1.5 Pro',
    provider: 'gemini',
    type: 'multimodal',
    maxTokens: 32768,
    supportedFeatures: ['text', 'image', 'vision', 'long-context']
  },
  {
    id: 'gpt-4',
    name: 'GPT-4',
    provider: 'openai',
    type: 'text',
    maxTokens: 8192,
    supportedFeatures: ['text', 'function-calling']
  },
  {
    id: 'gpt-3.5-turbo',
    name: 'GPT-3.5 Turbo',
    provider: 'openai',
    type: 'text',
    maxTokens: 4096,
    supportedFeatures: ['text', 'function-calling']
  }
];

// Navigation Items
export const NAV_ITEMS: { id: string; label: string; icon: IconComponent }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'studio', label: 'Prompt Studio', icon: FileText },
  { id: 'lab', label: 'Prompt Lab', icon: Beaker },
  { id: 'assistant', label: 'AI Assistant', icon: Bot },
  { id: 'image', label: 'Image Studio', icon: Palette },
  { id: 'inspiration', label: 'Inspiration Hub', icon: Lightbulb },
  { id: 'settings', label: 'Settings', icon: SettingsIcon },
];

// Prompt Type Configuration
export const PROMPT_TYPE_CONFIG = {
  text: {
    label: 'Text Prompt',
    icon: FileText,
    color: 'bg-blue-500',
    textColor: 'text-blue-500',
    borderColor: 'border-blue-500',
  },
  image: {
    label: 'Image Prompt',
    icon: Image,
    color: 'bg-purple-500',
    textColor: 'text-purple-500',
    borderColor: 'border-purple-500',
  },
};

// Default Categories
export const DEFAULT_PROMPT_CATEGORIES = [
  'Creative Writing',
  'Code Generation',
  'Data Analysis',
  'Marketing',
  'Education',
  'Research',
  'Image Generation',
  'Content Creation',
  'Problem Solving',
  'Other'
];

// Built-in Prompt Templates
export const BUILT_IN_TEMPLATES: PromptTemplate[] = [
  {
    id: 'creative-story',
    name: 'Creative Story Writer',
    description: 'Generate creative stories with specific themes and characters',
    template: 'Write a {{genre}} story about {{character}} who {{situation}}. The story should be {{length}} and have a {{tone}} tone.',
    variables: ['genre', 'character', 'situation', 'length', 'tone'],
    category: 'Creative Writing',
    tags: ['story', 'creative', 'fiction'],
    isBuiltIn: true
  },
  {
    id: 'code-generator',
    name: 'Code Generator',
    description: 'Generate code in various programming languages',
    template: 'Generate {{language}} code that {{functionality}}. The code should be {{style}} and include {{requirements}}.',
    variables: ['language', 'functionality', 'style', 'requirements'],
    category: 'Code Generation',
    tags: ['code', 'programming', 'development'],
    isBuiltIn: true
  },
  {
    id: 'data-analyst',
    name: 'Data Analysis Assistant',
    description: 'Analyze data and provide insights',
    template: 'Analyze the following {{data_type}} data and provide insights about {{focus_area}}. Include {{analysis_type}} and suggest {{recommendations}}.',
    variables: ['data_type', 'focus_area', 'analysis_type', 'recommendations'],
    category: 'Data Analysis',
    tags: ['data', 'analysis', 'insights'],
    isBuiltIn: true
  },
  {
    id: 'marketing-copy',
    name: 'Marketing Copy Creator',
    description: 'Create compelling marketing content',
    template: 'Create {{content_type}} for {{product}} targeting {{audience}}. The tone should be {{tone}} and highlight {{benefits}}.',
    variables: ['content_type', 'product', 'audience', 'tone', 'benefits'],
    category: 'Marketing',
    tags: ['marketing', 'copy', 'content'],
    isBuiltIn: true
  },
  {
    id: 'image-prompt',
    name: 'Image Generation Prompt',
    description: 'Create detailed prompts for AI image generation',
    template: 'Create a {{style}} image of {{subject}} in {{setting}}. Use {{colors}} color palette, {{lighting}} lighting, and {{composition}} composition. Style: {{art_style}}',
    variables: ['style', 'subject', 'setting', 'colors', 'lighting', 'composition', 'art_style'],
    category: 'Image Generation',
    tags: ['image', 'art', 'visual'],
    isBuiltIn: true
  }
];

// Inspiration Prompts
export const INSPIRATION_PROMPTS: InspirationPrompt[] = [
  {
    id: 'storyteller',
    title: 'Master Storyteller',
    content: 'You are a master storyteller with decades of experience. Create an engaging narrative that captivates readers from the first sentence to the last.',
    description: 'Perfect for creative writing and narrative generation',
    category: 'Creative Writing',
    tags: ['storytelling', 'narrative', 'creative'],
    difficulty: 'intermediate',
    useCase: 'Generate compelling stories and narratives',
    example: 'Write a mystery story set in Victorian London...',
    author: 'Prompt Studio'
  },
  {
    id: 'code-architect',
    title: 'Senior Software Architect',
    content: 'You are a senior software architect with expertise in multiple programming languages and design patterns. Provide clean, efficient, and well-documented code solutions.',
    description: 'Ideal for complex coding tasks and architecture decisions',
    category: 'Code Generation',
    tags: ['programming', 'architecture', 'best-practices'],
    difficulty: 'advanced',
    useCase: 'Generate high-quality code and architectural solutions',
    example: 'Design a scalable microservices architecture for...',
    author: 'Prompt Studio'
  },
  {
    id: 'data-scientist',
    title: 'Expert Data Scientist',
    content: 'You are an expert data scientist with deep knowledge of statistics, machine learning, and data visualization. Provide clear insights and actionable recommendations.',
    description: 'Perfect for data analysis and machine learning tasks',
    category: 'Data Analysis',
    tags: ['data-science', 'analytics', 'insights'],
    difficulty: 'advanced',
    useCase: 'Analyze complex datasets and provide insights',
    example: 'Analyze customer behavior patterns in...',
    author: 'Prompt Studio'
  },
  {
    id: 'marketing-guru',
    title: 'Marketing Strategy Expert',
    content: 'You are a marketing strategy expert with proven success in digital marketing, brand building, and customer acquisition. Create compelling and effective marketing content.',
    description: 'Great for marketing campaigns and brand messaging',
    category: 'Marketing',
    tags: ['marketing', 'strategy', 'branding'],
    difficulty: 'intermediate',
    useCase: 'Develop marketing strategies and create compelling copy',
    example: 'Create a marketing campaign for...',
    author: 'Prompt Studio'
  },
  {
    id: 'visual-artist',
    title: 'Digital Art Director',
    content: 'You are a creative digital art director with expertise in visual composition, color theory, and artistic styles. Create detailed descriptions for stunning visual artwork.',
    description: 'Excellent for image generation and visual content',
    category: 'Image Generation',
    tags: ['art', 'visual', 'creative'],
    difficulty: 'intermediate',
    useCase: 'Generate detailed prompts for AI image creation',
    example: 'Create a surreal landscape featuring...',
    author: 'Prompt Studio'
  }
];

// Default User Settings
export const DEFAULT_SETTINGS: UserSettings = {
  theme: 'system',
  language: 'en',
  autoSave: true,
  showLineNumbers: true,
  fontSize: 'md',
  apiConfig: {
    defaultModel: 'gemini-1.5-flash',
    defaultTemperature: 0.7,
    defaultMaxTokens: 2048
  },
  shortcuts: {
    'save': 'Ctrl+S',
    'new': 'Ctrl+N',
    'search': 'Ctrl+F',
    'run': 'Ctrl+Enter'
  }
};

// Application Configuration
export const APP_CONFIG = {
  name: 'Prompt Studio',
  version: '1.0.0',
  description: 'A comprehensive AI prompt management and testing platform',
  maxPrompts: 10000,
  maxExperiments: 1000,
  maxFileSize: 10 * 1024 * 1024, // 10MB
  supportedImageFormats: ['jpg', 'jpeg', 'png', 'webp', 'gif'],
  autoSaveInterval: 30000, // 30 seconds
  debounceDelay: 500, // 500ms
};

// UI Constants
export const SIDEBAR_WIDTH = 280;
export const HEADER_HEIGHT = 64;
export const ANIMATION_DURATION = 300;

// Storage Keys
export const STORAGE_KEYS = {
  prompts: 'prompt-studio-prompts',
  experiments: 'prompt-studio-experiments',
  templates: 'prompt-studio-templates',
  comparisons: 'prompt-studio-comparisons',
  imageResults: 'prompt-studio-images',
  settings: 'prompt-studio-settings',
  theme: 'prompt-studio-theme',
  apiKeys: 'prompt-studio-api-keys'
};

// Error Messages
export const ERROR_MESSAGES = {
  apiKeyMissing: 'API key is required. Please configure it in Settings.',
  networkError: 'Network error. Please check your connection.',
  invalidPrompt: 'Please enter a valid prompt.',
  generationFailed: 'Failed to generate response. Please try again.',
  saveFailed: 'Failed to save data. Please try again.',
  loadFailed: 'Failed to load data.',
  exportFailed: 'Failed to export data.',
  importFailed: 'Failed to import data. Please check the file format.'
};

// Success Messages
export const SUCCESS_MESSAGES = {
  promptSaved: 'Prompt saved successfully!',
  promptDeleted: 'Prompt deleted successfully!',
  experimentCompleted: 'Experiment completed successfully!',
  settingsSaved: 'Settings saved successfully!',
  dataExported: 'Data exported successfully!',
  dataImported: 'Data imported successfully!'
};