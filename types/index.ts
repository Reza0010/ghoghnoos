export interface ProxyConfig {
  id: string;
  name: string;
  type: 'VLESS' | 'VMESS' | 'SS' | 'Trojan' | 'HTTP' | 'SOCKS';
  server: string;
  port: number;
  // Add other protocol-specific fields here
}

export interface ProxyTestResult {
  id: string;
  proxyId: string;
  latency: number;
  success: boolean;
  timestamp: number;
}
