import { NavLink } from 'react-router-dom';
import { IconChartCandle, IconRobot, IconCoin, IconChartLine, IconSettings } from '@tabler/icons-react';
import { motion } from 'framer-motion';

const navItems = [
  { path: '/', icon: IconChartCandle, label: 'Dashboard' },
  { path: '/agents', icon: IconRobot, label: 'Agents' },
  { path: '/trades', icon: IconCoin, label: 'Trades' },
  { path: '/market', icon: IconChartLine, label: 'Market' },
  { path: '/settings', icon: IconSettings, label: 'Settings' },
];

export function Navbar() {
  return (
    <nav className="w-20 md:w-64 bg-dark-900 border-r border-dark-700 flex flex-col">
      <div className="p-4 border-b border-dark-700">
        <h1 className="text-2xl font-bold text-center md:text-left text-neon-primary hidden md:block">
          AgenticTrader
        </h1>
        <div className="md:hidden flex justify-center">
          <div className="w-10 h-10 rounded-full bg-neon-primary/10 flex items-center justify-center">
            <IconRobot className="text-neon-primary" />
          </div>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-2 px-2">
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center p-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-neon-primary/10 text-neon-primary'
                      : 'text-gray-400 hover:bg-dark-800 hover:text-gray-200'
                  }`
                }
              >
                <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}>
                  <item.icon className="w-6 h-6" />
                </motion.div>
                <span className="ml-3 hidden md:block">{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </div>
      <div className="p-4 border-t border-dark-700 text-center text-xs text-gray-500">
        <p className="hidden md:block">Agentic Trading System</p>
        <p className="hidden md:block">v1.0.0</p>
      </div>
    </nav>
  );
}
