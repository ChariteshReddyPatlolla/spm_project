import React, { useState } from 'react';
import {
  FileText,
  Sparkles,
  RefreshCw,
  ExternalLink,
  BookOpen,
  Target,
  AlertCircle,
  Cpu,
  Database,
  BarChart2,
  Award,
  Compass
} from 'lucide-react';
import { useResearch } from '../context/ResearchContext';
import { api } from '../services/api';
import { CitationBadge } from '../components/CitationBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const PaperSummaries = () => {
  const { documents, selectedDocIds } = useResearch();

  const [selectedDocId, setSelectedDocId] = useState(
    selectedDocIds[0] || (documents[0] ? documents[0].id : '')
  );
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFetchSummary = async (regenerate = false) => {
    if (!selectedDocId) return;
    setLoading(true);
    setError('');

    try {
      const res = await api.getSummary(selectedDocId, regenerate);
      setSummary(res.data);
    } catch (err) {
      console.error('Failed to generate summary:', err);
      setError(err.response?.data?.detail || 'Failed to generate paper summary.');
    } finally {
      setLoading(false);
    }
  };

  const sections = [
    { title: 'Research Objective', content: summary?.research_objective, icon: Target, color: 'text-brand-400' },
    { title: 'Problem Statement', content: summary?.problem_statement, icon: AlertCircle, color: 'text-amber-400' },
    { title: 'Methodology', content: summary?.methodology, icon: BookOpen, color: 'text-indigo-400' },
    { title: 'Proposed Architecture', content: summary?.proposed_architecture, icon: Cpu, color: 'text-blue-400' },
    { title: 'Algorithms and Models', content: summary?.algorithms_and_models, icon: Sparkles, color: 'text-purple-400' },
    { title: 'Datasets', content: summary?.datasets, icon: Database, color: 'text-cyan-400' },
    { title: 'Evaluation Metrics', content: summary?.evaluation_metrics, icon: BarChart2, color: 'text-emerald-400' },
    { title: 'Experimental Results', content: summary?.experimental_results, icon: Award, color: 'text-yellow-400' },
    { title: 'Main Contributions', content: summary?.main_contributions, icon: Sparkles, color: 'text-brand-300' },
    { title: 'Limitations', content: summary?.limitations, icon: AlertCircle, color: 'text-rose-400' },
    { title: 'Future Research Directions', content: summary?.future_research_directions, icon: Compass, color: 'text-teal-400' },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight">Structured Paper Summaries</h2>
          <p className="text-xs text-slate-400">
            Automated 11-dimension extraction grounded with page-specific citations. Results are cached in SQLite.
          </p>
        </div>

        {/* Paper Selector & Actions */}
        <div className="flex items-center gap-3">
          <select
            value={selectedDocId}
            onChange={(e) => {
              setSelectedDocId(e.target.value);
              setSummary(null);
            }}
            className="px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-brand-500 max-w-xs"
          >
            {documents.length === 0 ? (
              <option value="">No papers uploaded</option>
            ) : (
              documents.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.title}
                </option>
              ))
            )}
          </select>

          <button
            onClick={() => handleFetchSummary(false)}
            disabled={!selectedDocId || loading}
            className="px-4 py-2 bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white font-medium text-xs rounded-lg transition-colors shadow-md shadow-brand-500/20 flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Generate / View</span>
          </button>

          {summary && (
            <button
              onClick={() => handleFetchSummary(true)}
              disabled={loading}
              className="p-2 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition-colors border border-slate-700"
              title="Regenerate summary"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-500/40 text-rose-300 text-xs">
          {error}
        </div>
      )}

      {loading && (
        <div className="p-16 text-center bg-slate-900/60 border border-slate-800 rounded-2xl">
          <LoadingSpinner label="Extracting 11 structural dimensions and page citations from paper..." />
        </div>
      )}

      {!summary && !loading && (
        <div className="text-center py-20 text-slate-500 text-sm max-w-md mx-auto space-y-3">
          <div className="w-12 h-12 rounded-2xl bg-slate-800 text-slate-400 flex items-center justify-center mx-auto border border-slate-700">
            <FileText className="w-6 h-6" />
          </div>
          <p>Select a research paper from above to view or generate its structured 11-dimension summary.</p>
        </div>
      )}

      {/* Structured Summary Output */}
      {summary && !loading && (
        <div className="space-y-6">
          {/* Header Card */}
          <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 border border-slate-800 shadow-xl space-y-2">
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30">
              Cached Summary
            </span>
            <h3 className="text-xl font-bold text-white leading-snug">{summary.title}</h3>
            {summary.authors && (
              <p className="text-xs text-slate-400">Authors: {summary.authors}</p>
            )}
          </div>

          {/* 11 Section Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {sections.map((sec, idx) => {
              const Icon = sec.icon;
              return (
                <div
                  key={idx}
                  className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-2 flex flex-col justify-between"
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                      <Icon className={`w-4 h-4 ${sec.color} shrink-0`} />
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                        {sec.title}
                      </h4>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-wrap font-sans">
                      {sec.content || 'Not explicitly detailed in document sections.'}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Citations Strip */}
          {summary.citations?.length > 0 && (
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-wrap items-center gap-2">
              <span className="text-xs font-semibold uppercase text-slate-400 mr-2">
                Page Citations:
              </span>
              {summary.citations.map((c, i) => (
                <CitationBadge key={i} citation={c} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

