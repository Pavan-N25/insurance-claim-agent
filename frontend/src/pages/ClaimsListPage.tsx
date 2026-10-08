import React, { useState, useEffect } from 'react';
import { 
  Search, Filter, Plus, Sparkles, RefreshCw, ChevronRight, 
  AlertTriangle, ShieldCheck, CheckCircle2 
} from 'lucide-react';
import { apiClient } from '../api/client';
import { Claim } from '../types';

interface ClaimsListPageProps {
  onSelectClaim: (claimId: string) => void;
  onNewClaim: () => void;
  onAnalyzeClaim: (claimId: string) => void;
}

export const ClaimsListPage: React.FC<ClaimsListPageProps> = ({ 
  onSelectClaim, 
  onNewClaim,
  onAnalyzeClaim 
}) => {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [search, setSearch] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');

  const fetchClaims = async () => {
    setLoading(true);
    try {
      let endpoint = `/claims?search=${encodeURIComponent(search)}`;
      if (statusFilter !== 'ALL') endpoint += `&status=${statusFilter}`;
      if (priorityFilter !== 'ALL') endpoint += `&priority=${priorityFilter}`;
      const res = await apiClient.get(endpoint);
      setClaims(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClaims();
  }, [statusFilter, priorityFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchClaims();
  };

  return (
    <div className="space-y-6">
      
      {/* Top Title & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">Claims Adjudication Queue</h1>
          <p className="text-sm text-slate-400">Search, triage, and route claims across auto, property, and commercial lines.</p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchClaims}
            className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition-all"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={onNewClaim}
            className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-4 py-2.5 rounded-xl shadow-lg transition-all flex items-center space-x-1.5"
          >
            <Plus className="w-4 h-4" />
            <span>Intake New Claim</span>
          </button>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-slate-900 border border-slate-800 p-4 rounded-2xl flex flex-col md:flex-row gap-3">
        <form onSubmit={handleSearchSubmit} className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by Claim ID, Claimant Name, or Policy Number..."
            className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </form>

        <div className="flex items-center space-x-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-slate-300 text-xs rounded-xl px-3 py-2 focus:outline-none cursor-pointer"
          >
            <option value="ALL">All Statuses</option>
            <option value="SUBMITTED">Submitted</option>
            <option value="AUTO_APPROVED">Auto Approved</option>
            <option value="MANUAL_REVIEW">Manual Review</option>
            <option value="FLAGGED_INVESTIGATION">Flagged Investigation</option>
            <option value="REQUEST_INFO">Request Info</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-slate-300 text-xs rounded-xl px-3 py-2 focus:outline-none cursor-pointer"
          >
            <option value="ALL">All Priorities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="NORMAL">Normal</option>
            <option value="LOW">Low</option>
          </select>
        </div>
      </div>

      {/* Claims Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-3.5">Claim ID</th>
                <th className="p-3.5">Policy Number</th>
                <th className="p-3.5">Claimant</th>
                <th className="p-3.5">Line of Business</th>
                <th className="p-3.5">Claimed Payout</th>
                <th className="p-3.5">Fraud Score</th>
                <th className="p-3.5">Triage Recommendation</th>
                <th className="p-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {claims.map((c) => {
                const isHighFraud = c.fraud_score >= 60;

                return (
                  <tr 
                    key={c.id} 
                    className="hover:bg-slate-800/40 transition-colors group cursor-pointer"
                    onClick={() => onSelectClaim(c.id)}
                  >
                    <td className="p-3.5 font-mono font-bold text-blue-400 group-hover:underline">
                      {c.id}
                    </td>
                    <td className="p-3.5 font-mono text-slate-400">{c.policy_number}</td>
                    <td className="p-3.5 font-medium text-white">{c.claimant_name}</td>
                    <td className="p-3.5 text-slate-300">{c.claim_type}</td>
                    <td className="p-3.5 font-mono font-semibold text-slate-100">
                      ₹{c.claimed_amount?.toLocaleString()}
                    </td>
                    <td className="p-3.5">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        isHighFraud 
                          ? 'bg-red-500/10 text-red-400 border border-red-500/20' 
                          : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      }`}>
                        {c.fraud_score ? `${c.fraud_score}/100` : '0/100'}
                      </span>
                    </td>
                    <td className="p-3.5">
                      <span className={`px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                        c.status === 'AUTO_APPROVED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
                        c.status === 'FLAGGED_INVESTIGATION' ? 'bg-red-500/10 text-red-400 border border-red-500/30' :
                        c.status === 'MANUAL_REVIEW' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' :
                        'bg-blue-500/10 text-blue-400 border border-blue-500/30'
                      }`}>
                        {c.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="p-3.5 text-right space-x-2" onClick={(e) => e.stopPropagation()}>
                      {c.status === 'SUBMITTED' && (
                        <button
                          onClick={() => onAnalyzeClaim(c.id)}
                          className="bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-medium px-3 py-1.5 rounded-lg shadow-sm transition-all inline-flex items-center space-x-1"
                        >
                          <Sparkles className="w-3 h-3" />
                          <span>Run Triage</span>
                        </button>
                      )}
                      <button
                        onClick={() => onSelectClaim(c.id)}
                        className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-medium px-3 py-1.5 rounded-lg border border-slate-700 transition-all inline-flex items-center space-x-1"
                      >
                        <span>Workbench</span>
                        <ChevronRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                );
              })}
              {claims.length === 0 && !loading && (
                <tr>
                  <td colSpan={8} className="p-8 text-center text-slate-500 italic">
                    No claims found matching current filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
