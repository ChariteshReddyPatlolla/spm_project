import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const ResearchContext = createContext(null);

export const ResearchProvider = ({ children }) => {
  const [documents, setDocuments] = useState([]);
  const [selectedDocIds, setSelectedDocIds] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [systemStatus, setSystemStatus] = useState(null);
  const [loadingDocs, setLoadingDocs] = useState(false);
  
  // Citation Drawer state
  const [selectedCitation, setSelectedCitation] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const refreshStatus = async () => {
    try {
      const res = await api.getStatus();
      setSystemStatus(res.data);
    } catch (err) {
      console.warn('Status check failed:', err);
    }
  };

  const fetchDocuments = async () => {
    setLoadingDocs(true);
    try {
      const res = await api.getDocuments();
      setDocuments(res.data);
      // Auto-select first document if none selected
      if (selectedDocIds.length === 0 && res.data.length > 0) {
        setSelectedDocIds([res.data[0].id]);
      }
    } catch (err) {
      console.error('Failed to load documents:', err);
    } finally {
      setLoadingDocs(false);
    }
  };

  const fetchSessions = async () => {
    try {
      const res = await api.getSessions();
      setSessions(res.data);
      if (res.data.length > 0 && !activeSession) {
        const fullSession = await api.getSession(res.data[0].id);
        setActiveSession(fullSession.data);
        if (fullSession.data.selected_document_ids?.length > 0) {
          setSelectedDocIds(fullSession.data.selected_document_ids);
        }
      }
    } catch (err) {
      console.error('Failed to load sessions:', err);
    }
  };

  const switchSession = async (sessionId) => {
    try {
      const res = await api.getSession(sessionId);
      setActiveSession(res.data);
      if (res.data.selected_document_ids?.length > 0) {
        setSelectedDocIds(res.data.selected_document_ids);
      }
      setActiveTab('chat');
    } catch (err) {
      console.error('Failed to switch session:', err);
    }
  };

  const createNewSession = async (title = 'New Research Session') => {
    try {
      const res = await api.createSession({
        title,
        selected_document_ids: selectedDocIds,
      });
      setSessions((prev) => [res.data, ...prev]);
      setActiveSession({ ...res.data, messages: [] });
      setActiveTab('chat');
      return res.data;
    } catch (err) {
      console.error('Failed to create session:', err);
    }
  };

  const deleteSession = async (sessionId) => {
    try {
      await api.deleteSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (activeSession?.id === sessionId) {
        setActiveSession(null);
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  const toggleDocSelection = (docId) => {
    setSelectedDocIds((prev) => {
      const updated = prev.includes(docId)
        ? prev.filter((id) => id !== docId)
        : [...prev, docId];
      
      // Sync with active session if present
      if (activeSession) {
        api.updateSessionDocuments(activeSession.id, updated).catch(console.error);
      }
      return updated;
    });
  };

  const selectAllDocs = () => {
    const allIds = documents.map((d) => d.id);
    setSelectedDocIds(allIds);
    if (activeSession) {
      api.updateSessionDocuments(activeSession.id, allIds).catch(console.error);
    }
  };

  const deselectAllDocs = () => {
    setSelectedDocIds([]);
    if (activeSession) {
      api.updateSessionDocuments(activeSession.id, []).catch(console.error);
    }
  };

  const openCitationPreview = (citation) => {
    setSelectedCitation(citation);
    setIsDrawerOpen(true);
  };

  const closeCitationPreview = () => {
    setIsDrawerOpen(false);
    setSelectedCitation(null);
  };

  useEffect(() => {
    refreshStatus();
    fetchDocuments();
    fetchSessions();
  }, []);

  return (
    <ResearchContext.Provider
      value={{
        documents,
        selectedDocIds,
        sessions,
        activeSession,
        activeTab,
        systemStatus,
        loadingDocs,
        selectedCitation,
        isDrawerOpen,
        setActiveTab,
        setActiveSession,
        fetchDocuments,
        fetchSessions,
        switchSession,
        createNewSession,
        deleteSession,
        toggleDocSelection,
        selectAllDocs,
        deselectAllDocs,
        openCitationPreview,
        closeCitationPreview,
        refreshStatus,
      }}
    >
      {children}
    </ResearchContext.Provider>
  );
};

export const useResearch = () => useContext(ResearchContext);

