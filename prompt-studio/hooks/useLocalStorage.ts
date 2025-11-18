
import { useState, useEffect, Dispatch, SetStateAction } from 'react';

// FIX: Add Dispatch and SetStateAction to imports and use them directly.
function useLocalStorage<T,>(key: string, initialValue: T): [T, Dispatch<SetStateAction<T>>] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.log(error);
      return initialValue;
    }
  });

  // FIX: Use Dispatch and SetStateAction directly without the React namespace.
  const setValue: Dispatch<SetStateAction<T>> = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      // Attempt to save to localStorage first. If this fails, the state won't be updated,
      // keeping the UI consistent with the persisted data.
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
      setStoredValue(valueToStore);
    } catch (error) {
      console.error("Error saving to local storage:", error);
      alert("خطا در ذخیره‌سازی اطلاعات. ممکن است حافظه مرورگر پر شده باشد. لطفا برای آزاد کردن فضا، برخی از پرامپت‌های حجیم (مثلا عکس‌دار) را حذف کنید.");
    }
  };

  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key) {
        try {
          setStoredValue(e.newValue ? JSON.parse(e.newValue) : initialValue);
        } catch (error) {
          console.log(error);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  return [storedValue, setValue];
}

export default useLocalStorage;
