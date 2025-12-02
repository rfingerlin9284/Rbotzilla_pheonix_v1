import { useDashboardStore } from '../../store/useDashboardStore';
import { Badge } from '@mantine/core';
import { IconActivity, IconCheck, IconX } from '@tabler/icons-react';

export function AgentStatusGrid() {
  const agentStatus = useDashboardStore((state) => state.agentStatus);

  const agents = [
    { name: 'chartanalyst', label: 'Chart Analyst' },
    { name: 'riskmanager', label: 'Risk Manager' },
    { name: 'marketsentinel', label: 'Market Sentinel' },
    { name: 'macroforecaster', label: 'Macro Forecaster' },
    { name: 'tacticbot', label: 'Tactic Bot' },
    { name: 'platformpilot', label: 'Platform Pilot' },
  ];

  return (
    <div className="bg-dark-700 rounded-xl p-6">
      <h2 className="text-xl font-bold text-neon-primary mb-4">Agent Status</h2>
      <div className="grid grid-cols-2 gap-4">
        {agents.map((agent) => {
          const status = agentStatus[agent.name];
          const isOnline = status?.status === 'online';
          
          return (
            <div
              key={agent.name}
              className={`p-4 rounded-lg border ${isOnline ? 'border-neon-secondary' : 'border-red-500/50'} bg-dark-800`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-full ${isOnline ? 'bg-neon-secondary/10' : 'bg-red-500/10'}`}>
                    {isOnline ? (
                      <IconActivity className={`text-neon-secondary`} />
                    ) : (
                      <IconX className="text-red-500" />
                    )}
                  </div>
                  <div>
                    <h3 className="font-medium">{agent.label}</h3>
                    <p className="text-sm text-gray-400">{agent.name}</p>
                  </div>
                </div>
                <Badge
                  color={isOnline ? 'teal' : 'red'}
                  variant="light"
                  radius="sm"
                >
                  {isOnline ? 'Online' : 'Offline'}
                </Badge>
              </div>
              {status?.lastActive && (
                <div className="mt-2 text-xs text-gray-400">
                  Last active: {new Date(status.lastActive).toLocaleTimeString()}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
