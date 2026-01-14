import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { ForecastOutput } from '../../types';

interface RegimeChartProps {
  forecast: ForecastOutput | null;
}

const RegimeChart: React.FC<RegimeChartProps> = ({ forecast }) => {
  if (!forecast) {
    return (
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 h-80 flex items-center justify-center">
        <p className="text-gray-400">Loading regime data...</p>
      </div>
    );
  }

  // Prepare data for the pie chart
  const regimeData = Object.entries(forecast.regime.probabilities).map(([name, value]) => ({
    name,
    value: parseFloat((value * 100).toFixed(1)),
    probability: value
  }));

  const regimeColors: Record<string, string> = {
    'Low Vol Bull': '#10B981', // green
    'High Vol Bull': '#3B82F6', // blue
    'Consolidation': '#F59E0B', // yellow
    'Bear': '#F97316', // orange
    'Crisis': '#EF4444', // red
    'Recovery': '#8B5CF6'  // purple
  };

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
      <h3 className="text-lg font-semibold mb-4 text-cyan-400">Regime Analysis</h3>
      <div className="h-80 flex flex-col items-center">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={regimeData}
              cx="50%"
              cy="50%"
              labelLine={false}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
              nameKey="name"
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            >
              {regimeData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={regimeColors[entry.name] || '#8884d8'} 
                />
              ))}
            </Pie>
            <Tooltip 
              formatter={(value) => [`${value}%`, 'Probability']}
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
          </PieChart>
        </ResponsiveContainer>
        
        {/* Current regime indicator */}
        <div className="mt-4 text-center">
          <div className="text-sm text-gray-400">Current Regime</div>
          <div 
            className="text-xl font-bold"
            style={{ color: regimeColors[forecast.regime.current] || '#8884d8' }}
          >
            {forecast.regime.current}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegimeChart;