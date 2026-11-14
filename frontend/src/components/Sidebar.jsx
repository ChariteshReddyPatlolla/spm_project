import React from 'react';
import {
  LayoutDashboard,
  Files,
  MessageSquareText,
  GitCompare,
  FileText,
  PlusCircle,
  Trash2,
  CheckSquare,
  Square
} from 'lucide-react';
import { useResearch } from '../context/ResearchContext';

export const Sidebar = () => {
  const {
    activeTab,
    setActiveTab,
    documents,
    selectedDocIds,
    toggleDocSelection,
    selectAllDocs,
    deselectAllDocs,
    sessions,
    activeSession,
    switchSession,
    createNewSession,
    deleteSession
  } = useResearch();

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'library', label: 'Document Library', icon: Files, badge: documents.length },
    { id: 'chat', label: 'Research Chat', icon: MessageSquareText },
    { id: 'comparative', label: 'Comparative Analysis', icon: GitCompare },
    { id: 'summaries', label: 'Paper Summaries', icon: FileText },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-900/95 flex flex-col shrink-0 h-[calc(100vh-4rem)] select-none">
      {/* Navigation tabs */}
      <div className="p-3 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-brand-600 text-white shadow-md shadow-brand-500/20'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-slate-100'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && (
                <span
                  className={`text-xs px-2 py-0.5 rounded-full ${
                    isActive ? 'bg-white/20 text-white' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Active Paper Scope Selector */}
      <div className="p-3 border-t border-slate-800/80 flex flex-col flex-1 min-h-0">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Active Papers ({selectedDocIds.length}/{documents.length})
          </span>
          <div className="flex items-center gap-1 text-[11px] text-brand-400">
            <button onClick={selectAllDocs} className="hover:underline">All</button>
            <span>/</span>
            <button onClick={deselectAllDocs} className="hover:underline">Clear</button>
          </div>
        </div>

        <div className="overflow-y-auto space-y-1 pr-1 flex-1 min-h-[100px]">
          {documents.length === 0 ? (
            <div className="text-center py-6 text-xs text-slate-500">
              No papers uploaded yet
            </div>
          ) : (
            documents.map((doc) => {
              const isSelected = selectedDocIds.includes(doc.id);
              return (
                <div
                  key={doc.id}
                  onClick={() => toggleDocSelection(doc.id)}
                  className={`flex items-start gap-2 p-2 rounded-lg text-xs cursor-pointer border transition-colors ${
                    isSelected
                      ? 'bg-brand-950/40 border-brand-500/30 text-slate-200'
                      : 'bg-slate-800/40 border-transparent text-slate-400 hover:bg-slate-800'
                  }`}
                >
                  <div className="mt-0.5 text-brand-400">
                    {isSelected ? <CheckSquare className="w-3.5 h-3.5" /> : <Square className="w-3.5 h-3.5 text-slate-500" />}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium text-slate-200" title={doc.title}>{doc.title}</p>
                    <p className="text-[10px] text-slate-500">{doc.page_count} pages</p>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Research Sessions */}
      <div className="p-3 border-t border-slate-800/80">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Sessions</span>
          <button
            onClick={() => createNewSession()}
            className="flex items-center gap-1 text-xs text-brand-400 hover:text-brand-300 font-medium"
          >
            <PlusCircle className="w-3.5 h-3.5" /> New
          </button>
        </div>

        <div className="max-h-36 overflow-y-auto space-y-1 pr-1">
          {sessions.map((s) => {
            const isCurrent = activeSession?.id === s.id;
            return (
              <div
                key={s.id}
                className={`group flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs cursor-pointer ${
                  isCurrent ? 'bg-slate-800 text-brand-300 font-medium' : 'text-slate-400 hover:bg-slate-800/60'
                }`}
                onClick={() => switchSession(s.id)}
              >
                <span className="truncate max-w-[170px]" title={s.title}>{s.title}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteSession(s.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-rose-400 p-0.5"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </aside>
  );
};

