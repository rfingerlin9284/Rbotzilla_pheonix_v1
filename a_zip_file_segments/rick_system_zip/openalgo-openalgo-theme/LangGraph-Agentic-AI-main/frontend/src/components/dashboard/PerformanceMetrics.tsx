import { useQuery } from '@tanstack/react-query';
import { fetchTradeHistory } from '../../services/api';
import { DonutChart } from './DonutChart';
import { IconCurrencyDollar, IconTrendingUp, IconTrendingDown } from '@tabler/icons-react';

export function PerformanceMetrics() {
  const { data: trades, isLoading } = useQuery({
    queryKey: ['trade-history'],
    queryFn: () => fetchTradeHistory(7),
  });

  if (isLoading) {
    return (
      <div className="bg-dark-700 rounded-xl p-6 h-full">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-dark-600 rounded w-3/4"></div>
          <div className="h-4 bg-dark-600 rounded w-full"></div>
          <div className="h-4 bg-dark-600 rounded w-5/6"></div>
          <div className="h-32 bg-dark-600 rounded mt-4"></div>
        </div>
      </div>
    );
  }

  const winningTrades = trades?.filter((t: any) => t.pnl && t.pnl > 0) || [];
  const losingTrades = trades?.filter((t: any) => t.pnl && t.pnl <= 0) || [];
  const winRate = trades?.length
    ? Math.round((winningTrades.length / trades.length) * 100)
    : 0;
  const totalPnl = trades?.reduce((sum: number, t: any) => sum + (t.pnl || 0), 0) || 0;

  const chartData = {
    labels: ['Winning', 'Losing'],
    datasets: [
      {
        data: [winningTrades.length, losingTrades.length],
        backgroundColor: ['#00ff9d', '#ff2d75'],
        borderColor: ['#00ff9d', '#ff2d75'],
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className="bg-dark-700 rounded-xl p-6 h-full">
      <h2 className="text-xl font-bold text-neon-primary mb-4">Performance (7d)</h2>
      <div className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-dark-800 p-4 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-full bg-green-500/10">
                <IconTrendingUp className="text-green-500" />
              </div>
              <div>
                <p className="text-sm text-gray-400">Win Rate</p>
                <p className="text-2xl font-bold">{winRate}%</p>
              </div>
            </div>
          </div>
          <div className="bg-dark-800 p-4 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-full bg-neon-primary/10">
                <IconCurrencyDollar className="text-neon-primary" />
              </div>
              <div>
                <p className="text-sm text-gray-400">Total PnL</p>
                <p
                  className={`text-2xl font-bold ${
                    totalPnl >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}
                >
                  {totalPnl >= 0 ? '+' : ''}
                  {totalPnl.toFixed(2)}
                </p>
              </div>
            </div>
          </div>
        </div>
        <div className="h-48">
          <DonutChart data={chartData} />
        </div>
      </div>
    </div>
  );
}
