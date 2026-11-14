import React from 'react';
import { CitationBadge } from './CitationBadge';
import { useResearch } from '../context/ResearchContext';

export const ComparisonTable = ({ comparisonData }) => {
  const { openCitationPreview } = useResearch();

  if (!comparisonData || !comparisonData.comparison_table) {
    return null;
  }

  const { paper_titles, comparison_table, citations } = comparisonData;
  const paperKeys = Object.keys(paper_titles || {});

  // Helper to extract citation from cell text
  const renderCellWithCitations = (text) => {
    if (!text) return <span className="text-slate-500 italic">Not reported</span>;
    if (text.includes('Not explicitly reported') || text.includes('Not reported')) {
      return <span className="text-amber-400/80 italic text-xs">{text}</span>;
    }

    // Match [Paper Title, Page X]
    const parts = text.split(/(\[[^\]]+,\s*(?:Page|p\.)\s*\d+\])/g);
    return (
      <div className="space-y-1">
        <span>
          {parts.map((part, i) => {
            const match = part.match(/\[([^,\]]+),\s*(?:Page|p\.)\s*(\d+)\]/);
            if (match) {
              const matchedCit = citations?.find(
                (c) => c.page_number === parseInt(match[2])
              ) || {
                paper_title: match[1].trim(),
                page_number: parseInt(match[2]),
                is_validated: true,
                snippet: text,
              };
              return <CitationBadge key={i} citation={matchedCit} />;
            }
            return <span key={i}>{part}</span>;
          })}
        </span>
      </div>
    );
  };

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60 shadow-xl">
      <table className="w-full text-left text-xs border-collapse">
        <thead>
          <tr className="bg-slate-800/90 border-b border-slate-700 text-slate-200">
            <th className="p-3.5 font-bold uppercase tracking-wider w-48 text-brand-300">
              Comparison Aspect
            </th>
            {paperKeys.map((id) => (
              <th key={id} className="p-3.5 font-bold text-slate-100 min-w-[260px] max-w-[340px]">
                {paper_titles[id]}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800">
          {comparison_table.map((row, idx) => (
            <tr
              key={idx}
              className={`hover:bg-slate-800/40 transition-colors ${
                idx % 2 === 0 ? 'bg-slate-900/30' : 'bg-slate-900/70'
              }`}
            >
              <td className="p-3.5 font-semibold text-slate-300 bg-slate-850/40 border-r border-slate-800 align-top">
                {row.aspect}
              </td>
              {paperKeys.map((id) => {
                const title = paper_titles[id];
                const cellText = row.values[title] || row.values[id] || 'Not reported';
                return (
                  <td key={id} className="p-3.5 text-slate-300 align-top leading-relaxed border-r border-slate-800/60 last:border-r-0">
                    {renderCellWithCitations(cellText)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

