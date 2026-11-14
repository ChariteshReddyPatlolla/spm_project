import React, { useState, useRef } from 'react';
import {
  Upload,
  FileText,
  Trash2,
  Search,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Layers,
  Calendar,
  Users
} from 'lucide-react';
import { useResearch } from '../context/ResearchContext';
import { api } from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const DocumentLibrary = () => {
  const {
    documents,
    selectedDocIds,
    toggleDocSelection,
    fetchDocuments,
    loadingDocs,
    openCitationPreview
  } = useResearch();

  const [searchQuery, setSearchQuery] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState('');
  const [uploadError, setUploadError] = useState('');
  const fileInputRef = useRef(null);

  const filteredDocs = documents.filter((d) => {
    const q = searchQuery.toLowerCase();
    return (
      d.title.toLowerCase().includes(q) ||
      d.filename.toLowerCase().includes(q) ||
      (d.abstract && d.abstract.toLowerCase().includes(q))
    );
  });

  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    setUploadError('');
    setUploadProgress(`Uploading and processing ${files.length} paper(s)...`);

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    try {
      await api.uploadDocuments(formData);
      setUploadProgress('Processing layout, OCR, chunking, and embedding vectors...');
      await fetchDocuments();
      setUploadProgress('');
    } catch (err) {
      console.error('Upload failed:', err);
      setUploadError(err.response?.data?.detail || 'Failed to upload and ingest documents.');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId, title) => {
    if (window.confirm(`Are you sure you want to delete "${title}"? This will delete all extracted pages, vector embeddings, and cached summaries.`)) {
      try {
        await api.deleteDocument(docId);
        await fetchDocuments();
      } catch (err) {
        console.error('Delete failed:', err);
        alert('Failed to delete document.');
      }
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-200">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight">Document Library</h2>
          <p className="text-xs text-slate-400">
            Upload multi-column, layout-rich research papers. Original pages, tables, and sections are indexed with ChromaDB.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <input
            type="file"
            ref={fileInputRef}
            multiple
            accept=".pdf"
            className="hidden"
            onChange={(e) => handleFileUpload(e.target.files)}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="px-4 py-2.5 rounded-lg bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white font-medium text-sm transition-colors shadow-lg shadow-brand-500/20 flex items-center gap-2"
          >
            <Upload className="w-4 h-4" />
            <span>Upload Research Papers</span>
          </button>
        </div>
      </div>

      {/* Upload Dropzone / Banner */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          handleFileUpload(e.dataTransfer.files);
        }}
        className="border-2 border-dashed border-slate-700 hover:border-brand-500/60 rounded-2xl p-8 bg-slate-900/40 text-center transition-all cursor-pointer group"
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="max-w-md mx-auto space-y-3">
          <div className="w-12 h-12 rounded-full bg-slate-800 group-hover:bg-brand-500/10 text-slate-400 group-hover:text-brand-400 flex items-center justify-center mx-auto transition-colors border border-slate-700">
            <Upload className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-200">
              Drag and drop multiple PDF papers here, or <span className="text-brand-400 underline">browse</span>
            </p>
            <p className="text-xs text-slate-500 mt-1">
              Supports multi-column PDFs, tables, scanned papers (OCR), arXiv preprints, and conference proceedings.
            </p>
          </div>
        </div>
      </div>

      {/* Progress & Error States */}
      {uploading && (
        <div className="p-4 rounded-xl bg-brand-950/60 border border-brand-500/30 flex items-center gap-3">
          <LoadingSpinner label="" />
          <div className="text-xs text-brand-200 font-medium">{uploadProgress}</div>
        </div>
      )}
      {uploadError && (
        <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-500/30 flex items-center gap-3 text-rose-300 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{uploadError}</span>
        </div>
      )}

      {/* Search and Filters */}
      <div className="flex items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search papers by title, author, or keyword..."
            className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-brand-500"
          />
        </div>
        <div className="text-xs text-slate-400">
          Showing <span className="font-bold text-slate-200">{filteredDocs.length}</span> of {documents.length} paper(s)
        </div>
      </div>

      {/* Paper Cards Grid */}
      {loadingDocs ? (
        <LoadingSpinner label="Loading document catalog..." />
      ) : filteredDocs.length === 0 ? (
        <div className="text-center py-16 text-slate-500 text-sm">
          No papers found matching your query.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredDocs.map((doc) => {
            const isSelected = selectedDocIds.includes(doc.id);
            const authors = Array.isArray(doc.authors) ? doc.authors.join(', ') : '';

            return (
              <div
                key={doc.id}
                className={`p-6 rounded-2xl border transition-all flex flex-col justify-between ${
                  isSelected
                    ? 'bg-slate-900 border-brand-500/50 shadow-lg shadow-brand-500/5'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <span className="p-2 rounded-lg bg-brand-500/10 text-brand-400 border border-brand-500/20">
                        <FileText className="w-5 h-5" />
                      </span>
                      <div>
                        <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          {doc.status}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDelete(doc.id, doc.title)}
                      className="p-1.5 text-slate-500 hover:text-rose-400 rounded-lg hover:bg-slate-800 transition-colors"
                      title="Delete document and vector index"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <div>
                    <h3 className="text-base font-bold text-slate-100 line-clamp-2 leading-snug" title={doc.title}>
                      {doc.title}
                    </h3>
                    {authors && (
                      <p className="text-xs text-slate-400 flex items-center gap-1.5 mt-1 truncate">
                        <Users className="w-3.5 h-3.5 shrink-0 text-slate-500" />
                        <span>{authors}</span>
                      </p>
                    )}
                  </div>

                  {doc.abstract && (
                    <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed font-serif italic bg-slate-950/40 p-2.5 rounded-lg border border-slate-800/80">
                      "{doc.abstract}"
                    </p>
                  )}
                </div>

                <div className="pt-4 mt-4 border-t border-slate-800 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-4 text-slate-400">
                    <span className="flex items-center gap-1">
                      <Layers className="w-3.5 h-3.5 text-slate-500" />
                      <b>{doc.page_count}</b> pages
                    </span>
                    {doc.year && (
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5 text-slate-500" />
                        {doc.year}
                      </span>
                    )}
                  </div>

                  <button
                    onClick={() => toggleDocSelection(doc.id)}
                    className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                      isSelected
                        ? 'bg-brand-600 text-white shadow-sm'
                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    {isSelected ? '✓ Selected in Scope' : '+ Add to Scope'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

