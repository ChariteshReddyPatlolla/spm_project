import React from 'react';
import { Layers, Sparkles, HardDrive, Cpu, RefreshCw } from 'lucide-react';
import { useResearch } from '../context/ResearchContext';

export const Navbar = () => {
  const { systemStatus, documents, activeSession, refreshStatus } = useResearch();

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/90 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-40">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-brand-500/20 text-white font-bold">
          <Layers className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-bold text-slate-100 tracking-tight">Antigravity Research Assistant</h1>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30">
              Agentic RAG
            </span>
          </div>
          <p className="text-xs text-slate-400">Multi-Paper Synthesis & Verified Page Citations</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* LLM Engine Status Pill */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/80 text-xs">
          <Cpu className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-slate-400">LLM:</span>
          <span className="text-slate-200 font-medium">
            {systemStatus?.llm_model || systemStatus?.gemini_model || systemStatus?.ollama_model || 'Gemini 1.5 Flash'}
          </span>
          <span
            className={`w-2 h-2 rounded-full ${
              (systemStatus?.llm_connected || systemStatus?.gemini_connected || systemStatus?.ollama_connected)
                ? 'bg-emerald-500 shadow-sm shadow-emerald-500/50'
                : 'bg-amber-500'
            }`}
            title={
              (systemStatus?.llm_connected || systemStatus?.gemini_connected)
                ? (systemStatus?.llm_provider === 'gemini' ? 'Gemini API Online (Google Cloud)' : 'LLM Online')
                : systemStatus?.ollama_connected
                ? 'Ollama Online'
                : 'Local Synthesis Active'
            }
          />
        </div>

        {/* ChromaDB Status */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/80 text-xs">
          <HardDrive className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-slate-400">Corpus:</span>
          <span className="text-brand-300 font-bold">{documents.length}</span>
          <span className="text-slate-500">papers</span>
        </div>

        <button
          onClick={refreshStatus}
          className="p-2 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition-colors"
          title="Refresh system status"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};

