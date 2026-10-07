# FRONTEND PROVIDER ARCHITECTURE

## 1. Provider Interfaces
To cleanly abstract the frontend from the FastAPI backend implementation, we have introduced a Provider Factory pattern.

All domain contracts are defined as standard TypeScript interfaces in `frontend/lib/providers/types/interfaces.ts`. 

Current interfaces:
- `AuthProvider`: Manages active user session and tenant state.
- `AgentProvider`: Exposes methods to retrieve and interact with AI agents.
*(Further interfaces for workflows, content, campaigns, etc., will follow this exact pattern).*

## 2. Mock Implementations
Mock implementations reside in `frontend/lib/providers/mock/`. They implement the exact same TypeScript interfaces as the API providers, but resolve standard promises instantly using the static data found in `frontend/lib/mock/data.ts`.

Example: `MockAgentProvider` implements `AgentProvider` and returns `mockAgents`.

## 3. API Implementations
API implementations reside in `frontend/lib/providers/api/`. They use the shared `ApiClient` to make HTTP requests against the FastAPI backend, while satisfying the exact same Provider interfaces. 

Example: `ApiAgentProvider` implements `AgentProvider` and resolves using `ApiClient.get('/api/agents')`.

## 4. DATA_MODE Switching
The Application Context (`frontend/lib/providers/index.tsx`) dynamically resolves the implementation via the `NEXT_PUBLIC_DATA_MODE` environment variable.

- If `NEXT_PUBLIC_DATA_MODE=mock`, it initializes `MockAgentProvider`.
- If `NEXT_PUBLIC_DATA_MODE=api`, it initializes `ApiAgentProvider`.

The rest of the React application simply consumes `useAppProvider().agents` and remains entirely unaware of which environment is feeding the data.

## 5. API Base URL
The `ApiClient` reads `NEXT_PUBLIC_API_URL` to route requests. No hardcoded `localhost:8000` strings are scattered in the UI.

## 6. Authentication Expectations
The `ApiClient` is configured with `credentials: 'include'`. It strictly relies on HTTP-only secure cookies returned by the backend. We do not use LocalStorage for access tokens. 

## 7. Error Handling
`ApiClient.request<T>` globally catches HTTP exceptions (e.g. 401, 403, 404, 500) and formats them into a standard `Error(message)` throw. This allows UI components to simply use standard `try/catch` or Promise rejections to show appropriate localized UI errors without having to parse Response objects repeatedly. 

## 8. How to add a new domain
1. Define the DTO types in `frontend/lib/types/`.
2. Define the Provider Interface in `frontend/lib/providers/types/interfaces.ts`.
3. Build the `ApiClient` methods in `frontend/lib/api/domain.ts`.
4. Create the `MockDomainProvider` class in `mock/`.
5. Create the `ApiDomainProvider` class in `api/`.
6. Instantiate it conditionally in the `AppProvider` factory inside `lib/providers/index.tsx`.
