import { useState, useEffect, useCallback } from 'react';

export function useLocalStorage<T>(key: string, initialValue: T) {
  // Get from local storage then parse stored json or return initialValue
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return initialValue;
    }
    
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // Return a wrapped version of useState's setter function that persists the new value to localStorage
  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      // Allow value to be a function so we have the same API as useState
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  // Listen for changes to this key from other tabs/windows
  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key && e.newValue !== null) {
        try {
          setStoredValue(JSON.parse(e.newValue));
        } catch (error) {
          console.error(`Error parsing localStorage key "${key}":`, error);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [key]);

  return [storedValue, setValue] as const;
}

// Hook for managing multiple localStorage keys with a common prefix
export function useLocalStorageState<T extends Record<string, any>>(
  prefix: string,
  initialState: T
) {
  const [state, setState] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return initialState;
    }

    const savedState = { ...initialState };
    
    Object.keys(initialState).forEach(key => {
      try {
        const item = window.localStorage.getItem(`${prefix}-${key}`);
        if (item) {
          savedState[key as keyof T] = JSON.parse(item);
        }
      } catch (error) {
        console.error(`Error reading localStorage key "${prefix}-${key}":`, error);
      }
    });

    return savedState;
  });

  const updateState = useCallback((updates: Partial<T>) => {
    setState(prevState => {
      const newState = { ...prevState, ...updates };
      
      // Save each updated key to localStorage
      Object.entries(updates).forEach(([key, value]) => {
        try {
          if (typeof window !== 'undefined') {
            window.localStorage.setItem(`${prefix}-${key}`, JSON.stringify(value));
          }
        } catch (error) {
          console.error(`Error setting localStorage key "${prefix}-${key}":`, error);
        }
      });

      return newState;
    });
  }, [prefix]);

  const resetState = useCallback(() => {
    setState(initialState);
    
    // Clear all keys with this prefix from localStorage
    Object.keys(initialState).forEach(key => {
      try {
        if (typeof window !== 'undefined') {
          window.localStorage.removeItem(`${prefix}-${key}`);
        }
      } catch (error) {
        console.error(`Error removing localStorage key "${prefix}-${key}":`, error);
      }
    });
  }, [prefix, initialState]);

  return [state, updateState, resetState] as const;
}

// Hook for managing app-wide settings with validation
export function useSettings<T>(key: string, defaultSettings: T, validator?: (value: any) => value is T) {
  const [settings, setSettings] = useLocalStorage(key, defaultSettings);

  const updateSettings = useCallback((updates: Partial<T>) => {
    const newSettings = { ...settings, ...updates };
    
    // Validate settings if validator is provided
    if (validator && !validator(newSettings)) {
      console.error('Invalid settings update:', updates);
      return;
    }
    
    setSettings(newSettings);
  }, [settings, setSettings, validator]);

  const resetSettings = useCallback(() => {
    setSettings(defaultSettings);
  }, [setSettings, defaultSettings]);

  return [settings, updateSettings, resetSettings] as const;
}

export default useLocalStorage;