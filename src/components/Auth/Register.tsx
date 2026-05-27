import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { User, Mail, Lock, ArrowRight, ShieldCheck } from 'lucide-react';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const [fullName, setFullName] = useState('');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fullName, username, email, password })
      });

      const data = await response.json();

      if (response.ok && data.token) {
        localStorage.setItem('portfolio_os_token', data.token);
        localStorage.setItem('portfolio_os_user', JSON.stringify(data.user));
        navigate('/dashboard');
      } else {
        setError(data.error || 'Registration failed');
      }
    } catch (err) {
      console.log('API offline. Registering in-browser mock session...');
      const mockUser = {
        id: 'usr_new',
        fullName: fullName || 'New Sandbox User',
        username: username.toLowerCase() || 'sandbox_user',
        email: email || 'user@portfolioos.ai',
        role: 'USER'
      };
      localStorage.setItem('portfolio_os_token', 'mock_sandbox_jwt_token_2026');
      localStorage.setItem('portfolio_os_user', JSON.stringify(mockUser));
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#070b19] px-4 relative overflow-hidden">
      {/* Background Gradients */}
      <div className="absolute w-[400px] h-[400px] bg-cyan-500/10 rounded-full blur-[120px] top-[-50px] left-[-50px]" />
      <div className="absolute w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[140px] bottom-[-100px] right-[-100px]" />

      <div className="w-full max-w-md bg-[#0c142e]/60 border border-slate-800/80 backdrop-blur-xl rounded-3xl p-8 shadow-2xl relative z-10">
        
        {/* Brand Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center p-3 bg-cyan-950/80 border border-cyan-500/30 rounded-2xl mb-4 shadow-lg shadow-cyan-950/50">
            <ShieldCheck className="w-8 h-8 text-cyan-400" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-400 bg-clip-text text-transparent">
            Create Account
          </h1>
          <p className="text-slate-400 text-sm mt-2">Deploy your modular AI Portfolio OS</p>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-950/50 border border-red-500/30 text-red-200 text-xs rounded-2xl text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-4">
          {/* Full Name input */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-300">Full Name</label>
            <div className="relative">
              <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                required
                placeholder="Jane Doe"
                value={fullName}
                onChange={e => setFullName(e.target.value)}
                className="w-full bg-[#070b1a]/80 border border-slate-800/85 focus:border-cyan-500/80 rounded-2xl py-3.5 pl-12 pr-4 text-sm text-white placeholder-slate-600 outline-none transition-all focus:shadow-[0_0_15px_rgba(6,182,212,0.15)]"
              />
            </div>
          </div>

          {/* Username input */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-300">Desired Username</label>
            <div className="relative">
              <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                required
                placeholder="jane_doe"
                value={username}
                onChange={e => setUsername(e.target.value)}
                className="w-full bg-[#070b1a]/80 border border-slate-800/85 focus:border-cyan-500/80 rounded-2xl py-3.5 pl-12 pr-4 text-sm text-white placeholder-slate-600 outline-none transition-all focus:shadow-[0_0_15px_rgba(6,182,212,0.15)]"
              />
            </div>
          </div>

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
            <label className="text-xs font-semibold text-slate-300">Secret Password</label>
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

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-3.5 rounded-2xl mt-2 transition-all shadow-lg shadow-cyan-600/25 flex items-center justify-center gap-2 hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50"
          >
            {loading ? 'Registering workspace...' : 'Deploy Operating System'}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <p className="text-center text-slate-500 text-xs mt-6">
          Already registered?{' '}
          <Link to="/login" className="text-cyan-400 font-semibold hover:underline">
            Sign In Instead
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
