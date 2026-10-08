"use client"
import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { ApiDocumentProvider } from './api/ApiDocumentProvider';
import { MockDocumentProvider } from './mock/MockDocumentProvider';
import { useAuth } from './MockProvider';

export interface BrandDocument {
  id: string;
  name: string;
  type: string;
  source: string;
  status: string;
  file_size: number;
  category: string;
  processing_status: string;
  retrieval_status: string;
  uploaded_by: string;
  created_at: string;
  updated_at: string;
  metadata_json: any;
}

export interface DocumentProviderContextType {
  documents: BrandDocument[];
  loading: boolean;
  error: string | null;
  fetchDocuments: () => Promise<void>;
  uploadDocument: (file: File, category?: string) => Promise<void>;
  deleteDocument: (id: string) => Promise<void>;
}

const DocumentContext = createContext<DocumentProviderContextType | undefined>(undefined);

export const DocumentProvider = ({ children }: { children: ReactNode }) => {
  const { authState } = useAuth();
  
  // Use API mode if authenticated, otherwise mock
  const provider = authState === 'loggedIn' ? ApiDocumentProvider : MockDocumentProvider;
  
  const [documents, setDocuments] = useState<BrandDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      const docs = await provider.getDocuments();
      setDocuments(docs);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  const uploadDocument = async (file: File, category: string = 'Uncategorized') => {
    try {
      setLoading(true);
      setError(null);
      await provider.uploadDocument(file, category);
      await fetchDocuments();
    } catch (err: any) {
      setError(err.message || 'Failed to upload document');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteDocument = async (id: string) => {
    try {
      setLoading(true);
      setError(null);
      await provider.deleteDocument(id);
      await fetchDocuments();
    } catch (err: any) {
      setError(err.message || 'Failed to delete document');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
    
    // Poll processing documents every 5s
    const interval = setInterval(() => {
      setDocuments(prev => {
        const hasProcessing = prev.some(d => ['UPLOADED', 'PROCESSING'].includes(d.processing_status));
        if (hasProcessing) {
          provider.getDocuments().then(setDocuments).catch(console.error);
        }
        return prev;
      });
    }, 5000);
    
    return () => clearInterval(interval);
  }, [authState]);

  return (
    <DocumentContext.Provider value={{ documents, loading, error, fetchDocuments, uploadDocument, deleteDocument }}>
      {children}
    </DocumentContext.Provider>
  );
};

export const useDocuments = () => {
  const context = useContext(DocumentContext);
  if (context === undefined) {
    throw new Error('useDocuments must be used within a DocumentProvider');
  }
  return context;
};
