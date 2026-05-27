import React, { useState, useEffect } from 'react';
import { Users, CheckCircle, XCircle, ShieldAlert, Cpu, Key, UserCheck } from 'lucide-react';

interface AdminHubProps {
  token: string;
}

interface UserRecord {
  id: string;
  fullName: string;
  username: string;
  email: string;
  role: string;
  isVerified: boolean;
  createdAt: string;
}

interface StatsData {
  totalUsers: number;
  totalPortfolios: number;
  totalPositions: number;
  totalTransactions: number;
  transactionVolume: number;
}

const AdminHub: React.FC<AdminHubProps> = ({ token }) => {
  const [stats, setStats] = useState<StatsData | null>(null);
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState('');
  const [sandboxResult, setSandboxResult] = useState<string>('');
  const [sandboxBlocked, setSandboxBlocked] = useState<boolean>(false);

  const fetchAdminData = async () => {
    try {
      setLoading(true);
      // Fetch Stats
      const statsRes = await fetch('http://localhost:8000/api/admin/stats', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const statsData = await statsRes.json();
      if (statsRes.ok) setStats(statsData);

      // Fetch Users
      const usersRes = await fetch('http://localhost:8000/api/admin/users', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const usersData = await usersRes.json();
      if (usersRes.ok) setUsers(usersData.users || []);
    } catch (err) {
      console.error('Failed to load admin telemetry:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, [token]);

  // Toggles user verification
  const handleToggleVerify = async (userId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/admin/users/${userId}/toggle-verify`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      if (res.ok) {
        showToast('User verification toggled successfully!');
        // Update local list
        setUsers(prev => prev.map(u => u.id === userId ? { ...u, isVerified: data.isVerified } : u));
      } else {
        showToast(data.error || 'Failed to update user.');
      }
    } catch (err) {
      showToast('API Connection Error.');
    }
  };

  // Alters user role
  const handleChangeRole = async (userId: string, newRole: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/admin/users/${userId}/role`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ role: newRole })
      });
      const data = await res.json();
      if (res.ok) {
        showToast(`Role updated to ${newRole}!`);
        setUsers(prev => prev.map(u => u.id === userId ? { ...u, role: data.role } : u));
      } else {
        showToast(data.error || 'Failed to modify role.');
      }
    } catch (err) {
      showToast('API Connection Error.');
    }
  };

  // Test User-Only Restricted API: /api/user/profile
  const testUserOnlyApi = async () => {
    setSandboxResult('Pinging User-only profile feeds...');
    setSandboxBlocked(false);
    try {
      const res = await fetch('http://localhost:8000/api/user/profile', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      
      if (res.status === 403) {
        setSandboxBlocked(true);
        setSandboxResult('⚠️ ACCESS BLOCKED (403 Forbidden): Standard or Premium User scope required. Admins are strictly blocked.');
      } else if (res.ok) {
        setSandboxBlocked(false);
        setSandboxResult(`✅ ACCESS ALLOWED: Loaded profile for ${data.profile.fullName} (Role: ${data.profile.role})`);
      } else {
        setSandboxBlocked(true);
        setSandboxResult(`❌ Error (${res.status}): ${data.error || 'Request rejected.'}`);
      }
    } catch (err) {
      setSandboxResult('❌ API Connection Failure.');
    }
  };

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(''), 3000);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12 bg-[#0c142e]/30 border border-slate-800/80 rounded-3xl">
        <div className="w-6 h-6 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Dynamic Action Toast */}
      {toast && (
        <div className="fixed bottom-6 right-6 p-4 bg-emerald-950/90 border border-emerald-500/30 backdrop-blur-md rounded-2xl text-emerald-300 text-xs shadow-2xl flex items-center gap-2 z-50 animate-fadeIn">
          <CheckCircle className="w-4 h-4 text-emerald-400" />
          <span>{toast}</span>
        </div>
      )}

      {/* 1. Stats Summary Cards */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-[#0c142e]/60 border border-slate-800/80 p-4.5 rounded-2xl">
            <span className="text-[9px] text-slate-500 font-extrabold uppercase tracking-widest block">Total Registered Users</span>
            <span className="text-xl font-black font-mono text-white block mt-1">{stats.totalUsers}</span>
          </div>
          <div className="bg-[#0c142e]/60 border border-slate-800/80 p-4.5 rounded-2xl">
            <span className="text-[9px] text-slate-500 font-extrabold uppercase tracking-widest block">Exposed Portfolios</span>
            <span className="text-xl font-black font-mono text-cyan-400 block mt-1">{stats.totalPortfolios}</span>
          </div>
          <div className="bg-[#0c142e]/60 border border-slate-800/80 p-4.5 rounded-2xl">
            <span className="text-[9px] text-slate-500 font-extrabold uppercase tracking-widest block">Logged Positions</span>
            <span className="text-xl font-black font-mono text-emerald-400 block mt-1">{stats.totalPositions}</span>
          </div>
          <div className="bg-[#0c142e]/60 border border-slate-800/80 p-4.5 rounded-2xl">
            <span className="text-[9px] text-slate-500 font-extrabold uppercase tracking-widest block">Transaction Volume</span>
            <span className="text-xl font-black font-mono text-purple-400 block mt-1">${stats.transactionVolume.toLocaleString()}</span>
          </div>
        </div>
      )}

      {/* 2. User Directory & Role Management Grid */}
      <div className="bg-[#0c142e]/60 border border-slate-800/80 p-6 rounded-3xl space-y-4">
        <div className="flex items-center gap-2">
          <Users className="w-5 h-5 text-cyan-400" />
          <h4 className="text-base font-bold text-white">System User Management</h4>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-850 text-slate-400 uppercase text-[9px] font-black tracking-widest">
                <th className="py-3 px-4">User Details</th>
                <th className="py-3 px-4">Email</th>
                <th className="py-3 px-4">Role System</th>
                <th className="py-3 px-4 text-center">Verified</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id} className="border-b border-slate-900 hover:bg-[#070b1a]/20 transition-all">
                  <td className="py-3.5 px-4 font-bold text-white flex flex-col">
                    <span>{u.fullName}</span>
                    <span className="text-[9px] text-slate-500 font-mono">@{u.username}</span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-300 font-mono">{u.email}</td>
                  <td className="py-3.5 px-4">
                    <select
                      value={u.role}
                      onChange={e => handleChangeRole(u.id, e.target.value)}
                      className="bg-slate-950 border border-slate-800 focus:border-cyan-500/50 rounded-lg text-cyan-400 font-bold px-2 py-1 outline-none text-[10px]"
                    >
                      <option value="USER">USER</option>
                      <option value="PREMIUM_USER">PREMIUM_USER</option>
                      <option value="ADMIN">ADMIN</option>
                    </select>
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <button
                      onClick={() => handleToggleVerify(u.id)}
                      className={`inline-flex p-1 rounded-lg ${u.isVerified ? 'bg-emerald-950/20 text-emerald-400 border border-emerald-500/20' : 'bg-rose-950/20 text-rose-400 border border-rose-500/20'}`}
                    >
                      {u.isVerified ? <CheckCircle className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                    </button>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={() => handleToggleVerify(u.id)}
                      className="text-[9px] uppercase tracking-wider font-extrabold bg-slate-900 border border-slate-850 px-2.5 py-1.5 rounded-lg text-slate-400 hover:text-white transition-all"
                    >
                      Toggle Verify
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 3. User-Only API Security Isolation Testing Sandbox */}
      <div className="bg-[#0c142e]/60 border border-slate-800/80 p-6 rounded-3xl space-y-4">
        <div className="flex items-center gap-2">
          <Key className="w-5 h-5 text-purple-400" />
          <h4 className="text-base font-bold text-white">Route Guard Security Sandbox</h4>
        </div>
        <p className="text-xs text-slate-400">
          Verify role isolation. Pinging the strictly User-Only profile endpoint (`/api/user/profile`) should reject admins automatically with a **403 Forbidden** error, whilst allowing basic user credentials to pass.
        </p>

        <div className="flex flex-col md:flex-row gap-4 items-center bg-[#070b1a]/40 p-4.5 rounded-2xl border border-slate-900/60">
          <button
            onClick={testUserOnlyApi}
            className="w-full md:w-auto shrink-0 bg-purple-600 hover:bg-purple-500 text-white font-semibold py-2.5 px-5 rounded-xl transition-all flex items-center justify-center gap-2 text-xs"
          >
            <Cpu className="w-4 h-4" />
            Ping User Profile API
          </button>

          {sandboxResult && (
            <div className={`flex-1 text-xs font-mono font-bold p-3 rounded-lg border leading-relaxed ${sandboxBlocked ? 'bg-rose-950/20 border-rose-500/20 text-rose-400' : 'bg-emerald-950/20 border-emerald-500/20 text-emerald-400'}`}>
              {sandboxResult}
            </div>
          )}
        </div>
      </div>

    </div>
  );
};

export default AdminHub;
