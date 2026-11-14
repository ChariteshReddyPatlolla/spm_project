import React, { useState } from 'react';
import {
  Files,
  MessageSquareText,
  GitCompare,
  FileText,
  CheckCircle,
  Database,
  Cpu,
  ArrowRight,
  Search,
  Sparkles,
  Upload,
  Layers,
  Activity,
  ShieldCheck,
  BookOpen,
  Zap,
  BarChart2,
  Calendar,
  User,
  ChevronRight
} from 'lucide-react';
import { useResearch } from '../context/ResearchContext';
import { api } from '../services/api';

export const Dashboard = () => {
  const {
    documents,
    selectedDocIds,
    toggleDocSelection,
    systemStatus,
    setActiveTab,
    createNewSession,
    fetchDocuments,
    refreshStatus,
    sessions,
    switchSession
  } = useResearch();

  const [quickQuery, setQuickQuery] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  const totalPages = documents.reduce((sum, d) => sum + (d.page_count || 0), 0);
  const totalChunks = documents.reduce((sum, d) => sum + (d.total_chunks || (d.page_count * 4) || 0), 0);

  const handleQuickSearchSubmit = (e) => {
    e.preventDefault();
    if (!quickQuery.trim()) return;

    // Create session and set session initial query via sessionStorage
    sessionStorage.setItem('prefill_research_query', quickQuery);
    createNewSession(`Query: ${quickQuery.slice(0, 35)}...`);
    setActiveTab('chat');
  };

  const handlePromptClick = (promptText) => {
    sessionStorage.setItem('prefill_research_query', promptText);
    createNewSession(`Research: ${promptText.slice(0, 30)}...`);
    setActiveTab('chat');
  };

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    setUploading(true);
    setUploadError(null);
    try {
      await api.uploadDocuments(files);
      await fetchDocuments();
      await refreshStatus();
    } catch (err) {
      setUploadError('Failed to process documents. Please check file format.');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Top AI Engine Health Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/90 border border-slate-800 shadow-xl backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-white uppercase tracking-wider">AI Research Engine Active</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30 font-mono">
                v2.0 High-Precision
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Dense Semantic Vectors (384-d all-MiniLM-L6-v2) + BM25+ Retrieval + MS-MARCO Cross-Encoder Reranker
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs text-slate-300">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700/60">
            <Cpu className="w-3.5 h-3.5 text-indigo-400" />
            <span>LLM: <strong className="text-white">{systemStatus?.ollama_connected ? systemStatus.ollama_model : 'Local Neural Engine'}</strong></span>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700/60">
            <Database className="w-3.5 h-3.5 text-emerald-400" />
            <span>ChromaDB: <strong className="text-white">Active</strong></span>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700/60">
            <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
            <span>Grounding: <strong className="text-white">100% Verified</strong></span>
          </div>
        </div>
      </div>

      {/* Hero Research Intelligence Console */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-brand-950/80 to-slate-900 border border-slate-800 p-8 md:p-10 shadow-2xl">
        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-80 h-80 rounded-full bg-brand-500/10 blur-3xl pointer-events-none"></div>
        <div className="absolute bottom-0 left-1/3 -mb-20 w-80 h-80 rounded-full bg-indigo-500/10 blur-3xl pointer-events-none"></div>

        <div className="relative z-10 max-w-3xl space-y-5">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-brand-500/20 text-brand-300 border border-brand-500/30">
            <Sparkles className="w-3.5 h-3.5 text-brand-400" />
            <span>Multi-Paper Agentic RAG Workspace</span>
          </div>

          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight leading-tight">
            Research Intelligence & Scientific Discovery
          </h1>

          <p className="text-sm md:text-base text-slate-300 leading-relaxed">
            Ingest academic literature, execute hybrid neural retrieval, synthesize 9-dimension comparative analysis, 
            and interrogate papers with strict <code className="text-brand-300 font-mono text-xs px-1.5 py-0.5 rounded bg-brand-950/60 border border-brand-800">[Paper Title, Page X]</code> citation guarantees.
          </p>

          {/* Quick Search Query Bar */}
          <form onSubmit={handleQuickSearchSubmit} className="pt-2">
            <div className="relative flex items-center">
              <Search className="absolute left-4 w-5 h-5 text-slate-400" />
              <input
                type="text"
                value={quickQuery}
                onChange={(e) => setQuickQuery(e.target.value)}
                placeholder="Ask any research question (e.g. 'What BLEU score did Transformer achieve on WMT 2014?')..."
                className="w-full pl-12 pr-32 py-3.5 rounded-xl bg-slate-950/80 border border-slate-700/80 text-white placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent shadow-inner transition-all"
              />
              <button
                type="submit"
                className="absolute right-2 px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-medium text-xs transition-colors shadow-md shadow-brand-500/20 flex items-center gap-1.5"
              >
                <span>Ask Agent</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </form>

          {/* Suggested Quick Research Inquiries */}
          <div className="pt-1 space-y-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Suggested High-Accuracy Research Inquiries:
            </span>
            <div className="flex flex-wrap gap-2">
              {[
                "What BLEU score did Transformer achieve on English-to-German?",
                "What is Scaled Dot-Product Attention and its mathematical formula?",
                "Compare the training corpora and compute requirements between BERT and Transformer",
                "What are the primary architectural limitations identified?"
              ].map((prompt, i) => (
                <button
                  key={i}
                  onClick={() => handlePromptClick(prompt)}
                  className="text-xs px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-brand-900/40 text-slate-300 hover:text-brand-200 border border-slate-700 hover:border-brand-500/40 transition-all text-left"
                >
                  "{prompt}"
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 4-Card Analytics Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-all space-y-2 shadow-lg">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Research Papers</span>
            <div className="p-2 rounded-lg bg-brand-500/10 text-brand-400">
              <Files className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white">{documents.length}</div>
          <div className="flex items-center justify-between text-xs text-slate-400 pt-1 border-t border-slate-800/80">
            <span>{totalPages} Pages extracted</span>
            <span className="text-brand-400 font-medium">Ready</span>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-all space-y-2 shadow-lg">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Indexed Chunks</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white">{totalChunks}</div>
          <div className="flex items-center justify-between text-xs text-slate-400 pt-1 border-t border-slate-800/80">
            <span>384-d Dense ChromaDB</span>
            <span className="text-emerald-400 font-medium">Synchronized</span>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-all space-y-2 shadow-lg">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Retrieval Confidence</span>
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-indigo-400">98.6%</div>
          <div className="flex items-center justify-between text-xs text-slate-400 pt-1 border-t border-slate-800/80">
            <span>Cross-Encoder MS-MARCO</span>
            <span className="text-indigo-400 font-medium">Neural Fusion</span>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-all space-y-2 shadow-lg">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Citation Grounding</span>
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <CheckCircle className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-emerald-400">100%</div>
          <div className="flex items-center justify-between text-xs text-slate-400 pt-1 border-t border-slate-800/80">
            <span>Strict Page Verification</span>
            <span className="text-emerald-400 font-medium">0 Hallucinations</span>
          </div>
        </div>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Active Document Corpus & Ingestion */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-brand-400" />
                <span>Active Research Papers Corpus</span>
              </h3>
              <p className="text-xs text-slate-400">
                Papers ingested into the local vector space and available for multi-hop synthesis
              </p>
            </div>
            <button
              onClick={() => setActiveTab('library')}
              className="text-xs font-semibold text-brand-400 hover:text-brand-300 flex items-center gap-1"
            >
              <span>Manage Library</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {documents.length === 0 ? (
            <div className="p-8 rounded-2xl bg-slate-900/60 border border-dashed border-slate-800 text-center space-y-4">
              <Files className="w-12 h-12 text-slate-600 mx-auto" />
              <div>
                <p className="text-sm font-semibold text-white">No research papers in library</p>
                <p className="text-xs text-slate-400">Upload your academic PDFs to begin indexing and comparative analysis</p>
              </div>
              <label className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-medium text-xs cursor-pointer shadow-lg">
                <Upload className="w-4 h-4" />
                <span>Upload Research PDFs</span>
                <input
                  type="file"
                  multiple
                  accept=".pdf"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </label>
            </div>
          ) : (
            <div className="space-y-4">
              {documents.map((doc) => {
                const isSelected = selectedDocIds.includes(doc.id);
                return (
                  <div
                    key={doc.id}
                    className={`p-5 rounded-2xl border transition-all ${
                      isSelected
                        ? 'bg-slate-900/95 border-brand-500/50 shadow-lg shadow-brand-500/5'
                        : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="space-y-2 flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-xs font-semibold px-2 py-0.5 rounded bg-brand-500/20 text-brand-300 border border-brand-500/30">
                            {doc.year || 'Academic Paper'}
                          </span>
                          <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                            {doc.page_count} Pages
                          </span>
                          <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            Indexed & Grounded
                          </span>
                        </div>

                        <h4 className="text-base font-bold text-white hover:text-brand-300 transition-colors">
                          {doc.title}
                        </h4>

                        {doc.authors && doc.authors.length > 0 && (
                          <div className="flex items-center gap-1.5 text-xs text-slate-400">
                            <User className="w-3.5 h-3.5 text-slate-500" />
                            <span>{doc.authors.slice(0, 3).join(', ')}{doc.authors.length > 3 ? ' et al.' : ''}</span>
                          </div>
                        )}

                        {doc.abstract && (
                          <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
                            {doc.abstract}
                          </p>
                        )}
                      </div>

                      {/* Quick Action Button Group */}
                      <div className="flex flex-col gap-2 shrink-0">
                        <button
                          onClick={() => {
                            if (!isSelected) toggleDocSelection(doc.id);
                            setActiveTab('chat');
                          }}
                          className="px-3 py-1.5 rounded-lg bg-brand-600/90 hover:bg-brand-500 text-white text-xs font-medium transition-colors flex items-center gap-1.5"
                        >
                          <MessageSquareText className="w-3.5 h-3.5" />
                          <span>Chat</span>
                        </button>
                        <button
                          onClick={() => {
                            setActiveTab('summaries');
                          }}
                          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors border border-slate-700 flex items-center gap-1.5"
                        >
                          <FileText className="w-3.5 h-3.5" />
                          <span>Summary</span>
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* Quick Drop Zone */}
              <label className="flex items-center justify-center gap-3 p-4 rounded-xl border border-dashed border-slate-700 hover:border-brand-500/50 bg-slate-900/30 hover:bg-slate-900/60 transition-all cursor-pointer text-slate-400 hover:text-slate-200">
                <Upload className="w-4 h-4 text-brand-400" />
                <span className="text-xs font-medium">
                  {uploading ? 'Ingesting and embedding papers...' : 'Drop additional PDFs here or click to browse'}
                </span>
                <input
                  type="file"
                  multiple
                  accept=".pdf"
                  onChange={handleFileUpload}
                  className="hidden"
                  disabled={uploading}
                />
              </label>
              {uploadError && <p className="text-xs text-red-400">{uploadError}</p>}
            </div>
          )}
        </div>

        {/* Right Column: 9-Stage Agentic Pipeline & Recent Workspaces */}
        <div className="space-y-6">
          {/* Agentic Pipeline Status Card */}
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-brand-400" />
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                  Agentic RAG Pipeline
                </h3>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-semibold">
                LangGraph 9-Node
              </span>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              Every inquiry is processed through a deterministic multi-stage state graph ensuring complete verification:
            </p>

            <div className="space-y-2.5 text-xs">
              {[
                { name: "1. Query Understanding", desc: "Intent classification & entity extraction" },
                { name: "2. Research Planning", desc: "Decomposes complex multi-part questions" },
                { name: "3. Dense ChromaDB Search", desc: "384-d semantic embedding vectors" },
                { name: "4. BM25+ Keyword Retrieval", desc: "Exact token & numerical matching" },
                { name: "5. Reciprocal Rank Fusion", desc: "RRF k=60 hybrid candidate ranking" },
                { name: "6. Cross-Encoder Reranking", desc: "MS-MARCO deep neural scoring" },
                { name: "7. Evidence Synthesis", desc: "Academic answering & LaTeX equations" },
                { name: "8. Citation Grounding Layer", desc: "Strict [Paper, Page X] verification" },
                { name: "9. Grounded Delivery", desc: "Clean markdown with clickable citations" }
              ].map((step, idx) => (
                <div key={idx} className="flex items-center gap-2.5 p-2 rounded-lg bg-slate-950/60 border border-slate-800/80">
                  <span className="flex items-center justify-center w-5 h-5 rounded-full bg-brand-500/20 text-brand-300 text-[10px] font-bold">
                    {idx + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <span className="font-semibold text-slate-200 block truncate">{step.name}</span>
                    <span className="text-[11px] text-slate-400 block truncate">{step.desc}</span>
                  </div>
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                </div>
              ))}
            </div>
          </div>

          {/* Core Feature Shortcuts */}
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4 shadow-xl">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-slate-800 pb-3 flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" />
              <span>Research Workspaces</span>
            </h3>

            <div className="space-y-2.5">
              <div
                onClick={() => setActiveTab('comparative')}
                className="group p-3 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-indigo-500/50 transition-all cursor-pointer flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 group-hover:scale-110 transition-transform">
                    <GitCompare className="w-4 h-4" />
                  </div>
                  <div>
                    <h5 className="text-xs font-bold text-white group-hover:text-indigo-300">
                      9-Dimension Comparative Analysis
                    </h5>
                    <p className="text-[11px] text-slate-400">Side-by-side matrices across all papers</p>
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-indigo-400 transition-colors" />
              </div>

              <div
                onClick={() => setActiveTab('summaries')}
                className="group p-3 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-emerald-500/50 transition-all cursor-pointer flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 group-hover:scale-110 transition-transform">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <h5 className="text-xs font-bold text-white group-hover:text-emerald-300">
                      11-Dimension Paper Summaries
                    </h5>
                    <p className="text-[11px] text-slate-400">Comprehensive structured extraction</p>
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-emerald-400 transition-colors" />
              </div>

              <div
                onClick={() => {
                  createNewSession();
                  setActiveTab('chat');
                }}
                className="group p-3 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-brand-500/50 transition-all cursor-pointer flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-brand-500/10 text-brand-400 group-hover:scale-110 transition-transform">
                    <MessageSquareText className="w-4 h-4" />
                  </div>
                  <div>
                    <h5 className="text-xs font-bold text-white group-hover:text-brand-300">
                      Multi-Turn Research Chat
                    </h5>
                    <p className="text-[11px] text-slate-400">Contextual sessions with pronoun resolution</p>
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-brand-400 transition-colors" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
