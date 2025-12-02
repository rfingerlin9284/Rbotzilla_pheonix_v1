import io from 'socket.io-client';

const SOCKET_URL = import.meta.env.VITE_WS_URL || 'ws://websocket_server:8008';

export const createSocket = () => {
  const socket = io(SOCKET_URL, {
    transports: ['websocket'],
    reconnectionAttempts: 5,
    reconnectionDelay: 5000,
  });

  return socket;
};

export type MarketEvent = {
  type: string;
  symbol: string;
  price: number;
  timestamp: string;
  news?: string;
  source: string;
};

export type AgentSignal = {
  agent: string;
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  reasoning: string;
  timestamp: string;
};

export type TradeExecution = {
  id: string;
  symbol: string;
  direction: 'LONG' | 'SHORT';
  entryPrice: number;
  exitPrice?: number;
  size: number;
  pnl?: number;
  status: 'OPEN' | 'CLOSED' | 'PENDING';
  openedAt: string;
  closedAt?: string;
  agentsInvolved: string[];
};
