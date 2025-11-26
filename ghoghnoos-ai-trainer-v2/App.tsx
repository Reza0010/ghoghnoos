
import React, { useState, useEffect, useRef } from 'react';
import { Message, UserProfile } from './types';
import { QUESTIONS } from './constants';
import { ChatMessage, TypingBubble } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';
import { LoadingIndicator } from './components/LoadingIndicator';
import { RestTimer } from './components/RestTimer';
import { generateWorkoutPlan, chatWithCoach } from './services/geminiService';
import confetti from 'canvas-confetti';

const STORAGE_KEY = 'ghoghnoos_state_v1';

// --- Haptic Feedback Utility ---
const triggerHaptic = (type: 'light' | 'medium' | 'heavy' | 'success') => {
  if (!navigator.vibrate) return;
  
  switch (type) {
    case 'light': navigator.vibrate(10); break;
    case 'medium': navigator.vibrate(20); break;
    case 'heavy': navigator.vibrate(40); break;
    case 'success': navigator.vibrate([30, 50, 30]); break;
  }
};

// --- Sound Utilities using Web Audio API ---
const playSoundEffect = (type: 'send' | 'receive' | 'water') => {
  // Trigger haptic along with sound
  triggerHaptic(type === 'send' ? 'medium' : 'light');

  try {
    const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
    if (!AudioContext) return;
    
    const ctx = new AudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    
    osc.connect(gain);
    gain.connect(ctx.destination);
    
    if (type === 'send') {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(600, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(1200, ctx.currentTime + 0.08);
      gain.gain.setValueAtTime(0.05, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);
      osc.start();
      osc.stop(ctx.currentTime + 0.1);
    } else if (type === 'receive') {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(400, ctx.currentTime);
      gain.gain.setValueAtTime(0.0, ctx.currentTime);
      gain.gain.linearRampToValueAtTime(0.08, ctx.currentTime + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
      osc.start();
      osc.stop(ctx.currentTime + 0.3);
    } else if (type === 'water') {
      // Water droplet sound
      osc.type = 'sine';
      osc.frequency.setValueAtTime(1000, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(600, ctx.currentTime + 0.1);
      gain.gain.setValueAtTime(0.05, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.1);
      osc.start();
      osc.stop(ctx.currentTime + 0.1);
    }
  } catch (e) {
    // Ignore sound errors
  }
};

// --- Floating Particles Component ---
const ParticlesBg = () => {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0 particles-container">
      {[...Array(15)].map((_, i) => (
        <div 
          key={i}
          className="particle"
          style={{
            left: `${Math.random() * 100}%`,
            width: `${Math.random() * 6 + 2}px`,
            height: `${Math.random() * 6 + 2}px`,
            animationDuration: `${Math.random() * 10 + 10}s`,
            animationDelay: `${Math.random() * 5}s`,
            opacity: Math.random() * 0.5
          }}
        />
      ))}
    </div>
  );
};

// --- Custom Confirmation Modal ---
const ConfirmModal: React.FC<{ isOpen: boolean; onClose: () => void; onConfirm: () => void; title: string; description: string }> = ({ isOpen, onClose, onConfirm, title, description }) => {
    if (!isOpen) return null;
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-slide-up">
            <div className="bg-slate-900 border border-white/10 w-full max-w-sm rounded-2xl p-6 shadow-2xl">
                <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
                <p className="text-slate-400 text-sm mb-6 leading-6">{description}</p>
                <div className="flex gap-3">
                    <button onClick={onClose} className="flex-1 bg-slate-800 text-white py-2.5 rounded-xl hover:bg-slate-700 transition-colors">
                        انصراف
                    </button>
                    <button onClick={onConfirm} className="flex-1 bg-amber-600 text-white py-2.5 rounded-xl hover:bg-amber-500 transition-colors shadow-lg shadow-amber-600/20">
                        تایید
                    </button>
                </div>
            </div>
        </div>
    );
};

// --- 1RM Calculator Modal ---
const OneRepMaxModal: React.FC<{ onClose: () => void }> = ({ onClose }) => {
    const [weight, setWeight] = useState('');
    const [reps, setReps] = useState('');
    const [result, setResult] = useState<number | null>(null);

    const calculate = () => {
        const w = parseFloat(weight);
        const r = parseFloat(reps);
        if (w > 0 && r > 0) {
            // Epley Formula: w * (1 + r/30)
            const oneRm = Math.round(w * (1 + r / 30));
            setResult(oneRm);
            triggerHaptic('success');
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-slide-up">
            <div className="bg-slate-900 border border-amber-500/30 w-full max-w-sm rounded-2xl p-6 shadow-2xl relative">
                <button onClick={onClose} className="absolute top-4 left-4 text-slate-400 hover:text-white">✕</button>
                <h3 className="text-xl font-bold text-amber-500 mb-4 text-center">ماشین‌حساب رکورد (1RM) 💪</h3>
                
                <div className="space-y-4">
                    <div>
                        <label className="text-xs text-slate-400 block mb-1">وزن (کیلوگرم)</label>
                        <input 
                            type="number" 
                            value={weight} 
                            onChange={e => setWeight(e.target.value)}
                            className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-white text-center text-lg focus:border-amber-500 focus:outline-none"
                            placeholder="مثلاً: 80"
                        />
                    </div>
                    <div>
                        <label className="text-xs text-slate-400 block mb-1">تعداد تکرار</label>
                        <input 
                            type="number" 
                            value={reps} 
                            onChange={e => setReps(e.target.value)}
                            className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-white text-center text-lg focus:border-amber-500 focus:outline-none"
                            placeholder="مثلاً: 8"
                        />
                    </div>

                    <button 
                        onClick={calculate}
                        className="w-full bg-amber-600 hover:bg-amber-500 text-white font-bold py-3 rounded-xl transition-all active:scale-95 shadow-lg shadow-amber-600/20"
                    >
                        محاسبه کن
                    </button>

                    {result !== null && (
                        <div className="mt-4 bg-slate-800/80 p-4 rounded-xl text-center border border-amber-500/20 animate-slide-up">
                            <span className="text-slate-400 text-sm">رکورد یک تکرار شما:</span>
                            <div className="text-3xl font-black text-white mt-1">{result} <span className="text-sm font-normal text-amber-500">کیلو</span></div>
                            <div className="text-[10px] text-slate-500 mt-2">بر اساس فرمول Epley</div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [userProfile, setUserProfile] = useState<UserProfile>({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [planGenerated, setPlanGenerated] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isBotTyping, setIsBotTyping] = useState(false);
  const [showCalculator, setShowCalculator] = useState(false);
  const [showResetModal, setShowResetModal] = useState(false);
  const [isGymMode, setIsGymMode] = useState(false);
  const [waterIntake, setWaterIntake] = useState(0);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load state from local storage on mount
  useEffect(() => {
    const savedState = localStorage.getItem(STORAGE_KEY);
    if (savedState) {
      try {
        const parsed = JSON.parse(savedState);
        setMessages(parsed.messages || []);
        setCurrentStepIndex(parsed.currentStepIndex || 0);
        setUserProfile(parsed.userProfile || {});
        setPlanGenerated(parsed.planGenerated || false);
        setWaterIntake(parsed.waterIntake || 0);
      } catch (e) {
        console.error("Failed to load state", e);
      }
    }
    setIsInitialized(true);
  }, []);

  // Save state whenever it changes
  useEffect(() => {
    if (!isInitialized) return;
    
    if (messages.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        messages,
        currentStepIndex,
        userProfile,
        planGenerated,
        waterIntake
      }));
    }
  }, [messages, currentStepIndex, userProfile, planGenerated, isInitialized, waterIntake]);

  // Auto-scroll to bottom with safety delay to prevent "getBoundingClientRect" errors
  useEffect(() => {
    const timer = setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 150);
    return () => clearTimeout(timer);
  }, [messages, isGenerating, isBotTyping]);

  const startNewChat = () => {
    setIsBotTyping(true);
      
    const hour = new Date().getHours();
    let timeGreeting = 'سلام!';
    if (hour >= 5 && hour < 12) timeGreeting = 'صبح بخیر قهرمان! ☀️';
    else if (hour >= 12 && hour < 17) timeGreeting = 'ظهر بخیر! خسته نباشی 💪';
    else if (hour >= 17 && hour < 21) timeGreeting = 'عصر بخیر ورزشکار! 🌇';
    else timeGreeting = 'شب بخیر! امیدوارم روز خوبی داشته باشی 🌙';

    const fullGreeting = `${timeGreeting}\nمن ققنوسم، مربی شخصی تو. 🔥\nقبل از هر چیز، جنسیتت چیه؟ 👤 (مرد / زن)`;

    setTimeout(() => {
      setIsBotTyping(false);
      addBotMessage(fullGreeting);
    }, 1000);
  };

  // Initial greeting on first load
  useEffect(() => {
    if (isInitialized && messages.length === 0) {
      startNewChat();
    }
  }, [isInitialized]);

  const addBotMessage = (text: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      sender: 'bot',
      text,
    };
    setMessages((prev) => [...prev, newMessage]);
    playSoundEffect('receive');
  };

  const addUserMessage = (text: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text,
    };
    setMessages((prev) => [...prev, newMessage]);
    playSoundEffect('send');
  };

  const checkKeywordEffects = (text: string) => {
    const t = text.toLowerCase();
    if (t.includes('دمبل') || t.includes('وزنه') || t.includes('باشگاه') || t.includes('سنگین')) {
      confetti({
        colors: ['#94a3b8', '#cbd5e1'], // Silver
        shapes: ['circle', 'square'],
        particleCount: 30,
        spread: 40,
        origin: { y: 0.8 }
      });
    } else if (t.includes('عالی') || t.includes('مرسی') || t.includes('خوب') || t.includes('عشق')) {
      confetti({
        colors: ['#ef4444', '#ec4899', '#f43f5e'], // Hearts/Red
        shapes: ['circle'], 
        particleCount: 30,
        spread: 40,
        origin: { y: 0.8 }
      });
    } else if (t.includes('آتش') || t.includes('سوز') || t.includes('فشار') || t.includes('قوی')) {
      confetti({
        colors: ['#ef4444', '#f97316', '#fbbf24'], // Fire
        particleCount: 50,
        spread: 60,
        origin: { y: 0.8 }
      });
    } else if (t.includes('آب') || t.includes('تشنه')) {
        confetti({
          colors: ['#3b82f6', '#60a5fa', '#93c5fd'], // Water
          particleCount: 30,
          spread: 40,
          origin: { y: 0.8 }
        });
    }
  };

  const handleResetConfirm = () => {
    triggerHaptic('medium');
    localStorage.removeItem(STORAGE_KEY);
    
    // Reset State Manually
    setMessages([]);
    setUserProfile({});
    setCurrentStepIndex(0);
    setPlanGenerated(false);
    setWaterIntake(0);
    setIsGenerating(false);
    setShowResetModal(false);
    
    // Start new chat sequence
    startNewChat();
  };

  const handleResetClick = () => {
      setShowResetModal(true);
  };

  const handleBack = () => {
    triggerHaptic('medium');
    if (currentStepIndex > 0 && !planGenerated && !isGenerating) {
       const newMessages = [...messages];
       // Remove current bot question
       if (newMessages.length > 0 && newMessages[newMessages.length - 1].sender === 'bot') {
         newMessages.pop();
       }
       // Remove previous user answer
       if (newMessages.length > 0 && newMessages[newMessages.length - 1].sender === 'user') {
          newMessages.pop();
       }
       
       setMessages(newMessages);

       // Re-calculate index logic
       let newIndex = currentStepIndex - 1;
       while (newIndex > 0 && QUESTIONS[newIndex].condition && !QUESTIONS[newIndex].condition(userProfile)) {
         newIndex--;
       }
       setCurrentStepIndex(newIndex);
    }
  };

  const handleWaterClick = () => {
      setWaterIntake(prev => prev + 1);
      triggerHaptic('medium');
      playSoundEffect('water');
  };

  const checkHealthStats = (profile: UserProfile) => {
      if (profile.age && profile.weight && profile.height && profile.gender) {
          try {
             const weight = parseFloat(profile.weight.replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d).toString()));
             const height = parseFloat(profile.height.replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d).toString()));
             const age = parseFloat(profile.age.replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d).toString()));

             if (isNaN(weight) || isNaN(height) || isNaN(age)) return;

             const heightM = height / 100;
             const bmi = (weight / (heightM * heightM)).toFixed(1);
             let bmiStatus = '';
             if (parseFloat(bmi) < 18.5) bmiStatus = 'کم‌وزن';
             else if (parseFloat(bmi) < 25) bmiStatus = 'نرمال ✅';
             else if (parseFloat(bmi) < 30) bmiStatus = 'اضافه وزن';
             else bmiStatus = 'چاق';

             let bmr = 0;
             if (profile.gender === 'مرد') {
                 bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5;
             } else {
                 bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161;
             }
             const bmrFixed = Math.round(bmr);

             const statsMsg = `📊 **آنالیز اولیه بدن تو:**\n\n- **BMI (شاخص توده بدنی):** ${bmi} (${bmiStatus})\n- **BMR (کالری پایه روزانه):** حدود ${bmrFixed} کالری\n\nاین اطلاعات رو برای طراحی دقیق برنامه‌ت در نظر می‌گیرم. بریم سوال بعدی! 👇`;
             
             setTimeout(() => {
                 addBotMessage(statsMsg);
             }, 800);

          } catch (e) {
              console.error("Calc error", e);
          }
      }
  };

  const checkHydration = (profile: UserProfile) => {
    if (profile.weight && profile.level) {
      try {
        const weight = parseFloat(profile.weight.replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d).toString()));
        if (isNaN(weight)) return;

        let waterNeed = weight * 33;

        if (profile.level.includes('متوسط')) waterNeed += 350;
        if (profile.level.includes('حرفه‌ای')) waterNeed += 750;

        const liters = (waterNeed / 1000).toFixed(1);
        const glasses = Math.round(waterNeed / 250);

        const waterMsg = `💧 **نکته هیدراتاسیون:**\nبا توجه به وزنت و سطح تمرینت، بدنت روزانه به حدود **${liters} لیتر آب** (تقریباً ${glasses} لیوان) نیاز داره تا عضله‌سازی و چربی‌سوزی مختل نشه. حواست باشه! 🥤`;
        
        setTimeout(() => {
            addBotMessage(waterMsg);
        }, 800);

      } catch (e) {
        console.error("Hydration calc error", e);
      }
    }
  };

  const handleSendMessage = async (text: string) => {
    // Check keywords for visual effects
    checkKeywordEffects(text);

    addUserMessage(text);
    setIsBotTyping(true);

    if (planGenerated) {
       try {
         const reply = await chatWithCoach(messages, userProfile, text);
         setIsBotTyping(false);
         addBotMessage(reply);
       } catch (error) {
         setIsBotTyping(false);
         addBotMessage("متاسفانه در ارتباط با سرور مشکلی پیش آمد.");
       }
       return;
    }

    const currentQ = QUESTIONS[currentStepIndex];

    const isRequestingPlanEarly = 
      !text.startsWith('data:image') && 
      (text.includes('برنامه') && (text.includes('بده') || text.includes('میخوام') || text.includes('کامل'))) &&
      currentStepIndex < QUESTIONS.length - 1;

    if (isRequestingPlanEarly) {
      setTimeout(() => {
        setIsBotTyping(false);
        addBotMessage('برای درست و امن نوشتن برنامه باید این چند سوال رو جواب بدی؛ اولیه رو خواستم ...');
        
        setIsBotTyping(true);
        setTimeout(() => {
            setIsBotTyping(false);
            addBotMessage(currentQ.text(userProfile));
        }, 1200);
      }, 800);
      return;
    }

    if (currentQ.validate) {
      const error = currentQ.validate(text);
      if (error) {
        setTimeout(() => {
          setIsBotTyping(false);
          addBotMessage(error);
          triggerHaptic('medium');
        }, 800);
        return;
      }
    }

    let updatedProfile = { ...userProfile, [currentQ.id]: text };
    
    if (currentQ.id === 'gender') {
      if (text.includes('زن') || text.includes('خانم') || text.toLowerCase().includes('female') || text.includes('دختر')) {
        updatedProfile.gender = 'زن';
      } else {
        updatedProfile.gender = 'مرد'; 
      }
    }

    setUserProfile(updatedProfile);

    if (currentQ.id === 'height') {
        checkHealthStats(updatedProfile);
    }
    
    if (currentQ.id === 'level') {
        checkHydration(updatedProfile);
    }

    let nextIndex = currentStepIndex + 1;

    while (
      nextIndex < QUESTIONS.length &&
      QUESTIONS[nextIndex].condition &&
      !QUESTIONS[nextIndex].condition(updatedProfile)
    ) {
      nextIndex++;
    }

    const isFinished = nextIndex >= QUESTIONS.length;

    if (!isFinished) {
      const delay = (currentQ.id === 'height' || currentQ.id === 'level') ? 2500 : 1000;
      
      setTimeout(() => {
        const nextQ = QUESTIONS[nextIndex];
        setIsBotTyping(false);
        addBotMessage(nextQ.text(updatedProfile));
        setCurrentStepIndex(nextIndex);
      }, delay); 
    } else {
      setIsGenerating(true);
      setIsBotTyping(false);
      
      // Before generating plan, show athlete card
      const cardMsg: Message = {
        id: 'card-' + Date.now(),
        sender: 'bot',
        text: '',
        type: 'card',
        cardData: updatedProfile
      };
      setMessages(prev => [...prev, cardMsg]);

      setTimeout(async () => {
         const plan = await generateWorkoutPlan(updatedProfile);
         setIsGenerating(false);
         setPlanGenerated(true);
         addBotMessage(plan);
         triggerHaptic('success');
         
         const duration = 3000;
         const end = Date.now() + duration;

         (function frame() {
           confetti({
             particleCount: 5,
             angle: 60,
             spread: 55,
             origin: { x: 0 },
             colors: ['#f59e0b', '#ea580c', '#fbbf24']
           });
           confetti({
             particleCount: 5,
             angle: 120,
             spread: 55,
             origin: { x: 1 },
             colors: ['#f59e0b', '#ea580c', '#fbbf24']
           });

           if (Date.now() < end) {
             requestAnimationFrame(frame);
           }
         }());
         
         setTimeout(() => {
            addBotMessage("برنامه‌ت آماده‌ست! هر سوالی داری یا تغییری میخوای، همینجا بگو. من اینجام! 😊");
         }, 3000);

      }, 2500); // Increased delay slightly for effect
    }
  };

  if (!isInitialized) return null;

  const currentQ = QUESTIONS[currentStepIndex];
  
  let currentPlaceholder = 'پیام خود را بنویسید...';
  let currentInputMode: 'text' | 'image' = 'text';
  let currentOptions: string[] | undefined = undefined;

  if (planGenerated) {
      currentPlaceholder = 'سوال تکمیلی یا درخواست تغییر داری؟ بپرس...';
      currentOptions = ['حرکات شکم رو بیشتر کن', 'یه برنامه غذایی ارزون‌تر میخوام', 'جایگزین اسکات چیه؟'];
  } else if (currentQ) {
      currentPlaceholder = currentQ.placeholder;
      currentInputMode = currentQ.inputType || 'text';
      currentOptions = currentQ.options;
  }

  const progressPercent = planGenerated ? 100 : Math.min(100, Math.max(5, ((currentStepIndex) / QUESTIONS.length) * 100));

  return (
    <div className={`min-h-screen flex flex-col items-center relative transition-colors duration-500 ${isGymMode ? 'bg-black' : 'mesh-bg'}`}>
      
      {!isGymMode && <ParticlesBg />}
      
      <RestTimer />

      {showCalculator && <OneRepMaxModal onClose={() => setShowCalculator(false)} />}
      
      <ConfirmModal 
        isOpen={showResetModal} 
        onClose={() => setShowResetModal(false)} 
        onConfirm={handleResetConfirm}
        title="شروع برنامه جدید"
        description="آیا مطمئنی می‌خواهی همه چیز را پاک کنی و از اول شروع کنی؟ تمام اطلاعات فعلی از دست می‌رود."
      />
      
      {/* Header */}
      <header className={`w-full p-4 sticky top-0 z-30 transition-all duration-300 ${isGymMode ? 'bg-black border-b border-white/20' : 'bg-slate-950/70 backdrop-blur-xl border-b border-white/5 shadow-[0_10px_40px_-10px_rgba(245,158,11,0.1)]'}`}>
        <div className="max-w-3xl mx-auto">
            <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
                {currentStepIndex > 0 && !planGenerated && (
                    <button 
                    onClick={handleBack}
                    className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center hover:bg-white/10 text-slate-400 hover:text-white transition-all mr-1"
                    title="مرحله قبل"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
                        </svg>
                    </button>
                )}
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center shadow-lg transition-transform duration-300 ${isGymMode ? 'bg-white text-black' : 'bg-gradient-to-br from-amber-500 to-orange-600 shadow-[0_0_20px_rgba(245,158,11,0.6)] rotate-3 hover:rotate-0'}`}>
                   <span className="text-xl drop-shadow-md">💪</span>
                </div>
                <div>
                <h1 className={`text-lg font-bold tracking-wide ${isGymMode ? 'text-white' : 'text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-200 drop-shadow-[0_0_10px_rgba(245,158,11,0.5)]'}`}>Ghoghnoos AI</h1>
                <p className={`text-[9px] font-medium tracking-wider uppercase ${isGymMode ? 'text-gray-400' : 'text-amber-500 drop-shadow-[0_0_5px_rgba(245,158,11,0.8)]'}`}>Your Personal Coach</p>
                </div>
            </div>
            
            <div className="flex gap-2 items-center">
                {/* Water Tracker Widget */}
                <button 
                  onClick={handleWaterClick}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all active:scale-95 ${isGymMode ? 'bg-white text-black border border-white' : 'bg-blue-500/10 border border-blue-500/30 text-blue-400 hover:bg-blue-500/20'}`}
                  title="ثبت آب مصرفی"
                >
                   <span>💧</span>
                   <span className="font-bold text-xs">{waterIntake}</span>
                </button>

                {/* Gym Mode Toggle */}
                <button 
                   onClick={() => setIsGymMode(!isGymMode)}
                   className={`px-3 py-1.5 rounded-lg transition-all active:scale-95 ${isGymMode ? 'bg-white text-black font-bold' : 'bg-white/5 text-slate-300 hover:bg-white/10 hover:text-white border border-white/10'}`}
                   title="حالت تمرکز (باشگاه)"
                >
                   {isGymMode ? '👁️' : '🕶️'}
                </button>

                 <button 
                    onClick={() => setShowCalculator(true)}
                    className={`text-[10px] px-3 py-1.5 rounded-lg transition-all active:scale-95 ${isGymMode ? 'bg-white text-black font-bold border border-white' : 'text-amber-500/90 bg-amber-500/10 border border-amber-500/20 hover:bg-amber-500/20'}`}
                    title="ماشین‌حساب رکورد"
                >
                    1RM
                </button>
                <button 
                    onClick={handleResetClick}
                    className={`text-[10px] px-3 py-1.5 rounded-lg transition-all active:scale-95 ${isGymMode ? 'bg-transparent text-white border border-white' : 'text-slate-300 bg-white/5 border border-white/10 hover:bg-white/10 hover:text-white'}`}
                >
                    🔄
                </button>
            </div>

            </div>
            
            {/* Progress Bar */}
            {!planGenerated && !isGymMode && (
                <div className="w-full h-1 bg-slate-800/50 rounded-full overflow-hidden relative">
                    <div 
                        className="absolute top-0 right-0 h-full bg-gradient-to-l from-amber-400 to-orange-600 shadow-[0_0_10px_rgba(245,158,11,0.5)] transition-all duration-700 ease-out rounded-full"
                        style={{ width: `${progressPercent}%` }}
                    />
                </div>
            )}
            {/* Simple Progress Bar for Gym Mode */}
            {!planGenerated && isGymMode && (
                <div className="w-full h-2 bg-gray-800 rounded-none overflow-hidden relative mt-2">
                    <div 
                        className="absolute top-0 right-0 h-full bg-white transition-all duration-700 ease-out"
                        style={{ width: `${progressPercent}%` }}
                    />
                </div>
            )}
        </div>
      </header>

      {/* Chat Area */}
      <main className="flex-1 w-full max-w-3xl p-4 pb-48 md:pb-40 chat-input-container z-10">
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} isGymMode={isGymMode} />
        ))}
        
        {isBotTyping && <TypingBubble />}
        {isGenerating && <LoadingIndicator />}
        
        <div ref={messagesEndRef} />
      </main>

      {/* Input Area */}
      <div className="chat-input-container z-20">
        <ChatInput 
            onSend={handleSendMessage} 
            disabled={isGenerating || isBotTyping} 
            placeholder={currentPlaceholder}
            mode={currentInputMode}
            options={currentOptions}
        />
      </div>
    </div>
  );
}
