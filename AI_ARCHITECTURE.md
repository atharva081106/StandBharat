# AI Architecture

## 1. AI Gateway
All AI interactions are routed through a unified **AI Gateway**. This ensures consistent rate limiting, error handling, retries, and usage tracking.

## 2. Providers
The architecture supports multiple providers and does not hard-code a single solution:
- **Generation:** OpenAI, Anthropic, Gemini, Groq/OpenAI-compatible
- **Embeddings:** Jina, and other future providers

**Important:** Generation and embeddings MUST be maintained as separate abstractions.

## 3. Usage Tracking & Observability
Every AI API call must be trackable. 
The following metadata is recorded for every operation:
- `provider`
- `model`
- `operation` (e.g., generation, embedding)
- `tokens` (prompt, completion, total)
- `estimated_cost`
- `workspace_id`
- `brand_id`
- `agent_id`
- `task_id`
- `run_id`
- `timestamp`

## 4. Brand Brain (RAG Context)
The AI architecture utilizes **Brand Brain** to provide relevant context to agents. Brand context (product info, positioning, guidelines) is vectorized via pgvector and injected into agent prompts contextually based on the task.
