# STANDBHARAT - CURRENT AGENT & INTEGRATION AUDIT

## 1. Agent Architecture
**Current State:**
- `BaseAgent` exists with simple `execute(context: AgentContext) -> AgentResult` contract.
- Agents are registered statically via `AgentRegistry`.
- Simple classes (like `ContentWriterAgent`, `GrowthAgent`, `AnalyticsAgent`, etc.) are subclassing `BaseAgent`.

**Gaps to fulfill OKR:**
- **Missing `AgentRuntime`:** Agents currently perform execution internally without a managed runtime wrapper that tracks budgets, retries, celery timeouts, token costs, permissions, and tool schemas.
- **Missing Handoffs:** Agents cannot explicitly invoke or return tasks to other agents; there is no `AgentHandoff` model to chain work (e.g. `SEO -> Content Strategy -> Writer`).
- **Missing Definition Contract:** Agents need an `AgentDefinition` exposing input/output schemas, required integrations, and strict capability enums.
- **Missing Dependencies:** No system checks if an Agent has the required Integrations connected prior to scheduling its execution.

## 2. AI Gateway
**Current State:**
- Gateway isolates providers (currently just `OpenAIProvider`).
- Correctly propagates `AINotConfiguredException` rather than mocking.
- Has a `generate()` method taking a list of `AIRequestMessage`.

**Gaps to fulfill OKR:**
- **No Tool Calling (Function Calling):** The current signature (`generate(messages, ...)`) does not support injecting tool JSON schemas (`tools=[]`) or handling tool execution loops. 
- **No Cost/Token Persistence:** Does not pipe `total_tokens` and `estimated_cost` out into an `AIUsageEvent` table for budget accounting per agent run.

## 3. Integration Architecture
**Current State:**
- Very simple REST model (`Integration`).
- Basic APIs exist under `/api/integrations` to fetch enabled providers.

**Gaps to fulfill OKR:**
- **Missing Integration Provider Framework:** There is no `IntegrationProvider` abstraction defining `connect`, `sync`, `validate`, `publish`, and `get_metrics` interfaces.
- **Missing OAuth Management:** No secure encrypted storage, state parameters, refresh token flows, or secure redirection logic.
- **Missing Capability Matrix:** The system doesn't know what an integration provides (e.g., GA4 provides `metrics`, WordPress provides `publishing`).
- **Missing Sync Jobs:** No background workers exist to regularly synchronize data (e.g., pull GSC data into internal representations).

## 4. BrandContextService
**Current State:**
- `BrandContextService` fetches `Brand`, `Workspace`, `Audience`, `BrandVoice`, `Products`, `Competitors`, etc., and packages them into `AgentContext`.
- Operates reliably as a data aggregator.

**Gaps to fulfill OKR:**
- **No Dynamic Strategy Document Caching:** The strategy documents (ICP, Marketing Strategy, Brand Voice) do not currently compile into persistent, versioned artifacts with `stale` tracking.
- **No Vector Retrieval:** Document parsing is missing an embedded vector search pathway (`RETRIEVAL_NOT_CONFIGURED`), meaning uploaded files are not semantically queryable by agents.
- **No Performance/Execution Context:** The service doesn't fetch real-time active campaign structures or recent performance indicators to feed agents.

## 5. Content / Approval / Publishing
**Current State:**
- Database models for `Opportunity`, `ContentProject`, `ContentDraft`, `ContentApproval`, and `Campaign` exist.
- Basic CRUD APIs support them.

**Gaps to fulfill OKR:**
- **No Approval Policy Engine:** Hardcoded REST rules rather than an engine determining if "SOCIAL POST" needs explicit review versus "DRAFT" which requires none.
- **No Publishing Router:** The pipeline ends at `ContentApproval`. There is no `PublishingRouter` linking approved content to the specific Integration connection (e.g., WordPress, LinkedIn).
- **Missing Handoff State Machine:** Workflow states are disconnected; `ContentDraft` isn't seamlessly tied to a Celery publish job upon `ContentApproval` clearance.

## 6. Celery Worker Architecture
**Current State:**
- Operates a reliable worker processing `execute_agent_task`.
- Retries and connection limits have been hardened to withstand Redis timeouts.
- Task status routes to the `AgentRun` table (`RUNNING`, `COMPLETED`, `FAILED`).

**Gaps to fulfill OKR:**
- **Missing Integration Task Execution:** Celery only knows `AgentTask`; it lacks queues for `IntegrationSyncRun` or `PublishingAttempt`.
- **Missing Master AI CMO Cron Loop:** `celerybeat-schedule` does not execute the "Daily/Weekly CMO Loop" where the orchestrator autonomously queries metrics and assigns work without explicit human triggering.

## Next Steps
To begin Phase A and B, we must:
1. Re-architect the AI Gateway to support native LLM function/tool calling.
2. Build the `AgentRuntime` and `AgentDefinition` models to support standardized, managed agent executions with cost tracking and context injection.
