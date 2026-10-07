import { DashboardProvider } from '../types/interfaces';
import { mockKPIs, mockOpportunities, mockRecentActivity } from '../../mock/data';

export class MockDashboardProvider implements DashboardProvider {
  async getDashboard() {
    return {
      kpis: Object.entries(mockKPIs).map(([key, data]) => ({
        label: key.replace(/([A-Z])/g, ' $1').trim(),
        value: data.value,
        change: data.change,
        trend: (data as any).trend || 'up'
      })),
      opportunities: mockOpportunities,
      recent_activity: mockRecentActivity,
      system_status: "Operational"
    };
  }
}
