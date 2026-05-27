import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Plus, Landmark, ArrowUpRight, ArrowDownRight, DollarSign, Wallet } from 'lucide-react';

interface Transaction {
  id: string;
  amount: number;
  type: 'INCOME' | 'EXPENSE';
  category: string;
  notes?: string;
  createdAt: string;
}

interface LedgerHubProps {
  token: string;
}

const LedgerHub: React.FC<LedgerHubProps> = ({ token }) => {
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState({ totalIncome: 12700, totalExpenses: 1650, netProfit: 11050, savingsRate: 87.0 });
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [chartData, setChartData] = useState<any[]>([]);

  // Input states
  const [amount, setAmount] = useState('');
  const [type, setType] = useState<'INCOME' | 'EXPENSE'>('INCOME');
  const [category, setCategory] = useState('SaaS');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchLedgerData();
  }, [token]);

  const fetchLedgerData = async () => {
    try {
      // 1. Fetch History
      const histResponse = await fetch('http://localhost:8000/api/transactions/history', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const histData = await histResponse.json();

      // 2. Fetch Aggregations
      const analResponse = await fetch('http://localhost:8000/api/transactions/analytics', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const analData = await analResponse.json();

      if (histResponse.ok && analResponse.ok) {
        setTransactions(histData.transactions);
        setSummary(analData.summary);
        setChartData(analData.chartData);
      } else {
        generateMockLedger();
      }
    } catch (err) {
      generateMockLedger();
    } finally {
      setLoading(false);
    }
  };

  const generateMockLedger = () => {
    setSummary({ totalIncome: 12700, totalExpenses: 1650, netProfit: 11050, savingsRate: 87.0 });
    setTransactions([
      { id: 'tx_1', amount: 8500, type: 'INCOME', category: 'SaaS', notes: 'Monthly Subscription Revenue', createdAt: new Date(Date.now() - 5*24*60*60*1000).toISOString() },
      { id: 'tx_2', amount: 4200, type: 'INCOME', category: 'Freelance', notes: 'API Architecture Consulting', createdAt: new Date(Date.now() - 3*24*60*60*1000).toISOString() },
      { id: 'tx_3', amount: 1200, type: 'EXPENSE', category: 'Hardware', notes: 'GPU Server Lease', createdAt: new Date(Date.now() - 2*24*60*60*1000).toISOString() },
      { id: 'tx_4', amount: 450, type: 'EXPENSE', category: 'Marketing', notes: 'SaaS Growth Ads', createdAt: new Date(Date.now() - 1*24*60*60*1000).toISOString() }
    ]);
    setChartData([
      { name: 'Jan', income: 1000, expenses: 300, net: 700 },
      { name: 'Feb', income: 1500, expenses: 400, net: 1100 },
      { name: 'Mar', income: 1200, expenses: 350, net: 850 },
      { name: 'Apr', income: 1900, expenses: 500, net: 1400 },
      { name: 'May', income: 2800, expenses: 600, net: 2200 },
      { name: 'Jun', income: 4300, expenses: 800, net: 3500 }
    ]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!amount || parseFloat(amount) <= 0) return;

    setSubmitting(true);

    const payload = {
      amount: parseFloat(amount),
      type,
      category,
      notes
    };

    try {
      const response = await fetch('http://localhost:8000/api/transactions/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        setAmount('');
        setNotes('');
        await fetchLedgerData();
      } else {
        handleSandboxAdd();
      }
    } catch (err) {
      handleSandboxAdd();
    } finally {
      setSubmitting(false);
    }
  };

  const handleSandboxAdd = () => {
    const val = parseFloat(amount);
    const mockTx: Transaction = {
      id: 'tx_' + Math.random().toString(36).substr(2, 9),
      amount: val,
      type,
      category,
      notes: notes || 'Sandbox Mock Ledger',
      createdAt: new Date().toISOString()
    };

    // Recalculate states
    const updatedTxs = [mockTx, ...transactions];
    setTransactions(updatedTxs);

    let inc = summary.totalIncome;
    let exp = summary.totalExpenses;
    if (type === 'INCOME') inc += val;
    else exp += val;

    setSummary({
      totalIncome: inc,
      totalExpenses: exp,
      netProfit: inc - exp,
      savingsRate: inc > 0 ? ((inc - exp) / inc) * 100 : 0
    });

    // Append to charts progression
    const updatedCharts = [...chartData];
    if (updatedCharts.length > 0) {
      const last = updatedCharts[updatedCharts.length - 1];
      if (type === 'INCOME') last.income += val;
      else last.expenses += val;
      last.net = last.income - last.expenses;
    }
    setChartData(updatedCharts);

    setAmount('');
    setNotes('');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      
      {/* Finance Balance Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        
        {/* Net Cashflow */}
        <div className="bg-gradient-to-br from-[#0c1e3d]/80 to-[#070b1a]/90 border border-cyan-500/20 p-5 rounded-2xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/5 rounded-bl-full group-hover:bg-cyan-500/10 transition-all" />
          <div className="flex justify-between items-start relative z-10">
            <div>
              <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Net Operating Profits</p>
              <h3 className="text-3xl font-extrabold mt-2 text-cyan-400">${summary.netProfit.toLocaleString()}</h3>
            </div>
            <div className="p-2.5 bg-cyan-950/60 border border-cyan-500/20 text-cyan-400 rounded-xl">
              <Wallet className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-center gap-1.5 text-emerald-400 text-xs mt-4 font-semibold">
            <Landmark className="w-3.5 h-3.5" />
            <span>Savings rate: {summary.savingsRate.toFixed(1)}%</span>
          </div>
        </div>

        {/* Total Incomes */}
        <div className="bg-[#0c142e]/55 border border-slate-800/80 p-5 rounded-2xl relative overflow-hidden group hover:border-emerald-500/40 transition-all">
          <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-bl-full" />
          <div className="flex justify-between items-start">
            <div>
              <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Gross Income Stream</p>
              <h3 className="text-3xl font-bold mt-2 text-emerald-400">${summary.totalIncome.toLocaleString()}</h3>
            </div>
            <div className="p-2.5 bg-emerald-950/60 border border-emerald-500/20 text-emerald-400 rounded-xl">
              <ArrowUpRight className="w-5 h-5" />
            </div>
          </div>
          <div className="text-slate-500 text-xs mt-4">Accumulated SaaS & contracts ledger</div>
        </div>

        {/* Total Expenses */}
        <div className="bg-[#0c142e]/55 border border-slate-800/80 p-5 rounded-2xl relative overflow-hidden group hover:border-red-500/40 transition-all">
          <div className="absolute top-0 right-0 w-24 h-24 bg-red-500/5 rounded-bl-full" />
          <div className="flex justify-between items-start">
            <div>
              <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Total SaaS Expenses</p>
              <h3 className="text-3xl font-bold mt-2 text-rose-500">${summary.totalExpenses.toLocaleString()}</h3>
            </div>
            <div className="p-2.5 bg-red-950/60 border border-red-500/20 text-rose-500 rounded-xl">
              <ArrowDownRight className="w-5 h-5" />
            </div>
          </div>
          <div className="text-slate-500 text-xs mt-4">Marketing, nodes, cloud computing costs</div>
        </div>

      </div>

      {/* Trailing Ledger Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Ledger Entry Form & Lists */}
        <div className="lg:col-span-1 bg-[#0c142e]/60 border border-slate-800/80 p-6 rounded-3xl h-fit">
          <div className="flex items-center gap-2 mb-4">
            <DollarSign className="w-5 h-5 text-cyan-400" />
            <h4 className="text-base font-bold text-white">Record Transaction</h4>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Amount */}
            <div className="space-y-1">
              <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400 font-semibold">Value ($) *</label>
              <input
                type="number"
                required
                min="0.01"
                step="0.01"
                placeholder="4500.00"
                value={amount}
                onChange={e => setAmount(e.target.value)}
                className="w-full bg-[#070b1a]/85 border border-slate-800 focus:border-cyan-500/60 rounded-xl py-2 px-3.5 text-xs text-white outline-none transition-all"
              />
            </div>

            {/* Type */}
            <div className="space-y-1">
              <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400 font-semibold">Ledger Stream</label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setType('INCOME')}
                  className={`py-2 px-3 text-xs font-semibold rounded-xl transition-all border ${type === 'INCOME' ? 'bg-emerald-950/50 border-emerald-500/30 text-emerald-400' : 'bg-slate-950/40 border-slate-800 text-slate-400'}`}
                >
                  Income
                </button>
                <button
                  type="button"
                  onClick={() => setType('EXPENSE')}
                  className={`py-2 px-3 text-xs font-semibold rounded-xl transition-all border ${type === 'EXPENSE' ? 'bg-rose-950/50 border-rose-500/30 text-rose-400' : 'bg-slate-950/40 border-slate-800 text-slate-400'}`}
                >
                  Expense
                </button>
              </div>
            </div>

            {/* Category */}
            <div className="space-y-1">
              <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400 font-semibold">Category</label>
              <select
                value={category}
                onChange={e => setCategory(e.target.value)}
                className="w-full bg-[#070b1a]/85 border border-slate-800 focus:border-cyan-500/60 rounded-xl py-2 px-3.5 text-xs text-white outline-none transition-all"
              >
                <option value="SaaS">SaaS Subscriptions</option>
                <option value="Freelance">Freelance Contracts</option>
                <option value="Hardware">Hardware Devices</option>
                <option value="Marketing">Growth Marketing</option>
                <option value="Other">Miscellaneous Costs</option>
              </select>
            </div>

            {/* Notes */}
            <div className="space-y-1">
              <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400 font-semibold">Memo details</label>
              <input
                type="text"
                placeholder="e.g. AWS server configurations"
                value={notes}
                onChange={e => setNotes(e.target.value)}
                className="w-full bg-[#070b1a]/85 border border-slate-800 focus:border-cyan-500/60 rounded-xl py-2 px-3.5 text-xs text-white placeholder-slate-600 outline-none transition-all"
              />
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-3 rounded-xl transition-all flex items-center justify-center gap-2 text-xs"
            >
              <Plus className="w-4 h-4" />
              {submitting ? 'Recording...' : 'Record Transaction'}
            </button>
          </form>

        </div>

        {/* ledger history tables & chart */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Monthly Trajectory Recharts */}
          <div className="bg-[#0c142e]/50 border border-slate-800/85 p-6 rounded-3xl">
            <h4 className="text-base font-bold text-white mb-6">Operating Net-Revenue Trajectory</h4>
            <div className="h-[200px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorNet" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.15}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.2} />
                  <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0c142e', border: '1px solid #334155', borderRadius: '12px' }}
                  />
                  <Area type="monotone" dataKey="income" stroke="#10b981" strokeWidth={1.5} fillOpacity={0} />
                  <Area type="monotone" dataKey="expenses" stroke="#f43f5e" strokeWidth={1.5} fillOpacity={0} />
                  <Area type="monotone" dataKey="net" stroke="#06b6d4" strokeWidth={2.5} fillOpacity={1} fill="url(#colorNet)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Ledger historical records table */}
          <div className="bg-[#0c142e]/50 border border-slate-800/85 p-6 rounded-3xl">
            <h4 className="text-base font-bold text-white mb-4">Historical Cashbook Ledger</h4>
            
            {transactions.length === 0 ? (
              <p className="text-center text-slate-500 text-xs py-8">No transaction ledger history recorded</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-slate-800/80 text-[10px] uppercase font-bold tracking-wider text-slate-500">
                      <th className="pb-3">Date</th>
                      <th className="pb-3">Category</th>
                      <th className="pb-3">Memo</th>
                      <th className="pb-3 text-right">Value</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-900 text-xs">
                    {transactions.map(tx => (
                      <tr key={tx.id} className="text-slate-300">
                        <td className="py-3.5 text-slate-400">
                          {new Date(tx.createdAt).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                        </td>
                        <td className="py-3.5 font-semibold text-slate-200">{tx.category}</td>
                        <td className="py-3.5 text-slate-400 max-w-[150px] truncate">{tx.notes || '—'}</td>
                        <td className={`py-3.5 text-right font-extrabold ${tx.type === 'INCOME' ? 'text-emerald-400' : 'text-rose-500'}`}>
                          {tx.type === 'INCOME' ? '+' : '-'}${tx.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
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

export default LedgerHub;
