import React, { useState, useRef } from 'react';
import { useDocuments, BrandDocument } from '@/lib/providers/DocumentProvider';
import { FileText, Upload, Plus, Trash2, AlertCircle, File, CheckCircle2, Loader2, Info } from 'lucide-react';

export const DocumentsPanel = () => {
  const { documents, loading, error, uploadDocument, deleteDocument } = useDocuments();
  const [uploading, setUploading] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<BrandDocument | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      await uploadDocument(file, 'Uncategorized');
      // Reset input
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'UPLOADED':
      case 'PROCESSING':
        return <Loader2 className="w-4 h-4 text-[#A9A4A0] animate-spin" />;
      case 'READY':
        return <CheckCircle2 className="w-4 h-4 text-[#00A650]" />;
      case 'FAILED':
      case 'UNSUPPORTED':
        return <AlertCircle className="w-4 h-4 text-[#8F0028]" />;
      default:
        return <Info className="w-4 h-4 text-[#A9A4A0]" />;
    }
  };

  if (selectedDoc) {
    return (
      <div className="flex-1 flex flex-col h-full bg-[#1C1A1A]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-[#373333] flex items-center justify-between shrink-0">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <button onClick={() => setSelectedDoc(null)} className="text-[#A9A4A0] hover:text-[#F5F3F1] text-[12px] font-medium transition-colors">
                &larr; Back to Documents
              </button>
            </div>
            <h2 className="text-[18px] font-bold text-[#F5F3F1] flex items-center gap-2">
              <FileText className="w-5 h-5 text-[#8F0028]" />
              {selectedDoc.name}
            </h2>
          </div>
          <button 
            onClick={() => {
              if (confirm('Are you sure you want to delete this document?')) {
                deleteDocument(selectedDoc.id);
                setSelectedDoc(null);
              }
            }}
            className="flex items-center gap-2 px-3 py-1.5 text-[#8F0028] bg-[#8F0028]/10 hover:bg-[#8F0028]/20 rounded-md text-[13px] font-semibold transition-colors"
          >
            <Trash2 className="w-4 h-4" /> Delete
          </button>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-6">
          {/* Metadata */}
          <div className="bg-[#242222] border border-[#373333] rounded-xl p-5">
            <h3 className="text-[13px] font-bold text-[#F5F3F1] mb-4">Metadata</h3>
            <div className="grid grid-cols-2 gap-x-8 gap-y-4">
              <div>
                <div className="text-[11px] text-[#A9A4A0] uppercase tracking-wider mb-1">Status</div>
                <div className="flex items-center gap-2 text-[13px] font-medium text-[#F5F3F1]">
                  {getStatusIcon(selectedDoc.processing_status)}
                  {selectedDoc.processing_status}
                </div>
              </div>
              <div>
                <div className="text-[11px] text-[#A9A4A0] uppercase tracking-wider mb-1">Retrieval / AI</div>
                <div className="text-[13px] font-medium text-[#A9A4A0]">{selectedDoc.retrieval_status}</div>
              </div>
              <div>
                <div className="text-[11px] text-[#A9A4A0] uppercase tracking-wider mb-1">Type</div>
                <div className="text-[13px] font-medium text-[#F5F3F1]">{selectedDoc.type || 'Unknown'}</div>
              </div>
              <div>
                <div className="text-[11px] text-[#A9A4A0] uppercase tracking-wider mb-1">Size</div>
                <div className="text-[13px] font-medium text-[#F5F3F1]">{formatSize(selectedDoc.file_size)}</div>
              </div>
              <div>
                <div className="text-[11px] text-[#A9A4A0] uppercase tracking-wider mb-1">Category</div>
                <div className="text-[13px] font-medium text-[#F5F3F1]">{selectedDoc.category}</div>
              </div>
              <div>
                <div className="text-[11px] text-[#A9A4A0] uppercase tracking-wider mb-1">Uploaded</div>
                <div className="text-[13px] font-medium text-[#F5F3F1]">{new Date(selectedDoc.created_at).toLocaleString()}</div>
              </div>
              {selectedDoc.metadata_json?.word_count && (
                <div>
                  <div className="text-[11px] text-[#A9A4A0] uppercase tracking-wider mb-1">Word Count</div>
                  <div className="text-[13px] font-medium text-[#F5F3F1]">{selectedDoc.metadata_json.word_count.toLocaleString()} words</div>
                </div>
              )}
            </div>
          </div>

          {/* Extracted Content Preview */}
          <div className="bg-[#242222] border border-[#373333] rounded-xl p-5">
            <h3 className="text-[13px] font-bold text-[#F5F3F1] mb-4">Content Preview</h3>
            {['FAILED', 'UNSUPPORTED'].includes(selectedDoc.processing_status) ? (
              <div className="text-[13px] text-[#8F0028] p-4 bg-[#8F0028]/10 rounded-lg">
                Extraction failed: {selectedDoc.metadata_json?.error || 'Unsupported file format.'}
              </div>
            ) : selectedDoc.processing_status === 'PROCESSING' || selectedDoc.processing_status === 'UPLOADED' ? (
              <div className="text-[13px] text-[#A9A4A0] p-4 flex items-center justify-center">
                <Loader2 className="w-5 h-5 animate-spin mr-2" /> Processing document text...
              </div>
            ) : (
              <div className="text-[13px] text-[#A9A4A0] leading-relaxed max-h-[300px] overflow-y-auto p-4 bg-[#1C1A1A] rounded-lg border border-[#373333] custom-scrollbar whitespace-pre-wrap">
                {/* Note: In a real app we'd fetch the extracted_text from a detail endpoint, but for now we might only have metadata. */}
                {selectedDoc.metadata_json?.word_count ? `(Extracted text preview available on backend: ${selectedDoc.metadata_json.word_count} words)` : 'No preview available.'}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-[#1C1A1A]">
      {/* Header */}
      <div className="px-6 py-4 border-b border-[#373333] flex items-center justify-between shrink-0">
        <div>
          <h2 className="text-[18px] font-bold text-[#F5F3F1] flex items-center gap-2">
            <FileText className="w-5 h-5 text-[#8F0028]" />
            Knowledge Base
          </h2>
          <p className="text-[12px] text-[#A9A4A0] mt-1">Upload and manage documents for your AI CMO</p>
        </div>
        
        <input 
          type="file" 
          ref={fileInputRef} 
          className="hidden" 
          onChange={handleFileChange}
          accept=".pdf,.docx,.txt,.md,.csv"
        />
        <button 
          onClick={handleUploadClick}
          disabled={uploading}
          className="flex items-center gap-2 px-4 py-2 bg-[#8F0028] hover:bg-[#A80030] disabled:bg-[#8F0028]/50 disabled:cursor-not-allowed text-white rounded-lg text-[13px] font-bold transition-colors"
        >
          {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
          {uploading ? 'Uploading...' : 'Upload Document'}
        </button>
      </div>

      {error && (
        <div className="m-6 p-4 bg-[#8F0028]/10 border border-[#8F0028]/50 rounded-xl text-[13px] text-[#F5F3F1] flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-[#8F0028] shrink-0" />
          {error}
        </div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-6">
        {loading && !documents.length ? (
          <div className="flex flex-col items-center justify-center h-full opacity-50">
            <Loader2 className="w-8 h-8 text-[#A9A4A0] animate-spin mb-4" />
            <p className="text-[#A9A4A0] text-[13px]">Loading documents...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center border-2 border-dashed border-[#373333] rounded-xl p-10">
            <File className="w-12 h-12 text-[#373333] mb-4" />
            <h3 className="text-[#F5F3F1] font-bold text-[15px] mb-2">No documents yet</h3>
            <p className="text-[#A9A4A0] text-[13px] max-w-sm mb-6">
              Upload product guides, brand guidelines, or marketing strategies to give your AI CMO better context.
            </p>
            <button 
              onClick={handleUploadClick}
              className="flex items-center gap-2 px-4 py-2 bg-[#242222] hover:bg-[#2A2828] text-[#F5F3F1] border border-[#373333] rounded-lg text-[13px] font-bold transition-colors"
            >
              <Plus className="w-4 h-4" /> Add your first document
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {documents.map((doc) => (
              <div 
                key={doc.id}
                onClick={() => setSelectedDoc(doc)}
                className="flex items-center justify-between p-4 bg-[#242222] border border-[#373333] hover:border-[#4A4545] rounded-xl cursor-pointer transition-colors group"
              >
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${
                    doc.processing_status === 'READY' ? 'bg-[#00A650]/10 text-[#00A650]' :
                    ['FAILED', 'UNSUPPORTED'].includes(doc.processing_status) ? 'bg-[#8F0028]/10 text-[#8F0028]' :
                    'bg-[#A9A4A0]/10 text-[#A9A4A0]'
                  }`}>
                    {getStatusIcon(doc.processing_status)}
                  </div>
                  <div>
                    <h3 className="text-[14px] font-bold text-[#F5F3F1] mb-1 group-hover:text-white transition-colors">{doc.name}</h3>
                    <div className="flex items-center gap-3 text-[12px] text-[#A9A4A0]">
                      <span>{doc.category}</span>
                      <span className="w-1 h-1 rounded-full bg-[#373333]"></span>
                      <span>{formatSize(doc.file_size)}</span>
                      <span className="w-1 h-1 rounded-full bg-[#373333]"></span>
                      <span className="flex items-center gap-1">
                        {doc.processing_status === 'READY' && <CheckCircle2 className="w-3 h-3 text-[#00A650]" />}
                        {doc.processing_status === 'PROCESSING' && <Loader2 className="w-3 h-3 animate-spin" />}
                        {doc.processing_status}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex flex-col items-end gap-1">
                  <div className="text-[11px] font-medium text-[#A9A4A0] uppercase tracking-wider">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </div>
                  <div className="text-[11px] text-[#A9A4A0]">
                    AI Retrieval: {doc.retrieval_status === 'NOT_CONFIGURED' ? 'Unavailable' : 'Ready'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
