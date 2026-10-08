import React, { useState } from 'react';
import { Eye, Layers, Tag, ShieldCheck } from 'lucide-react';

interface DamageAnnotatorProps {
  originalImageUrl: string;
  annotatedImageUrl?: string;
  boxes?: Array<{
    box_2d: [number, number, number, number];
    label: string;
    score: number;
  }>;
  severity: string;
  confidence: number;
  damageTypes: string[];
}

export const DamageAnnotator: React.FC<DamageAnnotatorProps> = ({
  originalImageUrl,
  annotatedImageUrl,
  boxes = [],
  severity,
  confidence,
  damageTypes = []
}) => {
  const [showAnnotations, setShowAnnotations] = useState<boolean>(true);

  // Compute image url with fallback
  const activeUrl = showAnnotations && annotatedImageUrl ? annotatedImageUrl : originalImageUrl;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-lg">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/40">
        <div className="flex items-center space-x-2">
          <Layers className="w-4 h-4 text-blue-400" />
          <h4 className="text-sm font-semibold text-white">Computer Vision Damage Inspection</h4>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowAnnotations(!showAnnotations)}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              showAnnotations
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            <span>{showAnnotations ? 'Annotations: ON' : 'Original Photo'}</span>
          </button>
        </div>
      </div>

      {/* Image Display */}
      <div className="relative bg-slate-950 flex items-center justify-center min-h-[300px] max-h-[420px] overflow-hidden">
        <img
          src={activeUrl}
          alt="Damage Evidence"
          className="w-full h-full object-contain max-h-[420px]"
          onError={(e) => {
            // Fallback placeholder SVG if local image path fails
            (e.target as HTMLElement).style.display = 'none';
          }}
        />

        {/* Severity Badge overlay */}
        <div className="absolute top-3 left-3 flex items-center space-x-2">
          <span className={`px-2.5 py-1 rounded-md text-xs font-bold uppercase tracking-wider shadow-md ${
            severity === 'critical' ? 'bg-red-500 text-white' :
            severity === 'high' ? 'bg-amber-500 text-white' :
            severity === 'medium' ? 'bg-yellow-500 text-slate-900' :
            'bg-emerald-500 text-white'
          }`}>
            {severity} Severity
          </span>
          <span className="px-2 py-1 rounded-md text-xs font-mono bg-slate-900/90 text-slate-200 border border-slate-700 backdrop-blur-md">
            Model Conf: {Math.round(confidence * 100)}%
          </span>
        </div>
      </div>

      {/* Detected defect tags */}
      <div className="p-4 bg-slate-950/60 border-t border-slate-800">
        <div className="flex items-center justify-between text-xs mb-2">
          <span className="text-slate-400 font-medium flex items-center space-x-1.5">
            <Tag className="w-3.5 h-3.5 text-blue-400" />
            <span>Detected Structural Anomalies:</span>
          </span>
          <span className="text-slate-500 font-mono text-[11px]">{boxes.length || damageTypes.length} defects identified</span>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {damageTypes.map((type, idx) => (
            <span
              key={idx}
              className="px-2.5 py-1 rounded-lg text-xs bg-slate-800 text-slate-200 border border-slate-700 flex items-center space-x-1 font-medium"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-red-400" />
              <span>{type.replace('_', ' ')}</span>
            </span>
          ))}
          {damageTypes.length === 0 && (
            <span className="text-xs text-slate-500 italic">No defects identified.</span>
          )}
        </div>
      </div>
    </div>
  );
};
