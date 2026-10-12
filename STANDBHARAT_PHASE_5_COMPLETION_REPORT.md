# StandBharat Phase 5: Performance Intelligence, Attribution & Autonomous Learning — Completion Report

## 1. Executive Summary
The performance intelligence layer has been successfully structured and unified across all endpoints. We implemented a unified tracking architecture utilizing `PerformanceSnapshot`, `TrafficMetrics`, and `SearchMetrics`. The automated learning pipeline has been scheduled via Celery to ensure StandBharat consistently learns from actual execution outcomes and attributes them correctly to user campaigns or external posts.

## 2. Implementations & Technical Upgrades

### Unified Performance Data Layer
- Verified that GA4 naturally maps downstream to `TrafficMetrics`.
- Verified that GSC maps directly to `SearchMetrics`.
- Social Providers (LinkedIn, X, Reddit, Facebook, Instagram, YouTube, TikTok) are structurally mapped to write to `PerformanceSnapshot` when data syncing executes (currently mostly stubbed due to missing real permissions, but the schema mapping is identical).

### Celery Pipeline & Autonomous Learning
- **New Task**: Created `analyze_performance_loop` in `app/worker.py`. This task binds the `PerformanceAgent` and `GrowthAgent` together into a scheduled daily learning loop.
- **Workflow**: 
  1. The task initiates an AgentRun context.
  2. `PerformanceAgent` ingests recent `PerformanceSnapshot` records.
  3. AI Gateway processes the raw structured JSON and identifies trends, outputting actionable signals and tactical `Opportunities`.
  4. `GrowthAgent` reviews these signals combined with GA4 and GSC data to synthesize high-level strategic directives.
- **Idempotency & Deduplication**: Managed natively in the Agents by comparing newly suggested opportunities against active `Opportunity` entries in the DB via title and content similarity matching before persisting them.

### Responsible Attribution & The Feedback Loop
- **Methodology**: Rather than hallucinating metrics, the attribution methodology exclusively utilizes explicit markers (UTM parameters mapped in GA4 payloads and external `publication_id` mapped via `PublisherConnection`). 
- **Closing the Loop**: The architecture connects `Opportunity` → `ContentProject` → `Publication` → `PerformanceSnapshot`. This unbroken chain ensures that when the `analyze_performance_loop` executes, the AI can correlate a previously recommended opportunity directly against the observed outcome of the external post it triggered.

## 3. Verification & Test Execution
- **Tests**: Ran the backend schema tests for new celery functions and `PerformanceSnapshot` ingestion paths.
- **Tenant Isolation**: Confirmed that queries inside the scheduled Celery workers (`analyze_performance_loop`) exclusively fetch data filtered by the specific `workspace_id` and `brand_id`.
- **UI Consistency**: Verified that the Next Best Action engine (Opportunities) natively flows into the frozen dashboard UI without needing design modifications. Opportunities correctly show empty states when `NOT_CONFIGURED`.

## 4. Known Blockers & Limitations
- **Social Metrics Availability**: Social metric pipelines into `PerformanceSnapshot` remain marked as `MOCKED` or `PARTIAL` because StandBharat cannot access full impression or reach metrics on profiles without Enterprise API scopes (LinkedIn), or App Reviews (Meta).
- **Revenue Attribution**: Direct revenue (CPA, LTV) cannot be calculated without CRM integrations or valid GA4 conversion events bearing `value` and `currency`. The system gracefully falls back to ignoring these calculations rather than guessing them.

## Definition of Success
The loop is closed. Agents can now look at previous executions, observe the actual outcomes, generate new evidence-backed recommendations, and execute them recursively while safely stopping and asking for human approval before causing destructive changes.
