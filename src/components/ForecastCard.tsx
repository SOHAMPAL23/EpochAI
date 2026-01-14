import React from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle } from 'lucide-react';
import { ForecastOutput } from '../types';

interface ForecastCardProps {
  forecast: ForecastOutput;
}

const ForecastCard: React.FC<ForecastCardProps> = ({ forecast }) => {
  const isUp = forecast.direction === 'UP';
  const regimeColors: Record<string, string> = {
    'Low Vol Bull': 'bg-green-500/20 text-green-400',
    'High Vol Bull': 'bg-blue-500/20 text-blue-400',
    'Consolidation': 'bg-yellow-500/20 text-yellow-400',
    'Bear': 'bg-orange-500/20 text-orange-400',
    'Crisis': 'bg-red-500/20 text-red-400',
    'Recovery': 'bg-purple-500/20 text-purple-400'
  };

  const getRegimeColor = (regime: string) => {
    return regimeColors[regime] || 'bg-gray-500/20 text-gray-400';
  };

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Direction and Return */}
        <div className="flex items-center space-x-4">
          <div className={`p-3 rounded-full ${isUp ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
            {isUp ? (
              <TrendingUp className={`w-8 h-8 ${isUp ? 'text-green-400' : 'text-red-400'}`} />
            ) : (
              <TrendingDown className={`w-8 h-8 ${isUp ? 'text-green-400' : 'text-red-400'}`} />
            )}
          </div>
          
          <div>
            <h3 className="text-2xl font-bold">
              {isUp ? '▲ UP' : '▼ DOWN'}
            </h3>
            <p className={`text-3xl font-mono font-bold ${isUp ? 'text-green-400' : 'text-red-400'}`}>
              {forecast.expected_return >= 0 ? '+' : ''}{forecast.expected_return.toFixed(2)}%
            </p>
          </div>
        </div>
        
        {/* Confidence and Regime */}
        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-400">Confidence</span>
              <span className="font-medium">{(forecast.confidence * 100).toFixed(0)}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${forecast.confidence > 0.7 ? 'bg-green-500' : forecast.confidence > 0.5 ? 'bg-yellow-500' : 'bg-red-500'}`}
                style={{ width: `${forecast.confidence * 100}%` }}
              ></div>
            </div>
          </div>
          
          <div className="flex items-center">
            <span className="text-gray-400 mr-2">Regime:</span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRegimeColor(forecast.regime.current)}`}>
              {forecast.regime.current}
            </span>
          </div>
        </div>
      </div>
      
      {/* Quantiles */}
      <div className="mt-6 grid grid-cols-3 gap-4">
        <div className="text-center">
          <div className="text-gray-400 text-sm">P10</div>
          <div className="text-red-400 font-mono font-bold text-lg">
            {forecast.quantiles.p10 >= 0 ? '+' : ''}{forecast.quantiles.p10.toFixed(2)}%
          </div>
        </div>
        <div className="text-center">
          <div className="text-gray-400 text-sm">P50</div>
          <div className="text-cyan-400 font-mono font-bold text-lg">
            {forecast.quantiles.p50 >= 0 ? '+' : ''}{forecast.quantiles.p50.toFixed(2)}%
          </div>
        </div>
        <div className="text-center">
          <div className="text-gray-400 text-sm">P90</div>
          <div className="text-green-400 font-mono font-bold text-lg">
            {forecast.quantiles.p90 >= 0 ? '+' : ''}{forecast.quantiles.p90.toFixed(2)}%
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForecastCard;