import { getCookie } from 'cookies-next';
import { BrandDocument } from '../DocumentProvider';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const getHeaders = () => {
  const token = getCookie('access_token');
  const wsId = getCookie('workspace_id');
  const brandId = getCookie('brand_id');

  return {
    'Authorization': `Bearer ${token}`,
    'X-Workspace-Id': wsId as string,
    'X-Brand-Id': brandId as string,
  };
};

export const ApiDocumentProvider = {
  getDocuments: async (): Promise<BrandDocument[]> => {
    const headers = getHeaders();
    if (!headers['X-Brand-Id']) return [];

    const res = await fetch(`${API_BASE_URL}/api/brand-brain/documents`, {
      headers: {
        'Authorization': headers['Authorization'],
        'X-Workspace-Id': headers['X-Workspace-Id'],
        'X-Brand-Id': headers['X-Brand-Id'],
      }
    });

    if (!res.ok) {
      throw new Error('Failed to fetch documents');
    }

    return res.json();
  },

  uploadDocument: async (file: File, category: string): Promise<BrandDocument> => {
    const headers = getHeaders();
    if (!headers['X-Brand-Id']) throw new Error('No active brand');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);

    const res = await fetch(`${API_BASE_URL}/api/brand-brain/documents`, {
      method: 'POST',
      headers: {
        'Authorization': headers['Authorization'],
        'X-Workspace-Id': headers['X-Workspace-Id'],
        'X-Brand-Id': headers['X-Brand-Id'],
      },
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Upload failed');
    }

    return res.json();
  },

  deleteDocument: async (id: string): Promise<void> => {
    const headers = getHeaders();
    if (!headers['X-Brand-Id']) throw new Error('No active brand');

    const res = await fetch(`${API_BASE_URL}/api/brand-brain/documents/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': headers['Authorization'],
        'X-Workspace-Id': headers['X-Workspace-Id'],
        'X-Brand-Id': headers['X-Brand-Id'],
      }
    });

    if (!res.ok) {
      throw new Error('Failed to delete document');
    }
  }
};
