import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchMarketOverview, tradingSocket } from '../services/api';
import { AgentStatusGrid } from '../components/dashboard/AgentStatusGrid';
import { MarketOverview } from '../components/dashboard/MarketOverview';
import { RecentSignals } from '../components/dashboard/RecentSignals';
import { ActiveTrades } from '../components/dashboard/ActiveTrades';
import { PerformanceMetrics } from '../components/dashboard/PerformanceMetrics';
import { useDashboardStore } from '../store/useDashboardStore';

export function DashboardPage() {
  const { data: marketData, isLoading } = useQuery({
    queryKey: ['market-overview'],
    queryFn: fetchMarketOverview,
    refetchInterval: 30000,
  });

  const addMarketEvent = useDashboardStore((state) => state.addMarketEvent);
  const addAgentSignal = useDashboardStore((state) => state.addAgentSignal);
  const updateTrade = useDashboardStore((state) => state.updateTrade);
  const setAgentStatus = useDashboardStore((state) => state.setAgentStatus);

  useEffect(() => {
    const unsubscribeMarket = tradingSocket.onMarketEvent((event) => {
      console.log('Market update:', event);
      addMarketEvent(event);
    });

    const unsubscribeSignals = tradingSocket.onAgentSignal((signal) => {
      console.log(`${signal.agent} signal:`, signal);
      addAgentSignal(signal);
    });

    const unsubscribeTrades = tradingSocket.onTradeUpdate((trade) => {
      console.log('Trade update:', trade);
      updateTrade(trade);
    });

    const unsubscribeAgentStatus = tradingSocket.onAgentStatus((status) => {
      console.log('Agent status update:', status);
      setAgentStatus(status);
    });

    tradingSocket.onConnectionFailed(() => {
      console.error('Connection to trading system lost');
      // Optionally update a global connection status in store
    });

    return () => {
      unsubscribeMarket();
      unsubscribeSignals();
      unsubscribeTrades();
      unsubscribeAgentStatus();
      // Do not close the socket here if it's meant to be persistent across the app
      // tradingSocket.close(); 
    };
  }, [addMarketEvent, addAgentSignal, updateTrade, setAgentStatus]);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <MarketOverview data={marketData} loading={isLoading} />
        </div>
        <div>
          <PerformanceMetrics />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <AgentStatusGrid />
        </div>
        <div className="lg:col-span-2">
          <RecentSignals />
        </div>
      </div>

      <div>
        <ActiveTrades />
      </div>
    </div>
  );
}