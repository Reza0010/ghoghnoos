import React from 'react';
import { saveBackup, loadBackup } from '../services/storage';

type SettingsState = {
  apiKey: string;
  useEncryption: boolean;
  autoBackup: boolean;
  backupIntervalSec: number;
};

const defaultState: SettingsState = {
  apiKey: '',
  useEncryption: false,
  autoBackup: true,
  backupIntervalSec: 30
};

export default function SettingsPanel() {
  const [state, setState] = React.useState<SettingsState>(() => {
    try {
      const raw = localStorage.getItem('prompt-studio-settings');
      return raw ? JSON.parse(raw) : defaultState;
    } catch {
      return defaultState;
    }
  });

  React.useEffect(() => {
    localStorage.setItem('prompt-studio-settings', JSON.stringify(state));
  }, [state]);

  const onChange = (k: keyof SettingsState, v: any) => {
    setState(prev => ({ ...prev, [k]: v }));
  };

  const exportBackup = async () => {
    const data = { prompts: [] };
    await saveBackup(data);
    alert('پشتیبان محلی ساخته شد.');
  };

  const restoreBackup = async () => {
    const b = await loadBackup();
    if (b) {
      alert('پشتیبان بازیابی شد. (بایستی داده‌ها در استیت بارگذاری شوند)');
    } else {
      alert('پشتیبانی پیدا نشد.');
    }
  };

  return (
    <div className="settings-panel">
      <h2>تنظیمات</h2>

      <label>کلید API</label>
      <input
        type="password"
        value={state.apiKey}
        onChange={e => onChange('apiKey', e.target.value)}
        placeholder="API Key"
      />

      <label>
        <input
          type="checkbox"
          checked={state.useEncryption}
          onChange={e => onChange('useEncryption', e.target.checked)}
        /> رمزگذاری محلی کلید API
      </label>

      <label>
        <input
          type="checkbox"
          checked={state.autoBackup}
          onChange={e => onChange('autoBackup', e.target.checked)}
        /> پشتیبان‌گیری خودکار
      </label>

      <label>
        فاصلهٔ پشتیبان (ثانیه)
        <input
          type="number"
          min={5}
          value={state.backupIntervalSec}
          onChange={e => onChange('backupIntervalSec', Number(e.target.value))}
        />
      </label>

      <div style={{ marginTop: 12 }}>
        <button onClick={exportBackup}>ساخت پشتیبان فوری</button>
        <button onClick={restoreBackup}>بازیابی پشتیبان</button>
      </div>
    </div>
  );
}
