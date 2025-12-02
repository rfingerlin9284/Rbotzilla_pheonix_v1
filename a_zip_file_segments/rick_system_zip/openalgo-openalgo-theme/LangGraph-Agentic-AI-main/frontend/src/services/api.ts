import { SignalWebSocket } from './websocket';

// Initialize WebSocket connection
export const tradingSocket = new SignalWebSocket();

// Placeholder for API calls (replace with actual backend API calls)
export const fetchMarketOverview = async () => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 500));
  return {
    timestamps: ["10:00", "10:05", "10:10", "10:15", "10:20", "10:25", "10:30"],
    prices: {
      gold: [1900, 1905, 1902, 1908, 1910, 1907, 1912],
      silver: [24.0, 24.1, 23.9, 24.2, 24.3, 24.1, 24.4],
      dxy: [105.0, 105.1, 104.9, 105.2, 105.3, 105.1, 105.4],
    },
  };
};

export const fetchTradeHistory = async (days: number) => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 700));
  return [
    { id: '1', symbol: 'XAUUSD', direction: 'LONG', entryPrice: 1900, exitPrice: 1910, size: 0.1, pnl: 100, status: 'CLOSED', openedAt: '2025-08-01T10:00:00Z', closedAt: '2025-08-01T10:30:00Z', agentsInvolved: ['ChartAnalyst', 'TacticBot'] },
    { id: '2', symbol: 'EURUSD', direction: 'SHORT', entryPrice: 1.08, exitPrice: 1.075, size: 0.5, pnl: 50, status: 'CLOSED', openedAt: '2025-08-02T11:00:00Z', closedAt: '2025-08-02T11:15:00Z', agentsInvolved: ['RiskManager', 'PlatformPilot'] },
    { id: '3', symbol: 'XAGUSD', direction: 'LONG', entryPrice: 24.0, exitPrice: 24.1, size: 0.2, pnl: 20, status: 'OPEN', openedAt: '2025-08-03T12:00:00Z', agentsInvolved: ['MarketSentinel'] },
  ];
};