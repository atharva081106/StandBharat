import { OpportunityProvider } from '../types/interfaces';

export class MockOpportunityProvider implements OpportunityProvider {
  async executeOpportunity(id: string) {
    console.log(`Mock executing opportunity ${id}`);
  }
  
  async dismissOpportunity(id: string) {
    console.log(`Mock dismissing opportunity ${id}`);
  }
}
