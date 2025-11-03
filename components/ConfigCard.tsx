import React from 'react';
import { Shield, FileCode, Ghost, Network, Globe, Server } from 'lucide-react';
import { ProxyConfig } from '../types';

interface ConfigCardProps {
  config: ProxyConfig;
}

const protocolIcons = {
  VLESS: <Shield size={24} />,
  VMESS: <FileCode size={24} />,
  SS: <Ghost size={24} />,
  Trojan: <Network size={24} />,
  HTTP: <Globe size={24} />,
  SOCKS: <Server size={24} />,
};

const ConfigCard: React.FC<ConfigCardProps> = ({ config }) => {
  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md flex items-center justify-between">
      <div className="flex items-center">
        <div className="mr-4">{protocolIcons[config.type]}</div>
        <div>
          <h3 className="font-bold">{config.name}</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">{config.server}:{config.port}</p>
        </div>
      </div>
    </div>
  );
};

export default ConfigCard;
