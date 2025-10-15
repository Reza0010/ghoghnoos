import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage } from '../types';
import { getAIAssistantResponse } from '../services/geminiService';
import { Bot, Send } from './icons';

interface AIAssistantProps {
  // FIX: Removed apiKeys prop as it's no longer needed.
}

const AIAssistant: React.FC<AIAssistantProps> = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'model', text: 'سلام! من دستیار هوشمند شما برای نوشتن پرامپت هستم. چطور می‌توانم کمکتان کنم؟ مثلا می‌توانید بپرسید: "چطور این پرامپت رو واضح‌تر بنیسم برای Midjourney؟"' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async () => {
    if (input.trim() === '' || isLoading) return;
    
    // FIX: Removed API key check as per guidelines.
    const userMessage: ChatMessage = { role: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const historyForApi = messages.map(msg => ({
        role: msg.role,
        parts: [{ text: msg.text }]
      }));

      // FIX: Removed apiKeys from function call.
      const responseText = await getAIAssistantResponse(historyForApi, input);
      const modelMessage: ChatMessage = { role: 'model', text: responseText };
      setMessages(prev => [...prev, modelMessage]);
    } catch (error) {
      console.error('Error fetching AI response:', error);
      const errorMessage: ChatMessage = { role: 'model', text: 'متاسفانه مشکلی پیش آمد. لطفا دوباره تلاش کنید.' };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
    }
  }

  return (
    <div className="flex flex-col h-full bg-gray-100 dark:bg-dark-bg p-4" dir="rtl">
      <h1 className="text-2xl font-bold text-gray-800 dark:text-dark-text mb-4">دستیار شخصی پرامپت‌نویس</h1>
      <div className="flex-grow bg-white dark:bg-dark-surface rounded-2xl shadow-inner overflow-y-auto p-6 space-y-6">
        {messages.map((msg, index) => (
          <div key={index} className={`flex items-start gap-4 animate-fade-in ${msg.role === 'user' ? 'justify-end' : ''}`}>
            {msg.role === 'model' && (
              <div className="w-10 h-10 rounded-full bg-dark-secondary flex items-center justify-center flex-shrink-0">
                <Bot className="w-6 h-6 text-white" />
              </div>
            )}
            <div className={`max-w-xl p-4 rounded-2xl ${msg.role === 'user' ? 'bg-dark-primary text-white rounded-br-none' : 'bg-gray-200 dark:bg-dark-overlay text-gray-800 dark:text-dark-text rounded-bl-none'}`}>
              <p className="whitespace-pre-wrap">{msg.text}</p>
            </div>
          </div>
        ))}
        {isLoading && (
            <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-full bg-dark-secondary flex items-center justify-center flex-shrink-0">
                  <Bot className="w-6 h-6 text-white" />
                </div>
                <div className="max-w-xl p-4 rounded-2xl bg-gray-200 dark:bg-dark-overlay text-gray-800 dark:text-dark-text rounded-bl-none">
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-dark-subtext rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-dark-subtext rounded-full animate-bounce [animation-delay:0.2s]"></div>
                        <div className="w-2 h-2 bg-dark-subtext rounded-full animate-bounce [animation-delay:0.4s]"></div>
                    </div>
                </div>
            </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="mt-4 p-4 bg-white dark:bg-dark-surface rounded-2xl shadow-lg">
        <div className="relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="پیام خود را تایپ کنید..."
            rows={2}
            className="w-full bg-gray-100 dark:bg-dark-overlay rounded-lg border-transparent focus:border-dark-primary focus:ring-0 resize-none pr-4 pl-12 py-3"
            disabled={isLoading}
          />
          <button onClick={handleSend} disabled={isLoading} className="absolute left-3 top-1/2 -translate-y-1/2 p-2 rounded-full bg-dark-primary text-white hover:bg-opacity-90 disabled:bg-gray-400 disabled:dark:bg-dark-overlay transition">
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
