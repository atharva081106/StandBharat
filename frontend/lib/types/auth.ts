export type AuthState = 'loading' | 'loggedOut' | 'loggedIn' | 'onboarding' | 'onboardingComplete';
export interface User {
  id: string;
  name: string;
  email: string;
}
