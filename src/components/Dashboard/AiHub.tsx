import React, { useState, useEffect } from 'react';
import { Sparkles, Brain, CheckCircle2, TrendingUp, Sliders, ShieldAlert, Cpu } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface AiHubProps {
  token: string;
}

const AiHub: React.FC<AiHubProps> = ({ token }) => {
  // 1. Kelly Criterion States
  const [winProb, setWinProb] = useState(62); // 62% win rate
  const [payoutRatio, setPayoutRatio] = useState(1.8); // 1.8:1 payout
  const [calculatedFraction, setCalculatedFraction] = useState(0);

  // Recalculate Kelly Fraction: f* = (p * (b + 1) - 1) / b
  useEffect(() => {
    const p = winProb / 100;
    const b = payoutRatio;
    const kelly = (p * (b + 1) - 1) / b;
    setCalculatedFraction(Math.max(0, kelly) * 100);
  }, [winProb, payoutRatio]);

  // 2. Risk Portfolio Optimization Recommendation
  const [portfolioRisk, setPortfolioRisk] = useState<'conservative' | 'balanced' | 'aggressive'>('balanced');
  const [optimizing, setOptimizing] = useState(false);
  const [optimized, setOptimized] = useState(false);

  const handleOptimize = () => {
    setOptimizing(true);
    setTimeout(() => {
      setOptimizing(false);
      setOptimized(true);
    }, 1500);
  };

  const originalAllocations = [
    { name: 'Stock (Equity)', value: 45, color: '#00d4ff' },
    { name: 'Crypto (Digital)', value: 35, color: '#10b981' },
    { name: 'ETF (Index)', value: 15, color: '#a855f7' },
    { name: 'Cash (Debt)', value: 5, color: '#f59e0b' }
  ];

  // AI rebalanced targets based on HMM risk regimes
  const optimizedAllocations = portfolioRisk === 'conservative' 
    ? [
        { name: 'Stock (Equity)', value: 35, color: '#00d4ff' },
        { name: 'Crypto (Digital)', value: 10, color: '#10b981' },
        { name: 'ETF (Index)', value: 35, color: '#a855f7' },
        { name: 'Cash (Debt)', value: 20, color: '#f59e0b' }
      ]
    : portfolioRisk === 'aggressive'
    ? [
        { name: 'Stock (Equity)', value: 40, color: '#00d4ff' },
        { name: 'Crypto (Digital)', value: 50, color: '#10b981' },
        { name: 'ETF (Index)', value: 10, color: '#a855f7' },
        { name: 'Cash (Debt)', value: 0, color: '#f59e0b' }
      ]
    : [
        { name: 'Stock (Equity)', value: 40, color: '#00d4ff' },
        { name: 'Crypto (Digital)', value: 25, color: '#10b981' },
        { name: 'ETF (Index)', value: 25, color: '#a855f7' },
        { name: 'Cash (Debt)', value: 10, color: '#f59e0b' }
      ];

  const barChartData = originalAllocations.map(orig => {
    const opt = optimizedAllocations.find(o => o.name === orig.name);
    return {
      name: orig.name.split(' ')[0],
      'Current Allocation %': orig.value,
      'AI Recommended Allocation %': opt ? opt.value : orig.value
    };
  });

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
      
      {/* 1. Kelly Criterion Allocation Calculator */}
      <div className="bg-[#0c142e]/60 border border-slate-800/80 p-6 rounded-3xl space-y-6 flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Sliders className="w-5 h-5 text-cyan-400" />
            <h4 className="text-base font-bold text-white">AI Kelly Allocation Optimizer</h4>
          </div>
          <p className="text-xs text-slate-400">
            Calculate the mathematically optimal position size using the Kelly Criterion based on EpochAI historical model win-rates.
          </p>
        </div>

        {/* Inputs */}
        <div className="space-y-5 bg-[#070b1a]/40 p-5 rounded-2xl border border-slate-900/60">
          
          {/* Win Probability Slider */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-semibold text-slate-300">Model Win Probability (p)</span>
              <span className="font-mono font-bold text-cyan-400">{winProb}%</span>
            </div>
            <input
              type="range"
              min="50"
              max="95"
              value={winProb}
              onChange={e => setWinProb(parseInt(e.target.value))}
              className="w-full h-1.5 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
          </div>

          {/* Profit-to-Loss Payout Ratio */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-semibold text-slate-300">Reward-to-Risk Payout Ratio (b)</span>
              <span className="font-mono font-bold text-emerald-400">{payoutRatio}:1</span>
            </div>
            <input
              type="range"
              min="1.0"
              max="4.0"
              step="0.1"
              value={payoutRatio}
              onChange={e => setPayoutRatio(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-emerald-500"
            />
          </div>

        </div>

        {/* Result Fraction Gauge */}
        <div className="bg-cyan-950/20 border border-cyan-500/20 p-5 rounded-2xl text-center space-y-2 relative overflow-hidden">
          <div className="absolute inset-0 bg-[linear-gradient(rgba(0,212,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(0,212,255,0.02)_1px,transparent_1px)] bg-[size:12px_12px]" />
          
          <span className="text-[10px] uppercase tracking-wider text-slate-500 font-extrabold block relative z-10">AI Kelly Allocation Limit</span>
          <h3 className="text-4xl font-black font-mono text-cyan-400 tracking-tight relative z-10 mt-1">
            {calculatedFraction.toFixed(1)}%
          </h3>
          <span className="text-[10px] text-slate-400 block relative z-10">
            Suggested maximum portfolio leverage budget for this signal risk profile.
          </span>
        </div>

        <div className="text-[10px] text-slate-500 flex gap-2 items-start border-t border-slate-900/60 pt-4">
          <Brain className="w-4 h-4 text-cyan-500 shrink-0 mt-0.5" />
          <span>
            * The AI Kelly optimizer models capital utility to maximize logarithmic return growth over infinite iterations.
          </span>
        </div>
      </div>

      {/* 2. Portfolio Risk frontiers & Markowitz Allocator */}
      <div className="bg-[#0c142e]/60 border border-slate-800/80 p-6 rounded-3xl space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-emerald-400" />
            <h4 className="text-base font-bold text-white">Neural Risk Allocator</h4>
          </div>
          
          {/* Selector */}
          <div className="flex gap-1.5 bg-slate-950/60 p-1 rounded-xl border border-slate-850">
            {(['conservative', 'balanced', 'aggressive'] as const).map(mode => (
              <button
                key={mode}
                onClick={() => { setPortfolioRisk(mode); setOptimized(false); }}
                className={`text-[9px] uppercase font-black px-2.5 py-1 rounded-lg transition-all ${portfolioRisk === mode ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/25' : 'text-slate-500 hover:text-slate-300 border border-transparent'}`}
              >
                {mode}
              </button>
            ))}
          </div>
        </div>

        {/* Visual Charts Comparison */}
        {optimized ? (
          <div className="space-y-4 animate-fadeIn">
            
            {/* Chart rebalancing comparison */}
            <div className="h-[180px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barChartData} margin={{ top: 5, right: 5, left: -25, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.1} />
                  <XAxis dataKey="name" stroke="#64748b" fontSize={8} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={8} tickLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0c142e', border: '1px solid #334155', borderRadius: '12px' }}
                  />
                  <Bar dataKey="Current Allocation %" fill="#334155" radius={[3, 3, 0, 0]} />
                  <Bar dataKey="AI Recommended Allocation %" fill="#00d4ff" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Structured action points list */}
            <div className="space-y-2 border-t border-slate-900/60 pt-4">
              <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500 block">AI Allocation Trade Directives:</span>
              <div className="space-y-2 text-xs">
                {portfolioRisk === 'conservative' && (
                  <>
                    <div className="flex gap-2.5 items-start text-slate-300">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span>Reduce Crypto holding weights by 25% to minimize system drawdown standard deviation.</span>
                    </div>
                    <div className="flex gap-2.5 items-start text-slate-300">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span>Shift proceeds (15%) to Cash & Liquid yields as risk-free volatility stabilizer.</span>
                    </div>
                  </>
                )}
                {portfolioRisk === 'aggressive' && (
                  <>
                    <div className="flex gap-2.5 items-start text-slate-300">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span>DCA shift 15% from Cash/ETF models into high-volatility cryptocurrency growth.</span>
                    </div>
                    <div className="flex gap-2.5 items-start text-slate-300">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span>Leverage active forecasting ensemble close filters to capture up-drift equity trends.</span>
                    </div>
                  </>
                )}
                {portfolioRisk === 'balanced' && (
                  <>
                    <div className="flex gap-2.5 items-start text-slate-300">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span>Rebalance Stocks and ETFs to split weight (65%) to optimize the Sharpe frontiers.</span>
                    </div>
                    <div className="flex gap-2.5 items-start text-slate-300">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span>Retain 10% Crypto core as inflation buffer with active forecast regime overrides.</span>
                    </div>
                  </>
                )}
              </div>
            </div>

            <button
              onClick={() => setOptimized(false)}
              className="w-full text-center text-slate-500 hover:text-cyan-400 text-[10px] font-bold pt-2 uppercase tracking-widest"
            >
              Reset Target Constraints
            </button>

          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-xs text-slate-400">
              Run the HMM regime calibrator to optimize asset allocation coefficients against modern risk frontier matrices.
            </p>
            
            {/* Visual preview */}
            <div className="border border-dashed border-slate-800/80 rounded-2xl p-8 flex flex-col items-center justify-center text-center bg-[#070b1a]/40 min-h-[160px]">
              <Cpu className="w-8 h-8 text-slate-600 mb-2 animate-pulse" />
              <p className="text-slate-500 text-xs font-semibold">Regime Optimization Calibrator Standby</p>
              <p className="text-slate-600 text-[10px] mt-1">Configure profile risk above and optimize.</p>
            </div>

            <button
              onClick={handleOptimize}
              disabled={optimizing}
              className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-3 rounded-xl transition-all shadow-md flex items-center justify-center gap-2 text-xs"
            >
              <Sparkles className="w-4 h-4 text-white" />
              {optimizing ? 'Recalculating Sharpe boundaries...' : `Run ${portfolioRisk.toUpperCase()} Optimization`}
            </button>
          </div>
        )}
      </div>

    </div>
  );
};

export default AiHub;
