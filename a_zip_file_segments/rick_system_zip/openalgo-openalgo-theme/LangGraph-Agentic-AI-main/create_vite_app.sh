#!/bin/bash

set -e

# Project name
PROJECT_NAME="agentic-frontend"

echo "Creating a new Vite React + TypeScript project: $PROJECT_NAME"

# Create a new Vite project and navigate into it
npm create vite@latest "$PROJECT_NAME" -- --template react-ts
cd "$PROJECT_NAME"

echo "Installing dependencies..."
npm install tailwindcss postcss autoprefixer react-router-dom zustand @tanstack/react-query recharts framer-motion axios

echo "Initializing Tailwind CSS..."
npx tailwindcss init -p

# Create the full directory structure
mkdir -p src/{api,components,hooks,store,features/dashboard,features/agent-detail,styles,types}

echo "Writing file contents..."

# === CONFIGURATION AND STYLING FILES ===
cat << EOF > tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'background-dark': '#0a0a0f',
        'primary-neon': '#00ffc8',
        'secondary-neon': '#ff33ff',
        'tertiary-neon': '#33ffff',
        'glow-green': 'rgba(0, 255, 200, 0.5)',
        'glow-purple': 'rgba(255, 51, 255, 0.5)',
      },
      fontFamily: {
        'mono': ['Fira Code', 'monospace'],
      },
      boxShadow: {
        'neon-glow': '0 0 10px rgba(0, 255, 200, 0.7), 0 0 20px rgba(0, 255, 200, 0.5)',
        'neon-glow-purple': '0 0 10px rgba(255, 51, 255, 0.7), 0 0 20px rgba(255, 51, 255, 0.5)',
      },
    },
  },
  plugins: [],
}
EOF

cat << EOF > src/styles/globals.css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html, body, #root {
    @apply h-full bg-background-dark text-primary-neon font-mono;
  }

  /* Global styles for neon text and elements */
  .neon-text {
    text-shadow: 0 0 5px #00ffc8, 0 0 10px #00ffc8, 0 0 20px #00ffc8, 0 0 40px #00ffc8;
  }

  .neon-border {
    border: 1px solid #00ffc8;
    box-shadow: 0 0 5px rgba(0, 255, 200, 0.5);
  }
  
  /* Additional effects */
  @keyframes pulse-glow {
    0%, 100% {
      box-shadow: 0 0 10px rgba(0, 255, 200, 0.7);
    }
    50% {
      box-shadow: 0 0 20px rgba(0, 255, 200, 0.9);
    }
  }
}
EOF

# === TYPE DEFINITIONS ===
cat << EOF > src/types/index.ts
export interface AgentSignal {
  id: string;
  agent: string;
  signal_type: 'buy' | 'sell' | 'hold';
  symbol: string;
  reasoning: string;
  timestamp: string;
  value?: number;
}

export interface TradeOutcome {
  id: string;
  symbol: string;
  pnl: number;
  direction: 'long' | 'short';
  timestamp: string;
}

export interface SystemStatus {
  agents: Record<string, 'active' | 'inactive' | 'error'>;
  eventBusConnected: boolean;
  lastUpdate: string;
}

export interface AgentInfo {
  name: string;
  model: string;
  description: string;
}
EOF

# === STATE MANAGEMENT ===
cat << EOF > src/store/useTradingStore.ts
import { create } from 'zustand';
import { AgentSignal, TradeOutcome, SystemStatus, AgentInfo } from '../types';

interface TradingState {
  signals: AgentSignal[];
  tradeOutcomes: TradeOutcome[];
  systemStatus: SystemStatus;
  agentsInfo: AgentInfo[];
  addSignal: (signal: AgentSignal) => void;
  addTradeOutcome: (outcome: TradeOutcome) => void;
  setSystemStatus: (status: Partial<SystemStatus>) => void;
  setAgentsInfo: (info: AgentInfo[]) => void;
}

const MAX_SIGNALS = 50;
const MAX_TRADES = 20;

export const useTradingStore = create<TradingState>((set) => ({
  signals: [],
  tradeOutcomes: [],
  systemStatus: {
    agents: {},
    eventBusConnected: false,
    lastUpdate: new Date().toISOString(),
  },
  agentsInfo: [
    { name: 'chartanalyst', model: 'Mistral/LLaMA', description: 'Analyzes price charts...' },
    { name: 'riskmanager', model: 'Kimi K2/Claude', description: 'Applies sizing...' },
    { name: 'marketsentinel', model: 'Qwen/GPT-4', description: 'Monitors news...' },
    { name: 'macroforecaster', model: 'TNG/Gemini-2.5', description: 'Analyzes macro trends...' },
    { name: 'tacticbot', model: 'GLM/Horizon', description: 'Entry/exit strategies...' },
    { name: 'platformpilot', model: 'Kimi Dev 72B', description: 'Logs all actions...' },
  ],

  addSignal: (newSignal) => set((state) => ({
    signals: [newSignal, ...state.signals].slice(0, MAX_SIGNALS),
  })),

  addTradeOutcome: (newOutcome) => set((state) => ({
    tradeOutcomes: [newOutcome, ...state.tradeOutcomes].slice(0, MAX_TRADES),
  })),

  setSystemStatus: (status) => set((state) => ({
    systemStatus: { ...state.systemStatus, ...status, lastUpdate: new Date().toISOString() },
  })),

  setAgentsInfo: (info) => set({ agentsInfo: info }),
}));
EOF

# === HOOKS ===
cat << EOF > src/hooks/useWebSocket.ts
import { useEffect, useRef } from 'react';
import { useTradingStore } from '../store/useTradingStore';

export const useWebSocket = (url: string) => {
  const store = useTradingStore();
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      console.log('WebSocket connected');
      store.setSystemStatus({ eventBusConnected: true });
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Received from WebSocket:', data);

        if (data.type === 'agent_signal') {
          store.addSignal(data.payload);
        } else if (data.type === 'trade_outcome') {
          store.addTradeOutcome(data.payload);
        } else if (data.type === 'system_status') {
          store.setSystemStatus(data.payload);
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
      store.setSystemStatus({ eventBusConnected: false });
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      store.setSystemStatus({ eventBusConnected: false });
    };

    return () => {
      ws.current?.close();
    };
  }, [url, store]);

  return ws.current;
};
EOF

# === COMPONENTS ===
cat << EOF > src/components/Panel.tsx
import React from 'react';
import { motion } from 'framer-motion';

interface PanelProps {
  title: string;
  children: React.ReactNode;
}

export const Panel: React.FC<PanelProps> = ({ title, children }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-background-dark p-6 rounded-xl neon-border"
    >
      <h2 className="text-xl font-bold text-primary-neon mb-4 neon-text">{title}</h2>
      <div>{children}</div>
    </motion.div>
  );
};
EOF

cat << EOF > src/components/SignalCard.tsx
import React from 'react';
import { motion } from 'framer-motion';
import { AgentSignal } from '../types';

interface SignalCardProps {
  signal: AgentSignal;
}

const getSignalColors = (type: 'buy' | 'sell' | 'hold') => {
  switch (type) {
    case 'buy': return { text: 'text-primary-neon', bg: 'bg-green-500/10', border: 'border-green-500' };
    case 'sell': return { text: 'text-red-500', bg: 'bg-red-500/10', border: 'border-red-500' };
    case 'hold': return { text: 'text-gray-500', bg: 'bg-gray-500/10', border: 'border-gray-500' };
  }
};

export const SignalCard: React.FC<SignalCardProps> = ({ signal }) => {
  const { text, bg, border } = getSignalColors(signal.signal_type);
  const time = new Date(signal.timestamp).toLocaleTimeString();

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={\`p-4 rounded-lg border \${border} \${bg} mb-2 cursor-pointer hover:shadow-neon-glow-purple transition-shadow\`}
    >
      <div className="flex justify-between items-center mb-1">
        <span className="font-bold uppercase text-sm">{signal.agent}</span>
        <span className={\`text-xs \${text} font-bold\`}>{time}</span>
      </div>
      <p className="text-sm text-gray-300">{signal.reasoning}</p>
    </motion.div>
  );
};
EOF

# === FEATURE COMPONENTS ===
cat << EOF > src/features/dashboard/Dashboard.tsx
import { Panel } from '../../components/Panel';
import { SignalCard } from '../../components/SignalCard';
import { useTradingStore } from '../../store/useTradingStore';
import { Link } from 'react-router-dom';

export const Dashboard = () => {
  const signals = useTradingStore(s => s.signals);
  const tradeOutcomes = useTradingStore(s => s.tradeOutcomes);
  const agentsInfo = useTradingStore(s => s.agentsInfo);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Real-time signals panel */}
      <div className="lg:col-span-1">
        <Panel title="Real-time Agent Signals">
          <div className="h-[500px] overflow-y-scroll pr-2">
            {signals.length > 0 ? (
              signals.map((signal) => (
                <SignalCard key={signal.id} signal={signal} />
              ))
            ) : (
              <p className="text-gray-500">Awaiting signals...</p>
            )}
          </div>
        </Panel>
      </div>

      {/* Main trading view (placeholder for chart) */}
      <div className="lg:col-span-2">
        <Panel title="Live Chart & Strategy Execution">
          <div className="h-[500px] bg-gray-900 rounded-lg flex items-center justify-center">
            <p className="text-gray-500">Live Chart Integration Here (e.g., Recharts, ApexCharts)</p>
          </div>
        </Panel>
      </div>

      {/* Agents status and trade outcomes */}
      <div className="lg:col-span-1 grid grid-rows-2 gap-6">
        <Panel title="Agents Overview">
          <ul>
            {agentsInfo.map(agent => (
              <li key={agent.name} className="flex justify-between items-center py-2 border-b border-gray-800 last:border-b-0">
                <span className="text-lg text-tertiary-neon">{agent.name}</span>
                <Link to={\`/agent/\${agent.name}\`} className="text-sm underline text-gray-500 hover:text-primary-neon">
                  View Details
                </Link>
              </li>
            ))}
          </ul>
        </Panel>
        <Panel title="Recent Trade Outcomes">
          <ul>
            {tradeOutcomes.length > 0 ? (
              tradeOutcomes.map(trade => (
                <li key={trade.id} className="py-2 border-b border-gray-800 last:border-b-0 flex justify-between items-center">
                  <span className="text-sm">{trade.symbol}</span>
                  <span className={\`text-sm font-bold \${trade.pnl >= 0 ? 'text-primary-neon' : 'text-red-500'}\`}>
                    {trade.pnl > 0 ? '+' : ''}{trade.pnl.toFixed(2)}
                  </span>
                </li>
              ))
            ) : (
              <p className="text-gray-500">No recent trades.</p>
            )}
          </ul>
        </Panel>
      </div>
    </div>
  );
};
EOF

# Agent detail placeholder
cat << EOF > src/features/agent-detail/AgentDetail.tsx
import React from 'react';
import { useParams } from 'react-router-dom';
import { Panel } from '../../components/Panel';

export const AgentDetail = () => {
  const { agentName } = useParams();

  return (
    <div className="p-4">
      <h1 className="text-4xl font-bold mb-6 neon-text">Agent: {agentName}</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Panel title="Agent Log">
          <div className="h-96 overflow-y-scroll bg-gray-900 p-4 rounded-lg text-sm text-gray-300">
            {/* Live log will be streamed here */}
            <p>Awaiting live log from {agentName}...</p>
          </div>
        </Panel>
        <Panel title="Historical Signals">
          <div className="h-96 overflow-y-scroll bg-gray-900 p-4 rounded-lg text-sm text-gray-300">
            {/* Historical signals from the DB will be listed here */}
            <p>No historical data for {agentName}.</p>
          </div>
        </Panel>
      </div>
    </div>
  );
};
EOF


# === MAIN APPLICATION FILES ===
cat << EOF > src/App.tsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useWebSocket } from './hooks/useWebSocket';
import { Dashboard } from './features/dashboard/Dashboard';
import { AgentDetail } from './features/agent-detail/AgentDetail';
import { Panel } from './components/Panel';
import { useTradingStore } from './store/useTradingStore';

const WS_URL = 'ws://localhost:8000/ws/dashboard'; // Update this to your FastAPI WebSocket URL

function App() {
  useWebSocket(WS_URL);
  const status = useTradingStore(s => s.systemStatus);

  return (
    <Router>
      <div className="min-h-screen p-8 bg-background-dark text-white font-mono">
        <header className="flex justify-between items-center pb-6 border-b border-gray-700 mb-6">
          <h1 className="text-3xl font-bold neon-text">Agentic Trader Dashboard</h1>
          <div className="flex items-center">
            <span className={\`h-3 w-3 rounded-full mr-2 animate-pulse \${status.eventBusConnected ? 'bg-primary-neon' : 'bg-red-500'}\`} />
            <span className="text-sm text-gray-400">
              {status.eventBusConnected ? 'System Operational' : 'Connection Lost'}
            </span>
          </div>
        </header>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/agent/:agentName" element={<AgentDetail />} />
          <Route path="*" element={<Panel title="404 - Not Found">Page not found.</Panel>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
EOF

cat << EOF > src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './styles/globals.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
EOF

echo "Done! The Vite app '$PROJECT_NAME' has been created."
echo "Navigate into the directory and run 'npm run dev' to start the development server."

