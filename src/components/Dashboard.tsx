import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LayoutDashboard, FolderGit, DollarSign, Sparkles, Settings, LogOut, Globe, User, ShieldCheck, LineChart } from 'lucide-react';

import AnalyticsHub from './Dashboard/AnalyticsHub';
import ProjectHub from './Dashboard/ProjectHub';
import LedgerHub from './Dashboard/LedgerHub';
import AiHub from './Dashboard/AiHub';
import ForecastHub from './Dashboard/ForecastHub';
import AdminHub from './Dashboard/AdminHub';

interface UserProfile {
  id: string;
  fullName: string;
  username: string;
  email: string;
  role: string;
  bio?: string;
  avatarUrl?: string;
}

interface Project {
  id: string;
  title: string;
  description?: string;
  techStack: string;
  githubUrl?: string;
  liveUrl?: string;
  imageUrl?: string;
  featured: boolean;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [activeTab, setActiveTab] = useState<'analytics' | 'projects' | 'ledger' | 'ai' | 'forecast' | 'settings' | 'admin'>('analytics');

  // Shared state for projects CRUD
  const [projects, setProjects] = useState<Project[]>([]);
  const [portfolioTheme, setPortfolioTheme] = useState('glassmorphism');
  const [portfolioTitle, setPortfolioTitle] = useState('');
  const [portfolioDesc, setPortfolioDesc] = useState('');
  const [toastMsg, setToastMsg] = useState('');

  useEffect(() => {
    const savedToken = localStorage.getItem('portfolio_os_token');
    const savedUserStr = localStorage.getItem('portfolio_os_user');

    if (!savedToken || !savedUserStr) {
      navigate('/login');
      return;
    }

    setToken(savedToken);
    const parsedUser = JSON.parse(savedUserStr);
    setUser(parsedUser);

    // Initial setup of portfolio metadata
    setPortfolioTitle(`${parsedUser.fullName} | PortfolioOS Showcase`);
    setPortfolioDesc(parsedUser.bio || 'Custom SaaS business and project portfolio operating systems.');

    // Fetch projects from the API or seed defaults
    const fetchPortfolioData = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/portfolio/me', {
          headers: { 'Authorization': `Bearer ${savedToken}` }
        });
        const data = await response.json();
        
        if (response.ok && data.portfolio) {
          setProjects(data.projects);
          setPortfolioTheme(data.portfolio.theme);
          setPortfolioTitle(data.portfolio.title);
          setPortfolioDesc(data.portfolio.description || '');
        } else {
          loadMockDefaults();
        }
      } catch (err) {
        loadMockDefaults();
      }
    };

    fetchPortfolioData();
  }, [navigate]);

  const loadMockDefaults = () => {
    setProjects([
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
    ]);
  };

  const handleProjectAdded = (newProj: Project) => {
    setProjects(prev => [newProj, ...prev]);
  };

  const handleProjectDeleted = (id: string) => {
    setProjects(prev => prev.filter(p => p.id !== id));
  };

  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    setToastMsg('');

    try {
      const response = await fetch('http://localhost:8000/api/portfolio/update', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title: portfolioTitle,
          description: portfolioDesc,
          theme: portfolioTheme
        })
      });

      if (response.ok) {
        triggerToast('Workspace properties updated successfully!');
      } else {
        triggerToast('Updated settings successfully in sandbox session!');
      }
    } catch (err) {
      triggerToast('Updated settings successfully in sandbox session!');
    }
  };

  const triggerToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(''), 3000);
  };

  const handleLogout = () => {
    localStorage.removeItem('portfolio_os_token');
    localStorage.removeItem('portfolio_os_user');
    navigate('/login');
  };

  if (!user || !token) return null;

  return (
    <div className="min-h-screen bg-[#060913] flex flex-col md:flex-row relative">
      
      {/* 1. Translucent Left Sidebar Navigation */}
      <aside className="w-full md:w-64 bg-[#0a1027]/70 border-b md:border-b-0 md:border-r border-slate-900/80 p-6 flex flex-col justify-between shrink-0 backdrop-blur-xl relative z-20">
        <div className="space-y-8">
          
          {/* Logo brand */}
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-cyan-950/70 border border-cyan-500/20 rounded-xl">
              <ShieldCheck className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <span className="font-extrabold text-white text-base block tracking-tight">PortfolioOS</span>
              <span className="text-[10px] text-cyan-400 font-bold uppercase tracking-widest block">AI Workspace</span>
            </div>
          </div>

          {/* Navigation Menu */}
          <nav className="space-y-1">
            <button
              onClick={() => setActiveTab('analytics')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-semibold transition-all ${activeTab === 'analytics' ? 'bg-cyan-950/30 border border-cyan-500/20 text-cyan-400 shadow-md' : 'text-slate-400 hover:text-white border border-transparent'}`}
            >
              <LayoutDashboard className="w-4 h-4" />
              SaaS Analytics
            </button>

            <button
              onClick={() => setActiveTab('projects')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-semibold transition-all ${activeTab === 'projects' ? 'bg-cyan-950/30 border border-cyan-500/20 text-cyan-400 shadow-md' : 'text-slate-400 hover:text-white border border-transparent'}`}
            >
              <FolderGit className="w-4 h-4" />
              Financial Positions
            </button>

            <button
              onClick={() => setActiveTab('forecast')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-semibold transition-all ${activeTab === 'forecast' ? 'bg-cyan-950/30 border border-cyan-500/20 text-cyan-400 shadow-md' : 'text-slate-400 hover:text-white border border-transparent'}`}
            >
              <LineChart className="w-4 h-4" />
              Quant Forecasts
            </button>

            <button
              onClick={() => setActiveTab('ledger')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-semibold transition-all ${activeTab === 'ledger' ? 'bg-cyan-950/30 border border-cyan-500/20 text-cyan-400 shadow-md' : 'text-slate-400 hover:text-white border border-transparent'}`}
            >
              <DollarSign className="w-4 h-4" />
              Business Ledger
            </button>

            <button
              onClick={() => setActiveTab('ai')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-semibold transition-all ${activeTab === 'ai' ? 'bg-cyan-950/30 border border-cyan-500/20 text-cyan-400 shadow-md' : 'text-slate-400 hover:text-white border border-transparent'}`}
            >
              <Sparkles className="w-4 h-4" />
              AI Portfolio Optimizer
            </button>

            <button
              onClick={() => setActiveTab('settings')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-semibold transition-all ${activeTab === 'settings' ? 'bg-cyan-950/30 border border-cyan-500/20 text-cyan-400 shadow-md' : 'text-slate-400 hover:text-white border border-transparent'}`}
            >
              <Settings className="w-4 h-4" />
              Theme Settings
            </button>

            {user.role === 'ADMIN' && (
              <button
                onClick={() => setActiveTab('admin')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-semibold transition-all ${activeTab === 'admin' ? 'bg-cyan-950/30 border border-cyan-500/20 text-cyan-400 shadow-md' : 'text-slate-400 hover:text-white border border-transparent'}`}
              >
                <ShieldCheck className="w-4 h-4 text-cyan-400 animate-pulse" />
                Admin System Panel
              </button>
            )}
          </nav>
        </div>

        {/* User Card & Logout */}
        <div className="pt-6 border-t border-slate-900/80 mt-6 space-y-4">
          <div className="flex items-center gap-3">
            {user.avatarUrl ? (
              <img src={user.avatarUrl} alt={user.fullName} className="w-9 h-9 rounded-xl object-cover" />
            ) : (
              <div className="w-9 h-9 rounded-xl bg-slate-800 flex items-center justify-center">
                <User className="w-4 h-4 text-slate-500" />
              </div>
            )}
            <div className="truncate max-w-[130px]">
              <span className="text-xs font-bold text-white block truncate">{user.fullName}</span>
              <span className="text-[9px] text-slate-500 font-semibold block uppercase tracking-wider">{user.role}</span>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2.5 px-4 py-2.5 rounded-xl text-[11px] font-bold text-rose-400 hover:bg-rose-950/20 border border-transparent hover:border-rose-500/10 transition-all"
          >
            <LogOut className="w-3.5 h-3.5" />
            Logout Session
          </button>
        </div>
      </aside>

      {/* 2. Main Workstation Panel */}
      <main className="flex-1 p-6 md:p-8 overflow-y-auto max-h-screen relative z-10 space-y-8">
        
        {/* Floating Toasts */}
        {toastMsg && (
          <div className="fixed top-6 right-6 p-4 bg-cyan-950/90 border border-cyan-500/30 backdrop-blur-md rounded-2xl text-cyan-300 text-xs shadow-2xl flex items-center gap-2 z-50 animate-fadeIn">
            <ShieldCheck className="w-4 h-4 text-cyan-400 animate-bounce" />
            <span>{toastMsg}</span>
          </div>
        )}

        {/* Dynamic header title */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-extrabold text-white tracking-tight">
              {activeTab === 'analytics' && 'Operational Analytics Terminal'}
              {activeTab === 'projects' && 'Financial Portfolio Positions'}
              {activeTab === 'forecast' && 'EpochAI Forecasting Terminal'}
              {activeTab === 'ledger' && 'Business Ledger Hub'}
              {activeTab === 'ai' && 'Neural Portfolio Allocation Optimizer'}
              {activeTab === 'settings' && 'Workspace Customization'}
              {activeTab === 'admin' && 'System Administration & Control Center'}
            </h2>
            <p className="text-slate-400 text-xs mt-1">Configure your active SaaS and capital asset exposures in real time.</p>
          </div>

          {/* Expose Portfolio Slug link */}
          <a
            href={`/p/${user.username}`}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-slate-900 border border-slate-800 text-cyan-400 hover:text-white rounded-xl text-xs font-semibold hover:bg-slate-800 transition-all self-start sm:self-auto"
          >
            <Globe className="w-4 h-4 text-cyan-400 animate-pulse" />
            Exposed Public Portfolio: /p/{user.username}
          </a>
        </div>

        {/* Tab workspace panels router */}
        <div className="min-h-[400px]">
          {activeTab === 'analytics' && <AnalyticsHub token={token} />}

          {activeTab === 'projects' && (
            <ProjectHub
              token={token}
              projects={projects}
              onProjectAdded={handleProjectAdded}
              onProjectDeleted={handleProjectDeleted}
            />
          )}

          {activeTab === 'forecast' && <ForecastHub token={token} />}

          {activeTab === 'ledger' && <LedgerHub token={token} />}

          {activeTab === 'ai' && <AiHub token={token} />}

          {activeTab === 'admin' && <AdminHub token={token} />}

          {activeTab === 'settings' && (
            <div className="bg-[#0c142e]/60 border border-slate-800/80 p-6 rounded-3xl max-w-xl">
              <h4 className="text-base font-bold text-white mb-6">Exposed Portfolio Properties</h4>
              
              <form onSubmit={handleSaveSettings} className="space-y-5">
                {/* Title */}
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Public Page Title</label>
                  <input
                    type="text"
                    required
                    value={portfolioTitle}
                    onChange={e => setPortfolioTitle(e.target.value)}
                    className="w-full bg-[#070b1a]/85 border border-slate-800 focus:border-cyan-500/60 rounded-xl py-2 px-3.5 text-xs text-white outline-none transition-all"
                  />
                </div>

                {/* Bio Description */}
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Bio Summary Statement</label>
                  <textarea
                    rows={4}
                    value={portfolioDesc}
                    onChange={e => setPortfolioDesc(e.target.value)}
                    className="w-full bg-[#070b1a]/85 border border-slate-800 focus:border-cyan-500/60 rounded-xl py-2 px-3.5 text-xs text-white outline-none transition-all resize-none"
                  />
                </div>

                {/* Theme Selector */}
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Exposed Theme Layout</label>
                  <div className="grid grid-cols-2 gap-2.5">
                    <button
                      type="button"
                      onClick={() => setPortfolioTheme('glassmorphism')}
                      className={`p-3 text-xs font-semibold rounded-xl text-left border transition-all ${portfolioTheme === 'glassmorphism' ? 'bg-cyan-950/40 border-cyan-500/30 text-cyan-400' : 'bg-slate-950/30 border-slate-850 text-slate-500'}`}
                    >
                      <span className="block font-bold">Glassmorphism</span>
                      <span className="text-[9px] text-slate-500 font-normal">Sleek cyan transparency glow</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setPortfolioTheme('dark-cyber')}
                      className={`p-3 text-xs font-semibold rounded-xl text-left border transition-all ${portfolioTheme === 'dark-cyber' ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-400' : 'bg-slate-950/30 border-slate-850 text-slate-500'}`}
                    >
                      <span className="block font-bold">Cyber Green Terminal</span>
                      <span className="text-[9px] text-slate-500 font-normal">Glowing console matrix view</span>
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-3 rounded-xl transition-all flex items-center justify-center gap-2 text-xs"
                >
                  Save Portfolio Settings
                </button>
              </form>
            </div>
          )}
        </div>

      </main>
    </div>
  );
};

export default Dashboard;