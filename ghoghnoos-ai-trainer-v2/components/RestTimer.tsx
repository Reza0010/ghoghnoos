
import React, { useState, useEffect, useRef } from 'react';

export const RestTimer: React.FC = () => {
  const [timeLeft, setTimeLeft] = useState(0);
  const [initialTime, setInitialTime] = useState(0);
  const [isActive, setIsActive] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  
  // Audio context ref to reuse context if needed
  const audioCtxRef = useRef<AudioContext | null>(null);

  useEffect(() => {
    let interval: any = null;
    if (isActive && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (timeLeft === 0 && isActive) {
      setIsActive(false);
      setIsOpen(false);
      if (navigator.vibrate) navigator.vibrate([200, 100, 200, 100, 500]);
      playBeep();
    }
    return () => clearInterval(interval);
  }, [isActive, timeLeft]);

  const playBeep = () => {
    try {
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }
      const ctx = audioCtxRef.current;
      if (ctx.state === 'suspended') ctx.resume();

      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      
      // Pleasant "Ding" sound
      osc.type = 'sine';
      osc.frequency.setValueAtTime(523.25, ctx.currentTime); // C5
      osc.frequency.exponentialRampToValueAtTime(1046.5, ctx.currentTime + 0.1); // C6
      
      gain.gain.setValueAtTime(0.1, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5);
      
      osc.start();
      osc.stop(ctx.currentTime + 0.5);
    } catch(e) {
      console.error(e);
    }
  };

  const startTimer = (seconds: number) => {
    setInitialTime(seconds);
    setTimeLeft(seconds);
    setIsActive(true);
    setIsOpen(false);
    if (navigator.vibrate) navigator.vibrate(20);
  };

  const addTime = () => {
      setTimeLeft(prev => {
          const newTime = prev + 30;
          setInitialTime(Math.max(initialTime, newTime)); // Adjust progress bar scale
          return newTime;
      });
      if (navigator.vibrate) navigator.vibrate(10);
  };

  const stopTimer = () => {
    setIsActive(false);
    setTimeLeft(0);
    if (navigator.vibrate) navigator.vibrate(10);
  };

  const toggleMenu = () => {
      if (!isActive) {
          setIsOpen(!isOpen);
      }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  // Circular Progress Calculation
  const radius = 22;
  const circumference = 2 * Math.PI * radius;
  const progressOffset = initialTime > 0 ? circumference -