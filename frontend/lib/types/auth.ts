export type AuthState = 'loading' | 'loggedOut' | 'loggedIn' | 'onboarding' | 'onboardingComplete' | 'needsOnboarding';
export interface User {
  id: string;
  name: string;
  email: string;
  has_workspace?: boolean;
}
