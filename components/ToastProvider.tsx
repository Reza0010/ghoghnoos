import React, { createContext, useCallback, useContext, useMemo, useState } from 'react';

export type Toast = {
  id: string;
  message: string;
  type?: 'success' | 'error' | 'info';
  durationMs?: number;
};

interface ToastContextValue {
  showToast: (message: string, options?: { type?: Toast['type']; durationMs?: number }) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export const useToast = (): ToastContextValue => {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
};

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const remove = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const showToast = useCallback<ToastContextValue['showToast']>((message, options) => {
    const id = `${Date.now()}-${Math.random()}`;
    const toast: Toast = { id, message, type: options?.type || 'info', durationMs: options?.durationMs ?? 2500 };
    setToasts(prev => [...prev, toast]);
    window.setTimeout(() => remove(id), toast.durationMs);
  }, [remove]);

  const value = useMemo(() => ({ showToast }), [showToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      {/* Toast stack */}
      <div className="fixed bottom-4 right-4 z-50 space-y-2" dir="rtl">
        {toasts.map(t => (
          <div
            key={t.id}
            className={
              `min-w-[220px] max-w-[360px] px-4 py-3 rounded-xl shadow-lg text-sm font-semibold ` +
              (t.type === 'success'
                ? 'bg-green-500 text-white'
                : t.type === 'error'
                ? 'bg-red-500 text-white'
                : 'bg-gray-800 text-white')
            }
          >
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};
