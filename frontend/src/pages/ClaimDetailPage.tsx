import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, Sparkles, ShieldAlert, CheckCircle, AlertOctagon, 
  Clock, DollarSign, FileText, User, MapPin, Calendar, Layers, 
  Download, Sliders, ChevronDown, ChevronUp, Bot, ExternalLink,
  AlertTriangle, RefreshCw
} from 'lucide-react';
import { apiClient } from '../api/client';
import { ClaimDetailResponse } from '../types';
import { DamageAnnotator } from '../components/DamageAnnotator';

interface ClaimDetailPageProps {
  claimId: string;
  onBack: () => void;
  onAnalyzeClaim: (claimId: string) => void;
}

export const ClaimDetailPage: React.FC<ClaimDetailPageProps> = ({ 
  claimId, 
  onBack,
  onAnalyzeClaim
}) => {
  const [data, setData] = useState<ClaimDetailResponse | null>(null);
  const [timeline, setTimeline] = useState<any>(null);
  const [similarClaims, setSimilarClaims] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Review & Override State
  const [humanDecision, setHumanDecision] = useState<string>('APPROVED');
  const [overrideReason, setOverrideReason] = useState<string>('');
  const [reviewerNotes, setReviewerNotes] = useState<string>('');
  const [submittingReview, setSubmittingReview] = useState<boolean>(false);
  const [reviewSuccess, setReviewSuccess] = useState<string | null>(null);

  // What-If Simulator State
  const [showSimulator, setShowSimulator] = useState<boolean>(false);
  const [simAmount, setSimAmount] = useState<number>(50000);
  const [simFraudScore, setSimFraudScore] = useState<number>(20);
  const [simConfidence, setSimConfidence] = useState<number>(0.85);
  const [simResult, setSimResult] = useState<any>(null);

  const fetchClaimDetails = async () => {
    setLoading(true);
    try {
      const [claimRes, timelineRes, similarRes] = await Promise.all([
        apiClient.get(`/claims/${claimId}`),
        apiClient.get(`/claims/${claimId}/timeline`),
        apiClient.get(`/claims/${claimId}/similar`)
      ]);
      setData(claimRes);
      setTimeline(timelineRes);
      setSimilarClaims(similarRes);
      setSimAmount(claimRes.claim.claimed_amount || 50000);
      setSimFraudScore(claimRes.claim.fraud_score || 20);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClaimDetails();
  }, [claimId]);

  const handleSimulate = async () => {
    try {
      const res = await apiClient.post('/simulator/evaluate', {
        claimed_amount: simAmount,
        damage_severity: data?.damage_assessments[0]?.severity || 'MEDIUM',
        fraud_score: simFraudScore,
        policy_limit: 500000.0,
        deductible: 5000.0,
        confidence: simConfidence
      });
      setSimResult(res);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!data) return;
    setSubmittingReview(true);
    try {
      await apiClient.post(`/claims/${claimId}/review`, {
        human_decision: humanDecision,
        override_reason: overrideReason,
        reviewer_notes: reviewerNotes
      });
      setReviewSuccess('Review decision logged and audit trail updated successfully!');
      fetchClaimDetails();
    } catch (err: any) {
      alert(`Error submitting review: ${err.message}`);
    } finally {
      setSubmittingReview(false);
    }
  };

  const handleDownloadReport = () => {
    window.open(`/api/v1/claims/${claimId}/report`, '_blank');
  };

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
      </div>
    );
  }

  const { claim, documents, damage_assessments, fraud_signals, ai_decisions, human_reviews, audit_logs } = data;
  const primaryDamage = damage_assessments[0];
  const primaryDecision = ai_decisions[0];

  return (
    <div className="space-y-6">
      
      {/* Top Bar Navigation & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <button
          onClick={onBack}
          className="flex items-center space-x-2 text-xs font-semibold text-slate-400 hover:text-white transition-all w-fit"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Claims Queue</span>
        </button>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => onAnalyzeClaim(claim.id)}
            className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition-all shadow-lg shadow-indigo-600/20 flex items-center space-x-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Re-run Multi-Agent Pipeline</span>
          </button>
          <button
            onClick={handleDownloadReport}
            className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold px-4 py-2.5 rounded-xl border border-slate-700 transition-all flex items-center space-x-1.5"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Formal Claim Report</span>
          </button>
        </div>
      </div>

      {/* Main Claim Header Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-black text-white font-mono">{claim.id}</h1>
              <span className={`px-2.5 py-1 rounded-md text-xs font-bold uppercase tracking-wider ${
                claim.status === 'AUTO_APPROVED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
                claim.status === 'FLAGGED_INVESTIGATION' ? 'bg-red-500/10 text-red-400 border border-red-500/30' :
                claim.status === 'MANUAL_REVIEW' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' :
                'bg-blue-500/10 text-blue-400 border border-blue-500/30'
              }`}>
                {claim.status.replace('_', ' ')}
              </span>
              <span className="px-2 py-0.5 rounded-md text-[11px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                Priority: {claim.priority}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Policy: <span className="text-slate-200 font-mono">{claim.policy_number}</span> • Claimant: <span className="text-white font-semibold">{claim.claimant_name}</span>
            </p>
          </div>

          {/* Quick Metrics Bar */}
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <span className="text-[10px] text-slate-500 block uppercase font-medium">Claimed Amount</span>
              <span className="text-xl font-bold font-mono text-white">₹{claim.claimed_amount?.toLocaleString()}</span>
            </div>
            <div className="h-8 w-px bg-slate-800" />
            <div className="text-right">
              <span className="text-[10px] text-slate-500 block uppercase font-medium">Fraud Score</span>
              <span className={`text-xl font-bold font-mono ${claim.fraud_score >= 60 ? 'text-red-400' : 'text-emerald-400'}`}>
                {claim.fraud_score}/100
              </span>
            </div>
            <div className="h-8 w-px bg-slate-800" />
            <div className="text-right">
              <span className="text-[10px] text-slate-500 block uppercase font-medium">AI Confidence</span>
              <span className="text-xl font-bold font-mono text-blue-400">{Math.round(claim.ai_confidence * 100)}%</span>
            </div>
          </div>
        </div>

        {/* Customer & Incident Details */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-5 text-xs">
          <div>
            <h2 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center space-x-1">
              <User className="w-3.5 h-3.5 text-blue-400" />
              <span>Customer Information</span>
            </h2>
            <div className="space-y-1 text-slate-300">
              <p><span className="text-slate-500">Name:</span> {claim.claimant_name}</p>
              <p><span className="text-slate-500">Contact:</span> {claim.claimant_email || 'customer@insurance.ai'}</p>
              <p><span className="text-slate-500">Asset / Plate:</span> <span className="font-mono text-white">{claim.asset_identifier || 'KA-01-MJ-9921'}</span></p>
            </div>
          </div>

          <div>
            <h2 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center space-x-1">
              <MapPin className="w-3.5 h-3.5 text-blue-400" />
              <span>Incident Metadata</span>
            </h2>
            <div className="space-y-1 text-slate-300">
              <p><span className="text-slate-500">Date/Time:</span> {claim.incident_date}</p>
              <p><span className="text-slate-500">Location:</span> {claim.incident_location}</p>
              <p><span className="text-slate-500">Designated Facility:</span> {claim.repair_shop_name || 'Authorized Network'}</p>
            </div>
          </div>

          <div>
            <h2 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center space-x-1">
              <FileText className="w-3.5 h-3.5 text-blue-400" />
              <span>Incident Description</span>
            </h2>
            <p className="text-slate-300 leading-relaxed italic bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80">
              "{claim.incident_description}"
            </p>
          </div>
        </div>
      </div>

      {/* Grid: Evidence & Computer Vision vs Policy & Fraud Signals */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Left Column: Visual Damage Inspection */}
        <div className="space-y-6">
          <DamageAnnotator
            originalImageUrl={documents[0]?.file_path?.replace('backend/', '/') || '/uploads/CLM-2026-1001_damage.jpg'}
            annotatedImageUrl={primaryDamage?.annotated_image_path?.replace('backend/', '/') || '/uploads/CLM-2026-1001_damage_annotated.jpg'}
            boxes={primaryDamage?.bounding_boxes || []}
            severity={primaryDamage?.severity || 'medium'}
            confidence={primaryDamage?.confidence || 0.9}
            damageTypes={primaryDamage?.damage_types || ['impact_dent']}
          />

          {/* Submitted Documents & Multimodal Evidence List */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
            <h2 className="text-sm font-bold text-white mb-3 flex items-center space-x-2">
              <FileText className="w-4 h-4 text-blue-400" />
              <span>Submitted Multimodal Dossier ({documents.length} files)</span>
            </h2>

            <div className="space-y-2">
              {documents.map((doc) => (
                <div key={doc.id} className="p-3 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between text-xs">
                  <div>
                    <span className="font-medium text-white block">{doc.file_name}</span>
                    <span className="text-[10px] text-slate-400 uppercase font-mono">{doc.doc_category.replace('_', ' ')} • {(doc.file_size / 1024).toFixed(1)} KB</span>
                  </div>
                  {doc.perceptual_hash && (
                    <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                      dHash: {doc.perceptual_hash.slice(0, 10)}...
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: AI Analysis, Policy RAG, Fraud Signals, and Decisions */}
        <div className="space-y-6">
          
          {/* AI Decision & Plain-English Explainability */}
          <div className="bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950/40 border border-indigo-900/40 rounded-2xl p-5 shadow-xl">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Bot className="w-5 h-5 text-indigo-400" />
                <h2 className="text-sm font-bold text-white uppercase tracking-wider">AI Recommendation & Explainability</h2>
              </div>
              <span className="text-xs font-mono font-bold text-indigo-300">
                {primaryDecision?.recommendation || claim.status}
              </span>
            </div>

            <div className="p-3.5 bg-slate-950/80 rounded-xl border border-slate-800 text-xs mb-3">
              <span className="font-bold text-indigo-300 block mb-1">Decision Rationale:</span>
              <p className="text-slate-200 leading-relaxed">
                {primaryDecision?.reasoning_summary || "Automated multi-agent triage completed. All primary evidence evaluated against corporate guidelines."}
              </p>
            </div>

            <div className="p-3.5 bg-slate-950/80 rounded-xl border border-slate-800 text-xs">
              <span className="font-bold text-emerald-400 block mb-1">Recommended Adjuster Action:</span>
              <p className="text-slate-300">
                {primaryDecision?.recommended_action || "Verify physical invoice line items and authorize straight-through payout."}
              </p>
            </div>
          </div>

          {/* Fraud & Anomaly Signals Panel */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <ShieldAlert className="w-4 h-4 text-red-400" />
                <h2 className="text-sm font-bold text-white uppercase tracking-wider">Fraud & Anomaly Telemetry</h2>
              </div>
              <span className={`text-xs font-bold font-mono px-2 py-0.5 rounded-full ${
                claim.fraud_score >= 60 ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'
              }`}>
                Score: {claim.fraud_score}/100 ({claim.fraud_risk_level})
              </span>
            </div>

            <div className="space-y-2">
              {fraud_signals.map((sig) => (
                <div key={sig.id} className="p-3 rounded-xl bg-red-950/20 border border-red-900/40 text-xs">
                  <div className="flex justify-between font-semibold text-red-400 mb-1">
                    <span>{sig.signal}</span>
                    <span className="uppercase text-[10px] tracking-wider px-1.5 py-0.5 rounded bg-red-900/40">
                      {sig.severity}
                    </span>
                  </div>
                  <span className="text-slate-400 text-[11px]">
                    Anomaly Category: {sig.category} • Confidence: {Math.round(sig.confidence * 100)}%
                  </span>
                </div>
              ))}
              {fraud_signals.length === 0 && (
                <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-900/30 text-xs text-emerald-300 flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                  <span>Zero duplicate image hashes or network anomaly clusters detected.</span>
                </div>
              )}
            </div>
          </div>

          {/* Repair Estimation Range */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <DollarSign className="w-4 h-4 text-amber-400" />
                <h2 className="text-sm font-bold text-white uppercase tracking-wider">Independent Repair Payout Valuation</h2>
              </div>
              <span className="text-xs text-slate-400">Benchmark Model</span>
            </div>

            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-400">Estimated Reimbursable Range:</span>
                <span className="font-mono font-bold text-white">
                  ₹{claim.estimated_min?.toLocaleString() || '42,000'} — ₹{claim.estimated_max?.toLocaleString() || '54,000'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Applied Compulsory Deductible:</span>
                <span className="font-mono text-slate-300">₹5,000</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Standard Parts Depreciation:</span>
                <span className="font-mono text-slate-300">10% Metal / 50% Plastic</span>
              </div>
            </div>
          </div>

        </div>

      </div>

      {/* Reconstructed Timeline & Similar Historical Claims */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Chronological Timeline */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
          <div className="flex items-center space-x-2 mb-4">
            <Clock className="w-4 h-4 text-blue-400" />
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">Reconstructed Claim Lifecycle Timeline</h2>
          </div>

          <div className="relative border-l border-slate-800 ml-3 space-y-4 text-xs">
            {timeline?.events?.map((ev: any, idx: number) => (
              <div key={idx} className="relative pl-5">
                <div className="absolute -left-1.5 top-1 w-3 h-3 rounded-full bg-blue-500 border-2 border-slate-950" />
                <div className="font-semibold text-white">{ev.title}</div>
                <div className="text-[11px] text-slate-400 font-mono">{ev.timestamp?.slice(0, 16)}</div>
                <p className="text-slate-300 mt-0.5">{ev.description}</p>
              </div>
            ))}
          </div>

          {timeline?.anomalies?.length > 0 && (
            <div className="mt-4 p-3 rounded-xl bg-red-950/30 border border-red-900/40 text-xs text-red-300">
              <span className="font-bold block">Temporal Inconsistency Detected:</span>
              {timeline.anomalies.map((a: any, i: number) => (
                <p key={i} className="mt-0.5">• {a.issue}</p>
              ))}
            </div>
          )}
        </div>

        {/* Similar Historical Claims */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
          <div className="flex items-center space-x-2 mb-4">
            <FileText className="w-4 h-4 text-purple-400" />
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">Semantic Similar Claims Precedents</h2>
          </div>

          <div className="space-y-2.5">
            {similarClaims.map((s, idx) => (
              <div key={idx} className="p-3 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between text-xs">
                <div>
                  <span className="font-bold text-blue-400 font-mono block">{s.claim_id}</span>
                  <span className="text-slate-300">{s.claimant} • {s.claim_type}</span>
                </div>
                <div className="text-right">
                  <span className="text-white font-mono block">₹{s.claimed_amount?.toLocaleString()}</span>
                  <span className="text-emerald-400 font-medium">{Math.round(s.similarity * 100)}% match</span>
                </div>
              </div>
            ))}
            {similarClaims.length === 0 && (
              <p className="text-slate-500 text-xs italic">No prior matches recorded.</p>
            )}
          </div>
        </div>

      </div>

      {/* Decision Simulator (What-If Analysis) Collapsible Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
        <div 
          className="flex items-center justify-between cursor-pointer"
          onClick={() => setShowSimulator(!showSimulator)}
        >
          <div className="flex items-center space-x-2">
            <Sliders className="w-4 h-4 text-blue-400" />
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">AI Decision Simulator & What-If Sandbox</h2>
          </div>
          {showSimulator ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
        </div>

        {showSimulator && (
          <div className="mt-4 pt-4 border-t border-slate-800 space-y-4 text-xs">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-slate-400 block mb-1 font-medium">Claim Amount: ₹{simAmount.toLocaleString()}</label>
                <input 
                  type="range" min="10000" max="300000" step="5000"
                  value={simAmount}
                  onChange={(e) => setSimAmount(Number(e.target.value))}
                  className="w-full"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1 font-medium">Fraud Score: {simFraudScore}/100</label>
                <input 
                  type="range" min="0" max="100" step="5"
                  value={simFraudScore}
                  onChange={(e) => setSimFraudScore(Number(e.target.value))}
                  className="w-full"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1 font-medium">Model Confidence: {Math.round(simConfidence * 100)}%</label>
                <input 
                  type="range" min="0.4" max="1.0" step="0.05"
                  value={simConfidence}
                  onChange={(e) => setSimConfidence(Number(e.target.value))}
                  className="w-full"
                />
              </div>
            </div>

            <button
              onClick={handleSimulate}
              className="bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs px-4 py-2 rounded-xl transition-all"
            >
              Run Scenario Simulation
            </button>

            {simResult && (
              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs">
                <div className="flex justify-between font-semibold mb-1">
                  <span className="text-slate-300">Simulated Recommendation:</span>
                  <span className="text-blue-400 font-bold">{simResult.simulated_recommendation}</span>
                </div>
                <div className="text-slate-400">
                  Priority Score: {simResult.simulated_priority_score}/100
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Human Review & Adjuster Sign-Off Panel */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl">
        <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-2 flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 text-emerald-400" />
          <span>Human Adjuster Adjudication & Sign-Off</span>
        </h2>
        <p className="text-xs text-slate-400 mb-4">
          Senior adjuster review mandatory. When overriding AI triage recommendations, an audit justification is strictly enforced.
        </p>

        {reviewSuccess && (
          <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-900 text-xs text-emerald-300 mb-4 font-medium">
            {reviewSuccess}
          </div>
        )}

        <form onSubmit={handleSubmitReview} className="space-y-4 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-slate-300 block mb-1 font-medium">Adjudication Action</label>
              <select
                value={humanDecision}
                onChange={(e) => setHumanDecision(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none"
              >
                <option value="APPROVED">Approve Claim & Payout</option>
                <option value="REJECTED">Reject Claim</option>
                <option value="REQUEST_INFO">Request Additional Documentation</option>
                <option value="ESCALATED_INVESTIGATION">Escalate to Special Investigation Unit (SIU)</option>
              </select>
            </div>

            <div>
              <label className="text-slate-300 block mb-1 font-medium">Override Justification Reason</label>
              <input
                type="text"
                value={overrideReason}
                onChange={(e) => setOverrideReason(e.target.value)}
                placeholder="Required if changing AI recommendation..."
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white placeholder-slate-600 focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="text-slate-300 block mb-1 font-medium">Adjuster Notes & Audit Commentary</label>
            <textarea
              rows={3}
              value={reviewerNotes}
              onChange={(e) => setReviewerNotes(e.target.value)}
              placeholder="Enter technical notes regarding physical inspection, OEM repair scope, or customer call notes..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-white placeholder-slate-600 focus:outline-none"
            />
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={submittingReview}
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs px-6 py-2.5 rounded-xl shadow-lg transition-all disabled:opacity-50"
            >
              {submittingReview ? 'Submitting Review...' : 'Commit Review Decision'}
            </button>
          </div>
        </form>
      </div>

    </div>
  );
};
