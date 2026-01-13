import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ForecastOutput } from '../../types';

interface ReturnDistributionChartProps {
  forecast: ForecastOutput | null;
}

const ReturnDistributionChart: React.FC<ReturnDistributionChartProps> = ({ forecast }) => {
  if (!forecast) {
    return (
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 h-80 flex items-center justify-center">
        <p className="text-gray-400">Loading forecast data...</p>
      </div>
    );
  }

  // Generate data for the chart
  const chartData = Array.from({ length: 20 }, (_, i) => {
    const day = i + 1;
    return {
      day: `${day}D`,
      p10: forecast.quantiles.p10 + (i * 0.01), // Simulate slight drift
      p50: forecast.quantiles.p50 + (i * 0.02),
      p90: forecast.quantiles.p90 + (i * 0.03)
    };
  });

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
      <h3 className="text-lg font-semibold mb-4 text-cyan-400">Return Distribution</h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="day" 
              stroke="#9CA3AF"
              tick={{ fill: '#9CA3AF' }}
            />
            <YAxis 
              stroke="#9CA3AF"
              tick={{ fill: '#9CA3AF' }}
              tickFormatter={(value) => `${value.toFixed(2)}%`}
            />
            <Tooltip 
              formatter={(value) => [`${Number(value).toFixed(2)}%`, 'Return']}
              labelFormatter={(label) => `Day ${label.replace('D', '')}`}
              contentStyle={{ 
                backgroundColor: 'rgba(17, 24, 39, 0.8)', 
                borderColor: 'rgba(255, 255, 255, 0.2)',
                borderRadius: '0.5rem',
                backdropFilter: 'blur(10px)'
              }}
              itemStyle={{ color: 'white' }}
              labelStyle={{ color: '#93C5FD' }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="p10"
              stroke="#EF4444"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              name="P10 (Worst Case)"
            />
            <Line
              type="monotone"
              dataKey="p50"
              stroke="#0EA5E9"
              strokeWidth={3}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              name="P50 (Median)"
            />
            <Line
              type="monotone"
              dataKey="p90"
              stroke="#10B981"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              name="P90 (Best Case)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ReturnDistributionChart;