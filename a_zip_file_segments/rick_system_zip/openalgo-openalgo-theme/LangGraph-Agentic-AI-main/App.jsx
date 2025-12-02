import React, { useEffect, useState, useCallback, useMemo, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, 
  DollarSign, 
  Bot, 
  Shield,
  Eye,
  Globe,
  Zap,
  Settings,
  Wifi,
  WifiOff,
  Play,
  Pause,
  AlertTriangle,
  LayoutDashboard,
  BarChart2,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  Legend,
} from 'recharts';

// Dummy data for the trading analytics dashboard
const DUMMY_PERFORMANCE_DATA = [
  { name: 'Jan', PnL: 2400, Trades: 4 },
  { name: 'Feb', PnL: 1398, Trades: 2 },
  { name: 'Mar', PnL: 2980, Trades: 3 },
  { name: 'Apr', PnL: 3908, Trades: 5 },
  { name: 'May', PnL: 4800, Trades: 6 },
  { name: 'Jun', PnL: 3800, Trades: 4 },
  { name: 'Jul', PnL: 4300, Trades: 7 },
  { name: 'Aug', PnL: 5100, Trades: 9 },
];

const DUMMY_AGENT_SIGNALS = [
  { name: 'Week 1', buy: 12, sell: 8, neutral: 5 },
  { name: 'Week 2', buy: 15, sell: 10, neutral: 3 },
  { name: 'Week 3', buy: 8, sell: 14, neutral: 6 },
  { name: 'Week 4', buy: 20, sell: 11, neutral: 4 },
];

// Agent status indicator component from the original file
const AgentStatusIndicator = ({ status, lastUpdate }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const timeSinceUpdate = Date.now() - (lastUpdate || 0);
  const isStale = timeSinceUpdate > 30000; // 30 seconds

  return (
    <div className="flex items-center gap-2">
      <div className={`w-3 h-3 rounded-full ${getStatusColor()} ${status === 'active' ? 'animate-pulse' : ''}`} />
      <span className={`text-xs ${isStale ? 'text-red-400' : 'text-gray-400'}`}>
        {isStale ? 'Stale' : 'Live'}
      </span>
    </div>
  );
};

// Agent card component with real-time updates from the original file
const AgentCard = ({ agent, data, onToggle }) => {
  const { name, icon: Icon, description, status, isEnabled } = agent;
  const cardData = data || { updates: [], pnl: 0, positions: 0 };
  
  const statusColor = useMemo(() => {
    switch(status) {
      case 'active': return 'border-green-500';
      case 'warning': return 'border-yellow-500';
      case 'error': return 'border-red-500';
      default: return 'border-gray-700';
    }
  }, [status]);

  return (
    <div className={`
      p-6 rounded-xl shadow-lg border-2 ${statusColor}
      bg-gray-800/80 backdrop-blur-sm
      flex flex-col h-full transition-all duration-300
    `}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-gray-700 rounded-full">
            <Icon className="w-6 h-6 text-purple-400" />
          </div>
          <h3 className="text-xl font-bold text-gray-200">{name}</h3>
        </div>
        <button
          onClick={() => onToggle(name)}
          className={`
            p-2 rounded-full transition-colors duration-200
            ${isEnabled ? 'bg-green-500 hover:bg-green-600' : 'bg-gray-600 hover:bg-gray-700'}
          `}
        >
          {isEnabled ? <Pause className="w-5 h-5 text-white" /> : <Play className="w-5 h-5 text-white" />}
        </button>
      </div>

      <p className="text-sm text-gray-400 mb-4 flex-grow">{description}</p>
      
      <div className="grid grid-cols-2 gap-4 text-sm mb-4">
        <div className="flex flex-col">
          <span className="text-gray-500">P&L</span>
          <span className={`font-semibold ${cardData.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {cardData.pnl >= 0 ? '+' : ''}${cardData.pnl.toFixed(2)}
          </span>
        </div>
        <div className="flex flex-col">
          <span className="text-gray-500">Open Positions</span>
          <span className="font-semibold text-gray-200">{cardData.positions}</span>
        </div>
      </div>
      
      <div className="flex justify-between items-center mt-auto">
        <AgentStatusIndicator status={status} lastUpdate={cardData.lastUpdate} />
        <span className={`
          px-3 py-1 text-xs font-semibold rounded-full
          ${isEnabled ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}
        `}>
          {isEnabled ? 'Enabled' : 'Disabled'}
        </span>
      </div>
    </div>
  );
};


// The original App component, now a dedicated Agent Dashboard
const AgentDashboard = () => {
  const [agents, setAgents] = useState([
    { name: 'ChartAnalyst', icon: TrendingUp, description: 'Performs technical analysis and generates trading signals based on patterns.', status: 'active', isEnabled: true },
    { name: 'RiskManager', icon: Shield, description: 'Evaluates trading risk and position sizing based on predefined thresholds.', status: 'active', isEnabled: true },
    { name: 'MarketSentinel', icon: Eye, description: 'Monitors live market feeds for anomalies, news, and volatility spikes.', status: 'warning', isEnabled: true },
    { name: 'MacroForecaster', icon: Globe, description: 'Predicts macroeconomic trends and assesses their potential impact on the market.', status: 'active', isEnabled: false },
    { name: 'TacticBot', icon: Zap, description: 'Aggregates all signals, applies trading logic, and executes tactical strategies.', status: 'active', isEnabled: true },
    { name: 'PlatformPilot', icon: Settings, description: 'Manages platform-level operations, logs actions, and serves as an audit trail.', status: 'active', isEnabled: true },
  ]);

  const [agentData, setAgentData] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [isOnline, setIsOnline] = useState(true);

  // Simulated real-time data updates
  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate data updates for each agent
      const newAgentData = {};
      agents.forEach(agent => {
        const lastData = agentData[agent.name] || { updates: [], pnl: 0, positions: 0 };
        newAgentData[agent.name] = {
          updates: [...lastData.updates, { message: `Update from ${agent.name}`, timestamp: Date.now() }].slice(-5),
          pnl: lastData.pnl + (Math.random() - 0.5) * 100,
          positions: Math.floor(Math.random() * 5),
          lastUpdate: Date.now(),
        };
      });
      setAgentData(newAgentData);

      // Simulate alerts
      if (Math.random() > 0.8) {
        setAlerts(prev => [
          ...prev,
          { id: Date.now(), message: `Critical alert from MarketSentinel!`, timestamp: Date.now() }
        ]);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [agents, agentData]);

  const handleAgentToggle = useCallback((name) => {
    setAgents(prev => prev.map(agent => 
      agent.name === name ? { ...agent, isEnabled: !agent.isEnabled } : agent
    ));
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
  };
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="p-8 w-full"
    >
      <div className="max-w-7xl mx-auto">
        {/* Header Section */}
        <motion.header
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-12"
        >
          <h1 className="text-4xl font-extrabold text-white text-center">
            Multi-Agent Trading System
          </h1>
          <p className="text-center text-gray-400 mt-2">
            Real-time orchestration of autonomous trading agents.
          </p>
        </motion.header>

        {/* System Status and Alerts */}
        <AnimatePresence>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="flex flex-col md:flex-row justify-between items-center bg-gray-800/60 backdrop-blur-sm p-4 rounded-xl shadow-inner border border-gray-700 mb-8"
          >
            <div className="flex items-center space-x-4 mb-4 md:mb-0">
              <span className="text-gray-400 font-medium">System Status:</span>
              <span className={`px-4 py-2 rounded-full font-bold text-sm ${isOnline ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                <div className="flex items-center gap-2">
                  {isOnline ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
                  {isOnline ? 'Online' : 'Offline'}
                </div>
              </span>
            </div>
            <div className="relative w-full md:w-auto">
              <div className="flex items-center space-x-2 text-yellow-200">
                <AlertTriangle className="w-5 h-5" />
                <span className="font-semibold">Alerts ({alerts.length})</span>
              </div>
            </div>
          </motion.div>
        </AnimatePresence>

        <AnimatePresence>
          {alerts.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -20, height: 0 }}
              animate={{ opacity: 1, y: 0, height: 'auto' }}
              exit={{ opacity: 0, y: -20, height: 0 }}
              transition={{ duration: 0.3 }}
              className="bg-yellow-900/40 border border-yellow-700 text-yellow-100 p-4 rounded-xl mb-8 overflow-hidden"
            >
              <div className="max-h-24 overflow-y-auto">
                {alerts.map((alert, index) => (
                  <div key={alert.id} className="text-yellow-200 mb-1">
                    {new Date(alert.timestamp).toLocaleTimeString()}: {alert.message}
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Agent Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto"
        >
          {agents.map((agent, index) => (
            <motion.div
              key={agent.name}
              variants={itemVariants}
              transition={{ delay: index * 0.1 }}
            >
              <AgentCard
                agent={agent}
                data={agentData[agent.name]}
                onToggle={handleAgentToggle}
              />
            </motion.div>
          ))}
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1 }}
          className="text-center mt-12 text-gray-400"
        >
          <p className="text-sm">
            Powered by LangGraph Architecture • Redis Event Bus • PostgreSQL Analytics
          </p>
          <p className="text-xs mt-2">
            Real-time AI agents working in harmony to optimize your trading strategies
          </p>
        </motion.div>
      </div>
    </motion.div>
  );
};


// A helper component for the dashboard metric cards
const MetricCard = ({ title, value, change, icon: Icon }) => (
  <motion.div
    whileHover={{ scale: 1.03 }}
    className="bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 shadow-lg border border-gray-700 relative overflow-hidden"
  >
    <div className="relative z-10">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-semibold text-gray-300">{title}</h4>
        <Icon className="w-8 h-8 text-purple-400 opacity-70" />
      </div>
      <div className="text-4xl font-bold text-white mb-2">{value}</div>
      <div className="text-sm font-medium flex items-center gap-1">
        <span className={`py-1 px-2 rounded-full ${
          change.startsWith('+') ? 'bg-green-600/30 text-green-400' : 'bg-red-600/30 text-red-400'}
        }`}>
          {change}
        </span>
        <span className="text-gray-400">vs. last period</span>
      </div>
    </div>
  </motion.div>
);

// New component for the Trading Analytics Dashboard
const TradingAnalytics = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-8 w-full p-8"
    >
      <div className="max-w-7xl mx-auto">
        <h2 className="text-3xl font-bold text-gray-200 mb-8 text-center">Trading Analytics Dashboard</h2>
        
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.1 }}>
            <MetricCard title="Total P&L" value="$12,450" change="+12.3%" icon={DollarSign} />
          </motion.div>
          <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.2 }}>
            <MetricCard title="Total Trades" value="238" change="+5.1%" icon={TrendingUp} />
          </motion.div>
          <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.3 }}>
            <MetricCard title="Win Rate" value="68.2%" change="+1.8%" icon={BarChart2} />
          </motion.div>
        </div>

        {/* Performance Chart */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 shadow-lg border border-gray-700 mb-8"
        >
          <h3 className="text-xl font-semibold mb-4 text-gray-200">Monthly Performance (P&L)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={DUMMY_PERFORMANCE_DATA}>
              <CartesianGrid strokeDasharray="3 3" stroke="#4a5568" />
              <XAxis dataKey="name" stroke="#cbd5e0" />
              <YAxis stroke="#cbd5e0" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4a5568', borderRadius: '8px' }}
                labelStyle={{ color: '#e2e8f0' }}
                itemStyle={{ color: '#e2e8f0' }}
              />
              <Line type="monotone" dataKey="PnL" stroke="#8884d8" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Agent Signal Distribution Chart */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 shadow-lg border border-gray-700"
        >
          <h3 className="text-xl font-semibold mb-4 text-gray-200">Agent Signal Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={DUMMY_AGENT_SIGNALS}>
              <CartesianGrid strokeDasharray="3 3" stroke="#4a5568" />
              <XAxis dataKey="name" stroke="#cbd5e0" />
              <YAxis stroke="#cbd5e0" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4a5568', borderRadius: '8px' }}
                labelStyle={{ color: '#e2e8f0' }}
                itemStyle={{ color: '#e2e8f0' }}
              />
              <Legend wrapperStyle={{ color: '#cbd5e0' }} />
              <Bar dataKey="buy" stackId="a" fill="#34d399" name="Buy Signals" />
              <Bar dataKey="sell" stackId="a" fill="#ef4444" name="Sell Signals" />
              <Bar dataKey="neutral" stackId="a" fill="#facc15" name="Neutral Signals" />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>
    </motion.div>
  );
};


// The main App component with the new sidebar navigation
export default function App() {
  const [activeTab, setActiveTab] = useState('agents');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const sidebarVariants = {
    open: { width: '256px', transition: { duration: 0.3 } },
    closed: { width: '80px', transition: { duration: 0.3 } }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'agents':
        return <AgentDashboard />;
      case 'analytics':
        return <TradingAnalytics />;
      default:
        return <AgentDashboard />;
    }
  };

  const NavItem = ({ name, icon: Icon, onClick, isActive }) => (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={`
        flex items-center w-full text-left p-4 rounded-xl mb-2 transition-colors duration-200
        ${isActive ? 'bg-purple-600 text-white' : 'text-gray-300 hover:bg-gray-700 hover:text-white'}
      `}
    >
      <Icon className="w-6 h-6 shrink-0" />
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.span
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 16 }}
            exit={{ opacity: 0, x: -10 }}
            className="ml-4 font-medium whitespace-nowrap overflow-hidden"
          >
            {name}
          </motion.span>
        )}
      </AnimatePresence>
    </motion.button>
  );

  return (
    <div className="flex min-h-screen bg-gray-950 text-white font-sans">
      {/* Sidebar */}
      <motion.nav
        variants={sidebarVariants}
        initial="closed"
        animate={isSidebarOpen ? "open" : "closed"}
        className="flex flex-col bg-gray-900 border-r border-gray-800 p-4 relative"
      >
        <div className="flex items-center justify-between h-16 mb-8">
          {isSidebarOpen && (
            <motion.h2
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-2xl font-bold text-purple-400 px-4"
            >
              System
            </motion.h2>
          )}
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 rounded-full text-gray-400 hover:bg-gray-700"
          >
            {isSidebarOpen ? <ChevronLeft className="w-6 h-6" /> : <ChevronRight className="w-6 h-6" />}
          </button>
        </div>

        <div className="flex-grow">
          <NavItem 
            name="Agent Dashboard" 
            icon={Bot} 
            onClick={() => setActiveTab('agents')} 
            isActive={activeTab === 'agents'}
          />
          <NavItem 
            name="Trading Analytics" 
            icon={BarChart2} 
            onClick={() => setActiveTab('analytics')} 
            isActive={activeTab === 'analytics'}
          />
        </div>
      </motion.nav>

      {/* Main content area */}
      <div className="flex-1 overflow-y-auto">
        {renderContent()}
      </div>
    </div>
  );
}

