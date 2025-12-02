import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Skeleton } from '@mantine/core';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface MarketOverviewProps {
  data: any;
  loading: boolean;
}

export function MarketOverview({ data, loading }: MarketOverviewProps) {
  if (loading) {
    return (
      <div className="bg-dark-700 rounded-xl p-6 h-80">
        <Skeleton height="100%" />
      </div>
    );
  }

  const chartData = {
    labels: data?.timestamps || [],
    datasets: [
      {
        label: 'XAU/USD',
        data: data?.prices?.gold || [],
        borderColor: '#f5d300',
        backgroundColor: 'rgba(245, 211, 0, 0.1)',
        tension: 0.4,
        fill: true,
        pointRadius: 0,
      },
      {
        label: 'XAG/USD',
        data: data?.prices?.silver || [],
        borderColor: '#08f7fe',
        backgroundColor: 'rgba(8, 247, 254, 0.1)',
        tension: 0.4,
        fill: true,
        pointRadius: 0,
      },
      {
        label: 'DXY',
        data: data?.prices?.dxy || [],
        borderColor: '#fe53bb',
        backgroundColor: 'rgba(254, 83, 187, 0.1)',
        tension: 0.4,
        fill: true,
        pointRadius: 0,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#e2e8f0',
          font: {
            family: 'Rajdhani',
            size: 14,
            weight: '600',
          },
        },
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        backgroundColor: '#1e293b',
        titleColor: '#e2e8f0',
        bodyColor: '#e2e8f0',
        borderColor: '#334155',
        borderWidth: 1,
        padding: 12,
        usePointStyle: true,
      },
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.05)',
        },
        ticks: {
          color: '#94a3b8',
          font: {
            family: 'Rajdhani',
          },
        },
      },
      y: {
        grid: {
          color: 'rgba(255, 255, 255, 0.05)',
        },
        ticks: {
          color: '#94a3b8',
          font: {
            family: 'Rajdhani',
          },
        },
      },
    },
    interaction: {
      mode: 'nearest' as const,
      },
  };

  return (
    <div className="bg-dark-700 rounded-xl p-6 h-80 animated-border">
      <h2 className="text-xl font-bold text-neon-primary mb-4">Market Overview</h2>
      <div className="h-64">
        <Line data={chartData} options={options} />
      </div>
    </div>
  );
}
