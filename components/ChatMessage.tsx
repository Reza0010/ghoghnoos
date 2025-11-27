import React, { useState } from 'react';
import { Message } from '../types'; 
import ReactMarkdown from 'react-markdown';

// --- Type Definitions ---
interface ChatMessageProps {
  message: Message;
  isGymMode?: boolean;
}

// --- Component: TypingBubble ---
export const TypingBubble: React.FC = () => {
  return (
    <div className="flex w-full mb-6 justify-start animate-slide-up typing-bubble items-end gap-3">
      {/* Bot Avatar Placeholder for Typing */}
      <div className="w-8 h-8 rounded-full bg-slate-800 border border-amber-500/30 flex items-center justify-center text-sm shadow-lg shadow-amber-500/10">
        🔥
      </div>
      <div className="bg-slate-800/80 backdrop-blur-sm text-slate-100 rounded-2xl rounded-bl-none border border-white/5 p-4 shadow-xl">
        <div className="flex gap-1.5 items-center h-4">
          <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>
    </div>
  );
};

// --- Component: AthleteCard ---
const AthleteCard: React.FC<{ data: any }> = React.memo(({ data }) => {
  const athleteData = data || {}; 

  return (
    <div className="w-full max-w-sm mx-auto my-4 relative group perspective-1000">
      <div className="relative overflow-hidden rounded-xl bg-gradient-to-br from-slate-900 via-slate-800 to-black border border-amber-500/30 shadow-2xl transition-transform transform group-hover:scale-[1.02] duration-500 neon-glow">

        {/* Holographic Overlay Effect */}
        <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/5 to-transparent opacity-0 group-hover:opacity-30 transition-opacity duration-700 pointer-events-none z-10" style={{ mixBlendMode: 'overlay' }}></div>

        <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/20 blur-3xl rounded-full -mr-10 -mt-10"></div>
        <div className="absolute bottom-0 left-0 w-32 h-32 bg-orange-600/10 blur-3xl rounded-full -ml-10 -mb-10"></div>

        <div className="p-5 relative z-20">
          <div className="flex justify-between items-start mb-4 border-b border-white/10 pb-3">
            <div className="flex flex-col">
              <span className="text-[10px] text-amber-500 font-bold tracking-widest uppercase neon-text-glow">ATHLETE PASSPORT</span>
              <span className="text-xl font-black text-white tracking-wide">GHOGHNOOS</span>
            </div>
            <div className="w-10 h-10 bg-gradient-to-br from-amber-400 to-orange-600 rounded-lg flex items-center justify-center text-xl shadow-lg">
              💪
            </div>
          </div>

          <div className="flex gap-4">
            <div className="w-20 h-24 bg-slate-700/50 rounded-lg border border-white/10 flex items-center justify-center overflow-hidden">
              <span className="text-4xl filter drop-shadow-md">{athleteData.gender === 'مرد' ? '🧔' : '👩'}</span>
            </div>
            <div className="flex-1 space-y-2">
              <div className="flex justify-between">
                <span className="text-xs text-slate-400">LEVEL</span>
                <span className="text-xs font-bold text-white">{athleteData.level || 'Unknown'}</span>
              </div>
              <div className="w-full h-[1px] bg-white/10"></div>
              <div className="flex justify-between">
                <span className="text-xs text-slate-400">GOAL</span>
                <span className="text-xs font-bold text-amber-400">{athleteData.goal ? athleteData.goal.split(' ')[0] : 'Fitness'}</span>
              </div>
              <div className="w-full h-[1px] bg-white/10"></div>
              <div className="flex justify-between">
                <span className="text-xs text-slate-400">JOINED</span>
                <span className="text-xs font-bold text-white">{new Date().toLocaleDateString('fa-IR')}</span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-white/10 flex justify-between items-center">
            <div className="text-[9px] text-slate-500 font-mono">ID: {Math.random().toString(36).substr(2, 9).toUpperCase()}</div>
            <div className="px-2 py-0.5 bg-green-500/20 text-green-400 text-[10px] rounded font-bold border border-green-500/20">ACTIVE</div>
          </div>
        </div>
      </div>
    </div>
  );
});

// --- Component: ChatMessage ---
export const ChatMessage: React.FC<ChatMessageProps> = React.memo(({ message, isGymMode = false }) => {
  const isBot = message.sender === 'bot';
  
  // FIX: استفاده از Optional Chaining و Nullish Coalescing برای رفع خطای "Cannot read properties of undefined (reading 'startsWith')".
  // اگر message.text undefined یا null باشد، به صورت پیش‌فرض false برگردانده می‌شود.
  const isImage = message.text?.startsWith('data:image') ?? false; 
  
  const [copied, setCopied] = useState(false);

  // --- Handlers ---
  const handleCopy = () => {
    // از optional chaining برای اطمینان از وجود message.text استفاده می کنیم.
    navigator.clipboard.writeText(message.text ?? ''); 
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = () => {
    window.print();
  };

  const handleDownload = () => {
    try {
        const blob = new Blob([message.text ?? ''], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `Ghoghnoos-Plan-${new Date().toISOString().slice(0,10)}.txt`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (e) {
        console.error("Download failed", e);
        alert("خطا در دانلود فایل.");
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'برنامه تمرینی ققنوس',
          text: message.text ?? 'محتوایی برای اشتراک‌گذاری وجود ندارد.',
        });
      } catch (err) {
        console.error('Error sharing:', err);
      }
    } else {
      handleCopy();
      alert('متن کپی شد! (مرورگر شما از اشتراک‌گذاری پشتیبانی نمی‌کند)');
    }
  };
  // --- End Handlers ---

  // --- Styles ---
  const containerClasses = isGymMode
    ? `relative max-w-[95%] p-6 rounded-xl text-lg font-bold leading-relaxed whitespace-pre-wrap border-2 shadow-none ${
        isBot
          ? 'bg-black text-white border-white'
          : 'bg-white text-black border-black'
      }`
    : `relative max-w-[88%] md:max-w-[82%] p-5 rounded-2xl text-sm md:text-base leading-relaxed whitespace-pre-wrap shadow-xl message-content ${
        isBot
          ? 'bot-message-container bg-slate-900/90 backdrop-blur-md text-slate-100 rounded-bl-none border border-amber-500/10 shadow-[0_4px_20px_-5px_rgba(0,0,0,0.5)]'
          : 'bg-gradient-to-br from-amber-500 to-orange-600 text-white rounded-br-none shadow-lg shadow-orange-500/20'
      }`;

  // --- Card Message Rendering ---
  if (message.type === 'card' && message.cardData) {
      return (
          <div className="animate-slide-up">
              <AthleteCard data={message.cardData} />
          </div>
      );
  }

  // --- Regular Message Rendering ---
  return (
    <div className={`flex w-full mb-6 ${isBot ? 'justify-start items-end gap-3' : 'justify-end user-message'} group animate-slide-up`}>

      {/* Bot Avatar */}
      {isBot && !isGymMode && (
        <div className="avatar-container w-8 h-8 rounded-full bg-gradient-to-br from-slate-800 to-black border border-amber-500/40 flex items-center justify-center text-sm shadow-lg shadow-amber-500/10 flex-shrink-0 mb-1 z-10">
          <span className="filter drop-shadow-[0_0_3px_rgba(245,158,11,0.8)]">🦅</span>
        </div>
      )}

      <div className={containerClasses}>
        {isImage ? (
           <div className="flex flex-col items-center">
             <img src={message.text} alt="User upload" className={`max-w-full rounded-lg max-h-72 object-cover shadow-md ${isGymMode ? 'grayscale contrast-125' : 'border border-white/10'}`} />
             <span className="text-xs mt-3 opacity-90 font-medium bg-black/20 px-2 py-1 rounded-md">عکس ارسال شد ✅</span>
           </div>
        ) : isBot ? (
             <>
               <ReactMarkdown 
               components={{
                    ul: ({node, ...props}) => <ul className="list-disc pr-4 my-3 space-y-1" {...props} />,
                    ol: ({node, ...props}) => <ol className="list-decimal pr-4 my-3 space-y-1" {...props} />,
                    li: ({node, ...props}) => <li className="mb-1 pl-1" {...props} />,
                    strong: ({node, ...props}) => <strong className={isGymMode ? "font-black text-white underline decoration-2 underline-offset-4" : "font-bold text-amber-400 neon-text"} {...props} />,
                    h1: ({node, ...props}) => <h1 className={isGymMode ? "text-2xl font-black my-4 border-b-4 border-white pb-2 uppercase" : "text-xl md:text-2xl font-black my-4 text-transparent bg-clip-text bg-gradient-to-r from-amber-300 to-orange-400 border-b border-white/10 pb-2 neon-text"} {...props} />,
                    h2: ({node, ...props}) => <h2 className={isGymMode ? "text-xl font-black mt-6 mb-3 text-white border-l-4 border-white pl-2" : "text-lg md:text-xl font-bold mt-6 mb-3 text-amber-100 flex items-center gap-2 border-r-4 border-amber-500 pr-3 bg-gradient-to-l from-amber-500/10 to-transparent py-1"} {...props} />,
                    h3: ({node, ...props}) => <h3 className={isGymMode ? "text-lg font-bold mt-4 mb-2 text-white" : "text-md font-bold mt-4 mb-2 text-amber-200/90"} {...props} />,
                    p: ({node, ...props}) => <p className="mb-2 last:mb-0 leading-7 text-justify" {...props} />,
                    code: ({node, ...props}) => <code className={isGymMode ? "bg-white text-black px-1 font-bold" : "bg-black/30 px-1.5 py-0.5 rounded text-amber-300 font-mono text-sm border border-amber-500/10"} {...props} />,
                    table: ({node, ...props}) => (
                        <div className="markdown-table-container">
                            <table className={isGymMode ? "w-full border-collapse" : "cyberpunk-table"} {...props} />
                        </div>
                    ),
               }}
               >
                  {message.text ?? '...'}
                </ReactMarkdown>

                {/* Message Actions */}
                {!isGymMode && (
                  <div className="absolute -bottom-10 left-0 flex gap-2 message-actions opacity-0 group-hover:opacity-100 transition-opacity flex-wrap z-10">
                    {/* Copy Button */}
                    <button 
                    onClick={handleCopy}
                    className="p-1.5 flex items-center gap-1 text-xs text-slate-400 hover:text-white transition-colors bg-white/5 rounded-lg border border-white/5 hover:bg-white/10 hover:border-amber-500/30"
                    title="کپی متن"
                    >
                    {copied ? (
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                    ) : (
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                    )}
                    </button>

                    {/* Share Button */}
                    <button 
                      onClick={handleShare}
                      className="p-1.5 flex items-center gap-1 text-xs text-slate-400 hover:text-white transition-colors bg-white/5 rounded-lg border border-white/5 hover:bg-white/10 hover:border-amber-500/30"
                      title="اشتراک‌گذاری"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                      </svg>
                    </button>

                    {/* Print Button */}
                    <button 
                      onClick={handlePrint}
                      className="p-1.5 flex items-center gap-1 text-xs text-slate-400 hover:text-white transition-colors bg-white/5 rounded-lg border border-white/5 hover:bg-white/10 hover:border-amber-500/30"
                      title="پرینت / PDF"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                      </svg>
                    </button>

                      {/* Download Button */}
                      <button 
                      onClick={handleDownload}
                      className="p-1.5 flex items-center gap-1 text-xs text-slate-400 hover:text-white transition-colors bg-white/5 rounded-lg border border-white/5 hover:bg-white/10 hover:border-amber-500/30"
                      title="دانلود متن"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                    </button>
                  </div>
                )}
             </>
        ) : (
            // برای پیام‌های کاربری غیرعکس
            <span className="font-medium tracking-wide">{message.text}</span>
        )}
      </div>
    </div>
  );
});