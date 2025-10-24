import React, { useState } from 'react';
import { 
  Image as ImageIcon, 
  Play, 
  Download, 
  RefreshCw, 
  Settings,
  Palette,
  Wand2
} from './icons';

export const ImageRemixStudio: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImages, setGeneratedImages] = useState<string[]>([]);
  const [settings, setSettings] = useState({
    style: 'realistic',
    aspectRatio: '1:1',
    quality: 'standard',
    steps: 20,
    guidance: 7.5
  });

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setIsGenerating(true);
    
    // Simulate image generation
    setTimeout(() => {
      // Add placeholder images
      const newImages = [
        'https://via.placeholder.com/512x512/6366f1/ffffff?text=Generated+Image+1',
        'https://via.placeholder.com/512x512/8b5cf6/ffffff?text=Generated+Image+2',
        'https://via.placeholder.com/512x512/06b6d4/ffffff?text=Generated+Image+3',
        'https://via.placeholder.com/512x512/10b981/ffffff?text=Generated+Image+4'
      ];
      setGeneratedImages(newImages);
      setIsGenerating(false);
    }, 3000);
  };

  const styleOptions = [
    { value: 'realistic', label: 'Realistic' },
    { value: 'artistic', label: 'Artistic' },
    { value: 'cartoon', label: 'Cartoon' },
    { value: 'abstract', label: 'Abstract' },
    { value: 'vintage', label: 'Vintage' },
    { value: 'futuristic', label: 'Futuristic' }
  ];

  const aspectRatios = [
    { value: '1:1', label: 'Square (1:1)' },
    { value: '16:9', label: 'Landscape (16:9)' },
    { value: '9:16', label: 'Portrait (9:16)' },
    { value: '4:3', label: 'Standard (4:3)' }
  ];

  return (
    <div className="main-content">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center space-x-3 mb-8">
          <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl">
            <Palette size={20} className="text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Image Remix Studio
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Generate stunning images from your text prompts
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Input Panel */}
          <div className="lg:col-span-1 space-y-6">
            {/* Prompt Input */}
            <div className="card">
              <div className="card-header">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Image Prompt
                </h2>
              </div>
              <div className="card-body">
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  className="textarea min-h-[120px]"
                  placeholder="Describe the image you want to generate. Be specific about style, composition, colors, lighting, and details..."
                />
                <div className="mt-4">
                  <button
                    onClick={handleGenerate}
                    disabled={isGenerating || !prompt.trim()}
                    className="btn btn-primary w-full"
                  >
                    {isGenerating ? (
                      <div className="loading-spinner" />
                    ) : (
                      <Wand2 size={16} />
                    )}
                    <span className="ml-2">
                      {isGenerating ? 'Generating...' : 'Generate Images'}
                    </span>
                  </button>
                </div>
              </div>
            </div>

            {/* Settings */}
            <div className="card">
              <div className="card-header">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Generation Settings
                </h2>
              </div>
              <div className="card-body space-y-4">
                {/* Style */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Style
                  </label>
                  <select
                    value={settings.style}
                    onChange={(e) => setSettings(prev => ({ ...prev, style: e.target.value }))}
                    className="select"
                  >
                    {styleOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Aspect Ratio */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Aspect Ratio
                  </label>
                  <select
                    value={settings.aspectRatio}
                    onChange={(e) => setSettings(prev => ({ ...prev, aspectRatio: e.target.value }))}
                    className="select"
                  >
                    {aspectRatios.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Quality */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Quality
                  </label>
                  <select
                    value={settings.quality}
                    onChange={(e) => setSettings(prev => ({ ...prev, quality: e.target.value }))}
                    className="select"
                  >
                    <option value="draft">Draft</option>
                    <option value="standard">Standard</option>
                    <option value="high">High Quality</option>
                  </select>
                </div>

                {/* Steps */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Steps: {settings.steps}
                  </label>
                  <input
                    type="range"
                    min="10"
                    max="50"
                    value={settings.steps}
                    onChange={(e) => setSettings(prev => ({ ...prev, steps: parseInt(e.target.value) }))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Fast</span>
                    <span>Detailed</span>
                  </div>
                </div>

                {/* Guidance */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Guidance: {settings.guidance}
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="20"
                    step="0.5"
                    value={settings.guidance}
                    onChange={(e) => setSettings(prev => ({ ...prev, guidance: parseFloat(e.target.value) }))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Creative</span>
                    <span>Precise</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Prompts */}
            <div className="card">
              <div className="card-header">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Quick Prompts
                </h2>
              </div>
              <div className="card-body">
                <div className="space-y-2">
                  {[
                    'A serene landscape with mountains and a lake at sunset',
                    'A futuristic city with flying cars and neon lights',
                    'A cozy coffee shop with warm lighting and books',
                    'An abstract painting with vibrant colors and geometric shapes'
                  ].map((quickPrompt, index) => (
                    <button
                      key={index}
                      onClick={() => setPrompt(quickPrompt)}
                      className="w-full text-left p-2 text-sm bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                    >
                      {quickPrompt}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-2">
            <div className="card h-full">
              <div className="card-header">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Generated Images
                  </h2>
                  {generatedImages.length > 0 && (
                    <button
                      onClick={() => setGeneratedImages([])}
                      className="btn btn-ghost btn-sm"
                    >
                      <RefreshCw size={16} />
                      <span className="ml-2">Clear</span>
                    </button>
                  )}
                </div>
              </div>
              
              <div className="card-body">
                {isGenerating ? (
                  <div className="flex flex-col items-center justify-center h-96">
                    <div className="loading-spinner mb-4" />
                    <p className="text-gray-600 dark:text-gray-400 text-center">
                      Generating your images...<br />
                      <span className="text-sm">This may take a few moments</span>
                    </p>
                  </div>
                ) : generatedImages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-96">
                    <ImageIcon size={64} className="text-gray-400 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                      No images generated yet
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 text-center">
                      Enter a prompt and click "Generate Images" to create stunning visuals
                    </p>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 gap-4">
                    {generatedImages.map((imageUrl, index) => (
                      <div
                        key={index}
                        className="group relative bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden aspect-square fade-in"
                        style={{ animationDelay: `${index * 200}ms` }}
                      >
                        <img
                          src={imageUrl}
                          alt={`Generated image ${index + 1}`}
                          className="w-full h-full object-cover"
                        />
                        
                        {/* Overlay with actions */}
                        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all duration-300 flex items-center justify-center opacity-0 group-hover:opacity-100">
                          <div className="flex space-x-2">
                            <button
                              onClick={() => {
                                const link = document.createElement('a');
                                link.href = imageUrl;
                                link.download = `generated-image-${index + 1}.png`;
                                link.click();
                              }}
                              className="btn btn-primary btn-sm"
                              title="Download image"
                            >
                              <Download size={16} />
                            </button>
                            <button
                              className="btn btn-secondary btn-sm"
                              title="Regenerate similar"
                            >
                              <RefreshCw size={16} />
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Tips */}
        <div className="mt-8 card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Tips for Better Images
            </h3>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-gray-600 dark:text-gray-400">
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Be Specific</h4>
                <p>Include details about style, lighting, composition, and mood</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Use Keywords</h4>
                <p>Add artistic terms like "photorealistic", "oil painting", "minimalist"</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Describe Colors</h4>
                <p>Mention specific colors, palettes, or color schemes you want</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Set the Scene</h4>
                <p>Include environment, time of day, weather, and atmosphere</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};