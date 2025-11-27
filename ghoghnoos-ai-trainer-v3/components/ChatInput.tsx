
import React, { useState, FormEvent, useRef, useEffect, ChangeEvent } from 'react';

interface ChatInputProps {
  onSend: (text: string) => void;
  disabled: boolean;
  placeholder: string;
  mode?: 'text' | 'image';
  options?: string[];
}

export const ChatInput: React.FC<ChatInputProps> = React.memo(({ onSend, disabled, placeholder, mode = 'text', options }) => {
  const [input, setInput] = useState('');
  const [isProcessingImage, setIsProcessingImage] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [direction, setDirection] = useState<'rtl' | 'ltr'>('rtl');
  const inputRef = useRef<HTMLInputElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Voice Recognition Setup
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.lang = 'fa-IR';
      recognitionRef.current.interimResults = false;

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInput((prev) => (prev ? prev + ' ' + transcript : transcript));
        setIsListening(false);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error', event.error);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  // Auto-detect direction based on first strong character
  useEffect(() => {
    if (!input) {
      setDirection('rtl');
      return;
    }
    const checkDir = () => {
      const ltrChars = 'A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02B8\u0300-\u0590\u0800-\u1FFF\u2C00-\uFB1C\uFDF0-\uFE6F\uFEFD-\uFFFF';
      const rtlChars = '\u0591-\u07FF\uFB1D-\uFDFD\uFE70-\uFEFC';
      // eslint-disable-next-line
      const ltrDir = new RegExp('^[^' + rtlChars + ']*[' + ltrChars + ']');
      // eslint-disable-next-line
      const rtlDir = new RegExp('^[^' + ltrChars + ']*[' + rtlChars + ']');
      
      if (ltrDir.test(input)) return 'ltr';
      if (rtlDir.test(input)) return 'rtl';
      return 'rtl';
    };
    setDirection(checkDir());
  }, [input]);

  const toggleListening = () => {
    if (navigator.vibrate) navigator.vibrate(10);
    
    if (!recognitionRef.current) {
      alert('مرورگر شما از قابلیت تایپ صوتی پشتیبانی نمی‌کند.');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
    } else {
      setIsListening(true);
      recognitionRef.current.start();
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleOptionClick = (option: string) => {
      if (navigator.vibrate) navigator.vibrate(10);
      if (!disabled) {
          onSend(option);
      }
  };

  const compressImage = (file: File): Promise<string> => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = (event) => {
        const img = new Image();
        img.src = event.target?.result as string;
        img.onload = () => {
          const canvas = document.createElement('canvas');
          const MAX_WIDTH = 1024;
          const MAX_HEIGHT = 1024;
          let width = img.width;
          let height = img.height;

          if (width > height) {
            if (width > MAX_WIDTH) {
              height *= MAX_WIDTH / width;
              width = MAX_WIDTH;
            }
          } else {
            if (height > MAX_HEIGHT) {
              width *= MAX_HEIGHT / height;
              height = MAX_HEIGHT;
            }
          }

          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext('2d');
          ctx?.drawImage(img, 0, 0, width, height);
          resolve(canvas.toDataURL('image/jpeg', 0.7));
        };
      };
    });
  };

  const handleFileChange = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setIsProcessingImage(true);
      try {
        const compressedBase64 = await compressImage(file);
        onSend(compressedBase64);
      } catch (error) {
        console.error("Image processing failed", error);
        alert("خطا در پردازش تصویر. لطفا دوباره تلاش کنید.");
      } finally {
        setIsProcessingImage(false);
      }
    }
    if (fileInputRef.current) {
        fileInputRef.current.value = '';
    }
  };

  const handleCameraClick = () => {
    if (navigator.vibrate) navigator.vibrate(10);
    fileInputRef.current?.click();
  };

  useEffect(() => {
    if (!disabled && inputRef.current && !isListening) {
      inputRef.current.focus();
    }
  }, [disabled, options, isListening]);

  return (
    <div className="fixed bottom-0 left-0 w-full bg-slate-950/80 backdrop-blur-xl border-t border-white/5 pb-4 pt-2 z-20 transition-all duration-300">
      
      {/* Quick Reply Chips */}
      {options && options.length > 0 && !disabled && (
        <div className="max-w-3xl mx-auto px-4 mb-2 flex gap-2 overflow-x-auto no-scrollbar py-1 mask-linear-fade">
          {options.map((option, index) => (
            <button
              key={index}
              onClick={() => handleOptionClick(option)}
              className="whitespace-nowrap bg-slate-800/80 hover:bg-slate-700 text-amber-100/90 border border-amber-500/20 px-4 py-2 rounded-full text-sm transition-all active:scale-95 shadow-sm"
            >
              {option}
            </button>
          ))}
        </div>
      )}

      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto flex gap-3 px-4">
        
        {mode === 'image' && (
          <>
            <input 
              type="file" 
              accept="image/*" 
              capture="environment"
              ref={fileInputRef} 
              className="hidden"
              onChange={handleFileChange}
            />
            <button
              type="button"
              onClick={handleCameraClick}
              disabled={disabled || isProcessingImage}
              className="bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 border border-white/5 rounded-2xl px-4 py-3 transition-all disabled:opacity-50 relative active:scale-95 flex-shrink-0"
              title="ارسال عکس"
            >
               {isProcessingImage ? (
                 <div className="w-6 h-6 border-2 border-slate-300 border-t-transparent rounded-full animate-spin"></div>
               ) : (
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6.827 6.175A2.31 2.31 0 015.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 00-1.134-.175 2.31 2.31 0 01-1.64-1.055l-.822-1.316a2.192 2.192 0 00-1.736-1.039 48.774 48.774 0 00-5.232 0 2.192 2.192 0 00-1.736 1.039l-.821 1.316z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 12.75a4.5 4.5 0 11-9 0 4.5 4.5 0 019 0zM18.75 10.5h.008v.008h-.008V10.5z" />
                </svg>
               )}
            </button>
          </>
        )}

        <div className="relative flex-1 group flex items-center bg-slate-800/50 border border-white/5 rounded-2xl px-2 focus-within:ring-2 focus-within:ring-amber-500/50 focus-within:bg-slate-800/80 transition-all">
            <input
            ref={inputRef}
            type="text"
            value={input}
            dir={direction}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isListening ? 'در حال شنیدن...' : placeholder}
            disabled={disabled || isProcessingImage}
            className="w-full bg-transparent text-slate-100 px-3 py-4 focus:outline-none placeholder-slate-500 disabled:opacity-50"
            />
            
            {/* Microphone Button */}
            {!input && mode === 'text' && (
              <button
                type="button"
                onClick={toggleListening}
                className={`p-2 rounded-xl transition-all mr-1 ${isListening ? 'bg-red-500/20 text-red-400 animate-pulse' : 'text-slate-400 hover:text-white hover:bg-white/10'}`}
                disabled={disabled}
              >
                {isListening ? (
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                    <path d="M8.25 4.5a3.75 3.75 0 117.5 0v8.25a3.75 3.75 0 11-7.5 0V4.5z" />
                    <path d="M6 10.5a.75.75 0 01.75.75v1.5a5.25 5.25 0 1010.5 0v-1.5a.75.75 0 011.5 0v1.5a6.751 6.751 0 01-6 6.709v2.291h3a.75.75 0 010 1.5h-7.5a.75.75 0 010-1.5h3v-2.291a6.751 6.751 0 01-6-6.709v-1.5A.75.75 0 016 10.5z" />
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z" />
                  </svg>
                )}
              </button>
            )}
        </div>

        <button
          type="submit"
          disabled={disabled || !input.trim() || isProcessingImage}
          className="bg-gradient-to-br from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-white rounded-2xl px-6 py-3 font-medium transition-all shadow-lg shadow-orange-900/20 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none active:scale-95 flex items-center justify-center min-w-[3.5rem] flex-shrink-0"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-5 h-5 rotate-180">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
          </svg>
        </button>
      </form>
    </div>
  );
});
