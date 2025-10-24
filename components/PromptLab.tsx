import React, { useState } from 'react';
import { Prompt, ExperimentConfig, ExperimentResult } from '../types';
import { 
  Play, 
  Settings, 
  BarChart, 
  Clock, 
  Zap,
  Copy,
  Download,
  RefreshCw
} from './icons';
import { AI_MODELS } from '../constants';

interface PromptLabProps {
  prompts: Prompt[];
}

export const PromptLab: React.FC<PromptLabProps> = ({ prompts }) => {
  const [selectedPrompts, setSelectedPrompts] = useState<string[]>([]);
  const [experimentConfig, setExperimentConfig] = useState<ExperimentConfig>({
    model: 'gemini-1.5-flash',
    temperature: 0.7,
    maxTokens: 2048,
    prompt: ''
  });
  const [results, setResults] = useState<ExperimentResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [activeTab, setActiveTab] = useState<'setup' | 'results' | 'comparison'>('setup');

  const handlePromptSelection = (promptId: string) => {
    setSelectedPrompts(prev => 
      prev.includes(promptId) 
        ? prev.filter(id => id !== promptId)
        : [...prev, promptId]
    );
  };

  const handleRunExperiment = async () => {
    if (selectedPrompts.length === 0 && !experimentConfig.prompt.trim()) {
      return;
    }

    setIsRunning(true);
    setActiveTab('results');

    try {
      // Simulate API calls for each selected prompt
      const newResults: ExperimentResult[] = [];

      if (experimentConfig.prompt.trim()) {
        // Run single prompt
        const result = await simulateAPICall(experimentConfig.prompt, experimentConfig);
        newResults.push(result);
      }

      // Run selected prompts
      for (const promptId of selectedPrompts) {
        const prompt = prompts.find(p => p.id === promptId);
        if (prompt) {
          const result = await simulateAPICall(prompt.content, experimentConfig);
          result.promptId = promptId;
          newResults.push(result);
        }
      }

      setResults(newResults);
    } catch (error) {
      console.error('Experiment failed:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const simulateAPICall = async (prompt: string, config: ExperimentConfig): Promise<ExperimentResult> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

    // Simulate response
    const responses = [
      "This is a simulated response from the AI model. In a real implementation, this would be the actual response from the selected AI model.",
      "Here's another example response that demonstrates how the AI might interpret and respond to your prompt with different parameters.",
      "The AI model has processed your prompt and generated this response based on the specified temperature and token settings.",
      "This response showcases the variability in AI outputs when using different configurations and prompts."
    ];

    return {
      id: crypto.randomUUID(),
      promptId: '',
      model: config.model,
      temperature: config.temperature,
      maxTokens: config.maxTokens,
      response: responses[Math.floor(Math.random() * responses.length)],
      timestamp: new Date(),
      executionTime: Math.floor(1000 + Math.random() * 3000), // 1-4 seconds
      tokenUsage: {
        prompt: Math.floor(50 + Math.random() * 200),
        completion: Math.floor(100 + Math.random() * 500),
        total: 0
      }
    };
  };

  const handleExportResults = () => {
    const exportData = {
      experiment: {
        config: experimentConfig,
        selectedPrompts: selectedPrompts.map(id => prompts.find(p => p.id === id)),
        timestamp: new Date().toISOString()
      },
      results
    };

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `prompt-lab-results-${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const renderSetupTab = () => (
    <div className="space-y-6">
      {/* Experiment Configuration */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Experiment Configuration
          </h2>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                AI Model
              </label>
              <select
                value={experimentConfig.model}
                onChange={(e) => setExperimentConfig(prev => ({ ...prev, model: e.target.value }))}
                className="select"
              >
                {AI_MODELS.map(model => (
                  <option key={model.id} value={model.id}>
                    {model.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Temperature: {experimentConfig.temperature}
              </label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={experimentConfig.temperature}
                onChange={(e) => setExperimentConfig(prev => ({ ...prev, temperature: parseFloat(e.target.value) }))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Focused</span>
                <span>Balanced</span>
                <span>Creative</span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Max Tokens
              </label>
              <input
                type="number"
                min="1"
                max="8192"
                value={experimentConfig.maxTokens}
                onChange={(e) => setExperimentConfig(prev => ({ ...prev, maxTokens: parseInt(e.target.value) }))}
                className="input"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Custom Prompt */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Custom Prompt
          </h2>
        </div>
        <div className="card-body">
          <textarea
            value={experimentConfig.prompt}
            onChange={(e) => setExperimentConfig(prev => ({ ...prev, prompt: e.target.value }))}
            className="textarea min-h-[120px]"
            placeholder="Enter a custom prompt to test, or select prompts from your library below..."
          />
        </div>
      </div>

      {/* Prompt Selection */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Select Prompts to Test
            </h2>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {selectedPrompts.length} selected
            </span>
          </div>
        </div>
        <div className="card-body">
          {prompts.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500 dark:text-gray-400">
                No prompts available. Create some prompts first to test them here.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-96 overflow-y-auto">
              {prompts.map(prompt => (
                <div
                  key={prompt.id}
                  className={`p-4 border rounded-lg cursor-pointer transition-all ${
                    selectedPrompts.includes(prompt.id)
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                  onClick={() => handlePromptSelection(prompt.id)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-medium text-gray-900 dark:text-white text-sm">
                      {prompt.title}
                    </h3>
                    <input
                      type="checkbox"
                      checked={selectedPrompts.includes(prompt.id)}
                      onChange={() => handlePromptSelection(prompt.id)}
                      className="ml-2"
                    />
                  </div>
                  <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2">
                    {prompt.content}
                  </p>
                  <div className="flex items-center justify-between mt-2">
                    <span className={`text-xs px-2 py-1 rounded ${
                      prompt.type === 'text' 
                        ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                        : 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300'
                    }`}>
                      {prompt.type}
                    </span>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {prompt.category}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Run Experiment Button */}
      <div className="flex justify-center">
        <button
          onClick={handleRunExperiment}
          disabled={isRunning || (selectedPrompts.length === 0 && !experimentConfig.prompt.trim())}
          className="btn btn-primary btn-lg"
        >
          {isRunning ? (
            <div className="loading-spinner" />
          ) : (
            <Play size={20} />
          )}
          <span className="ml-2">
            {isRunning ? 'Running Experiment...' : 'Run Experiment'}
          </span>
        </button>
      </div>
    </div>
  );

  const renderResultsTab = () => (
    <div className="space-y-6">
      {/* Results Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Experiment Results
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            {results.length} result(s) from your experiment
          </p>
        </div>
        
        {results.length > 0 && (
          <div className="flex space-x-2">
            <button
              onClick={handleExportResults}
              className="btn btn-secondary btn-sm"
            >
              <Download size={16} />
              <span className="ml-2">Export</span>
            </button>
            <button
              onClick={() => setResults([])}
              className="btn btn-ghost btn-sm"
            >
              <RefreshCw size={16} />
              <span className="ml-2">Clear</span>
            </button>
          </div>
        )}
      </div>

      {/* Results List */}
      {results.length === 0 ? (
        <div className="card">
          <div className="card-body text-center py-12">
            <BarChart size={48} className="mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No Results Yet
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Run an experiment to see results here.
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {results.map((result, index) => {
            const prompt = result.promptId ? prompts.find(p => p.id === result.promptId) : null;
            
            return (
              <div key={result.id} className="card">
                <div className="card-header">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white">
                        {prompt ? prompt.title : `Custom Prompt ${index + 1}`}
                      </h3>
                      <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400 mt-1">
                        <span>{result.model}</span>
                        <span>Temperature: {result.temperature}</span>
                        <span>Tokens: {result.maxTokens}</span>
                        <div className="flex items-center space-x-1">
                          <Clock size={12} />
                          <span>{result.executionTime}ms</span>
                        </div>
                      </div>
                    </div>
                    
                    <button
                      onClick={() => navigator.clipboard.writeText(result.response)}
                      className="btn btn-ghost btn-sm"
                      title="Copy response"
                    >
                      <Copy size={16} />
                    </button>
                  </div>
                </div>
                
                <div className="card-body">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                        Input Prompt
                      </h4>
                      <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                          {prompt ? prompt.content : experimentConfig.prompt}
                        </p>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                        AI Response
                      </h4>
                      <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                          {result.response}
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  {/* Token Usage */}
                  {result.tokenUsage && (
                    <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400">Token Usage:</span>
                        <div className="flex space-x-4">
                          <span>Prompt: {result.tokenUsage.prompt}</span>
                          <span>Completion: {result.tokenUsage.completion}</span>
                          <span className="font-medium">Total: {result.tokenUsage.prompt + result.tokenUsage.completion}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );

  const renderComparisonTab = () => (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Results Comparison
          </h2>
        </div>
        <div className="card-body">
          {results.length < 2 ? (
            <div className="text-center py-8">
              <BarChart size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-gray-500 dark:text-gray-400">
                Run experiments with multiple prompts to compare results.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">Prompt</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">Model</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">Temperature</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">Execution Time</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">Tokens</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">Response Length</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((result) => {
                    const prompt = result.promptId ? prompts.find(p => p.id === result.promptId) : null;
                    return (
                      <tr key={result.id} className="border-b border-gray-100 dark:border-gray-800">
                        <td className="py-3 px-4">
                          <div className="font-medium text-gray-900 dark:text-white">
                            {prompt ? prompt.title : 'Custom Prompt'}
                          </div>
                        </td>
                        <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                          {result.model}
                        </td>
                        <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                          {result.temperature}
                        </td>
                        <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                          {result.executionTime}ms
                        </td>
                        <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                          {result.tokenUsage ? result.tokenUsage.prompt + result.tokenUsage.completion : 'N/A'}
                        </td>
                        <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                          {result.response.length} chars
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="main-content">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Prompt Lab
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Test, compare, and optimize your prompts with different AI models and parameters
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <Zap className="text-primary-500" size={24} />
          </div>
        </div>

        {/* Tabs */}
        <div className="tabs mb-6">
          <button
            onClick={() => setActiveTab('setup')}
            className={`tab ${activeTab === 'setup' ? 'active' : ''}`}
          >
            <Settings size={16} />
            <span className="ml-2">Setup</span>
          </button>
          <button
            onClick={() => setActiveTab('results')}
            className={`tab ${activeTab === 'results' ? 'active' : ''}`}
          >
            <BarChart size={16} />
            <span className="ml-2">Results</span>
            {results.length > 0 && (
              <span className="ml-1 px-2 py-1 text-xs bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-300 rounded-full">
                {results.length}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('comparison')}
            className={`tab ${activeTab === 'comparison' ? 'active' : ''}`}
          >
            <BarChart size={16} />
            <span className="ml-2">Comparison</span>
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'setup' && renderSetupTab()}
        {activeTab === 'results' && renderResultsTab()}
        {activeTab === 'comparison' && renderComparisonTab()}
      </div>
    </div>
  );
};