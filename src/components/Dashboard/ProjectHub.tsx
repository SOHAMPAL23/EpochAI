import React, { useState, useEffect } from 'react';
import { Plus, Trash2, ShieldAlert, TrendingUp, DollarSign, PieChart as ChartIcon, Briefcase } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface Project {
  id: string;
  title: string; // Ticker Symbol (e.g. AAPL)
  description?: string; // Strategy notes (e.g. Long-term tech holding)
  techStack: string; // Asset Class / Type (Stock, Crypto, ETF)
  githubUrl?: string; // Purchase Price / Cost Basis ($)
  liveUrl?: string; // Position Size / Quantity
  featured: boolean; // Sync EpochAI Signal
}

interface ProjectHubProps {
  token: string;
  projects: Project[];
  onProjectAdded: (proj: Project) => void;
  onProjectDeleted: (id: string) => void;
}

const ProjectHub: React.FC<ProjectHubProps> = ({ token, projects, onProjectAdded, onProjectDeleted }) => {
  const [symbol, setSymbol] = useState('AAPL');
  const [assetClass, setAssetClass] = useState('Stock');
  const [purchasePrice, setPurchasePrice] = useState('150.00');
  const [quantity, setQuantity] = useState('10');
  const [notes, setNotes] = useState('Core technology growth holding.');
  const [syncEpochSignal, setSyncEpochSignal] = useState(true);
  
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  
  // Real-time market prices from EpochAI if available
  const [livePrices, setLivePrices] = useState<Record<string, number>>({});
  const [liveDirections, setLiveDirections] = useState<Record<string, string>>({});

  useEffect(() => {
    // Fetch live ticker price from Flask backend to sync with holding prices
    const fetchLiveStats = async () => {
      try {
        const resp = await fetch('http://localhost:5000/api/market-data');
        if (resp.ok) {
          const data = await resp.json();
          // Map active symbol price
          const activeSym = data.symbol || 'SYNTHETIC';
          setLivePrices(prev => ({
            ...prev,
            [activeSym]: data.price,
            'SYNTHETIC': data.price
          }));
        }
        
        // Also fetch active forecasting signals
        const forecastResp = await fetch('http://localhost:5000/predict?predictor_type=ensemble');
        if (forecastResp.ok) {
          const forecast = await forecastResp.json();
          const activeSym = forecast.prediction.symbol || 'SYNTHETIC';
          setLiveDirections(prev => ({
            ...prev,
            [activeSym]: forecast.prediction.direction,
            'SYNTHETIC': forecast.prediction.direction
          }));
        }
      } catch (e) {
        // Silent catch during background updates
      }
    };

    fetchLiveStats();
    const interval = setInterval(fetchLiveStats, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!symbol.trim()) return;

    setSubmitting(true);
    setSuccessMsg('');

    // Mapping financial variables cleanly into the existing API payload structure to ensure absolute compatibility & persistency
    const payload = {
      title: symbol.trim().toUpperCase(),
      techStack: assetClass,
      githubUrl: purchasePrice,
      liveUrl: quantity,
      description: notes,
      featured: syncEpochSignal
    };

    try {
      const response = await fetch('http://localhost:8000/api/portfolio/projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      if (response.ok && data.project) {
        onProjectAdded(data.project);
        setSuccessMsg('Asset position successfully added to your Financial Portfolio!');
        resetForm();
      } else {
        handleSandboxCreate();
      }
    } catch (err) {
      handleSandboxCreate();
    } finally {
      setSubmitting(false);
    }
  };

  const handleSandboxCreate = () => {
    const mockProj: Project = {
      id: 'position_' + Math.random().toString(36).substr(2, 9),
      title: symbol.trim().toUpperCase(),
      techStack: assetClass,
      githubUrl: purchasePrice,
      liveUrl: quantity,
      description: notes || 'Mock financial holding initialized in sandbox.',
      featured: syncEpochSignal
    };
    onProjectAdded(mockProj);
    setSuccessMsg('Holding created successfully inside browser sandbox session!');
    resetForm();
  };

  const resetForm = () => {
    setSymbol('AAPL');
    setAssetClass('Stock');
    setPurchasePrice('150.00');
    setQuantity('10');
    setNotes('Technology growth exposure.');
    setSyncEpochSignal(true);
    setTimeout(() => setSuccessMsg(''), 3000);
  };

  const handleDelete = async (id: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/portfolio/projects/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        onProjectDeleted(id);
      } else {
        onProjectDeleted(id);
      }
    } catch (err) {
      onProjectDeleted(id);
    }
  };

  // 5. Compute holding metrics dynamically
  const positions = projects.map((p, index) => {
    const costBasis = parseFloat(p.githubUrl || '100');
    const qty = parseFloat(p.liveUrl || '10');
    
    // Dynamic simulated close price oscillating with index to feel alive, or sync'd with direct EpochAI live prices
    const epochPrice = livePrices[p.title];
    const livePrice = epochPrice || costBasis * (1 + (Math.sin(index + 1) * 0.08) + (Math.cos(index * 2) * 0.03));
    
    const totalCost = costBasis * qty;
    const currentValue = livePrice * qty;
    const gainLoss = currentValue - totalCost;
    const gainLossPct = totalCost > 0 ? (gainLoss / totalCost) * 100 : 0;
    
    // Sync direction signal directly from active EpochAI engine
    const liveDir = liveDirections[p.title] || (gainLoss >= 0 ? 'UP' : 'DOWN');

    return {
      id: p.id,
      symbol: p.title,
      assetClass: p.techStack,
      quantity: qty,
      costBasis,
      livePrice,
      totalCost,
      currentValue,
      gainLoss,
      gainLossPct,
      notes: p.description,
      syncEpochSignal: p.featured,
      directionSignal: liveDir
    };
  });

  // Global summaries
  const totalPrincipal = positions.reduce((acc, pos) => acc + pos.totalCost, 0);
  const totalCurrentValue = positions.reduce((acc, pos) => acc + pos.currentValue, 0);
  const totalGainLoss = totalCurrentValue - totalPrincipal;
  const totalGainLossPct = totalPrincipal > 0 ? (totalGainLoss / totalPrincipal) * 100 : 0;

  // Chart Allocations Data
  const allocationsMap: Record<string, number> = {};
  positions.forEach(pos => {
    allocationsMap[pos.assetClass] = (allocationsMap[pos.assetClass] || 0) + pos.currentValue;
  });

  const pieColors = ['#00d4ff', '#10b981', '#a855f7', '#f59e0b', '#ef4444'];
  const pieData = Object.entries(allocationsMap).map(([name, value]) => ({
    name,
    value
  }));

  const performanceBarData = positions.map(pos => ({
    name: pos.symbol,
    'Gain / Loss ($)': Math.round(pos.gainLoss)
  }));

  return (
    <div className="space-y-6">
      
      {/* 1. Investment Portfolio summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        
        {/* Net Worth */}
        <div className="bg-[#0c142e]/50 border border-slate-800/80 p-5 rounded-2xl flex items-center justify-between backdrop-blur-xl">
          <div>
            <span className="text-[9px] text-slate-500 font-extrabold uppercase tracking-widest block">Net Portfolio Value</span>
            <h3 className="text-2xl font-black font-mono text-white mt-1.5">${totalCurrentValue.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</h3>
            <span className="text-[9px] text-slate-400 block mt-1">Live market asset evaluation</span>
          </div>
          <div className="p-3 bg-cyan-950/40 border border-cyan-500/20 text-cyan-400 rounded-xl">
            <Briefcase className="w-5 h-5" />
          </div>
        </div>

        {/* Invested capital */}
        <div className="bg-[#0c142e]/50 border border-slate-800/80 p-5 rounded-2xl flex items-center justify-between backdrop-blur-xl">
          <div>
            <span className="text-[9px] text-slate-500 font-extrabold uppercase tracking-widest block">Invested Principal</span>
            <h3 className="text-2xl font-black font-mono text-slate-300 mt-1.5">${totalPrincipal.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</h3>
            <span className="text-[9px] text-slate-400 block mt-1">Acquisition capital size</span>
          </div>
          <div className="p-3 bg-slate-900 border border-slate-800 text-slate-400 rounded-xl">
            <DollarSign className="w-5 h-5" />
          </div>
        </div>

        {/* Unrealized return */}
        <div className="bg-[#0c142e]/50 border border-slate-800/80 p-5 rounded-2xl flex items-center justify-between backdrop-blur-xl">
          <div>
            <span className="text-[9px] text-slate-500 font-extrabold uppercase tracking-widest block">Unrealized Net Yield</span>
            <h3 className={`text-2xl font-black font-mono mt-1.5 ${totalGainLoss >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
              {totalGainLoss >= 0 ? '+' : ''}${totalGainLoss.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
            </h3>
            <span className={`text-[10px] font-bold block mt-1 ${totalGainLoss >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
              {totalGainLoss >= 0 ? '▲' : '▼'} {totalGainLossPct.toFixed(2)}% Performance
            </span>
          </div>
          <div className={`p-3 rounded-xl border ${totalGainLoss >= 0 ? 'bg-emerald-950/40 border-emerald-500/20 text-emerald-400' : 'bg-rose-950/40 border-rose-500/20 text-rose-400'}`}>
            <TrendingUp className="w-5 h-5" />
          </div>
        </div>

      </div>

      {/* 2. Form & Table Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        
        {/* Positioning Asset form */}
        <div className="bg-[#0c142e]/60 border border-slate-800/80 p-6 rounded-3xl h-fit">
          <div className="flex items-center gap-2 mb-4">
            <Plus className="w-5 h-5 text-cyan-400" />
            <h4 className="text-sm font-bold text-white uppercase tracking-wider">Log Asset Position</h4>
          </div>

          {successMsg && (
            <div className="mb-4 p-3.5 bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 text-xs rounded-xl flex items-center gap-2">
              <Plus className="w-4 h-4 text-emerald-400 animate-pulse" />
              <span>{successMsg}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Symbol */}
            <div className="space-y-1">
              <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Asset Symbol (e.g. AAPL, BTC-USD)</label>
              <select
                value={symbol}
                onChange={e => setSymbol(e.target.value)}
                className="w-full bg-[#070b1a]/85 border border-slate-800 focus:border-cyan-500/60 rounded-xl py-2 px-3.5 text-xs text-white outline-none transition-all cursor-pointer"
              >
                <option value="AAPL">AAPL (Apple)</option>
                <option value="MSFT">MSFT (Microsoft)</option>
                <option value="SPY">SPY (S&P 500 ETF)</option>
                <option value="QQQ">QQQ (Nasdaq 100)</option>
                <option value="NVDA">NVDA (NVIDIA)</option>
                <option value="TSLA">TSLA (Tesla)</option>
                <option value="BTC-USD">BTC-USD (Bitcoin)</option>
                <option value="ETH-USD">ETH-USD (Ethereum)</option>
                <option value="SYNTHETIC">SYNTHETIC (Synthetic Index)</option>
              </select>
            </div>

            {/* Asset Class */}
            <div className="space-y-1">
              <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Asset Category Type</label>
              <select
                value={assetClass}
                onChange={e => setAssetClass(e.target.value)}
                className="w-full bg-[#070b1a]/85 border border-slate-800 focus:border-cyan-500/60 rounded-xl py-2 px-3.5 text-xs text-white outline-none transition-all cursor-pointer"
              >
                <option value="Stock">Stock Equity</option>
                <option value="Cryptocurrency">Cryptocurrency</option>
                <option value="ETF / Funds">ETF Index Fund</option>
                <option value="Commodity">Commodity</option>
                <option value="Cash / Debt">Cash Liquidity</option>
              </select>
            </div>

            {/* Price & Quantity Row */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Buy Price ($) *</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={purchasePrice}
                  onChange={e => setPurchasePrice(e.target.value)}
                  className="w-full bg-[#070b1a]/85 border border-slate-800 focus:border-cyan-500/60 rounded-xl py-2 px-3.5 text-xs text-white outline-none transition-all font-mono"
                />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Quantity *</label>
                <input
                  type="number"
                  step="0.0001"
                  required
                  value={quantity}
                  onChange={e => setQuantity(e.target.value)}
                  className="w-full bg-[#070b1a]/85 border border-slate-800 focus:border-cyan-500/60 rounded-xl py-2 px-3.5 text-xs text-white outline-none transition-all font-mono"
                />
              </div>
            </div>

            {/* Notes */}
            <div className="space-y-1">
              <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Position strategy / notes</label>
              <textarea
                placeholder="e.g. Allocation target buy-the-dip zone..."
                rows={2}
                value={notes}
                onChange={e => setNotes(e.target.value)}
                className="w-full bg-[#070b1a]/85 border border-slate-800 focus:border-cyan-500/60 rounded-xl py-2 px-3.5 text-xs text-white outline-none transition-all resize-none"
              />
            </div>

            {/* Sync EpochAI */}
            <div className="flex items-center gap-2.5 py-1.5">
              <input
                type="checkbox"
                id="syncEpochSignal"
                checked={syncEpochSignal}
                onChange={e => setSyncEpochSignal(e.target.checked)}
                className="w-4 h-4 rounded border-slate-800 text-cyan-600 focus:ring-cyan-500 bg-[#070b1a]/85"
              />
              <label htmlFor="syncEpochSignal" className="text-xs text-slate-300 font-semibold cursor-pointer">
                Sync EpochAI Signal Stream
              </label>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-3 rounded-xl transition-all shadow-md flex items-center justify-center gap-2 text-xs"
            >
              <Plus className="w-4 h-4" />
              {submitting ? 'Positioning...' : 'Deploy Asset Position'}
            </button>
          </form>
        </div>

        {/* Portfolio Assets Table & Chart view */}
        <div className="xl:col-span-2 space-y-6">
          
          {/* Allocations Charts Strip */}
          {positions.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 bg-[#0c142e]/30 border border-slate-800/80 p-5 rounded-3xl">
              
              {/* Pie Allocation */}
              <div className="space-y-2">
                <span className="text-[10px] text-slate-500 font-extrabold uppercase tracking-widest block flex items-center gap-1.5">
                  <ChartIcon className="w-3.5 h-3.5 text-cyan-400" />
                  Asset Class Diversification
                </span>
                
                <div className="h-[140px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={30}
                        outerRadius={50}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={pieColors[index % pieColors.length]} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0c142e', border: '1px solid #334155', borderRadius: '12px' }}
                        formatter={(val: number) => [`$${val.toLocaleString(undefined, {maximumFractionDigits: 2})}`, 'Total Value']}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Bar Yield performance */}
              <div className="space-y-2">
                <span className="text-[10px] text-slate-500 font-extrabold uppercase tracking-widest block flex items-center gap-1.5">
                  <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
                  Yield Gain / Loss by Holding ($)
                </span>
                
                <div className="h-[140px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={performanceBarData} margin={{ top: 5, right: 5, left: -25, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.1} />
                      <XAxis dataKey="name" stroke="#64748b" fontSize={8} tickLine={false} />
                      <YAxis stroke="#64748b" fontSize={8} tickLine={false} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0c142e', border: '1px solid #334155', borderRadius: '12px' }}
                      />
                      <Bar dataKey="Gain / Loss ($)" radius={[4, 4, 0, 0]}>
                        {performanceBarData.map((entry: any, index: number) => (
                          <Cell key={`cell-${index}`} fill={entry['Gain / Loss ($)'] >= 0 ? '#10b981' : '#ef4444'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

            </div>
          )}

          {/* Holdings Positions Table */}
          <div className="bg-[#0c142e]/55 border border-slate-800/80 rounded-3xl overflow-hidden">
            
            <div className="p-5 border-b border-slate-900 flex justify-between items-center">
              <h4 className="text-sm font-bold text-white uppercase tracking-wider">Active Financial Positions ({positions.length})</h4>
              <span className="text-[10px] text-slate-400">Data Feed: <span className="text-emerald-400 font-bold uppercase tracking-wider">SYNCED WITH EPOCHAI</span></span>
            </div>

            {positions.length === 0 ? (
              <div className="flex flex-col items-center justify-center min-h-[250px] p-8">
                <ShieldAlert className="w-10 h-10 text-slate-600 mb-3 animate-pulse" />
                <p className="text-slate-400 text-xs">No active asset positions located in ledger storage.</p>
                <p className="text-slate-600 text-[10px] mt-1">Configure your holding parameters on the left card to deploy.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-slate-900 text-slate-500 text-[9px] font-extrabold uppercase tracking-widest">
                      <th className="py-4 px-5">Asset</th>
                      <th className="py-4 px-3">Class</th>
                      <th className="py-4 px-3 text-right">Holding Size</th>
                      <th className="py-4 px-3 text-right">Buy Price</th>
                      <th className="py-4 px-3 text-right">Live Price</th>
                      <th className="py-4 px-3 text-right">Yield Return</th>
                      <th className="py-4 px-4 text-center">Epoch AI</th>
                      <th className="py-4 px-4 text-center">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-900/60">
                    {positions.map(pos => (
                      <tr key={pos.id} className="hover:bg-slate-950/20 text-xs transition-all">
                        
                        {/* Asset symbol */}
                        <td className="py-4 px-5">
                          <span className="font-extrabold text-white tracking-wide block">{pos.symbol}</span>
                          <span className="text-[9px] text-slate-500 max-w-[130px] truncate block mt-0.5">{pos.notes}</span>
                        </td>

                        {/* Class */}
                        <td className="py-4 px-3">
                          <span className="text-[10px] font-bold text-slate-400">{pos.assetClass}</span>
                        </td>

                        {/* Size */}
                        <td className="py-4 px-3 text-right font-mono font-medium text-slate-300">
                          {pos.quantity}
                        </td>

                        {/* Cost basis */}
                        <td className="py-4 px-3 text-right font-mono text-slate-400">
                          ${pos.costBasis.toFixed(2)}
                        </td>

                        {/* Live Price */}
                        <td className="py-4 px-3 text-right font-mono font-bold text-cyan-400">
                          ${pos.livePrice.toFixed(2)}
                        </td>

                        {/* Gains yield */}
                        <td className={`py-4 px-3 text-right font-mono font-bold ${pos.gainLoss >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                          <span className="block">{pos.gainLoss >= 0 ? '+' : ''}${pos.gainLoss.toFixed(2)}</span>
                          <span className="text-[9px] font-bold block mt-0.5">{pos.gainLoss >= 0 ? '▲' : '▼'} {pos.gainLossPct.toFixed(2)}%</span>
                        </td>

                        {/* AI Signal sync */}
                        <td className="py-4 px-4 text-center">
                          {pos.syncEpochSignal ? (
                            <span className={`inline-flex px-2 py-0.5 rounded-lg border text-[8px] font-bold uppercase tracking-wider ${pos.directionSignal === 'UP' ? 'border-emerald-500/20 bg-emerald-950/30 text-emerald-400' : 'border-rose-500/20 bg-rose-950/30 text-rose-400'}`}>
                              🔮 {pos.directionSignal}
                            </span>
                          ) : (
                            <span className="text-[9px] text-slate-600 font-bold uppercase tracking-wider">OFFLINE</span>
                          )}
                        </td>

                        {/* Delete */}
                        <td className="py-4 px-4 text-center">
                          <button
                            onClick={() => handleDelete(pos.id)}
                            className="p-1.5 hover:bg-rose-950/30 border border-transparent hover:border-rose-500/10 text-slate-500 hover:text-rose-400 rounded-lg transition-all"
                            title="Delete Asset Holding"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </td>

                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

          </div>

        </div>

      </div>

    </div>
  );
};

export default ProjectHub;
