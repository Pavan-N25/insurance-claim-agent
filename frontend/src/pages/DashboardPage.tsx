import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, ShieldCheck, Clock, TrendingUp, CheckCircle, 
  ArrowUpRight, AlertOctagon, ChevronRight, Activity, DollarSign 
} from 'lucide-react';
import { apiClient } from '../api/client';
import { Claim } from '../types';

interface DashboardPageProps {
  onSelectClaim: (claimId: string) => void;
  onNavigateTab: (tab: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onSelectClaim, onNavigateTab }) => {
  const [analytics, setAnalytics] = useState<any>(null);
  const [recentClaims, setRecentClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [dashRes, claimsRes] = await Promise.all([
          apiClient.get('/analytics/dashboard'),
          apiClient.get('/claims?limit=6')
        ]);
        setAnalytics(dashRes);
        setRecentClaims(claimsRes);
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
      </div>
    );
  }

  const kpis = analytics?.kpis || {
    total_claims: 24,
    claims_today: 6,
    approval_rate_pct: 68.4,
    manual_review_rate_pct: 21.0,
    fraud_detection_rate_pct: 10.6,
    average_processing_time: '3.2 minutes',
    estimated_cost_savings_inr: 412500,
    ai_confidence_pct: 89.2
  };

  return (
    <div className="space-y-6">
      
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-slate-900 to-slate-800 p-6 rounded-2xl border border-slate-800 shadow-xl">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2.5">
            <span>Enterprise Triage Operations</span>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
              Live Pipeline Active
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time multi-agent triage, fraud anomaly signals, and adjuster escalation workbench.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => onNavigateTab('portal')}
            className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition-all shadow-lg shadow-emerald-600/20 flex items-center space-x-1.5"
          >
            <span>Submit New Claim</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => onNavigateTab('claims')}
            className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition-all shadow-lg shadow-blue-600/20 flex items-center space-x-1.5"
          >
            <span>View Full Queue</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Total Claims */}
        <div className="bg-slate-900/90 border border-slate-800 p-5 rounded-2xl shadow-lg relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Total Claims Processed</span>
            <Activity className="w-4 h-4 text-blue-400" />
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-bold text-white">{kpis.total_claims}</span>
            <span className="text-xs text-emerald-400 font-medium">+{kpis.claims_today} today</span>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Avg speed: <span className="text-slate-300 font-mono">{kpis.average_processing_time}</span>
          </div>
        </div>

        {/* Auto Approval Rate */}
        <div className="bg-slate-900/90 border border-slate-800 p-5 rounded-2xl shadow-lg relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Straight-Through Rate</span>
            <CheckCircle className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-bold text-emerald-400">{kpis.approval_rate_pct}%</span>
            <span className="text-xs text-slate-400">auto-approved</span>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Model confidence: <span className="text-slate-300 font-mono">{kpis.ai_confidence_pct}%</span>
          </div>
        </div>

        {/* Fraud Anomaly Rate */}
        <div className="bg-slate-900/90 border border-slate-800 p-5 rounded-2xl shadow-lg relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Fraud & Anomaly Rate</span>
            <AlertOctagon className="w-4 h-4 text-red-400" />
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-bold text-red-400">{kpis.fraud_detection_rate_pct}%</span>
            <span className="text-xs text-red-400/80 font-medium">flagged SIU</span>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Includes duplicate hash & network rings
          </div>
        </div>

        {/* Operational Cost Savings */}
        <div className="bg-slate-900/90 border border-slate-800 p-5 rounded-2xl shadow-lg relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Operational Savings</span>
            <DollarSign className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-amber-400 font-mono">₹{kpis.estimated_cost_savings_inr.toLocaleString()}</span>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            vs. 48hr manual adjuster triage
          </div>
        </div>

      </div>

      {/* Priority Claim Queue & Action Center */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Urgent Claims Queue */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-blue-400" />
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">Active Triage Queue</h2>
            </div>
            <span className="text-xs text-slate-400">Sorted by Priority & Urgency</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                <tr>
                  <th className="p-3">Claim ID</th>
                  <th className="p-3">Claimant</th>
                  <th className="p-3">Type</th>
                  <th className="p-3">Amount</th>
                  <th className="p-3">Fraud Risk</th>
                  <th className="p-3">Status</th>
                  <th className="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {recentClaims.map((c) => {
                  const isFraud = c.fraud_score >= 60;
                  const isCritical = c.priority === 'CRITICAL';

                  return (
                    <tr 
                      key={c.id} 
                      className="hover:bg-slate-800/40 transition-colors cursor-pointer group"
                      onClick={() => onSelectClaim(c.id)}
                    >
                      <td className="p-3 font-mono font-bold text-blue-400 group-hover:underline">
                        {c.id}
                      </td>
                      <td className="p-3 font-medium text-white">{c.claimant_name}</td>
                      <td className="p-3 text-slate-300">{c.claim_type}</td>
                      <td className="p-3 font-mono text-slate-200">₹{c.claimed_amount?.toLocaleString()}</td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          isFraud 
                            ? 'bg-red-500/10 text-red-400 border border-red-500/20' 
                            : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        }`}>
                          {c.fraud_score ? `${c.fraud_score}/100` : 'Scan Clean'}
                        </span>
                      </td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded-md text-[10px] font-semibold uppercase ${
                          c.status === 'AUTO_APPROVED' ? 'bg-emerald-600/20 text-emerald-300' :
                          c.status === 'FLAGGED_INVESTIGATION' ? 'bg-red-600/20 text-red-300' :
                          c.status === 'MANUAL_REVIEW' ? 'bg-amber-600/20 text-amber-300' :
                          'bg-blue-600/20 text-blue-300'
                        }`}>
                          {c.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="p-3 text-right">
                        <span className="text-blue-400 group-hover:text-blue-300 font-semibold inline-flex items-center space-x-1">
                          <span>Inspect</span>
                          <ChevronRight className="w-3.5 h-3.5" />
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Column: SLA Alerts & Quick Assist */}
        <div className="space-y-4">
          
          {/* SLA Alerts Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
            <div className="flex items-center space-x-2 mb-3">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">SLA Escalation Alerts</h3>
            </div>
            
            <div className="space-y-2.5">
              <div className="p-3 rounded-xl bg-red-950/30 border border-red-900/40 text-xs">
                <div className="flex justify-between font-semibold text-red-400">
                  <span>CLM-2026-1002 (Amit Verma)</span>
                  <span className="font-mono">1.2h remaining</span>
                </div>
                <p className="text-slate-400 mt-1">
                  Critical Fraud Signal flagged (Duplicate Image). Auto-escalation to SIU Manager in 48 mins.
                </p>
              </div>

              <div className="p-3 rounded-xl bg-amber-950/30 border border-amber-900/40 text-xs">
                <div className="flex justify-between font-semibold text-amber-400">
                  <span>CLM-2026-1003 (Rajesh Nair)</span>
                  <span className="font-mono">4.5h remaining</span>
                </div>
                <p className="text-slate-400 mt-1">
                  Property water damage pending contractor scope confirmation.
                </p>
              </div>
            </div>
          </div>

          {/* AI Copilot Quick Assist Card */}
          <div className="bg-gradient-to-br from-purple-950/40 via-slate-900 to-slate-900 border border-purple-900/40 rounded-2xl p-5 shadow-xl">
            <h3 className="text-sm font-bold text-purple-300 uppercase tracking-wider mb-2">Adjuster AI Copilot</h3>
            <p className="text-xs text-slate-300 mb-4">
              Ask natural language questions grounded in current claim files and corporate policy guidelines.
            </p>
            <button
              onClick={() => onNavigateTab('copilot')}
              className="w-full bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold py-2.5 rounded-xl transition-all shadow-lg shadow-purple-600/20"
            >
              Launch Copilot Workspace
            </button>
          </div>

        </div>

      </div>

    </div>
  );
};
