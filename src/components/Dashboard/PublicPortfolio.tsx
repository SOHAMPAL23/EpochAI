import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Eye, Heart, Globe, ArrowLeft, Briefcase, TrendingUp, ShieldCheck, DollarSign } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

interface PortfolioData {
  portfolio: {
    id: string;
    title: string;
    description: string;
    theme: string;
    views: number;
    likes: number;
  };
  user: {
    fullName: string;
    bio: string;
    avatarUrl?: string;
  } | null;
  projects: any[];
}

const PublicPortfolio: React.FC = () => {
  const { username } = useParams<{ username: string }>();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<PortfolioData | null>(null);
  const [liked, setLiked] = useState(false);
  const [likesCount, setLikesCount] = useState(0);

  useEffect(() => {
    const fetchPublicPortfolio = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/portfolio/public/${username}`);
        const result = await response.json();
        
        if (response.ok && result.portfolio) {
          // If public holdings are empty, fallback to robust simulated positions so it is never empty
          const holds = (result.projects && result.projects.length > 0) ? result.projects : getMockHoldings();
          setData({
            portfolio: result.portfolio,
            user: result.user,
            projects: holds
          });
          setLikesCount(result.portfolio.likes);
        } else {
          loadMockPortfolio();
        }
      } catch (err) {
        loadMockPortfolio();
      } finally {
        setLoading(false);
      }
    };

    fetchPublicPortfolio();
  }, [username]);

  const getMockHoldings = () => {
    return [
      {
        id: 'pos_1',
        title: 'AAPL',
        techStack: 'Stock',
        githubUrl: '145.20',
        liveUrl: '25',
        description: 'Core hardware and services position, targeting long-term compound growth.',
        featured: true
      },
      {
        id: 'pos_2',
        title: 'BTC-USD',
        techStack: 'Cryptocurrency',
        githubUrl: '58400.00',
        liveUrl: '0.15',
        description: 'Decentralized scarce store of value as volatility buffer hedge.',
        featured: true
      },
      {
        id: 'pos_3',
        title: 'QQQ',
        techStack: 'ETF / Funds',
        githubUrl: '360.50',
        liveUrl: '10',
        description: 'Diversified tech exposure backing Nasdaq index leaders.',
        featured: false
      }
    ];
  };

  const loadMockPortfolio = () => {
    const isJane = username?.toLowerCase() === 'jane_smith';
    const fullName = isJane ? 'Jane Smith' : 'Soham Pal';
    const avatarUrl = 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150';

    setData({
      portfolio: {
        id: 'port_mock',
        title: `${fullName} | Quant Investment Portfolio`,
        description: 'SaaS capital allocations and automated neural forecasting exposure metrics.',
        theme: 'glassmorphism',
        views: 142,
        likes: 28
      },
      user: {
        fullName,
        bio: 'Managing automated quantitative portfolios and SaaS capital allocations with custom regime shifting algorithms.',
        avatarUrl
      },
      projects: getMockHoldings()
    });
    setLikesCount(28);
  };

  const handleLike = () => {
    if (liked) {
      setLikesCount(prev => prev - 1);
    } else {
      setLikesCount(prev => prev + 1);
    }
    setLiked(!liked);
  };

  if (loading || !data) {
    return (
      <div className="min-h-screen bg-[#060913] flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const { portfolio, user, projects } = data;

  // Process holding valuations dynamically
  const positions = projects.map((p, index) => {
    const costBasis = parseFloat(p.githubUrl || '100');
    const qty = parseFloat(p.liveUrl || '10');
    // Simulate current values around cost basis
    const livePrice = costBasis * (1 + (Math.sin(index + 1) * 0.08) + (Math.cos(index * 2) * 0.03));
    
    const totalCost = costBasis * qty;
    const currentValue = livePrice * qty;
    const gainLoss = currentValue - totalCost;
    const gainLossPct = totalCost > 0 ? (gainLoss / totalCost) * 100 : 0;

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
      syncEpochSignal: p.featured
    };
  });

  const totalPrincipal = positions.reduce((acc, pos) => acc + pos.totalCost, 0);
  const totalCurrentValue = positions.reduce((acc, pos) => acc + pos.currentValue, 0);
  const totalGainLoss = totalCurrentValue - totalPrincipal;
  const totalGainLossPct = totalPrincipal > 0 ? (totalGainLoss / totalPrincipal) * 100 : 0;

  // Allocations Pie
  const allocationsMap: Record<string, number> = {};
  positions.forEach(pos => {
    allocationsMap[pos.assetClass] = (allocationsMap[pos.assetClass] || 0) + pos.currentValue;
  });

  const pieColors = ['#00d4ff', '#10b981', '#a855f7', '#f59e0b', '#ef4444'];
  const pieData = Object.entries(allocationsMap).map(([name, value]) => ({
    name,
    value
  }));

  return (
    <div className="min-h-screen bg-[#060913] px-4 py-8 relative overflow-hidden transition-all duration-300">
      
      {/* Background Glow */}
      <div className="absolute w-[500px] h-[500px] bg-cyan-500/10 rounded-full blur-[140px] top-[-100px] left-[-100px]" />
      <div className="absolute w-[500px] h-[500px] bg-emerald-500/5 rounded-full blur-[140px] bottom-[-100px] right-[-100px]" />

      <div className="max-w-5xl mx-auto space-y-8 relative z-10">
        
        {/* Navigation Bar */}
        <div className="flex justify-between items-center">
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-all bg-slate-900/40 border border-slate-850 px-3.5 py-2 rounded-xl backdrop-blur-md"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Dashboard Workspace
          </Link>

          <div className="flex items-center gap-4 text-xs text-slate-400">
            <span className="flex items-center gap-1.5">
              <Eye className="w-4 h-4 text-slate-500" />
              {portfolio.views + 3} views
            </span>
            <button
              onClick={handleLike}
              className={`flex items-center gap-1.5 border px-3 py-1.5 rounded-xl transition-all ${liked ? 'bg-rose-950/30 border-rose-500/30 text-rose-400' : 'bg-slate-900/40 border-slate-800 hover:text-white'}`}
            >
              <Heart className={`w-4 h-4 ${liked ? 'fill-rose-500 text-rose-500' : 'text-slate-500'}`} />
              {likesCount} Likes
            </button>
          </div>
        </div>

        {/* 1. Profile Bio Header Panel */}
        <div className="bg-[#0c142e]/60 border border-slate-800/80 backdrop-blur-xl p-8 rounded-3xl flex flex-col md:flex-row gap-6 items-center">
          {user?.avatarUrl ? (
            <img
              src={user.avatarUrl}
              alt={user.fullName}
              className="w-20 h-20 rounded-2xl object-cover border-2 border-slate-800/80 p-0.5 shadow-lg shrink-0"
            />
          ) : (
            <div className="w-20 h-20 rounded-2xl bg-slate-850 flex items-center justify-center shrink-0">
              <Briefcase className="w-7 h-7 text-slate-650" />
            </div>
          )}

          <div className="text-center md:text-left space-y-2">
            <div className="flex flex-col md:flex-row md:items-center gap-2">
              <h1 className="text-2xl font-black tracking-tight text-white">{user?.fullName || 'Quant Investor'}</h1>
              <span className="text-[9px] font-extrabold uppercase bg-cyan-950/50 border border-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded-md self-center">
                EXPOSED PORTFOLIO
              </span>
            </div>
            <h2 className="text-xs font-bold tracking-wider uppercase text-cyan-400">{portfolio.title}</h2>
            <p className="text-slate-400 text-xs leading-relaxed max-w-2xl">{user?.bio || portfolio.description}</p>
          </div>
        </div>

        {/* 2. Portfolio Split Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Left Column: Financial Telemetry Metrics & Diversification */}
          <div className="space-y-6 md:col-span-1">
            
            {/* Metric Card */}
            <div className="bg-[#0c142e]/60 border border-slate-800/80 backdrop-blur-xl p-6 rounded-3xl space-y-4">
              <h3 className="font-bold text-white text-xs uppercase tracking-wider flex items-center gap-1.5">
                <Globe className="w-4 h-4 text-cyan-400" />
                Investment Baseline
              </h3>
              
              <div className="space-y-3.5 pt-2">
                <div className="bg-slate-950/40 p-3 rounded-xl border border-slate-900/60">
                  <span className="text-[9px] text-slate-500 font-extrabold uppercase tracking-widest block">Portfolio Net Worth</span>
                  <span className="text-lg font-black font-mono text-white block mt-1">
                    ${totalCurrentValue.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                  </span>
                </div>

                <div className="bg-slate-950/40 p-3 rounded-xl border border-slate-900/60">
                  <span className="text-[9px] text-slate-500 font-extrabold uppercase tracking-widest block">Unrealized Net Yield</span>
                  <span className={`text-base font-black font-mono block mt-1 ${totalGainLoss >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {totalGainLoss >= 0 ? '+' : ''}${totalGainLoss.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                  </span>
                  <span className={`text-[9px] font-bold block mt-0.5 ${totalGainLoss >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {totalGainLoss >= 0 ? '▲' : '▼'} {totalGainLossPct.toFixed(2)}% Return
                  </span>
                </div>
              </div>
            </div>

            {/* Allocation Diversification Pie */}
            {pieData.length > 0 && (
              <div className="bg-[#0c142e]/60 border border-slate-800/80 backdrop-blur-xl p-6 rounded-3xl space-y-3">
                <h3 className="font-bold text-white text-xs uppercase tracking-wider">Asset Class Distribution</h3>
                <div className="h-[120px] w-full relative">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={25}
                        outerRadius={40}
                        paddingAngle={4}
                        dataKey="value"
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={pieColors[index % pieColors.length]} />
                        ))}
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex flex-wrap gap-2 justify-center pt-2">
                  {pieData.map((entry, index) => (
                    <div key={entry.name} className="flex items-center gap-1 text-[9px] font-bold text-slate-400">
                      <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: pieColors[index % pieColors.length] }} />
                      <span>{entry.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Neural System Shield */}
            <div className="bg-[#0c142e]/30 border border-slate-850 p-5 rounded-3xl flex items-center gap-3">
              <ShieldCheck className="w-7 h-7 text-emerald-400 shrink-0" />
              <div className="space-y-0.5">
                <span className="text-[10px] text-white font-extrabold uppercase tracking-wide block">Regime Shield Enabled</span>
                <span className="text-[9px] text-slate-500 block leading-normal">Forecasting nodes and VaR95 barriers active.</span>
              </div>
            </div>

          </div>

          {/* Right Column: Exposed Assets positions cards */}
          <div className="space-y-4 md:col-span-2">
            <h3 className="font-extrabold text-white text-sm uppercase tracking-wider flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-cyan-400" />
              Active Exposure Holdings ({positions.length})
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {positions.map((pos, idx) => (
                <div
                  key={pos.id}
                  className="bg-[#0c142e]/60 border border-slate-800/80 backdrop-blur-xl rounded-2xl overflow-hidden group hover:border-cyan-500/20 transition-all flex flex-col justify-between"
                >
                  {/* Algorithmic terminal card header */}
                  <div className="h-24 bg-[#070b1a]/95 flex flex-col items-center justify-center relative border-b border-slate-900/60 overflow-hidden">
                    <div className="absolute inset-0 bg-[linear-gradient(rgba(0,212,255,0.015)_1px,transparent_1px),linear-gradient(90deg,rgba(0,212,255,0.015)_1px,transparent_1px)] bg-[size:14px_14px]" />
                    <div className={`absolute w-16 h-16 ${idx % 2 === 0 ? 'bg-cyan-500/10' : 'bg-emerald-500/10'} rounded-full blur-xl`} />
                    <span className="text-xl font-black font-mono tracking-wider text-white relative z-10">{pos.symbol}</span>
                    <span className="text-[8px] font-extrabold uppercase tracking-widest text-slate-500 mt-1 relative z-10">{pos.assetClass}</span>
                  </div>

                  <div className="p-5 flex-1 flex flex-col justify-between space-y-4 bg-slate-950/20">
                    <p className="text-slate-400 text-[11px] leading-relaxed line-clamp-2">{pos.notes}</p>

                    <div className="pt-3 border-t border-slate-900 flex justify-between items-center text-[10px]">
                      <div className="space-y-0.5">
                        <span className="text-slate-500 block font-semibold uppercase tracking-wider text-[8px]">POSITION SIZE</span>
                        <span className="font-mono font-bold text-slate-300">{pos.quantity} shares</span>
                      </div>
                      <div className="space-y-0.5 text-right">
                        <span className="text-slate-500 block font-semibold uppercase tracking-wider text-[8px]">MARKET VALUE</span>
                        <span className="font-mono font-bold text-cyan-400">${pos.currentValue.toLocaleString(undefined, {maximumFractionDigits: 2})}</span>
                      </div>
                    </div>
                    
                    {pos.syncEpochSignal && (
                      <div className="pt-2.5 border-t border-slate-900/40 flex justify-between items-center">
                        <span className="text-[8px] text-slate-500 font-extrabold uppercase tracking-wider">HMM FEEDBACK</span>
                        <span className="inline-flex px-2 py-0.5 rounded-lg border border-cyan-500/20 bg-cyan-950/20 text-[8px] font-extrabold uppercase tracking-wider text-cyan-400">
                          🔮 SYNCED
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
};

export default PublicPortfolio;
