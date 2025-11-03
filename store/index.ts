import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { ProxyConfig, ProxyTestResult } from '../types';

interface ProxyState {
  configs: ProxyConfig[];
  results: ProxyTestResult[];
  addConfig: (config: ProxyConfig) => void;
  removeConfig: (id: string) => void;
  addResult: (result: ProxyTestResult) => void;
}

export const useProxyStore = create<ProxyState>()(
  persist(
    (set) => ({
      configs: [],
      results: [],
      addConfig: (config) => set((state) => ({ configs: [...state.configs, config] })),
      removeConfig: (id) => set((state) => ({ configs: state.configs.filter((c) => c.id !== id) })),
      addResult: (result) => set((state) => ({ results: [...state.results, result] })),
    }),
    {
      name: 'proxy-config-storage', // name of the item in the storage (must be unique)
      partialize: (state) => ({ configs: state.configs }), // only persist the 'configs' slice
    }
  )
);
