import { ProxyConfig } from '../types';

const VLESS_REGEX = /^vless:\/\/([a-fA-F0-9-]+)@([^:]+):(\d+)\??(.*)$/;
const VMESS_REGEX = /^vmess:\/\/(.*)$/;

export const parseConfig = (text: string): ProxyConfig | null => {
  const trimmedText = text.trim();

  if (VLESS_REGEX.test(trimmedText)) {
    const match = trimmedText.match(VLESS_REGEX);
    if (match) {
      const [, uuid, server, port, params] = match;
      const queryParams = new URLSearchParams(params);
      return {
        id: crypto.randomUUID(),
        name: queryParams.get('remarks') || `${server}:${port}`,
        type: 'VLESS',
        server,
        port: parseInt(port, 10),
      };
    }
  }

  if (VMESS_REGEX.test(trimmedText)) {
    try {
      const decoded = atob(trimmedText.replace('vmess://', ''));
      const vmessConfig = JSON.parse(decoded);
      return {
        id: crypto.randomUUID(),
        name: vmessConfig.ps || `${vmessConfig.add}:${vmessConfig.port}`,
        type: 'VMESS',
        server: vmessConfig.add,
        port: vmessConfig.port,
      };
    } catch (error) {
      console.error('Failed to parse VMESS config:', error);
      return null;
    }
  }

  return null;
};
