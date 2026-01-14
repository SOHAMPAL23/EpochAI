import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { ForecastOutput } from '../types';

interface ExplainabilityTabsProps {
  forecast: ForecastOutput;
}

const ExplainabilityTabs: React.FC<ExplainabilityTabsProps> = ({ forecast }) => {
  const [activeTab, setActiveTab] = useState<'feature' | 'attention' | 'counterfactual'>('feature');

  // Mock SHAP values for feature importance
  const shapValues = [
    { feature: 'momentum_20d', value: 0.45, importance: Math.abs(0.45) },
    { feature: 'vix_change', value: -0.28, importance: Math.abs(-0.28) },
    { feature: 'sentiment', value: 0.22, importance: Math.abs(0.22) },
    { feature: 'volatility', value: -0.18, importance: Math.abs(-0.18) },
    { feature: 'rsi', value: 0.15, importance: Math.abs(0.15) },
    { feature: 'macd', value: 0.12, importance: Math.abs(0.12) },
    { feature: 'bb_position', value: -0.10, importance: Math.abs(-0.10) },
    { feature: 'atr', value: 0.08, importance: Math.abs(0.08) },
    { feature: 'volume_ratio', value: -0.07, importance: Math.abs(-0.07) },
    { feature: 'fii_flow', value: 0.05, importance: Math.abs(0.05) },
  ].sort((a, b) => b.importance - a.importance);

  // Mock attention weights for heatmap
  const attentionMatrix = Array.from({ length: 30 }, (_, dayIndex) => 
    Array.from({ length: 8 }, (_, featureIndex) => ({
      day: dayIndex,
      feature: `F${featureIndex + 1}`,
      weight: Math.random() * 0.5 + 0.1, // Random weight between 0.1 and 0.6
    }))
  ).flat();

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
      <div className="border-b border-gray-700 mb-4">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab('feature')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'feature'
                ? 'border-cyan-500 text-cyan-400'
                : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
            }`}
          >
            Feature Importance
          </button>
          <button
            onClick={() => setActiveTab('attention')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'attention'
                ? 'border-cyan-500 text-cyan-400'
                : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
            }`}
          >
            Attention Heatmap
          </button>
          <button
            onClick={() => setActiveTab('counterfactual')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'counterfactual'
                ? 'border-cyan-500 text-cyan-400'
                : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
            }`}
          >
            Counterfactual Analysis
          </button>
        </nav>
      </div>

      <div className="h-96">
        {activeTab === 'feature' && (
          <div className="h-full">
            <h3 className="text-lg font-semibold mb-4 text-cyan-400">Top 10 Feature Contributions (SHAP)</h3>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={shapValues}
                layout="horizontal"
                margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis type="number" stroke="#9CA3AF" />
                <YAxis 
                  type="category" 
                  dataKey="feature" 
                  stroke="#9CA3AF"
                  tick={{ fill: '#9CA3AF' }}
                  width={90}
                />
                <Tooltip 
                  formatter={(value) => [`${Number(value).toFixed(3)}`, 'SHAP Value']}
                  contentStyle={{ 
                    backgroundColor: 'rgba(17, 24, 39, 0.8)', 
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderRadius: '0.5rem',
                    backdropFilter: 'blur(10px)'
                  }}
                  itemStyle={{ color: 'white' }}
                  labelStyle={{ color: '#93C5FD' }}
                />
                <Bar dataKey="value" name="SHAP Value">
                  {shapValues.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.value >= 0 ? '#10B981' : '#EF4444'} 
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {activeTab === 'attention' && (
          <div className="h-full">
            <h3 className="text-lg font-semibold mb-4 text-cyan-400">Attention Weights Heatmap (30×8)</h3>
            <div className="h-80 overflow-auto">
              <table className="w-full">
                <thead>
                  <tr>
                    <th className="p-1 text-left text-xs text-gray-400">Day</th>
                    {Array.from({ length: 8 }, (_, i) => (
                      <th key={i} className="p-1 text-center text-xs text-gray-400">F{i + 1}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Array.from({ length: 30 }, (_, dayIndex) => (
                    <tr key={dayIndex}>
                      <td className="p-1 text-xs text-gray-400 text-center">{dayIndex + 1}</td>
                      {Array.from({ length: 8 }, (_, featureIndex) => {
                        const weight = Math.random() * 0.5 + 0.1;
                        const intensity = Math.floor(weight * 255);
                        const color = weight > 0.3 ? `rgb(239, 68, 68, ${weight})` : 
                                     weight > 0.2 ? `rgb(245, 158, 11, ${weight})` : 
                                     `rgb(16, 185, 129, ${weight})`;
                        
                        return (
                          <td key={featureIndex} className="p-1">
                            <div 
                              className="h-4 rounded"
                              style={{ backgroundColor: color }}
                              title={`Weight: ${weight.toFixed(3)}`}
                            />
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'counterfactual' && (
          <div className="h-full">
            <h3 className="text-lg font-semibold mb-4 text-cyan-400">Counterfactual Analysis</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 h-full">
              <div className="bg-gray-800/50 rounded-lg p-4">
                <label className="block text-sm font-medium mb-2 text-gray-300">VIX Level</label>
                <input 
                  type="range" 
                  min="-20" 
                  max="20" 
                  defaultValue="0" 
                  className="w-full accent-cyan-500"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>-20%</span>
                  <span>Current</span>
                  <span>+20%</span>
                </div>
              </div>
              
              <div className="bg-gray-800/50 rounded-lg p-4">
                <label className="block text-sm font-medium mb-2 text-gray-300">Sentiment</label>
                <input 
                  type="range" 
                  min="-1" 
                  max="1" 
                  step="0.1"
                  defaultValue="0" 
                  className="w-full accent-cyan-500"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>Negative</span>
                  <span>Neutral</span>
                  <span>Positive</span>
                </div>
              </div>
              
              <div className="bg-gray-800/50 rounded-lg p-4">
                <label className="block text-sm font-medium mb-2 text-gray-300">Momentum</label>
                <input 
                  type="range" 
                  min="-15" 
                  max="15" 
                  defaultValue="0" 
                  className="w-full accent-cyan-500"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>-15%</span>
                  <span>Current</span>
                  <span>+15%</span>
                </div>
              </div>
            </div>
            
            <div className="mt-4 p-4 bg-gray-800/50 rounded-lg">
              <h4 className="font-medium mb-2 text-cyan-400">Scenario Comparison</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <div className="text-sm text-gray-400">Current Forecast</div>
                  <div className="text-2xl font-bold text-white">
                    {forecast.expected_return >= 0 ? '+' : ''}{forecast.expected_return.toFixed(2)}%
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-gray-400">Adjusted Forecast</div>
                  <div className="text-2xl font-bold text-cyan-400">+0.42%</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ExplainabilityTabs;