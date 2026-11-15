# Installation

## Requirements
- Python 3.12
- An API key from at least one LLM provider (Google Gemini, OpenAI or Anthropic)

## 1. Install dependencies
```bash
pip install -r requirements.txt
pip install uvicorn
```
`requirements.txt` pins `httpx<0.28`. Newer `httpx` versions break older `openai` releases
(error: `unexpected keyword argument 'proxies'`).

On Alpine Linux you may need build tools first and `--break-system-packages`:
```bash
apk add python3 python3-dev py3-pip build-base libffi-dev openssl-dev
pip install --break-system-packages -r requirements.txt
```

## 2. Configure the environment
Copy the example file. `.env` must be a **file**, not a folder.
```bash
cp .env.example .env
```
Edit `.env`:

| Variable | Purpose |
|---|---|
| `API_KEY` | Secret that clients send in the `x-api-key` header. Generate one yourself. |
| `GOOGLE_API_KEY` / `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | Provider keys. Fill at least one. |
| `SECRET_KEY` | Secret used for token generation. |
| `FASTAPI_ENV`, `FASTAPI_HOST`, `FASTAPI_PORT` | Server settings. |
| `CORS_ORIGINS`, `LOG_LEVEL`, `MAX_ITERATIONS`, `TIMEOUT` | Optional tuning. |

Generate a strong `API_KEY`:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
`API_KEY` is **not** a provider key. Never commit `.env`; it is listed in `.gitignore`.

### Provider selection
At startup the first provider that has a key is used, in this order:
OpenAI, then Anthropic, then Google. To use Gemini, leave `OPENAI_API_KEY` and
`ANTHROPIC_API_KEY` empty.

## 3. Run
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
Startup logs should contain `Initialized 4 agents using <provider>`.
Open `http://localhost:8000/docs` for the interactive API.

Note: `python main.py` fails because of `reload=True`; use the `uvicorn` command above.

## Troubleshooting
| Symptom | Cause and fix |
|---|---|
| `401 Invalid API key` | The `x-api-key` value does not match `API_KEY` in `.env`. Restart the server after editing `.env`. |
| `502 Task execution failed` | Read the server log. Common cause: provider quota exhausted (`429`). |
| `429` / `RESOURCE_EXHAUSTED` | Provider quota used up. Wait, use another model or key. |
| `404` on a Gemini model | The model name was retired. Pick a current model name. |
| `No module named 'uvicorn'` | Run `pip install uvicorn`. |
| `unexpected keyword argument 'proxies'` | Run `pip install "httpx<0.28"`. |
