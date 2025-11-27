
import React, { useState, useEffect, useRef } from 'react';

// Singleton Audio Context for timer
let timerAudioCtx: AudioContext | null = null;

const getTimerAudioContext = () => {
    if (!timerAudioCtx) {
        const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
        if (AudioContext) {
            timerAudioCtx = new AudioContext();
        }
    }
    return timerAudioCtx;
};

export const RestTimer: React.FC = React.memo(() => {
  const [timeLeft, setTimeLeft] = useState(0);
  const [isActive, setIsActive] = useState(false);
  const intervalRef = useRef<any>(null);

  useEffect(() => {
    if (isActive && timeLeft > 0) {
      intervalRef.current = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (timeLeft === 0 && isActive) {
      setIsActive(false);
      if (navigator.vibrate) navigator.vibrate([200, 100, 200]);
      
      // Play beep sound efficiently
      try {
        const ctx = getTimerAudioContext();
        if (ctx) {
           // Resume if suspended (common in browsers)
           if (ctx.state === 'suspended') ctx.resume();

           const osc = ctx.createOscillator();
           const gain = ctx.createGain();
           osc.connect(gain);
           gain.connect(ctx.destination);
           osc.type = 'square';
           osc.frequency.setValueAtTime(440, ctx.currentTime);
           osc.start();
           gain.gain.exponentialRampToValueAtTime(0.00001, ctx.currentTime + 0.5);
           osc.stop(ctx.currentTime + 0.5);
        }
      } catch(e) {}
    }
    return () => {
        if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isActive, timeLeft]);

  const startTimer = (seconds: number) => {
    // Resume audio context on user interaction to ensure it works later
    const ctx = getTimerAudioContext();
    if (ctx && ctx.state === 'suspended') ctx.resume();

    setTimeLeft(seconds);
    setIsActive(true);
    if (navigator.vibrate) navigator.vibrate(20);
  };

  const stopTimer = () => {
    setIsActive(false);
    setTimeLeft(0);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  return (
    <div className="fixed right-4 top-24 z-40 flex flex-col gap-2 items-end animate-slide-up">
       <div className={`bg-slate-900/90 backdrop-blur border border-amber-500/30 rounded-xl p-3 shadow-xl transition-all duration-300 ${isActive ? 'w-28' : 'w-12 h-12 flex items-center justify-center overflow-hidden hover:w-28 group'}`}>
           
           {!isActive ? (
               <button className="text-2xl w-full h-full flex items-center justify-center" title="تایمر استراحت">⏱️</button>
           ) : (
               <div className="text-center w-full">
                   <div className="text-2xl font-black text-white font-mono mb-1">{formatTime(timeLeft)}</div>
                   <button onClick={stopTimer} className="text-[10px] w-full bg-red-500/20 text-red-400 border border-red-500/30 px-1 py-1 rounded hover:bg-red-500/30 transition-colors">توقف</button>
               </div>
           )}

           <div className={`${isActive ? 'hidden' : 'hidden group-hover:flex'} flex-col gap-1.5 transition-all mt-1 w-full`}>
               <div className="text-[9px] text-center text-slate-400 pb-1 border-b border-white/10">استراحت</div>
               {[30, 60, 90, 120].map(time => (
                   <button 
                     key={time} 
                     onClick={() => startTimer(time)}
                     className="text-xs bg-slate-800 hover:bg-amber-600 text-white py-1.5 rounded transition-colors border border-white/5"
                   >
                       {time} ثانیه
                   </button>
               ))}
           </div>
       </div>
    </div>
  );
});
