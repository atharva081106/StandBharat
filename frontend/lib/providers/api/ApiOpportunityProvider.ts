import { OpportunityProvider } from '../types/interfaces';
import { ApiClient } from '../../api/client';

export class ApiOpportunityProvider implements OpportunityProvider {
  async executeOpportunity(id: string) {
    await ApiClient.patch(`/api/opportunities/${id}`, { status: 'IN_PROGRESS' });
  }
  
  async dismissOpportunity(id: string) {
    await ApiClient.patch(`/api/opportunities/${id}`, { status: 'DISMISSED' });
  }
}
