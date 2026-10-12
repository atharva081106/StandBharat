# StandBharat Performance Intelligence & Attribution Audit

## 1. Existing Data Foundation Assessment

### Models & Schema
- **PerformanceSnapshot**: Tracks individual post performance (`impressions`, `reach`, `engagements`, `engagement_rate`, etc.) per channel and external post ID.
- **TrafficMetrics**: Tracks daily `sessions`, `active_users`, `pageviews`, `engagement_rate`, and `conversions` segmented by `source`, `medium`, `campaign`, and `landing_page`.
- **SearchMetrics**: Tracks daily Google search performance (`clicks`, `impressions`, `ctr`, `position`) by `query` and `page`.
- **Opportunity**: Represents generated Next Best Actions with attributes like `title`, `description`, `impact`, `confidence`, `effort`, `priority`, and `status`.
- **ActivityEvent**: Generic tracking table used for logging events, which can be adapted to close the feedback loop on executed actions.
- **Publication** & **PublicationAttempt**: Exist in `app.publishing.models` tracking the real provider execution.

### Agents
- **PerformanceAgent**: Currently queries `PerformanceSnapshot`, uses AI to generate opportunities, and saves them to the DB.
- **AnalyticsAgent**: (Assumed to query Traffic/Search metrics for reporting).
- **GrowthAgent**: (Assumed to generate strategic opportunities).
- **AI CMO Agent**: Orchestrator that uses BrandContext and generated opportunities to output recommendations.

### Missing or Incomplete Elements
1. **Attribution Loop**: No explicit tie between a `Publication` (e.g., a LinkedIn post) and a downstream `TrafficMetrics` conversion. Needs a reliable UTM or URL parsing strategy.
2. **Scheduled Pipeline**: Celery `orchestrator_tick` exists, but there is no explicit `analyze_performance` Celery task that runs on a schedule to fetch data and trigger the PerformanceAgent.
3. **Execution Feedback**: Opportunities are created but there's no clear linkage mapping an approved Opportunity directly to an `ActivityEvent` or subsequent `PerformanceSnapshot` to measure if the recommendation worked.
4. **Provider Sync implementation**: GA4 and GSC successfully sync into `TrafficMetrics` and `SearchMetrics`. However, the social providers (LinkedIn, X, Reddit, etc.) currently return stubbed metrics (`0`) in their `get_metrics` implementation or do not sync historical post metrics into `PerformanceSnapshot`.

## 2. Capability Evaluation

- **Data Normalization**: `TrafficMetrics` and `PerformanceSnapshot` effectively normalize metrics across time periods, allowing isolated tenant-specific analysis.
- **Idempotency**: `Opportunity` generation in `PerformanceAgent` does simple deduplication by title, but lacks strict idempotency keys tied to data windows.
- **Data Sufficiency Rules**: Currently, `PerformanceAgent` runs if any data exists. It lacks a threshold (e.g., "Must have > 100 impressions to generate a confident recommendation").

## 3. Recommended Implementation Path
1. Update social providers to properly populate `PerformanceSnapshot` during syncs.
2. Build a unified Attribution module that joins `Publication` URLs (with UTM parameters) to `TrafficMetrics` to estimate impact.
3. Create a scheduled Celery task `analyze_performance` that runs daily.
4. Enhance `Opportunity` generation to include `target_entity` and `execution_status`, closing the loop by updating the opportunity when an agent executes a corresponding action.
