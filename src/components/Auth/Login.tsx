import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, Mail, ArrowRight, ShieldCheck } from 'lucide-react';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // 1. Attempt dynamic API request
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (response.ok && data.token) {
        localStorage.setItem('portfolio_os_token', data.token);
        localStorage.setItem('portfolio_os_user', JSON.stringify(data.user));
        navigate('/dashboard');
      } else {
        setError(data.error || 'Invalid login credentials');
      }
    } catch (err) {
      // 2. Client-Side Resilient Sandbox Fallback
      console.log('API offline. Launching client-side sandbox mode...');
      if (email === 'john@portfolioos.ai' && password === 'password123') {
        const mockUser = {
          id: 'usr_john',
          fullName: 'John Doe',
          username: 'john_doe',
          email: 'john@portfolioos.ai',
          role: 'PREMIUM_USER',
          avatarUrl: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150',
          bio: 'Senior Full-Stack Architect & AI Specialist crafting glassmorphic terminals.'
        };
        localStorage.setItem('portfolio_os_token', 'mock_sandbox_jwt_token_2026');
        localStorage.setItem('portfolio_os_user', JSON.stringify(mockUser));
        navigate('/dashboard');
      } else {
        setError('Try the seeded credentials: john@portfolioos.ai / password123 or click "Instant Sandbox Demo".');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSandboxDemo = () => {
    setLoading(true);
    setTimeout(() => {
      const mockUser = {
        id: 'usr_john',
        fullName: 'John Doe',
        username: 'john_doe',
        email: 'john@portfolioos.ai',
        role: 'PREMIUM_USER',
        avatarUrl: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150',
        bio: 'Senior Full-Stack Architect & AI Specialist crafting glassmorphic terminals.'
      };
      localStorage.setItem('portfolio_os_token', 'mock_sandbox_jwt_token_2026');
      localStorage.setItem('portfolio_os_user', JSON.stringify(mockUser));
      navigate('/dashboard');
    }, 600);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#070b19] px-4 relative overflow-hidden">
      {/* Background Gradients */}
      <div className="absolute w-[400px] h-[400px] bg-cyan-500/10 rounded-full blur-[120px] top-[-50px] left-[-50px]" />
      <div className="absolute w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[140px] bottom-[-100px] right-[-100px]" />

      <div className="w-full max-w-md bg-[#0c142e]/60 border border-slate-800/80 backdrop-blur-xl rounded-3xl p-8 shadow-2xl relative z-10">
        
        {/* Brand Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center p-3 bg-cyan-950/80 border border-cyan-500/30 rounded-2xl mb-4 shadow-lg shadow-cyan-950/50">
            <ShieldCheck className="w-8 h-8 text-cyan-400" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-400 bg-clip-text text-transparent">
            PortfolioOS <span className="text-cyan-400">AI</span>
          </h1>
          <p className="text-slate-400 text-sm mt-2">Log in to your secure operating dashboard</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-950/50 border border-red-500/30 text-red-200 text-xs rounded-2xl text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-5">
          {/* Email input */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-300">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="email"
                required
                placeholder="name@example.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full bg-[#070b1a]/80 border border-slate-800/85 focus:border-cyan-500/80 rounded-2xl py-3.5 pl-12 pr-4 text-sm text-white placeholder-slate-600 outline-none transition-all focus:shadow-[0_0_15px_rgba(6,182,212,0.15)]"
              />
            </div>
          </div>

          {/* Password input */}
          <div className="space-y-1">
            <div className="flex justify-between items-center">
              <label className="text-xs font-semibold text-slate-300">Password</label>
              <a href="#" className="text-xs text-cyan-400 hover:underline">Forgot password?</a>
            </div>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="password"
                required
                placeholder="••••••••"
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full bg-[#070b1a]/80 border border-slate-800/85 focus:border-cyan-500/80 rounded-2xl py-3.5 pl-12 pr-4 text-sm text-white placeholder-slate-600 outline-none transition-all focus:shadow-[0_0_15px_rgba(6,182,212,0.15)]"
              />
            </div>
          </div>

          {/* Login Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-3.5 rounded-2xl transition-all shadow-lg shadow-cyan-600/25 flex items-center justify-center gap-2 hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50"
          >
            {loading ? 'Authenticating...' : 'Sign In'}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Divider */}
        <div className="relative my-6 flex items-center justify-center">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-800/80"></div>
          </div>
          <span className="relative px-3 bg-[#0c142e] text-[10px] uppercase tracking-wider text-slate-500">Or Sandbox Sandbox</span>
        </div>

        {/* Instant Sandbox Bypass */}
        <button
          onClick={handleSandboxDemo}
          type="button"
          className="w-full bg-slate-900 hover:bg-slate-800 border border-slate-800 text-cyan-400 font-semibold py-3.5 rounded-2xl transition-all flex items-center justify-center gap-2"
        >
          <ShieldCheck className="w-4 h-4 text-cyan-400 animate-pulse" />
          Instant Sandbox Demo
        </button>

        <p className="text-center text-slate-500 text-xs mt-6">
          Don't have an operating account?{' '}
          <Link to="/register" className="text-cyan-400 font-semibold hover:underline">
            Register Account
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
