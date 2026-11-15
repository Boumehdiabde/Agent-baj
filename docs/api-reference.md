# API Reference

Base URL: `http://localhost:8000`. Interactive docs: `/docs`.

## Authentication
Protected endpoints require the header `x-api-key: <API_KEY>` (the value of `API_KEY` in `.env`).

| Status | Meaning |
|---|---|
| `401` `API key required` | Header missing |
| `401` `Invalid API key` | Header does not match |

## Agents
| `agent_type` | Role |
|---|---|
| `research` | Research and analysis |
| `coding` | Software engineering |
| `automation` | Workflow design (does not run workflows) |
| `marketing` | Strategy and copywriting |

## Endpoints

### `GET /` (public)
Basic service information.

### `GET /health` (public)
```json
{"status": "healthy", "environment": "development", "agents_available": 4}
```

### `GET /agents` (auth)
Lists the available agents.

### `POST /execute` (auth)
Request:
```json
{"task": "Write a Python function that checks if a number is prime", "agent_type": "coding"}
```
Response `200`:
```json
{"task": "...", "agent_type": "coding", "result": "...", "status": "..."}
```
Errors: `422` invalid body, `502` task execution failed (see server logs).

Example:
```bash
curl -X POST http://localhost:8000/execute \
  -H "x-api-key: $API_KEY" -H "Content-Type: application/json" \
  -d '{"task": "Suggest a one-week Instagram content plan", "agent_type": "marketing"}'
```

### `GET /agent/{agent_type}/info` (auth)
Details about one agent.

### `POST /token` (auth)
Generates a token for a `user_id`.

### `GET /router/stats` (auth)
Router statistics.

## How a task runs
1. The agent calls the model to draft a short plan.
2. The agent calls the model again with its role instructions, the plan and recent conversation.
3. The answer is returned in `result`.

## Known limitations
- Several modules are still empty placeholders: long-term and vector memory, the terminal,
  web and GitHub tools, sandbox and permissions, hooks.
- Agents do not execute code or actions; they only generate text.
- Only one provider is used per server run.
- The Gemini provider is the most tested one; the Anthropic provider is untested.
