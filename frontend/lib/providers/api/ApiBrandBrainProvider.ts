import { BrandBrainProvider } from '../types/interfaces';
import { ApiClient } from '../../api/client';

export class ApiBrandBrainProvider implements BrandBrainProvider {
  async getContext() {
    return await ApiClient.get<any>('/api/brand-brain/');
  }
  async updateVoice(data: any) {
    return await ApiClient.patch<any>('/api/brand-brain/voice', data);
  }
  async addAudience(data: any) {
    return await ApiClient.post<any>('/api/brand-brain/audiences', data);
  }
  async updateAudience(id: string, data: any) {
    return await ApiClient.patch<any>(`/api/brand-brain/audiences/${id}`, data);
  }
  async deleteAudience(id: string) {
    return await ApiClient.delete<any>(`/api/brand-brain/audiences/${id}`);
  }
  async addProduct(data: any) {
    return await ApiClient.post<any>('/api/brand-brain/products', data);
  }
  async updateProduct(id: string, data: any) {
    return await ApiClient.patch<any>(`/api/brand-brain/products/${id}`, data);
  }
  async deleteProduct(id: string) {
    return await ApiClient.delete<any>(`/api/brand-brain/products/${id}`);
  }
  async updatePositioning(data: any) {
    return await ApiClient.patch<any>('/api/brand-brain/positioning', data);
  }
  async addGoal(data: any) {
    return await ApiClient.post<any>('/api/brand-brain/goals', data);
  }
  async updateGoal(id: string, data: any) {
    return await ApiClient.patch<any>(`/api/brand-brain/goals/${id}`, data);
  }
  async deleteGoal(id: string) {
    return await ApiClient.delete<any>(`/api/brand-brain/goals/${id}`);
  }
  async addCompetitor(data: any) {
    return await ApiClient.post<any>('/api/brand-brain/competitors', data);
  }
  async updateCompetitor(id: string, data: any) {
    return await ApiClient.patch<any>(`/api/brand-brain/competitors/${id}`, data);
  }
  async deleteCompetitor(id: string) {
    return await ApiClient.delete<any>(`/api/brand-brain/competitors/${id}`);
  }
  async updateStrategy(data: any) {
    return await ApiClient.patch<any>('/api/brand-brain/strategy', data);
  }
}
