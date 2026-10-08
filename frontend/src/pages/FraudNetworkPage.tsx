import React, { useState, useEffect } from 'react';
import { Network, AlertOctagon, ShieldAlert, ArrowRight, Share2, Layers } from 'lucide-react';
import { apiClient } from '../api/client';

export const FraudNetworkPage: React.FC = () => {
  const [overview, setOverview] = useState<any>(null);
  const [graphData, setGraphData] = useState<any>(null);
  const [selectedClaimId, setSelectedClaimId] = useState<string>('CLM-2026-1002');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadFraudData() {
      setLoading(true);
      try {
        const [ovRes, grRes] = await Promise.all([
          apiClient.get('/fraud/overview'),
          apiClient.get(`/fraud/network-graph/${selectedClaimId}`)
        ]);
        setOverview(ovRes);
        setGraphData(grRes);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadFraudData();
  }, [selectedClaimId]);

  return (
    <div className="space-y-6">
      
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2.5">
            <Network className="w-6 h-6 text-amber-400" />
            <span>Fraud Entity Graph & Syndicate Detection</span>
          </h1>
          <p className="text-sm text-slate-400">
            Multi-hop relational cluster analysis between Claimants, Vehicles, Repair Shops, and Bank Accounts.
          </p>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <span className="text-xs text-slate-400 block mb-1">Total Claims Scanned</span>
          <span className="text-2xl font-bold text-white font-mono">{overview?.total_claims_scanned || 24}</span>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <span className="text-xs text-slate-400 block mb-1">High-Risk Fraud Flags</span>
          <span className="text-2xl font-bold text-red-400 font-mono">{overview?.high_risk_claims || 4}</span>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <span className="text-xs text-slate-400 block mb-1">Portfolio Fraud Exposure</span>
          <span className="text-2xl font-bold text-amber-400 font-mono">{overview?.fraud_rate_pct || 12.5}%</span>
        </div>
      </div>

      {/* Interactive Entity Graph Visualizer */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <Share2 className="w-4 h-4 text-blue-400" />
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">
              Entity Relationship Topology for {selectedClaimId}
            </h2>
          </div>
          <span className="text-xs text-slate-400">Nodes: {graphData?.nodes?.length || 0} • Edges: {graphData?.edges?.length || 0}</span>
        </div>

        {/* Graph Canvas representation */}
        <div className="min-h-[300px] bg-slate-950 rounded-xl border border-slate-800 p-6 flex flex-wrap items-center justify-around gap-6 relative overflow-hidden">
          {graphData?.nodes?.map((node: any) => (
            <div
              key={node.id}
              className="p-4 rounded-2xl border flex flex-col items-center justify-center text-center shadow-lg transition-all hover:scale-105"
              style={{
                backgroundColor: `${node.color}15`,
                borderColor: node.color
              }}
            >
              <span className="w-3 h-3 rounded-full mb-2" style={{ backgroundColor: node.color }} />
              <span className="text-xs font-bold text-white">{node.label}</span>
              <span className="text-[10px] uppercase font-mono text-slate-400 mt-1">{node.type}</span>
            </div>
          ))}
        </div>

        <div className="mt-4 flex flex-wrap gap-4 text-xs text-slate-400">
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-500" />
            <span>Claim Dossier</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
            <span>Claimant</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500" />
            <span>Vehicle / Asset</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
            <span>Repair Garage</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-pink-500" />
            <span>Payout Bank Account</span>
          </div>
        </div>
      </div>

      {/* Suspicious Repair Shop Clusters Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
        <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-3 flex items-center space-x-2">
          <ShieldAlert className="w-4 h-4 text-red-400" />
          <span>High-Frequency & Inflated Repair Shop Clusters</span>
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-3">Facility Name</th>
                <th className="p-3">Associated Claims</th>
                <th className="p-3">Average Fraud Score</th>
                <th className="p-3">Cluster Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {overview?.suspicious_repair_shops?.map((shop: any, i: number) => (
                <tr key={i} className="hover:bg-slate-800/30">
                  <td className="p-3 font-semibold text-white">{shop.shop_name}</td>
                  <td className="p-3 font-mono text-slate-300">{shop.claim_count} claims</td>
                  <td className="p-3 font-mono font-bold text-red-400">{shop.avg_fraud_score}/100</td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${
                      shop.flagged 
                        ? 'bg-red-500/10 text-red-400 border border-red-500/20' 
                        : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    }`}>
                      {shop.flagged ? 'UNDER SURVEILLANCE' : 'CLEAN'}
                    </span>
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
