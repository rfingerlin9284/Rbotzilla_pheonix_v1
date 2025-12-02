import { create } from 'zustand';
import { AgentSignal, MarketEvent, TradeExecution } from '../services/socket';

interface DashboardState {
  marketEvents: MarketEvent[];
  agentSignals: AgentSignal[];
  activeTrades: TradeExecution[];
  agentStatus: Record<string, { status: 'online' | 'offline'; lastActive: string }>;
  addMarketEvent: (event: MarketEvent) => void;
  addAgentSignal: (signal: AgentSignal) => void;
  updateTrade: (trade: TradeExecution) => void;
  setAgentStatus: (status: DashboardState['agentStatus']) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  marketEvents: [],
  agentSignals: [],
  activeTrades: [],
  agentStatus: {},
  addMarketEvent: (event) => set((state) => ({ marketEvents: [event, ...state.marketEvents].slice(0, 100) })),
  addAgentSignal: (signal) => set((state) => ({ agentSignals: [signal, ...state.agentSignals].slice(0, 50) })),
  updateTrade: (trade) => set((state) => {
    const existingIndex = state.activeTrades.findIndex(t => t.id === trade.id);
    if (existingIndex >= 0) {
      const updated = [...state.activeTrades];
      updated[existingIndex] = trade;
      return { activeTrades: updated };
    }
    return { activeTrades: [trade, ...state.activeTrades] };
  }),
  setAgentStatus: (status) => set({ agentStatus: status }),
}));
