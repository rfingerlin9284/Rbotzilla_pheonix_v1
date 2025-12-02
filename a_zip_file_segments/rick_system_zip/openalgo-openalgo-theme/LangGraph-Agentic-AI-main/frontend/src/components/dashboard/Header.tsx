import { useDashboardStore } from '../store/useDashboardStore';
import { IconRefresh, IconCircleCheck, IconAlertCircle } from '@tabler/icons-react';
import { NeonButton } from './NeonButton';

export function Header() {
  const agentStatus = useDashboardStore((state) => state.agentStatus);
  const onlineAgents = Object.values(agentStatus).filter(
    (status) => status?.status === 'online'
  ).length;
  const totalAgents = Object.keys(agentStatus).length;

  return (
    <header className="bg-dark-900 border-b border-dark-700 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            {onlineAgents === totalAgents ? (
              <IconCircleCheck className="text-green-500" />
            ) : (
              <IconAlertCircle className="text-yellow-500" />
            )}
            <span className="text-sm font-medium">
              Agents: {onlineAgents}/{totalAgents} online
            </span>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <NeonButton size="sm" variant="secondary">
            <IconRefresh size={18} />
            <span className="hidden md:inline ml-2">Refresh</span>
          </NeonButton>
        </div>
      </div>
    </header>
  );
}
