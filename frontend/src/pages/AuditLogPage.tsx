import React, { useState, useEffect } from 'react';
import { History, ShieldCheck, User, Bot, Clock } from 'lucide-react';
import { apiClient } from '../api/client';

export const AuditLogPage: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAuditLogs() {
      try {
        const claims = await apiClient.get('/claims?limit=10');
        const allLogs: any[] = [];
        for (const c of claims) {
          const detail = await apiClient.get(`/claims/${c.id}`);
          if (detail.audit_logs) {
            allLogs.push(...detail.audit_logs);
          }
        }
        allLogs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
        setLogs(allLogs);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadAuditLogs();
  }, []);

  return (
    <div className="space-y-6">
      
      {/* Title */}
      <div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2.5">
          <History className="w-6 h-6 text-blue-400" />
          <span>Immutable Audit & Compliance Trail</span>
        </h1>
        <p className="text-sm text-slate-400">
          Cryptographically auditable record of AI agent decisions, OCR events, and human reviewer overrides.
        </p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-3.5">Timestamp</th>
                <th className="p-3.5">Event Type</th>
                <th className="p-3.5">Claim ID</th>
                <th className="p-3.5">Actor</th>
                <th className="p-3.5">Event Telemetry Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/30">
                  <td className="p-3.5 font-mono text-slate-400">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="p-3.5 font-semibold text-white">
                    <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[11px]">
                      {log.event_type}
                    </span>
                  </td>
                  <td className="p-3.5 font-mono text-blue-400 font-bold">{log.claim_id}</td>
                  <td className="p-3.5 text-slate-300 flex items-center space-x-1.5">
                    {log.actor.includes('AI') ? (
                      <Bot className="w-3.5 h-3.5 text-purple-400" />
                    ) : (
                      <User className="w-3.5 h-3.5 text-emerald-400" />
                    )}
                    <span>{log.actor}</span>
                  </td>
                  <td className="p-3.5 text-slate-400 font-mono text-[11px] truncate max-w-md">
                    {JSON.stringify(log.details)}
                  </td>
                </tr>
              ))}
              {logs.length === 0 && !loading && (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-slate-500 italic">
                    No audit records registered yet.
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
