import { DashboardProvider } from '../types/interfaces';
import { ApiClient } from '../../api/client';

export class ApiDashboardProvider implements DashboardProvider {
  async getDashboard() {
    const data = await ApiClient.get<any>('/api/dashboard/command-center');
    return data;
  }
}
