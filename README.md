# Agent-baj (Agent OS)

A small multi-agent API built with FastAPI. You send a task to a specialized agent
and it answers using an LLM provider (Google Gemini, OpenAI or Anthropic).

**Status: early prototype.** The core API and four text-generating agents work.
Many planned modules are still empty placeholders (see [Status](#status)).

## Agents

| `agent_type` | Role |
|---|---|
| `research` | Research and analysis |
| `coding` | Software engineering |
| `automation` | Workflow design (designs only, does not run anything) |
| `marketing` | Strategy and copywriting |

Each agent first drafts a short plan, then writes the final answer using its own role instructions.

## Quick start

```bash
git clone https://github.com/Boumehdiabde/Agent-baj
cd Agent-baj
pip install -r requirements.txt uvicorn
cp .env.example .env
```

Edit `.env`:
- `API_KEY`: a secret you choose; clients send it in the `x-api-key` header.
  Generate one with `python -c "import secrets; print(secrets.token_urlsafe(32))"`.
- One provider key: `GOOGLE_API_KEY`, `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`.
  The first provider that has a key is used (order: OpenAI, Anthropic, Google).

Run:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000/docs`, enter your `API_KEY` in `x-api-key`, and try `POST /execute`:

```json
{"task": "Suggest a one-week Instagram content plan for a beekeeping account", "agent_type": "marketing"}
```

Never commit your `.env` file.

## Documentation
- [Installation and troubleshooting](docs/installation.md)
- [API reference](docs/api-reference.md)

## Status

Working:
- FastAPI server, `x-api-key` authentication, interactive docs at `/docs`
- Four agents with role-specific instructions
- Gemini provider (over plain HTTP, with retries and model fallback), tested end to end

Implemented but less tested:
- OpenAI provider (the provider initializes; a full run depends on your account credits)
- Anthropic provider (untested)

Not implemented yet (empty files):
- Long-term and vector memory
- Terminal, web and GitHub tools
- Sandbox and permissions
- Hooks (notifications, auto-commit, command blocking)
- Skills such as Django

Agents currently only generate text. They do not execute code, browse the web or run commands.

## Limits to know about
- Free provider tiers have quotas. When a quota is used up the API returns `502`
  and the server log shows `429`.
- Model names change over time. If a provider returns `404` for the model, update the model name in `core/llm/provider.py`.
- If you expose the server publicly, every request uses **your** provider key and quota.

## Roadmap
1. Web search for the research agent
2. Real tools with a sandbox and permission checks
3. Short-term and long-term memory
4. Tests and a web interface

## License
No license has been specified yet.
