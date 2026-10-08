import React, { useState, useEffect } from 'react';
import { BookOpen, Search, ShieldCheck, CheckCircle2, ChevronRight, Sparkles } from 'lucide-react';
import { apiClient } from '../api/client';

export const KnowledgePage: React.FC = () => {
  const [docs, setDocs] = useState<any[]>([]);
  const [testQuery, setTestQuery] = useState('');
  const [testResults, setTestResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadKnowledge() {
      try {
        const res = await apiClient.get('/knowledge');
        setDocs(res);
      } catch (err) {
        console.error(err);
      }
    }
    loadKnowledge();
  }, []);

  const handleTestQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!testQuery.trim()) return;
    setLoading(true);
    try {
      const res = await apiClient.post('/knowledge/query', { query: testQuery, top_k: 2 });
      setTestResults(res.results);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Title */}
      <div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2.5">
          <BookOpen className="w-6 h-6 text-blue-400" />
          <span>Policy RAG Knowledge Base & Clause Repository</span>
        </h1>
        <p className="text-sm text-slate-400">
          Indexed underwriting guidelines, deductibles, exclusion clauses, and SOP reference documents.
        </p>
      </div>

      {/* Semantic Retrieval Test Sandbox */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-blue-400" />
          <span>Semantic Vector Clause Matcher</span>
        </h2>

        <form onSubmit={handleTestQuery} className="flex gap-2">
          <input
            type="text"
            value={testQuery}
            onChange={(e) => setTestQuery(e.target.value)}
            placeholder="E.g. What is the deductible for front collision damage to bumper?"
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs px-5 py-2.5 rounded-xl transition-all disabled:opacity-50"
          >
            {loading ? 'Retrieving...' : 'Query RAG'}
          </button>
        </form>

        {testResults.length > 0 && (
          <div className="space-y-3 pt-2">
            <span className="text-xs text-slate-400 font-semibold block">Top Retrieved Matches:</span>
            {testResults.map((r, i) => (
              <div key={i} className="p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs space-y-2">
                <div className="flex justify-between font-bold text-white">
                  <span>{r.page_or_section}</span>
                  <span className="text-blue-400 font-mono">Confidence: {Math.round(r.confidence * 100)}%</span>
                </div>
                <p className="text-slate-300 italic">"{r.clause_text}"</p>
                <div className="flex gap-4 text-[11px] text-slate-400 font-mono">
                  <span>Source: {r.source_document}</span>
                  <span>Compulsory Deductible: ₹{r.deductible}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Indexed Document Library */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {docs.map((d) => (
          <div key={d.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-3 text-xs">
            <div className="flex justify-between items-start">
              <div>
                <span className="font-mono text-[10px] text-blue-400 block">{d.id}</span>
                <h3 className="font-bold text-white text-sm">{d.title}</h3>
                <span className="text-slate-400 text-[11px]">{d.section}</span>
              </div>
              <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${
                d.coverage_applicable ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
              }`}>
                {d.coverage_applicable ? 'COVERED' : 'EXCLUSION'}
              </span>
            </div>

            <p className="text-slate-300 leading-relaxed bg-slate-950 p-3 rounded-xl border border-slate-800">
              {d.content_preview}
            </p>

            <div className="flex justify-between text-slate-400 font-mono text-[11px] pt-1">
              <span>Doc: {d.source_document}</span>
              <span>Deductible: ₹{d.deductible}</span>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
};
