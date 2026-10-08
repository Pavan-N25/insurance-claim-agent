import React, { useState } from 'react';
import { Bot, Send, Sparkles, BookOpen, AlertCircle, User, ArrowRight } from 'lucide-react';
import { apiClient } from '../api/client';

export const CopilotPage: React.FC = () => {
  const [claimId, setClaimId] = useState('CLM-2026-1002');
  const [inputQuery, setInputQuery] = useState('');
  const [messages, setMessages] = useState<Array<{
    sender: 'user' | 'copilot';
    text: string;
    citations?: string[];
  }>>([
    {
      sender: 'copilot',
      text: "Hello! I am your AI Claims Copilot. Ask me anything regarding claim dossiers, policy coverage rules, fraud anomalies, or recommended investigation steps.",
      citations: ["Policy Knowledge Base v4.2"]
    }
  ]);
  const [loading, setLoading] = useState(false);

  const quickPrompts = [
    "Why was this claim flagged?",
    "Summarize this claim.",
    "What documents are missing?",
    "What policy clause is relevant?",
    "Show me the fraud indicators.",
    "What should I investigate next?"
  ];

  const handleSend = async (queryToSend?: string) => {
    const query = queryToSend || inputQuery;
    if (!query.trim()) return;

    setMessages(prev => [...prev, { sender: 'user', text: query }]);
    if (!queryToSend) setInputQuery('');
    setLoading(true);

    try {
      const res = await apiClient.post('/copilot/chat', {
        claim_id: claimId,
        query: query
      });

      setMessages(prev => [
        ...prev,
        {
          sender: 'copilot',
          text: res.response,
          citations: res.grounded_citations
        }
      ]);
    } catch (err: any) {
      setMessages(prev => [
        ...prev,
        {
          sender: 'copilot',
          text: `Error connecting to Copilot engine: ${err.message}`
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-4 h-[calc(100vh-140px)] flex flex-col">
      
      {/* Top Bar */}
      <div className="bg-slate-900 border border-slate-800 p-4 rounded-2xl flex items-center justify-between shrink-0 shadow-lg">
        <div className="flex items-center space-x-2.5">
          <div className="bg-purple-600/20 text-purple-400 p-2 rounded-xl border border-purple-500/30">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-white uppercase tracking-wider">AI Claims Copilot Workspace</h1>
            <p className="text-[11px] text-slate-400">Contextual RAG Assistant for Claims Adjusters</p>
          </div>
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <span className="text-slate-400 font-medium">Target Dossier:</span>
          <select
            value={claimId}
            onChange={(e) => setClaimId(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-xl px-2.5 py-1.5 text-blue-400 font-mono font-semibold focus:outline-none"
          >
            <option value="CLM-2026-1001">CLM-2026-1001 (Priya Sharma)</option>
            <option value="CLM-2026-1002">CLM-2026-1002 (Amit Verma)</option>
            <option value="CLM-2026-1003">CLM-2026-1003 (Rajesh Nair)</option>
          </select>
        </div>
      </div>

      {/* Chat Messages Body */}
      <div className="flex-1 bg-slate-900 border border-slate-800 rounded-2xl p-5 overflow-y-auto space-y-4 shadow-xl">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex space-x-3 text-xs ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {m.sender === 'copilot' && (
              <div className="w-7 h-7 rounded-xl bg-purple-600/20 border border-purple-500/30 text-purple-400 flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4" />
              </div>
            )}

            <div
              className={`p-4 rounded-2xl max-w-xl ${
                m.sender === 'user'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-slate-950 border border-slate-800 text-slate-200'
              }`}
            >
              <p className="whitespace-pre-wrap leading-relaxed">{m.text}</p>

              {m.citations && m.citations.length > 0 && (
                <div className="mt-3 pt-2 border-t border-slate-800/80 flex items-center space-x-2 text-[10px] text-purple-400 font-mono">
                  <BookOpen className="w-3 h-3" />
                  <span>Grounding: {m.citations.join(', ')}</span>
                </div>
              )}
            </div>

            {m.sender === 'user' && (
              <div className="w-7 h-7 rounded-xl bg-blue-600 text-white flex items-center justify-center shrink-0">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center space-x-2 text-xs text-purple-400 italic">
            <Bot className="w-4 h-4 animate-spin" />
            <span>Copilot is inspecting policy clauses and claim state...</span>
          </div>
        )}
      </div>

      {/* Quick Prompts */}
      <div className="flex flex-wrap gap-1.5 shrink-0">
        {quickPrompts.map((q, i) => (
          <button
            key={i}
            onClick={() => handleSend(q)}
            className="text-[11px] px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-all hover:text-white"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex items-center space-x-2 shrink-0 bg-slate-900 border border-slate-800 p-2 rounded-2xl"
      >
        <input
          type="text"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          placeholder={`Ask anything about claim ${claimId}...`}
          className="flex-1 bg-transparent px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading || !inputQuery.trim()}
          className="p-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white transition-all disabled:opacity-40"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>

    </div>
  );
};
