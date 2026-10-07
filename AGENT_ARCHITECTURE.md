# Agent Architecture

## 1. Agent Framework
StandBharat utilizes an extensible Agent Framework designed so new agents can be added without rewriting the orchestration system.

## 2. Agent Contract
Every agent must conform to a strict interface:
- `id`: Unique identifier
- `type`: Agent categorization
- `name`: Human-readable name
- `description`: Capabilities overview
- `capabilities`: Specific actions supported
- `input_schema`: Expected input data structure
- `output_schema`: Expected output data structure
- `permissions`: Required system permissions
- `autonomy_level`: Level of supervision required
- `cost_estimate`: Estimated resource/token cost
- `execution_method`: How the agent runs (e.g., synchronous, async task)
- `validation`: Data integrity checks
- `status`: Current state
- `retry_behavior`: How to handle transient failures

## 3. Agent States
- `QUEUED`
- `RUNNING`
- `WAITING_FOR_APPROVAL`
- `COMPLETED`
- `FAILED`
- `RETRYING`
- `CANCELLED`

## 4. Permissions & Approvals
Agents declare required permissions: `READ`, `WRITE`, `PUBLISH`, `EXTERNAL_ACTION`, `CODE_MODIFICATION`, `FINANCIAL_ACTION`.
High-risk actions route through the Approval System:
- `ANALYSIS` → Autonomous
- `DRAFT` → Autonomous
- `SCHEDULE` → Requires Approval
- `PUBLISH` → Requires Approval
- `FINANCIAL ACTION` → Requires Approval
- `DESTRUCTIVE ACTION` → Never Autonomous

## 5. List of Initial Agents
1. Analytics Agent
2. SEO Agent
3. GEO / AI Search Agent
4. Writer / Content Agent
5. Growth Agent
6. Competitor Intelligence Agent
7. LinkedIn Agent
8. X Agent
9. Reddit Agent
10. Influencer Agent
11. UGC / Creative Agent
12. Coding / Technical SEO Agent
13. Campaign Agent
14. Revenue Intelligence Agent
