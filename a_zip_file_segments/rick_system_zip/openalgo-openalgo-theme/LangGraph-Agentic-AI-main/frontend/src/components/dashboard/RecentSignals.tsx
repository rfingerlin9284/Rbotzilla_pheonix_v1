import { useDashboardStore } from '../../store/useDashboardStore';
import { Badge } from '@mantine/core';
import { IconArrowUp, IconArrowDown, IconHandStop } from '@tabler/icons-react';

export function RecentSignals() {
  const signals = useDashboardStore((state) => state.agentSignals);

  return (
    <div className="bg-dark-700 rounded-xl p-6">
      <h2 className="text-xl font-bold text-neon-primary mb-4">Recent Signals</h2>
      <div className="space-y-3">
        {signals.length === 0 ? (
          <div className="text-center py-8 text-gray-400">No signals received yet</div>
        ) : (
          signals.map((signal, index) => (
            <div
              key={`${signal.timestamp}-${index}`}
              className="p-4 rounded-lg border border-dark-600 bg-dark-800 hover:bg-dark-750 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center space-x-3">
                    {signal.signal === 'BUY' ? (
                      <div className="p-2 rounded-full bg-green-500/10">
                        <IconArrowUp className="text-green-500" />
                      </div>
                    ) : signal.signal === 'SELL' ? (
                      <div className="p-2 rounded-full bg-red-500/10">
                        <IconArrowDown className="text-red-500" />
                      </div>
                    ) : (
                      <div className="p-2 rounded-full bg-yellow-500/10">
                        <IconHandStop className="text-yellow-500" />
                      </div>
                    )}
                    <div>
                      <h3 className="font-medium">
                        {signal.signal} - {signal.agent.toUpperCase()}
                      </h3>
                      <p className="text-sm text-gray-400">
                        Confidence: {(signal.confidence * 100).toFixed(1)}%
                      </p>
                    </div>
                  </div>
                  <p className="mt-2 text-sm">{signal.reasoning}</p>
                </div>
                <div className="text-xs text-gray-400">
                  {new Date(signal.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
