import React from 'react';
import MultiInputSmartBox from './MultiInputSmartBox';
import ConfigCard from './ConfigCard';
import { useProxyStore } from '../store';

const ConfigManagement: React.FC = () => {
  const { configs } = useProxyStore();

  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Config Management</h1>
      <MultiInputSmartBox />
      <div className="mt-8 space-y-4">
        {configs.map((config) => (
          <ConfigCard key={config.id} config={config} />
        ))}
      </div>
    </div>
  );
};

export default ConfigManagement;
