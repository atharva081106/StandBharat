import { AiCmoProvider } from '../types/interfaces';

export class MockAiCmoProvider implements AiCmoProvider {
  async chat(message: string): Promise<{status: string, response: string}> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          status: "SUCCESS",
          response: "I've analyzed that request and will begin drafting a strategy. Check your opportunities for prioritized tasks."
        });
      }, 800);
    });
  }
}
