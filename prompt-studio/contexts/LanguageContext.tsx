import React, { createContext, useContext, PropsWithChildren, useCallback } from 'react';
import useLocalStorage from '../hooks/useLocalStorage';
import { translations } from '../translations';
import { Language } from '../types';

// Type for the translation function
export type TFunction = (key: string, options?: any) => string;

type LanguageContextType = {
  language: Language;
  setLanguage: (language: Language) => void;
  t: TFunction;
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<PropsWithChildren<{}>> = ({ children }) => {
  const [language, setLanguage] = useLocalStorage<Language>('language', 'fa');

  const t = useCallback((key: string, options: any = {}): string => {
    const keys = key.split('.');
    let result: any = translations[language];
    
    // Navigate through the translation object
    for (const k of keys) {
      result = result?.[k];
      if (result === undefined) {
        // Fallback to English if translation is missing in the current language
        let fallbackResult: any = translations['en'];
        for (const fk of keys) {
          fallbackResult = fallbackResult?.[fk];
        }
        result = fallbackResult;
        break; // Stop searching once fallback is found or fails
      }
    }
    
    let finalString = result || key;

    // Replace placeholders like {count}
    if (typeof finalString === 'string' && options) {
        Object.keys(options).forEach(optKey => {
            finalString = finalString.replace(`{${optKey}}`, options[optKey]);
        });
    }

    return finalString;
  }, [language]);


  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useTranslation = (): LanguageContextType => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useTranslation must be used within a LanguageProvider');
  }
  return context;
};