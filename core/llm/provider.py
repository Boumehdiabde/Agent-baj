"""Base LLM provider interface and implementations."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class LLMProvider(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        pass


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        super().__init__(api_key)
        self.model = model
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key)
        except ImportError as exc:
            raise ImportError("Install the openai package to use this provider") from exc

    async def generate(self, prompt: str, **kwargs) -> str:
        return await self.chat([{"role": "user", "content": prompt}], **kwargs)

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 2048),
                temperature=kwargs.get("temperature", 0.7),
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            raise RuntimeError(f"OpenAI API request failed: {exc}") from exc

    def get_model_info(self) -> Dict[str, Any]:
        return {"provider": "openai", "model": self.model, "type": "chat"}


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-latest"):
        super().__init__(api_key)
        self.model = model
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(api_key=api_key)
        except ImportError as exc:
            raise ImportError("Install the anthropic package to use this provider") from exc

    async def generate(self, prompt: str, **kwargs) -> str:
        return await self.chat([{"role": "user", "content": prompt}], **kwargs)

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        try:
            system_messages = [m["content"] for m in messages if m.get("role") == "system"]
            conversation = [m for m in messages if m.get("role") in {"user", "assistant"}]
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 2048),
                system="\n\n".join(system_messages),
                messages=conversation,
            )
            return "".join(block.text for block in response.content if hasattr(block, "text"))
        except Exception as exc:
            raise RuntimeError(f"Anthropic API request failed: {exc}") from exc

    def get_model_info(self) -> Dict[str, Any]:
        return {"provider": "anthropic", "model": self.model, "type": "chat"}


class GoogleProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        super().__init__(api_key)
        self.model = model
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(model)
        except ImportError as exc:
            raise ImportError("Install google-generativeai to use this provider") from exc

    async def generate(self, prompt: str, **kwargs) -> str:
        return await self.chat([{"role": "user", "content": prompt}], **kwargs)

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        import asyncio
        try:
            prompt = "\n\n".join(
                f"{message['role']}: {message['content']}" for message in messages
            )
            response = await asyncio.to_thread(self.client.generate_content, prompt)
            return getattr(response, "text", "") or ""
        except Exception as exc:
            raise RuntimeError(f"Google API request failed: {exc}") from exc

    def get_model_info(self) -> Dict[str, Any]:
        return {"provider": "google", "model": self.model, "type": "generative"}


def get_llm_provider(provider: str, api_key: str, **kwargs) -> LLMProvider:
    provider = provider.lower()
    if provider == "openai":
        return OpenAIProvider(api_key, model=kwargs.get("model", "gpt-4o-mini"))
    if provider == "anthropic":
        return AnthropicProvider(api_key, model=kwargs.get("model", "claude-3-5-sonnet-latest"))
    if provider == "google":
        return GoogleRestProvider(api_key, model=kwargs.get("model", "gemini-3.8-flash"))
    raise ValueError(f"Unknown LLM provider: {provider}")


class GoogleRestProvider(LLMProvider):
    """Gemini over plain HTTP, with retries and model fallback."""

    FALLBACKS = ["gemini-3.5-flash", "gemini-flash-latest"]

    def __init__(self, api_key: str, model: str = "gemini-3.8-flash"):
        super().__init__(api_key)
        self.model = model

    async def generate(self, prompt: str, **kwargs) -> str:
        return await self.chat([{"role": "user", "content": prompt}], **kwargs)

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        import asyncio
        import httpx
        system = "\n\n".join(m["content"] for m in messages if m.get("role") == "system")
        contents = [
            {"role": "model" if m["role"] == "assistant" else "user",
             "parts": [{"text": m["content"]}]}
            for m in messages if m.get("role") in {"user", "assistant"}
        ]
        body = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", 2048),
                "temperature": kwargs.get("temperature", 0.7),
            },
        }
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}

        last_error = "unknown error"
        for model in [self.model] + [m for m in self.FALLBACKS if m != self.model]:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            for attempt in range(3):
                try:
                    async with httpx.AsyncClient(timeout=60) as client:
                        resp = await client.post(url, json=body, headers={"x-goog-api-key": self.api_key})
                except Exception as exc:
                    last_error = f"{model}: {exc}"
                    await asyncio.sleep(2 * (attempt + 1))
                    continue
                if resp.status_code == 200:
                    try:
                        parts = resp.json()["candidates"][0]["content"]["parts"]
                        return "".join(p.get("text", "") for p in parts)
                    except Exception as exc:
                        last_error = f"{model}: unexpected response ({exc}): {resp.text[:200]}"
                        break
                last_error = f"{model}: HTTP {resp.status_code}: {resp.text[:300]}"
                if resp.status_code in (429, 500, 502, 503, 504):
                    await asyncio.sleep(2 * (attempt + 1))
                    continue
                break
        raise RuntimeError(f"Google API request failed: {last_error}")

    def get_model_info(self) -> Dict[str, Any]:
        return {"provider": "google", "model": self.model, "type": "chat"}
