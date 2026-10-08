import React, { useState, useEffect } from 'react';
import { Settings, Save, ShieldAlert, Cpu, Clock, CheckCircle } from 'lucide-react';
import { apiClient } from '../api/client';

export const AdminSettingsPage: React.FC = () => {
  const [fraudThreshold, setFraudThreshold] = useState(65);
  const [highValueCeiling, setHighValueCeiling] = useState(100000);
  const [minConfidence, setMinConfidence] = useState(0.85);
  const [slaCritical, setSlaCritical] = useState(2);
  const [slaHigh, setSlaHigh] = useState(6);
  const [slaNormal, setSlaNormal] = useState(24);
  const [llmProvider, setLlmProvider] = useState('local');
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    async function loadConfigs() {
      try {
        const res = await apiClient.get('/admin/configs');
        setFraudThreshold(res.fraud_flag_threshold);
        setHighValueCeiling(res.high_value_threshold_inr);
        setMinConfidence(res.min_confidence_auto_approve);
        setSlaCritical(res.sla_critical_hours);
        setSlaHigh(res.sla_high_hours);
        setSlaNormal(res.sla_normal_hours);
        setLlmProvider(res.llm_provider);
      } catch (err) {
        console.error(err);
      }
    }
    loadConfigs();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.put('/admin/configs', {
        fraud_flag_threshold: Number(fraudThreshold),
        high_value_threshold_inr: Number(highValueCeiling),
        min_confidence_auto_approve: Number(minConfidence),
        sla_critical_hours: Number(slaCritical),
        sla_high_hours: Number(slaHigh),
        sla_normal_hours: Number(slaNormal),
        llm_provider: llmProvider
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      alert(`Save failed: ${err.message}`);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      
      {/* Title */}
      <div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2.5">
          <Settings className="w-6 h-6 text-blue-400" />
          <span>System Triage & Governance Settings</span>
        </h1>
        <p className="text-sm text-slate-400">
          Configure business rules, model routing, fraud thresholds, and SLA escalation policies.
        </p>
      </div>

      {saveSuccess && (
        <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-900 text-emerald-300 text-xs font-semibold flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 text-emerald-400" />
          <span>Governance thresholds updated across all active multi-agent pipelines!</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6 text-xs">
        
        {/* Fraud & Guardrails */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
            <ShieldAlert className="w-4 h-4 text-red-400" />
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">Fraud Risk & Adjudication Guardrails</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-slate-300 block mb-1 font-medium">Fraud Escalation Threshold (0-100)</label>
              <input
                type="number"
                value={fraudThreshold}
                onChange={(e) => setFraudThreshold(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white font-mono focus:outline-none"
              />
              <span className="text-[10px] text-slate-500 mt-1 block">Claims &ge; this score trigger SIU flag</span>
            </div>

            <div>
              <label className="text-slate-300 block mb-1 font-medium">High-Value Ceilings (₹ INR)</label>
              <input
                type="number"
                value={highValueCeiling}
                onChange={(e) => setHighValueCeiling(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white font-mono focus:outline-none"
              />
              <span className="text-[10px] text-slate-500 mt-1 block">Requires manual senior review</span>
            </div>

            <div>
              <label className="text-slate-300 block mb-1 font-medium">Min Auto-Approval Confidence</label>
              <input
                type="number"
                step="0.05"
                value={minConfidence}
                onChange={(e) => setMinConfidence(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white font-mono focus:outline-none"
              />
              <span className="text-[10px] text-slate-500 mt-1 block">Currently {Math.round(minConfidence * 100)}%</span>
            </div>
          </div>
        </div>

        {/* SLA Escalation Rules */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
            <Clock className="w-4 h-4 text-amber-400" />
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">Service Level Agreements (SLA)</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-slate-300 block mb-1 font-medium">Critical Priority SLA (Hours)</label>
              <input
                type="number"
                value={slaCritical}
                onChange={(e) => setSlaCritical(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white font-mono focus:outline-none"
              />
            </div>
            <div>
              <label className="text-slate-300 block mb-1 font-medium">High Priority SLA (Hours)</label>
              <input
                type="number"
                value={slaHigh}
                onChange={(e) => setSlaHigh(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white font-mono focus:outline-none"
              />
            </div>
            <div>
              <label className="text-slate-300 block mb-1 font-medium">Normal Priority SLA (Hours)</label>
              <input
                type="number"
                value={slaNormal}
                onChange={(e) => setSlaNormal(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white font-mono focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* LLM Provider Routing */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
            <Cpu className="w-4 h-4 text-purple-400" />
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">LLM Engine & Model Routing</h2>
          </div>

          <div>
            <label className="text-slate-300 block mb-1 font-medium">Active Intelligence Engine</label>
            <select
              value={llmProvider}
              onChange={(e) => setLlmProvider(e.target.value)}
              className="w-full sm:w-80 bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white font-medium focus:outline-none cursor-pointer"
            >
              <option value="local">Local Intelligent Deterministic Engine (Offline)</option>
              <option value="gemini">Google Gemini 2.5 Flash / Pro</option>
              <option value="openai">OpenAI GPT-4o / GPT-4o-mini</option>
              <option value="anthropic">Anthropic Claude 3.5 Sonnet</option>
            </select>
            <p className="text-[10px] text-slate-500 mt-2">
              The platform gracefully auto-falls back to the Local Intelligent Engine when cloud API keys are not supplied.
            </p>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            className="bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs px-6 py-3 rounded-xl shadow-lg transition-all flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>Save Configuration Settings</span>
          </button>
        </div>

      </form>

    </div>
  );
};
