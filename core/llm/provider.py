"""Base LLM Provider interface"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from prompt"""
        pass
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat interface for conversational AI"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(api_key)
        self.model = model
        try:
            import openai
            openai.api_key = api_key
            self.client = openai.AsyncOpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI"""
        try:
            response = await self.client.completions.create(
                model=self.model,
                prompt=prompt,
                max_tokens=kwargs.get("max_tokens", 2048),
                temperature=kwargs.get("temperature", 0.7),
            )
            return response.choices[0].text.strip()
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat with OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 2048),
                temperature=kwargs.get("temperature", 0.7),
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get OpenAI model information"""
        return {
            "provider": "openai",
            "model": self.model,
            "type": "chat"
        }


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        super().__init__(api_key)
        self.model = model
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(api_key=api_key)
        except ImportError:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using Claude"""
        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 2048),
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text.strip()
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat with Claude"""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 2048),
                messages=messages,
            )
            return response.content[0].text.strip()
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Claude model information"""
        return {
            "provider": "anthropic",
            "model": self.model,
            "type": "chat"
        }


class GoogleProvider(LLMProvider):
    """Google Generative AI provider"""
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        super().__init__(api_key)
        self.model = model
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(model)
        except ImportError:
            raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using Google"""
        try:
            response = self.client.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise RuntimeError(f"Google API error: {str(e)}")
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat with Google"""
        try:
            chat = self.client.start_chat()
            response = chat.send_message(messages[-1]["content"] if messages else "")
            return response.text.strip()
        except Exception as e:
            raise RuntimeError(f"Google API error: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Google model information"""
        return {
            "provider": "google",
            "model": self.model,
            "type": "generative"
        }


def get_llm_provider(provider: str, api_key: str, **kwargs) -> LLMProvider:
    """Factory function to get LLM provider"""
    provider = provider.lower()
    
    if provider == "openai":
        return OpenAIProvider(api_key, model=kwargs.get("model", "gpt-4"))
    elif provider == "anthropic":
        return AnthropicProvider(api_key, model=kwargs.get("model", "claude-3-opus-20240229"))
    elif provider == "google":
        return GoogleProvider(api_key, model=kwargs.get("model", "gemini-pro"))
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
