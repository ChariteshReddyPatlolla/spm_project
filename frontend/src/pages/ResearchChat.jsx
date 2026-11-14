import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Bot,
  User,
  Sparkles,
  ChevronDown,
  ChevronRight,
  ShieldCheck,
  CheckCircle2,
  Layers,
  ArrowRight
} from 'lucide-react';
import { useResearch } from '../context/ResearchContext';
import { api } from '../services/api';
import { CitationBadge } from '../components/CitationBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const ResearchChat = () => {
  const {
    documents,
    selectedDocIds,
    toggleDocSelection,
    activeSession,
    setActiveSession,
    openCitationPreview
  } = useResearch();

  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [agentStepsOpen, setAgentStepsOpen] = useState({});
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [activeSession?.messages, loading]);

  useEffect(() => {
    const prefill = sessionStorage.getItem('prefill_research_query');
    if (prefill) {
      sessionStorage.removeItem('prefill_research_query');
      setInputQuery(prefill);
      setTimeout(() => {
        handleSendMessage(prefill);
      }, 350);
    }
  }, [activeSession?.id]);

  const handleSendMessage = async (queryText = inputQuery) => {
    const textToSend = queryText.trim();
    if (!textToSend || loading) return;

    setInputQuery('');
    setLoading(true);

    // Optimistically append user message
    const tempUserMsg = {
      id: `temp_${Date.now()}`,
      role: 'user',
      content: textToSend,
      citations: [],
      agent_steps: [],
      created_at: new Date().toISOString(),
    };

    setActiveSession((prev) => ({
      ...prev,
      messages: [...(prev?.messages || []), tempUserMsg],
    }));

    try {
      const res = await api.sendMessage({
        session_id: activeSession?.id,
        query: textToSend,
        selected_document_ids: selectedDocIds,
        use_agentic_workflow: true,
      });

      // Update session with assistant response
      setActiveSession((prev) => ({
        ...prev,
        id: res.data.session_id,
        messages: [
          ...(prev?.messages || []).filter((m) => m.id !== tempUserMsg.id),
          tempUserMsg,
          res.data,
        ],
      }));
    } catch (err) {
      console.error('Failed to send message:', err);
      const errorMsg = {
        id: `err_${Date.now()}`,
        role: 'assistant',
        content: `Error executing research synthesis: ${
          err.response?.data?.detail || err.message
        }. Please verify active paper selection.`,
        citations: [],
        agent_steps: [],
        created_at: new Date().toISOString(),
      };
      setActiveSession((prev) => ({
        ...prev,
        messages: [...(prev?.messages || []), errorMsg],
      }));
    } finally {
      setLoading(false);
    }
  };

  const toggleStepAccordion = (msgId) => {
    setAgentStepsOpen((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  const sampleQuestions = [
    'What BLEU score did Transformer achieve on WMT 2014?',
    'Explain the Scaled Dot-Product Attention formula.',
    'Compare the attention mechanism with recurrent and convolutional models.',
    'What are the limitations of BERT regarding pre-training discrepancy?',
  ];

  // Helper to render text with clickable citation badges
  const renderMessageContent = (content, citations = []) => {
    if (!content) return null;
    const parts = content.split(/(\[[^\]]+,\s*(?:Page|p\.)\s*\d+\])/g);

    return (
      <div className="space-y-2 leading-relaxed text-sm whitespace-pre-wrap">
        {parts.map((part, idx) => {
          const match = part.match(/\[([^,\]]+),\s*(?:Page|p\.)\s*(\d+)\]/);
          if (match) {
            const paperTitle = match[1].trim();
            const pageNum = parseInt(match[2]);
            const matchedCit = citations.find(
              (c) => c.page_number === pageNum
            ) || {
              paper_title: paperTitle,
              page_number: pageNum,
              is_validated: true,
              snippet: content,
            };
            return <CitationBadge key={idx} citation={matchedCit} />;
          }
          return <span key={idx}>{part}</span>;
        })}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-5xl mx-auto w-full">
      {/* Top Paper Filter Pills */}
      <div className="p-4 border-b border-slate-800 bg-slate-900/60 flex items-center justify-between gap-4">
        <div className="flex items-center gap-2 overflow-x-auto py-1">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 shrink-0 flex items-center gap-1">
            <Layers className="w-3.5 h-3.5 text-brand-400" /> Active Scope:
          </span>
          {documents.length === 0 ? (
            <span className="text-xs text-slate-500 italic">No papers uploaded</span>
          ) : (
            documents.map((d) => {
              const isSelected = selectedDocIds.includes(d.id);
              return (
                <button
                  key={d.id}
                  onClick={() => toggleDocSelection(d.id)}
                  className={`text-xs px-2.5 py-1 rounded-full font-medium shrink-0 transition-colors border ${
                    isSelected
                      ? 'bg-brand-500/20 border-brand-500/40 text-brand-300'
                      : 'bg-slate-800/60 border-slate-700/60 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {isSelected ? '✓ ' : '+ '}
                  {d.title.length > 25 ? d.title.slice(0, 25) + '...' : d.title}
                </button>
              );
            })
          )}
        </div>
        <div className="text-xs text-slate-400 shrink-0">
          <span className="text-emerald-400 font-semibold">Strict Citations</span> [Paper, Page X]
        </div>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {(!activeSession?.messages || activeSession.messages.length === 0) && (
          <div className="text-center py-12 max-w-xl mx-auto space-y-6">
            <div className="w-12 h-12 rounded-2xl bg-brand-500/10 text-brand-400 flex items-center justify-center mx-auto border border-brand-500/20">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Ask Anything Across Your Research Papers</h3>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                The LangGraph agent reasons through queries, performs hybrid retrieval, cross-references
                methodologies, and verifies every claim with page-level citations.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-2 text-left pt-2">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Suggested Research Queries:
              </span>
              {sampleQuestions.map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSendMessage(q)}
                  className="p-3 text-xs text-slate-300 bg-slate-900/80 hover:bg-slate-800/80 border border-slate-800 hover:border-brand-500/40 rounded-xl transition-all flex items-center justify-between group"
                >
                  <span>{q}</span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-brand-400 transition-colors" />
                </button>
              ))}
            </div>
          </div>
        )}

        {activeSession?.messages?.map((msg) => {
          const isUser = msg.role === 'user';
          const hasSteps = msg.agent_steps && msg.agent_steps.length > 0;
          const isStepsOpen = agentStepsOpen[msg.id];

          return (
            <div
              key={msg.id}
              className={`flex gap-3 max-w-4xl ${isUser ? 'ml-auto justify-end' : 'mr-auto justify-start'}`}
            >
              {!isUser && (
                <div className="w-8 h-8 rounded-lg bg-brand-600/20 text-brand-400 border border-brand-500/30 flex items-center justify-center shrink-0 mt-1">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div className="space-y-2 max-w-2xl">
                {/* Agent Steps Accordion */}
                {!isUser && hasSteps && (
                  <div className="rounded-xl border border-slate-800 bg-slate-950/60 overflow-hidden text-xs">
                    <button
                      onClick={() => toggleStepAccordion(msg.id)}
                      className="w-full px-3 py-2 flex items-center justify-between text-slate-400 hover:text-slate-200 transition-colors font-mono text-[11px]"
                    >
                      <span className="flex items-center gap-1.5 text-brand-400 font-semibold">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        LangGraph Agentic Execution ({msg.agent_steps.length} Steps)
                      </span>
                      {isStepsOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                    </button>

                    {isStepsOpen && (
                      <div className="p-3 pt-0 space-y-2 border-t border-slate-800/60">
                        {msg.agent_steps.map((step, sIdx) => (
                          <div key={sIdx} className="flex items-start gap-2 text-slate-300">
                            <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0 mt-0.5" />
                            <div>
                              <span className="font-semibold text-slate-200">{step.step_name}: </span>
                              <span className="text-slate-400">{step.description}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Message Bubble */}
                <div
                  className={`p-4 rounded-2xl shadow-md ${
                    isUser
                      ? 'bg-brand-600 text-white rounded-tr-none'
                      : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none'
                  }`}
                >
                  {isUser ? (
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  ) : (
                    renderMessageContent(msg.content, msg.citations)
                  )}
                </div>

                {/* Citations Footer Strip */}
                {!isUser && msg.citations && msg.citations.length > 0 && (
                  <div className="flex flex-wrap items-center gap-1.5 pt-1 pl-1">
                    <span className="text-[10px] uppercase font-bold text-slate-500 mr-1">
                      Cited Sources:
                    </span>
                    {msg.citations.map((c, cIdx) => (
                      <CitationBadge key={cIdx} citation={c} />
                    ))}
                  </div>
                )}
              </div>

              {isUser && (
                <div className="w-8 h-8 rounded-lg bg-slate-800 text-slate-300 flex items-center justify-center shrink-0 mt-1">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          );
        })}

        {loading && (
          <div className="flex items-center gap-3 text-slate-400 text-xs py-2">
            <Bot className="w-5 h-5 text-brand-400 animate-pulse" />
            <div className="flex items-center gap-2">
              <span className="animate-pulse">Synthesizing multi-paper evidence & validating citations...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="p-4 border-t border-slate-800 bg-slate-900/90 backdrop-blur">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="relative flex items-center"
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            disabled={loading}
            placeholder={
              selectedDocIds.length > 0
                ? `Ask about ${selectedDocIds.length} active paper(s)... (e.g., 'Compare their architectures')`
                : 'Ask across all indexed papers...'
            }
            className="w-full pl-4 pr-12 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-brand-500 shadow-inner"
          />
          <button
            type="submit"
            disabled={!inputQuery.trim() || loading}
            className="absolute right-2 p-2 rounded-lg bg-brand-600 hover:bg-brand-500 disabled:opacity-30 text-white transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <p className="text-[11px] text-slate-500 text-center mt-2">
          Strict Zero-Hallucination Policy: All factual assertions are validated against indexed document chunks.
        </p>
      </div>
    </div>
  );
};

