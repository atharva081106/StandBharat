export interface Agent {
  id: string;
  name: string;
  description: string;
  status: 'ACTIVE' | 'WAITING' | 'PAUSED';
}
