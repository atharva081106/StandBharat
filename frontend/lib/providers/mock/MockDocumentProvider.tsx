import { BrandDocument } from '../DocumentProvider';
import { v4 as uuidv4 } from 'uuid';

let mockDocuments: BrandDocument[] = [
  {
    id: uuidv4(),
    name: 'Brand_Guidelines_2024.pdf',
    type: 'application/pdf',
    source: 'upload',
    status: 'active',
    file_size: 2450000,
    category: 'Design Guide',
    processing_status: 'READY',
    retrieval_status: 'NOT_CONFIGURED',
    uploaded_by: 'user-1',
    created_at: new Date(Date.now() - 86400000).toISOString(),
    updated_at: new Date(Date.now() - 86400000).toISOString(),
    metadata_json: {
      character_count: 15200,
      word_count: 2400
    }
  },
  {
    id: uuidv4(),
    name: 'Q3_Marketing_Strategy.docx',
    type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    source: 'upload',
    status: 'active',
    file_size: 150000,
    category: 'Marketing Strategy',
    processing_status: 'READY',
    retrieval_status: 'NOT_CONFIGURED',
    uploaded_by: 'user-1',
    created_at: new Date(Date.now() - 172800000).toISOString(),
    updated_at: new Date(Date.now() - 172800000).toISOString(),
    metadata_json: {
      character_count: 45000,
      word_count: 8200
    }
  }
];

export const MockDocumentProvider = {
  getDocuments: async (): Promise<BrandDocument[]> => {
    return new Promise((resolve) => {
      setTimeout(() => resolve([...mockDocuments]), 500);
    });
  },

  uploadDocument: async (file: File, category: string): Promise<BrandDocument> => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (file.size > 10 * 1024 * 1024) {
          reject(new Error('File too large'));
          return;
        }

        const newDoc: BrandDocument = {
          id: uuidv4(),
          name: file.name,
          type: file.type || 'application/octet-stream',
          source: 'upload',
          status: 'active',
          file_size: file.size,
          category,
          processing_status: 'READY',
          retrieval_status: 'NOT_CONFIGURED',
          uploaded_by: 'mock-user',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          metadata_json: {
            word_count: Math.floor(Math.random() * 5000)
          }
        };

        mockDocuments = [newDoc, ...mockDocuments];
        resolve(newDoc);
      }, 1000);
    });
  },

  deleteDocument: async (id: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const initialLen = mockDocuments.length;
        mockDocuments = mockDocuments.filter(d => d.id !== id);
        if (mockDocuments.length === initialLen) {
          reject(new Error('Document not found'));
        } else {
          resolve();
        }
      }, 500);
    });
  }
};
