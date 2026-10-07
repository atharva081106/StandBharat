import { AiCmoProvider } from '../types/interfaces';
import { ApiClient } from '../../api/client';

export class ApiAiCmoProvider implements AiCmoProvider {
  async chat(message: string): Promise<{status: string, response: string}> {
    const res = await ApiClient.post<any>('/api/ai/cmo/chat', { message });
    return res as {status: string, response: string};
  }
}
