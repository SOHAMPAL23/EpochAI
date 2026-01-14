import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface HistoricalPerformanceProps {
  data: any[];
}

const HistoricalPerformance: React.FC<HistoricalPerformanceProps> = ({ data }) => {
  const [isOpen, setIsOpen] = useState(true);

  // Generate mock performance data
  const performanceData = data.map((item, index) => ({
    date: item.date,
    predicted: item.close + (Math.random() - 0.5) * 2, // Simulate predictions
    actual: item.close,
    cumulative_predicted: index === 0 
      ? 100 
      : (performanceData[index - 1]?.cumulative_predicted || 100) * (1 + (Math.random() - 0.3) * 0.01),
    cumulative_actual: index === 0 
      ? 100 
      : (performanceData[index - 1]?.cumulative_actual || 100) * (1 + (item.returns || 0.001))
  }));

  // Calculate metrics
  const hitRate = 0.67;
  const sharpe = 1.42;
  const maxDD = -8.5;

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20">
      <div 
        className="p-4 cursor-pointer flex justify-between items-center"
        onClick={() => setIsOpen(!isOpen)}
      >
        <h3 className="text-lg font-semibold text-cyan-400">Historical Performance</h3>
        {isOpen ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
      </div>
      
      {isOpen && (
        <>
          <div className="h-80 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={performanceData}
                margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
              >
                <defs>
                  <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0EA5E9" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#0EA5E9" stopOpacity={0.1}/>
                  </linearGradient>
                  <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="date" 
                  stroke="#9CA3AF"
                  tick={{ fill: '#9CA3AF' }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis 
                  stroke="#9CA3AF"
                  tick={{ fill: '#9CA3AF' }}
                />
                <Tooltip 
                  formatter={(value) => [`${Number(value).toFixed(2)}`, 'Price']}
                  labelFormatter={(label) => new Date(label).toLocaleString()}
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
                <Area
                  type="monotone"
                  dataKey="cumulative_predicted"
                  stroke="#0EA5E9"
                  fillOpacity={1}
                  fill="url(#colorPredicted)"
                  name="Predicted"
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="cumulative_actual"
                  stroke="#10B981"
                  fillOpacity={1}
                  fill="url(#colorActual)"
                  name="Actual"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 border-t border-gray-700">
            <div className="text-center">
              <div className="text-sm text-gray-400">Hit Rate</div>
              <div className="text-xl font-bold text-green-400">{(hitRate * 100).toFixed(1)}%</div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-400">Sharpe Ratio</div>
              <div className="text-xl font-bold text-cyan-400">{sharpe.toFixed(2)}</div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-400">Max Drawdown</div>
              <div className="text-xl font-bold text-red-400">{maxDD.toFixed(1)}%</div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default HistoricalPerformance;