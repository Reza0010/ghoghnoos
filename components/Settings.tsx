import React, { useState } from 'react';
import { UserSettings } from '../types';
import { 
  Settings as SettingsIcon, 
  Sun, 
  Moon, 
  Monitor,
  Download,
  Upload,
  Save,
  RefreshCw,
  Key,
  Palette,
  Globe
} from './icons';

interface SettingsProps {
  settings: UserSettings;
  onSettingsChange: (settings: UserSettings) => void;
  onImport: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onExport: () => void;
}

export const Settings: React.FC<SettingsProps> = ({
  settings,
  onSettingsChange,
  onImport,
  onExport
}) => {
  const [activeTab, setActiveTab] = useState<'general' | 'api' | 'data'>('general');
  const [tempSettings, setTempSettings] = useState(settings);

  const handleSave = () => {
    onSettingsChange(tempSettings);
  };

  const handleReset = () => {
    setTempSettings(settings);
  };

  const themeOptions = [
    { value: 'light', label: 'Light', icon: Sun },
    { value: 'dark', label: 'Dark', icon: Moon },
    { value: 'system', label: 'System', icon: Monitor }
  ];

  const languageOptions = [
    { value: 'en', label: 'English' },
    { value: 'fa', label: 'فارسی (Persian)' }
  ];

  const fontSizeOptions = [
    { value: 'sm', label: 'Small' },
    { value: 'md', label: 'Medium' },
    { value: 'lg', label: 'Large' }
  ];

  return (
    <div className="main-content">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center space-x-3 mb-8">
          <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-gray-500 to-gray-700 rounded-xl">
            <SettingsIcon size={20} className="text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Settings
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Customize your Prompt Studio experience
            </p>
          </div>
        </div>

        {/* Tabs */}
        <div className="tabs mb-6">
          <button
            onClick={() => setActiveTab('general')}
            className={`tab ${activeTab === 'general' ? 'active' : ''}`}
          >
            <Palette size={16} />
            <span className="ml-2">General</span>
          </button>
          <button
            onClick={() => setActiveTab('api')}
            className={`tab ${activeTab === 'api' ? 'active' : ''}`}
          >
            <Key size={16} />
            <span className="ml-2">API Keys</span>
          </button>
          <button
            onClick={() => setActiveTab('data')}
            className={`tab ${activeTab === 'data' ? 'active' : ''}`}
          >
            <Download size={16} />
            <span className="ml-2">Data</span>
          </button>
        </div>

        {/* General Settings */}
        {activeTab === 'general' && (
          <div className="space-y-6">
            {/* Appearance */}
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Appearance
                </h2>
              </div>
              <div className="card-body space-y-6">
                {/* Theme */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Theme
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {themeOptions.map(option => {
                      const Icon = option.icon;
                      return (
                        <button
                          key={option.value}
                          onClick={() => setTempSettings(prev => ({ ...prev, theme: option.value as any }))}
                          className={`p-4 border rounded-lg transition-all ${
                            tempSettings.theme === option.value
                              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                              : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                          }`}
                        >
                          <Icon size={24} className="mx-auto mb-2" />
                          <p className="text-sm font-medium">{option.label}</p>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Language */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Language
                  </label>
                  <select
                    value={tempSettings.language}
                    onChange={(e) => setTempSettings(prev => ({ ...prev, language: e.target.value as any }))}
                    className="select"
                  >
                    {languageOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Font Size */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Font Size
                  </label>
                  <select
                    value={tempSettings.fontSize}
                    onChange={(e) => setTempSettings(prev => ({ ...prev, fontSize: e.target.value as any }))}
                    className="select"
                  >
                    {fontSizeOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Behavior */}
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Behavior
                </h2>
              </div>
              <div className="card-body space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">
                      Auto-save
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Automatically save changes as you work
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={tempSettings.autoSave}
                      onChange={(e) => setTempSettings(prev => ({ ...prev, autoSave: e.target.checked }))}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">
                      Show line numbers
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Display line numbers in prompt editors
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={tempSettings.showLineNumbers}
                      onChange={(e) => setTempSettings(prev => ({ ...prev, showLineNumbers: e.target.checked }))}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* API Settings */}
        {activeTab === 'api' && (
          <div className="space-y-6">
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  API Configuration
                </h2>
              </div>
              <div className="card-body space-y-6">
                {/* OpenAI */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    OpenAI API Key
                  </label>
                  <input
                    type="password"
                    value={tempSettings.apiConfig.openaiKey || ''}
                    onChange={(e) => setTempSettings(prev => ({
                      ...prev,
                      apiConfig: { ...prev.apiConfig, openaiKey: e.target.value }
                    }))}
                    className="input"
                    placeholder="sk-..."
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Required for GPT models. Get your key from OpenAI dashboard.
                  </p>
                </div>

                {/* Gemini */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Gemini API Key
                  </label>
                  <input
                    type="password"
                    value={tempSettings.apiConfig.geminiKey || ''}
                    onChange={(e) => setTempSettings(prev => ({
                      ...prev,
                      apiConfig: { ...prev.apiConfig, geminiKey: e.target.value }
                    }))}
                    className="input"
                    placeholder="AI..."
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Required for Gemini models. Get your key from Google AI Studio.
                  </p>
                </div>

                {/* Claude */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Claude API Key
                  </label>
                  <input
                    type="password"
                    value={tempSettings.apiConfig.claudeKey || ''}
                    onChange={(e) => setTempSettings(prev => ({
                      ...prev,
                      apiConfig: { ...prev.apiConfig, claudeKey: e.target.value }
                    }))}
                    className="input"
                    placeholder="sk-ant-..."
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Required for Claude models. Get your key from Anthropic console.
                  </p>
                </div>

                {/* Default Model */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Default Model
                  </label>
                  <select
                    value={tempSettings.apiConfig.defaultModel}
                    onChange={(e) => setTempSettings(prev => ({
                      ...prev,
                      apiConfig: { ...prev.apiConfig, defaultModel: e.target.value }
                    }))}
                    className="select"
                  >
                    <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                    <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                    <option value="gpt-4">GPT-4</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  </select>
                </div>

                {/* Default Parameters */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Default Temperature: {tempSettings.apiConfig.defaultTemperature}
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="2"
                      step="0.1"
                      value={tempSettings.apiConfig.defaultTemperature}
                      onChange={(e) => setTempSettings(prev => ({
                        ...prev,
                        apiConfig: { ...prev.apiConfig, defaultTemperature: parseFloat(e.target.value) }
                      }))}
                      className="w-full"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Default Max Tokens
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="8192"
                      value={tempSettings.apiConfig.defaultMaxTokens}
                      onChange={(e) => setTempSettings(prev => ({
                        ...prev,
                        apiConfig: { ...prev.apiConfig, defaultMaxTokens: parseInt(e.target.value) }
                      }))}
                      className="input"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Data Management */}
        {activeTab === 'data' && (
          <div className="space-y-6">
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Data Management
                </h2>
              </div>
              <div className="card-body space-y-6">
                {/* Export */}
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                    Export Data
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Download all your prompts, experiments, and settings as a JSON file.
                  </p>
                  <button onClick={onExport} className="btn btn-secondary">
                    <Download size={16} />
                    <span className="ml-2">Export All Data</span>
                  </button>
                </div>

                {/* Import */}
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                    Import Data
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Import prompts and settings from a previously exported JSON file.
                  </p>
                  <label className="btn btn-secondary cursor-pointer">
                    <Upload size={16} />
                    <span className="ml-2">Import Data</span>
                    <input
                      type="file"
                      accept=".json"
                      onChange={onImport}
                      className="hidden"
                    />
                  </label>
                </div>

                {/* Reset */}
                <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
                  <h3 className="font-medium text-red-600 dark:text-red-400 mb-2">
                    Reset Settings
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Reset all settings to their default values. This action cannot be undone.
                  </p>
                  <button className="btn btn-danger">
                    <RefreshCw size={16} />
                    <span className="ml-2">Reset to Defaults</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 mt-8">
          <button
            onClick={handleReset}
            className="btn btn-secondary"
          >
            <RefreshCw size={16} />
            <span className="ml-2">Reset Changes</span>
          </button>
          <button
            onClick={handleSave}
            className="btn btn-primary"
          >
            <Save size={16} />
            <span className="ml-2">Save Settings</span>
          </button>
        </div>
      </div>
    </div>
  );
};