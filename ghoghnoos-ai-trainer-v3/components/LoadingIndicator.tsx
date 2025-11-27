
import React, { useState, useEffect } from 'react';
import { LOADING_QUOTES } from '../constants';

export const LoadingIndicator: React.FC = () => {
  const [quoteIndex, setQuoteIndex] = useState(0);

  useEffect(() => {
    // Rotate quotes every 3.5 seconds
    const interval = setInterval(() => {
      setQuoteIndex((prev) => (prev + 1) % LOADING_QUOTES.length);
    }, 3500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-6 animate-slide-up">
      <div className="relative w-20 h-20">
        <div className="absolute top-0 left-0 w-full h-full border-4 border-slate-700/50 rounded-full"></div>
        <div className="absolute top-0 left-0 w-full h-full border-4 border-amber-500 rounded-full border-t-transparent animate-spin"></div>
        <div className="absolute inset-0 flex items-center justify-center text-2xl animate-pulse">
           🔥
        </div>
      </div>
      
      <div className="text-center space-y-2 max-w-xs md:max-w-md">
        <h3 className="text-amber-400 font-bold text-lg animate-pulse">
          درحال طراحی برنامه اختصاصی...
        </h3>
        <p className="text-slate-300 text-sm leading-6 min-h-[3rem] transition-all duration-500 ease-in-out">
          "{LOADING_QUOTES[quoteIndex]}"
        </p>
      </div>
    </div>
  );
};
