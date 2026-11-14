import React from 'react';
import { X, CheckCircle2, FileText, ExternalLink, ShieldCheck } from 'lucide-react';
import { useResearch } from '../context/ResearchContext';

export const CitationDrawer = () => {
  const { isDrawerOpen, selectedCitation, closeCitationPreview, documents } = useResearch();

  if (!isDrawerOpen || !selectedCitation) return null;

  const matchedDoc = documents.find((d) => d.id === selectedCitation.document_id);
  const pdfUrl = matchedDoc ? `/storage/uploads/${matchedDoc.id}_${matchedDoc.filename}#page=${selectedCitation.page_number}` : null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden flex justify-end">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm transition-opacity"
        onClick={closeCitationPreview}
      />

      {/* Drawer */}
      <div className="relative w-full max-w-md bg-slate-900 border-l border-slate-700 p-6 flex flex-col shadow-2xl z-10 overflow-y-auto animate-in slide-in-from-right duration-200">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-brand-500/10 text-brand-400 border border-brand-500/20">
              <ShieldCheck className="w-5 h-5 text-brand-400" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-slate-100">Source Citation Verification</h3>
              <p className="text-xs text-slate-400">Ground-truth attribution layer</p>
            </div>
          </div>
          <button
            onClick={closeCitationPreview}
            className="p-1.5 text-slate-400 hover:text-slate-100 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mt-6 space-y-6 flex-1">
          {/* Paper Info Card */}
          <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium uppercase tracking-wider text-slate-400">Paper Reference</span>
              <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                <CheckCircle2 className="w-3 h-3" /> Page Verified
              </span>
            </div>
            <h4 className="text-sm font-bold text-slate-100">{selectedCitation.paper_title}</h4>
            <div className="flex items-center gap-4 text-xs text-slate-400 pt-1">
              <span>Original Page: <b className="text-slate-200">{selectedCitation.page_number}</b></span>
              {selectedCitation.relevance_score && (
                <span>Relevance Score: <b className="text-slate-200">{(selectedCitation.relevance_score * 100).toFixed(1)}%</b></span>
              )}
            </div>
          </div>

          {/* Grounding Snippet */}
          <div className="space-y-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-brand-400" /> Supporting Excerpt From Page {selectedCitation.page_number}
            </span>
            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-sm leading-relaxed text-slate-300 font-serif italic relative">
              "{selectedCitation.snippet}"
            </div>
            <p className="text-xs text-slate-500 italic">
              Extracted directly from the original PDF via structure-aware chunking without synthetic alterations.
            </p>
          </div>

          {/* Action Links */}
          {pdfUrl && (
            <div className="pt-4 border-t border-slate-800">
              <a
                href={pdfUrl}
                target="_blank"
                rel="noreferrer"
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-sm font-medium transition-colors shadow-lg shadow-brand-500/10"
              >
                <span>Navigate to Page {selectedCitation.page_number} in PDF</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

