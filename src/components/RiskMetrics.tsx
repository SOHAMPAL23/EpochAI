import React from 'react';
import { AlertTriangle, TrendingDown, Activity, Gauge } from 'lucide-react';
import { RiskMetrics } from '../types';

interface RiskMetricsProps {
  riskMetrics: RiskMetrics;
}

const RiskMetricsComponent: React.FC<RiskMetricsProps> = ({ riskMetrics }) => {
  const getRiskLevel = (value: number, threshold: number) => {
    if (value > threshold) return 'high';
    if (value > threshold * 0.7) return 'medium';
    return 'low';
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'high': return 'text-red-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  const getRiskBg = (level: string) => {
    switch (level) {
      case 'high': return 'bg-red-500/20';
      case 'medium': return 'bg-yellow-500/20';
      case 'low': return 'bg-green-500/20';
      default: return 'bg-gray-500/20';
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* VaR 95% */}
      <div className={`bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20 ${getRiskBg(getRiskLevel(Math.abs(riskMetrics.var95), 3))}`}>
        <div className="flex items-center justify-between mb-2">
          <h4 className="font-medium text-gray-300">VaR 95%</h4>
          <AlertTriangle className="w-5 h-5 text-red-400" />
        </div>
        <p className={`text-2xl font-bold font-mono ${getRiskColor(getRiskLevel(Math.abs(riskMetrics.var95), 3))}`}>
          {riskMetrics.var95.toFixed(2)}%
        </p>
        <p className="text-xs text-gray-500 mt-1">Value at Risk</p>
      </div>

      {/* CVaR 95% */}
      <div className={`bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20 ${getRiskBg(getRiskLevel(Math.abs(riskMetrics.cvar95), 5))}`}>
        <div className="flex items-center justify-between mb-2">
          <h4 className="font-medium text-gray-300">CVaR 95%</h4>
          <TrendingDown className="w-5 h-5 text-orange-400" />
        </div>
        <p className={`text-2xl font-bold font-mono ${getRiskColor(getRiskLevel(Math.abs(riskMetrics.cvar95), 5))}`}>
          {riskMetrics.cvar95.toFixed(2)}%
        </p>
        <p className="text-xs text-gray-500 mt-1">Conditional VaR</p>
      </div>

      {/* Max Drawdown */}
      <div className={`bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20 ${getRiskBg(getRiskLevel(Math.abs(riskMetrics.max_drawdown), 15))}`}>
        <div className="flex items-center justify-between mb-2">
          <h4 className="font-medium text-gray-300">Max DD</h4>
          <Activity className="w-5 h-5 text-purple-400" />
        </div>
        <p className={`text-2xl font-bold font-mono ${getRiskColor(getRiskLevel(Math.abs(riskMetrics.max_drawdown), 15))}`}>
          {riskMetrics.max_drawdown.toFixed(2)}%
        </p>
        <p className="text-xs text-gray-500 mt-1">Max Drawdown</p>
      </div>

      {/* Tail Risk */}
      <div className={`bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20 ${getRiskBg(getRiskLevel(riskMetrics.tail_risk_score, 0.5))}`}>
        <div className="flex items-center justify-between mb-2">
          <h4 className="font-medium text-gray-300">Tail Risk</h4>
          <Gauge className="w-5 h-5 text-cyan-400" />
        </div>
        <p className={`text-2xl font-bold font-mono ${getRiskColor(getRiskLevel(riskMetrics.tail_risk_score, 0.5))}`}>
          {(riskMetrics.tail_risk_score * 100).toFixed(1)}%
        </p>
        <p className="text-xs text-gray-500 mt-1">P(Loss > 3%)</p>
      </div>
    </div>
  );
};

export default RiskMetricsComponent;