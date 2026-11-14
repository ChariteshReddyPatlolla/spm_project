import React, { useState } from 'react';
import {
  GitCompare,
  Sparkles,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Layers,
  ArrowRight
} from 'lucide-react';
import { useResearch } from '../context/ResearchContext';
import { api } from '../services/api';
import { ComparisonTable } from '../components/ComparisonTable';
import { CitationBadge } from '../components/CitationBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const ComparativeAnalysis = () => {
  const { documents, selectedDocIds, toggleDocSelection } = useResearch();

  const [loading, setLoading] = useState(false);
  const [comparisonData, setComparisonData] = useState(null);
  const [error, setError] = useState('');

  const handleRunComparison = async () => {
    if (selectedDocIds.length < 1) {
      setError('Please select at least 1 (preferably 2 or more) papers to compare.');
      return;
    }
    setError('');
    setLoading(true);
    setComparisonData(null);

    try {
      const res = await api.runComparison({
        document_ids: selectedDocIds,
      });
      setComparisonData(res.data);
    } catch (err) {
      console.error('Comparative analysis failed:', err);
      setError(err.response?.data?.detail || 'Failed to generate comparative analysis.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight">Multi-Paper Comparative Analysis</h2>
          <p className="text-xs text-slate-400">
            Cross-evaluate objectives, architectures, datasets, experimental metrics, and identify open research gaps.
          </p>
        </div>
        <button
          onClick={handleRunComparison}
          disabled={loading || selectedDocIds.length < 1}
          className="px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium text-sm transition-colors shadow-lg shadow-indigo-500/20 flex items-center gap-2"
        >
          <GitCompare className="w-4 h-4" />
          <span>Compare Selected Papers ({selectedDocIds.length})</span>
        </button>
      </div>

      {/* Paper Selection Picker Strip */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <Layers className="w-4 h-4 text-indigo-400" /> Papers Selected for Comparison:
        </span>
        <div className="flex flex-wrap gap-2">
          {documents.map((doc) => {
            const isSelected = selectedDocIds.includes(doc.id);
            return (
              <button
                key={doc.id}
                onClick={() => toggleDocSelection(doc.id)}
                className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-all border ${
                  isSelected
                    ? 'bg-indigo-600/20 border-indigo-500/50 text-indigo-300'
                    : 'bg-slate-800/40 border-slate-700/60 text-slate-400 hover:bg-slate-800'
                }`}
              >
                {isSelected ? '✓ ' : '+ '}
                {doc.title}
              </button>
            );
          })}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-500/40 text-rose-300 text-xs">
          {error}
        </div>
      )}

      {loading && (
        <div className="p-12 text-center bg-slate-900/60 border border-slate-800 rounded-2xl">
          <LoadingSpinner label="Extracting comparative dimensions across papers and verifying experimental results..." />
        </div>
      )}

      {/* Results View */}
      {comparisonData && !loading && (
        <div className="space-y-8">
          {/* 1. Structured Comparison Table */}
          <div className="space-y-3">
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                1
              </span>
              Structured Comparison Matrix (9 Dimensions)
            </h3>
            <ComparisonTable comparisonData={comparisonData} />
          </div>

          {/* 2. Detailed Synthesis & Research Gaps */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Detailed Analysis */}
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
              <h4 className="text-sm font-bold uppercase tracking-wider text-indigo-300 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-indigo-400" /> Detailed Comparative Synthesis
              </h4>
              <div className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap font-sans">
                {comparisonData.detailed_analysis}
              </div>
            </div>

            {/* Research Gaps Across Papers */}
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
              <h4 className="text-sm font-bold uppercase tracking-wider text-amber-300 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" /> Cross-Paper Research Gaps
              </h4>
              <p className="text-sm text-slate-300 leading-relaxed font-sans">
                {comparisonData.research_gaps}
              </p>
            </div>
          </div>

          {/* 3. Advantages & Disadvantages Grid */}
          <div className="space-y-3">
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                2
              </span>
              Architectural Trade-offs & Critical Profiles
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {comparisonData.advantages_disadvantages.map((ad, idx) => (
                <div key={idx} className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4">
                  <h4 className="text-sm font-bold text-slate-100 border-b border-slate-800 pb-2">
                    {ad.paper_title}
                  </h4>
                  <div className="space-y-2">
                    <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                      <CheckCircle className="w-3.5 h-3.5" /> Advantages
                    </span>
                    <ul className="space-y-1.5 text-xs text-slate-300">
                      {ad.advantages.map((a, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-emerald-400 font-bold">•</span>
                          <span>{a}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="space-y-2 pt-2 border-t border-slate-800/60">
                    <span className="text-xs font-semibold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
                      <XCircle className="w-3.5 h-3.5" /> Disadvantages & Constraints
                    </span>
                    <ul className="space-y-1.5 text-xs text-slate-300">
                      {ad.disadvantages.map((d, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-rose-400 font-bold">•</span>
                          <span>{d}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Citations Strip */}
          {comparisonData.citations?.length > 0 && (
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-wrap items-center gap-2">
              <span className="text-xs font-semibold uppercase text-slate-400 mr-2">
                Ground-Truth Citations:
              </span>
              {comparisonData.citations.map((c, i) => (
                <CitationBadge key={i} citation={c} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

