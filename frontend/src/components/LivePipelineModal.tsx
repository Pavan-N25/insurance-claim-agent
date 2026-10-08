import React from 'react';
import { CheckCircle2, Loader2, Sparkles, AlertCircle } from 'lucide-react';

interface LivePipelineModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentStep: string;
  progress: number;
  message: string;
  claimId: string;
}

const PIPELINE_STEPS = [
  { id: 'INTAKE', label: '1. Ingestion & Modality Normalization', agent: 'Intake Agent' },
  { id: 'DOCUMENT_AI', label: '2. OCR & Document Table Extraction', agent: 'Document Intelligence Agent' },
  { id: 'UNDERSTANDING', label: '3. Claim State Normalization', agent: 'Claim Understanding Agent' },
  { id: 'ANALYSIS', label: '4. Computer Vision & Policy RAG Check', agent: 'CV & Policy RAG Agents' },
  { id: 'FRAUD_ANALYSIS', label: '5. Image Hashing & Network Graph Scan', agent: 'Fraud Detection Agent' },
  { id: 'SEVERITY', label: '6. Damage Severity & Priority Scoring', agent: 'Severity Agent' },
  { id: 'ESTIMATION', label: '7. Repair Valuation & Deductibles Range', agent: 'Estimation Agent' },
  { id: 'DECISION', label: '8. Safety Guardrails & Adjudication Rules', agent: 'Decision Engine' },
  { id: 'EXPLAINABILITY', label: '9. Transparent Decision Rationale', agent: 'Explainability Agent' },
  { id: 'COMPLETED', label: '10. Customer Notification & Review Dispatch', agent: 'Communication Agent' },
];

export const LivePipelineModal: React.FC<LivePipelineModalProps> = ({
  isOpen,
  onClose,
  currentStep,
  progress,
  message,
  claimId
}) => {
  if (!isOpen) return null;

  const getStepIndex = (stepId: string) => {
    const idx = PIPELINE_STEPS.findIndex(s => s.id === stepId);
    return idx === -1 ? 0 : idx;
  };

  const currentIdx = getStepIndex(currentStep);
  const isDone = progress >= 100 || currentStep === 'COMPLETED';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl relative overflow-hidden">
        
        {/* Glow accent */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500" />

        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-blue-400 animate-pulse" />
            <h3 className="text-lg font-bold text-white">Multi-Agent Triage Pipeline</h3>
          </div>
          <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-300">
            {claimId}
          </span>
        </div>

        {/* Progress bar */}
        <div className="mb-6">
          <div className="flex justify-between text-xs mb-1.5 font-medium">
            <span className="text-slate-400">Pipeline Execution Progress</span>
            <span className="text-blue-400 font-bold">{progress}%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-blue-500 to-indigo-500 h-2 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-slate-300 mt-2 italic flex items-center space-x-1.5">
            <span className="inline-block w-2 h-2 rounded-full bg-blue-400 animate-ping mr-1"></span>
            {message}
          </p>
        </div>

        {/* Steps List */}
        <div className="space-y-2.5 max-h-80 overflow-y-auto pr-1">
          {PIPELINE_STEPS.map((step, index) => {
            const isCompleted = isDone || index < currentIdx;
            const isCurrent = !isDone && index === currentIdx;

            return (
              <div 
                key={step.id} 
                className={`flex items-center justify-between p-2.5 rounded-xl border text-xs transition-all ${
                  isCurrent 
                    ? 'bg-blue-600/10 border-blue-500/40 text-blue-300 font-semibold shadow-sm'
                    : isCompleted
                    ? 'bg-slate-950/60 border-slate-800/80 text-slate-300'
                    : 'bg-slate-950/20 border-slate-900 text-slate-500'
                }`}
              >
                <div className="flex items-center space-x-2.5">
                  {isCompleted ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  ) : isCurrent ? (
                    <Loader2 className="w-4 h-4 text-blue-400 animate-spin shrink-0" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border border-slate-700 shrink-0" />
                  )}
                  <span>{step.label}</span>
                </div>
                <span className="text-[11px] font-mono text-slate-400">
                  {step.agent}
                </span>
              </div>
            );
          })}
        </div>

        {isDone && (
          <div className="mt-6 pt-4 border-t border-slate-800 flex justify-end">
            <button
              onClick={onClose}
              className="bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs px-5 py-2.5 rounded-xl shadow-lg transition-all"
            >
              View Triage Results
            </button>
          </div>
        )}

      </div>
    </div>
  );
};
