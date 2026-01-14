import React from 'react';
import { Play, TrendingUp, TrendingDown, DollarSign, BarChart3, Zap, Brain, Eye } from 'lucide-react';

interface SidebarProps {
  selectedAsset: string;
  setSelectedAsset: (asset: string) => void;
  horizon: string;
  setHorizon: (horizon: string) => void;
  sentimentEnabled: boolean;
  setSentimentEnabled: (enabled: boolean) => void;
  regimeEnabled: boolean;
  setRegimeEnabled: (enabled: boolean) => void;
  explanationsEnabled: boolean;
  setExplanationsEnabled: (enabled: boolean) => void;
  onGenerateForecast: () => void;
  loading: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({
  selectedAsset,
  setSelectedAsset,
  horizon,
  setHorizon,
  sentimentEnabled,
  setSentimentEnabled,
  regimeEnabled,
  setRegimeEnabled,
  explanationsEnabled,
  setExplanationsEnabled,
  onGenerateForecast,
  loading
}) => {
  return (
    <div className="lg:w-80 bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 h-fit">
      <h2 className="text-xl font-bold mb-6 text-cyan-400">Controls</h2>
      
      {/* Asset Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">Asset</label>
        <select
          value={selectedAsset}
          onChange={(e) => setSelectedAsset(e.target.value)}
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
        >
          <option value="NIFTY50">NIFTY 50</option>
          <option value="SENSEX">SENSEX</option>
          <option value="BANKNIFTY">BANKNIFTY</option>
        </select>
      </div>
      
      {/* Horizon Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">Horizon</label>
        <div className="flex space-x-2">
          {['1D', '5D', '20D'].map((h) => (
            <button
              key={h}
              onClick={() => setHorizon(h)}
              className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                horizon === h
                  ? 'bg-cyan-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              {h}
            </button>
          ))}
        </div>
      </div>
      
      {/* Feature Toggles */}
      <div className="space-y-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Zap className="w-4 h-4 text-cyan-400 mr-2" />
            <span className="text-sm">Sentiment</span>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={sentimentEnabled}
              onChange={(e) => setSentimentEnabled(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-600"></div>
          </label>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Brain className="w-4 h-4 text-cyan-400 mr-2" />
            <span className="text-sm">Regime</span>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={regimeEnabled}
              onChange={(e) => setRegimeEnabled(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-600"></div>
          </label>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Eye className="w-4 h-4 text-cyan-400 mr-2" />
            <span className="text-sm">Explanations</span>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={explanationsEnabled}
              onChange={(e) => setExplanationsEnabled(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-600"></div>
          </label>
        </div>
      </div>
      
      {/* Generate Forecast Button */}
      <button
        onClick={onGenerateForecast}
        disabled={loading}
        className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold py-3 px-4 rounded-xl hover:from-cyan-600 hover:to-blue-700 transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-cyan-500/25 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
      >
        {loading ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            Processing...
          </>
        ) : (
          <>
            <Play className="w-4 h-4 mr-2" />
            Generate Forecast
          </>
        )}
      </button>
      
      {/* Model Information */}
      <div className="mt-8 space-y-3">
        <h3 className="font-medium text-cyan-400">AI Models</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-400">XGBoost</span>
            <span className="text-green-400">67% Acc</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">HMM Regime</span>
            <span className="text-green-400">85% Acc</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">LSTM Quantile</span>
            <span className="text-green-400">12% RMSE</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;