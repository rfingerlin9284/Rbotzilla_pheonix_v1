import { useDashboardStore } from '../../store/useDashboardStore';
import { Badge } from '@mantine/core';
import { IconTrendingUp, IconTrendingDown, IconCurrencyDollar } from '@tabler/icons-react';

export function ActiveTrades() {
  const activeTrades = useDashboardStore((state) => state.activeTrades);

  return (
    <div className="bg-dark-700 rounded-xl p-6">
      <h2 className="text-xl font-bold text-neon-primary mb-4">Active Trades</h2>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left text-gray-400 border-b border-dark-600">
              <th className="pb-3 pl-2">Symbol</th>
              <th className="pb-3">Direction</th>
              <th className="pb-3">Entry</th>
              <th className="pb-3">Current</th>
              <th className="pb-3">Size</th>
              <th className="pb-3">PNL</th>
              <th className="pb-3">Agents</th>
              <th className="pb-3 pr-2">Opened</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-dark-600">
            {activeTrades.length === 0 ? (
              <tr>
                <td colSpan={8} className="py-8 text-center text-gray-400">
                  No active trades
                </td>
              </tr>
            ) : (
              activeTrades.map((trade) => (
                <tr key={trade.id} className="hover:bg-dark-750 transition-colors">
                  <td className="py-3 pl-2 font-medium">{trade.symbol}</td>
                  <td className="py-3">
                    {trade.direction === 'LONG' ? (
                      <Badge
                        leftSection={<IconTrendingUp size={14} />}
                        color="green"
                        variant="light"
                      >
                        LONG
                      </Badge>
                    ) : (
                      <Badge
                        leftSection={<IconTrendingDown size={14} />}
                        color="red"
                        variant="light"
                      >
                        SHORT
                      </Badge>
                    )}
                  </td>
                  <td className="py-3">{trade.entryPrice.toFixed(2)}</td>
                  <td className="py-3">
                    {trade.exitPrice ? trade.exitPrice.toFixed(2) : '—'}
                  </td>
                  <td className="py-3">{trade.size.toFixed(2)}</td>
                  <td className="py-3">
                    {trade.pnl !== undefined ? (
                      <span
                        className={`font-medium ${
                          trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                        }`}
                      >
                        {trade.pnl >= 0 ? '+' : ''}
                        {trade.pnl.toFixed(2)}
                      </span>
                    ) : (
                      '—'
                    )}
                  </td>
                  <td className="py-3">
                    <div className="flex flex-wrap gap-1">
                      {trade.agentsInvolved.slice(0, 3).map((agent) => (
                        <Badge
                          key={agent}
                          variant="dot"
                          color="gray"
                          size="sm"
                          radius="sm"
                        >
                          {agent}
                        </Badge>
                      ))}
                      {trade.agentsInvolved.length > 3 && (
                        <Badge variant="light" color="gray" size="sm" radius="sm">
                          +{trade.agentsInvolved.length - 3}
                        </Badge>
                      )}
                    </div>
                  </td>
                  <td className="py-3 pr-2 text-sm text-gray-400">
                    {new Date(trade.openedAt).toLocaleTimeString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
