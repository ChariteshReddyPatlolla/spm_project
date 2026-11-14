import React from 'react';
import { ResearchProvider, useResearch } from './context/ResearchContext';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { CitationDrawer } from './components/CitationDrawer';
import { Dashboard } from './pages/Dashboard';
import { DocumentLibrary } from './pages/DocumentLibrary';
import { ResearchChat } from './pages/ResearchChat';
import { ComparativeAnalysis } from './pages/ComparativeAnalysis';
import { PaperSummaries } from './pages/PaperSummaries';

const MainLayout = () => {
  const { activeTab } = useResearch();

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'library':
        return <DocumentLibrary />;
      case 'chat':
        return <ResearchChat />;
      case 'comparative':
        return <ComparativeAnalysis />;
      case 'summaries':
        return <PaperSummaries />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto bg-slate-950/60">
          {renderActiveTab()}
        </main>
      </div>
      <CitationDrawer />
    </div>
  );
};

export default function App() {
  return (
    <ResearchProvider>
      <MainLayout />
    </ResearchProvider>
  );
}

