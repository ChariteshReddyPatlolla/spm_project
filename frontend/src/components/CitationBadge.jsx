import React from 'react';
import { BookOpen, CheckCircle } from 'lucide-react';
import { useResearch } from '../context/ResearchContext';

export const CitationBadge = ({ citation, compact = false }) => {
  const { openCitationPreview } = useResearch();

  if (!citation) return null;

  return (
    <button
      onClick={() => openCitationPreview(citation)}
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 my-0.5 rounded-md text-xs font-medium transition-colors cursor-pointer border ${
        citation.is_validated
          ? 'bg-brand-950/70 border-brand-500/40 text-brand-300 hover:bg-brand-900/80 hover:border-brand-400'
          : 'bg-amber-950/50 border-amber-600/40 text-amber-300 hover:bg-amber-900/60'
      }`}
      title={`Verified Source: ${citation.paper_title}, Page ${citation.page_number}. Click to view supporting excerpt.`}
    >
      <BookOpen className="w-3 h-3 text-brand-400 shrink-0" />
      <span className="truncate max-w-[140px]">{citation.paper_title}</span>
      <span className="font-semibold text-brand-200">p.{citation.page_number}</span>
      {citation.is_validated && <CheckCircle className="w-3 h-3 text-emerald-400 shrink-0" />}
    </button>
  );
};

