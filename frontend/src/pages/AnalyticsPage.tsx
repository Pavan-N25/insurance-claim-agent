import React, { useState, useEffect } from 'react';
import { BarChart3, MapPin, TrendingUp, DollarSign, CheckCircle2, UserCheck } from 'lucide-react';
import { apiClient } from '../api/client';

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAnalytics() {
      try {
        const res = await apiClient.get('/analytics/dashboard');
        setData(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
      </div>
    );
  }

  const kpis = data?.kpis || {};
  const heatmap = data?.geographic_risk_heatmap || [];
  const trends = data?.monthly_trend || [];

  return (
    <div className="space-y-6">
      
      {/* Title */}
      <div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2.5">
          <BarChart3 className="w-6 h-6 text-blue-400" />
          <span>Portfolio Analytics & AI Risk Heatmap</span>
        </h1>
        <p className="text-sm text-slate-400">
          Executive performance metrics, underwriting loss ratios, and regional claims exposure.
        </p>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <span className="text-xs text-slate-400 block mb-1">Human Override Rate</span>
          <span className="text-2xl font-bold text-white font-mono">{kpis.human_override_rate_pct}%</span>
          <span className="text-[11px] text-slate-500 mt-1 block">Low model discrepancy</span>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <span className="text-xs text-slate-400 block mb-1">Model Calibration Confidence</span>
          <span className="text-2xl font-bold text-blue-400 font-mono">{kpis.ai_confidence_pct}%</span>
          <span className="text-[11px] text-slate-500 mt-1 block">Across all active agents</span>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <span className="text-xs text-slate-400 block mb-1">Straight-Through Processing</span>
          <span className="text-2xl font-bold text-emerald-400 font-mono">{kpis.approval_rate_pct}%</span>
          <span className="text-[11px] text-slate-500 mt-1 block">Zero manual touch</span>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <span className="text-xs text-slate-400 block mb-1">Operational Cost Savings</span>
          <span className="text-2xl font-bold text-amber-400 font-mono">₹{kpis.estimated_cost_savings_inr?.toLocaleString()}</span>
          <span className="text-[11px] text-slate-500 mt-1 block">Efficiency gain</span>
        </div>
      </div>

      {/* Regional AI Risk Heatmap */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <MapPin className="w-4 h-4 text-blue-400" />
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">Geographic AI Claims & Risk Heatmap</h2>
          </div>
          <span className="text-xs text-slate-400">Metropolitan Telemetry</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {heatmap.map((loc: any, i: number) => (
            <div key={i} className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-bold text-white text-sm">{loc.city}</span>
                <span className="text-[10px] text-slate-400 font-mono">{loc.region}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Claims Vol:</span>
                <span className="font-mono text-white">{loc.claims}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Risk Score:</span>
                <span className={`font-mono font-bold ${loc.risk_score >= 60 ? 'text-red-400' : 'text-emerald-400'}`}>
                  {loc.risk_score}/100
                </span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1">
                <div 
                  className={`h-full ${loc.risk_score >= 60 ? 'bg-red-500' : 'bg-emerald-500'}`} 
                  style={{ width: `${loc.risk_score}%` }} 
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Monthly Intake & Approval Trends */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center space-x-2">
          <TrendingUp className="w-4 h-4 text-emerald-400" />
          <span>Historical Monthly Trajectory</span>
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-3">Month</th>
                <th className="p-3">Claims Submitted</th>
                <th className="p-3">Auto-Approved</th>
                <th className="p-3">Fraud Flags Intercepted</th>
                <th className="p-3">Approval %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {trends.map((t: any, i: number) => (
                <tr key={i} className="hover:bg-slate-800/30">
                  <td className="p-3 font-semibold text-white">{t.month}</td>
                  <td className="p-3 font-mono text-slate-300">{t.submitted}</td>
                  <td className="p-3 font-mono text-emerald-400">{t.approved}</td>
                  <td className="p-3 font-mono text-red-400">{t.fraud}</td>
                  <td className="p-3 font-mono text-slate-200">
                    {Math.round((t.approved / Math.max(1, t.submitted)) * 100)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
