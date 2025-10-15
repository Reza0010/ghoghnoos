import React, { useState, useEffect } from 'react';
import { readTextFile, writeTextFile } from '@tauri-apps/api/fs';
import { resolve } from '@tauri-apps/api/path';

const Settings: React.FC = () => {
  const [apiKeys, setApiKeys] = useState<string[]>([]);
  const [newApiKey, setNewApiKey] = useState('');

  const configPath = async () => {
    const configDir = await resolve('.ghoghnoos');
    return `${configDir}/keys.json`;
  };

  useEffect(() => {
    const loadApiKeys = async () => {
      try {
        const path = await configPath();
        const keysJson = await readTextFile(path);
        setApiKeys(JSON.parse(keysJson));
      } catch (error) {
        // It's okay if the file doesn't exist yet
      }
    };
    loadApiKeys();
  }, []);

  const saveApiKeys = async (keys: string[]) => {
    const path = await configPath();
    await writeTextFile(path, JSON.stringify(keys));
  };

  const addApiKey = () => {
    if (newApiKey.trim()) {
      const updatedKeys = [...apiKeys, newApiKey.trim()];
      setApiKeys(updatedKeys);
      saveApiKeys(updatedKeys);
      setNewApiKey('');
    }
  };

  const removeApiKey = (index: number) => {
    const updatedKeys = apiKeys.filter((_, i) => i !== index);
    setApiKeys(updatedKeys);
    saveApiKeys(updatedKeys);
  };

  return (
    <div>
      <h1>Settings</h1>
      <p>Manage your API keys here.</p>
      <input
        type="text"
        value={newApiKey}
        onChange={(e) => setNewApiKey(e.target.value)}
        placeholder="Enter new API key"
      />
      <button onClick={addApiKey}>Add Key</button>
      <ul>
        {apiKeys.map((key, index) => (
          <li key={index}>
            {key} <button onClick={() => removeApiKey(index)}>Remove</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Settings;
