import React, { useState } from 'react';
import { Bot, Send, Wand2, Lightbulb, RefreshCw } from './icons';

export const AIAssistant: React.FC = () => {
  const [messages, setMessages] = useState([
    {
      id: '1',
      role: 'assistant' as const,
      content: 'Hello! I\'m your AI assistant. I can help you improve your prompts, suggest variations, and provide guidance on prompt engineering best practices. How can I assist you today?',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user' as const,
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: (Date.now() + 1).toString(),
        role: 'assistant' as const,
        content: 'I understand you\'re looking for help with that. In a full implementation, I would use the Gemini API to provide intelligent responses and suggestions for improving your prompts. For now, this is a simulated response to demonstrate the interface.',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, aiResponse]);
      setIsLoading(false);
    }, 1500);
  };

  const quickActions = [
    { id: 'improve', label: 'Improve my prompt', icon: Wand2 },
    { id: 'suggest', label: 'Suggest variations', icon: Lightbulb },
    { id: 'optimize', label: 'Optimize for clarity', icon: RefreshCw },
  ];

  return (
    <div className="main-content">
      <div className="max-w-4xl mx-auto h-full flex flex-col">
        {/* Header */}
        <div className="flex items-center space-x-3 mb-6">
          <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl">
            <Bot size={20} className="text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              AI Assistant
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Get help improving and optimizing your prompts
            </p>
          </div>
        </div>

        {/* Chat Container */}
        <div className="flex-1 flex flex-col card">
          {/* Messages */}
          <div className="flex-1 p-6 overflow-y-auto space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-4 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-primary-500 text-white'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  <p className={`text-xs mt-2 ${
                    message.role === 'user' 
                      ? 'text-primary-100' 
                      : 'text-gray-500 dark:text-gray-400'
                  }`}>
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="loading-spinner" />
                    <span className="text-gray-600 dark:text-gray-400">AI is thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex flex-wrap gap-2 mb-4">
              {quickActions.map((action) => {
                const Icon = action.icon;
                return (
                  <button
                    key={action.id}
                    onClick={() => setInputMessage(action.label)}
                    className="btn btn-ghost btn-sm"
                  >
                    <Icon size={14} />
                    <span className="ml-2">{action.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Input */}
            <div className="flex space-x-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                className="input flex-1"
                placeholder="Ask me anything about prompt engineering..."
                disabled={isLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !inputMessage.trim()}
                className="btn btn-primary"
              >
                <Send size={16} />
              </button>
            </div>
          </div>
        </div>

        {/* Tips Sidebar */}
        <div className="mt-6 card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Quick Tips
            </h3>
          </div>
          <div className="card-body">
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li>• Ask me to improve the clarity of your prompts</li>
              <li>• Request variations for different use cases</li>
              <li>• Get suggestions for better structure and formatting</li>
              <li>• Learn about prompt engineering best practices</li>
              <li>• Ask for help with specific AI model optimizations</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};