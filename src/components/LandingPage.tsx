import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, DollarSign, Brain, ShieldCheck, ArrowRight } from 'lucide-react';

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#060913] text-slate-100 flex flex-col items-center justify-center p-6 relative overflow-hidden">
      
      {/* Cinematic glows */}
      <div className="absolute w-[500px] h-[500px] bg-cyan-500/10 rounded-full blur-[140px] top-[-100px] left-[-100px]" />
      <div className="absolute w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[140px] bottom-[-100px] right-[-100px]" />

      <div className="max-w-4xl w-full text-center relative z-10 space-y-10">
        
        {/* Brand Badge */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-cyan-950/40 border border-cyan-500/20 text-cyan-400 rounded-full text-xs font-semibold backdrop-blur-md">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
          <span>Next-Generation Developer Operating System</span>
        </div>

        {/* Big Hero Header */}
        <div className="space-y-4">
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white leading-[1.1]">
            PortfolioOS <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-blue-500 to-indigo-400">AI</span>
          </h1>
          <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
            The multi-tenant AI Portfolio + Business Operating System. Track SaaS finances, showcase featured projects, analyze resumes, and expose gorgeous glassmorphic portfolios.
          </p>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
          
          <div className="bg-[#0c142e]/55 border border-slate-800/80 backdrop-blur-md rounded-2xl p-6 hover:border-cyan-500/20 transition-all text-center space-y-3 group">
            <div className="p-3 bg-cyan-950/60 border border-cyan-500/20 text-cyan-400 rounded-xl w-fit mx-auto group-hover:scale-105 transition-all">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="text-white font-bold text-sm">Professional Portfolios</h3>
            <p className="text-slate-400 text-xs leading-relaxed">Dynamic showcases mapping customizable themes and public slugs.</p>
          </div>

          <div className="bg-[#0c142e]/55 border border-slate-800/80 backdrop-blur-md rounded-2xl p-6 hover:border-blue-500/20 transition-all text-center space-y-3 group">
            <div className="p-3 bg-blue-950/60 border border-blue-500/20 text-blue-400 rounded-xl w-fit mx-auto group-hover:scale-105 transition-all">
              <DollarSign className="w-6 h-6" />
            </div>
            <h3 className="text-white font-bold text-sm">Business Ledgers</h3>
            <p className="text-slate-400 text-xs leading-relaxed">Track incomes, expenses, categories, and monthly trajectories.</p>
          </div>

          <div className="bg-[#0c142e]/55 border border-slate-800/80 backdrop-blur-md rounded-2xl p-6 hover:border-emerald-500/20 transition-all text-center space-y-3 group">
            <div className="p-3 bg-emerald-950/60 border border-emerald-500/20 text-emerald-400 rounded-xl w-fit mx-auto group-hover:scale-105 transition-all">
              <Brain className="w-6 h-6 animate-pulse" />
            </div>
            <h3 className="text-white font-bold text-sm">AI Recommendation</h3>
            <p className="text-slate-400 text-xs leading-relaxed">Synthesize profiles, analyze resumes, and optimize copywriting.</p>
          </div>

          <div className="bg-[#0c142e]/55 border border-slate-800/80 backdrop-blur-md rounded-2xl p-6 hover:border-amber-500/20 transition-all text-center space-y-3 group">
            <div className="p-3 bg-amber-950/60 border border-amber-500/20 text-amber-400 rounded-xl w-fit mx-auto group-hover:scale-105 transition-all">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-white font-bold text-sm">Secured Multi-Tenant</h3>
            <p className="text-slate-400 text-xs leading-relaxed">JWT secure authorization with Role-Based Access Control.</p>
          </div>

        </div>

        {/* CTA Launch Hub Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Link
            to="/login"
            className="w-full sm:w-auto inline-flex items-center justify-center px-8 py-4 bg-cyan-600 hover:bg-cyan-500 text-white font-semibold rounded-2xl transition-all shadow-lg shadow-cyan-600/20 hover:scale-[1.02] active:scale-[0.98] gap-2 text-sm"
          >
            Deploy OS Workstation
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/p/john_doe"
            className="w-full sm:w-auto inline-flex items-center justify-center px-8 py-4 bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white rounded-2xl border border-slate-800 transition-all text-sm"
          >
            Explore Public Portfolio
          </Link>
        </div>

      </div>
    </div>
  );
};

export default LandingPage;