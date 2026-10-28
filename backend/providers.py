import os
import requests
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)
load_dotenv()  # Fallback for system env vars

class BaseLLMClient(ABC):
    """Abstract Base Class for Free LLM Providers"""
    name: str = "base"

    @abstractmethod
    def complete(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None) -> str:
        pass


class GroqClient(BaseLLMClient):
    """Groq Cloud LPU Client (100% Free Tier - ultra low latency)"""
    name: str = "groq"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"
        # High capability models verified for user's account
        self.heavy_model = "openai/gpt-oss-120b"
        self.fast_model = "openai/gpt-oss-20b"
        self.fallback_model = "openai/gpt-oss-20b"

    def complete(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None) -> str:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept-Encoding": "identity"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        target_model = model or self.heavy_model
        payload = {
            "model": target_model,
            "messages": messages,
            "temperature": 0.2
        }

        # Auto-retry on 429
        for attempt in range(3):
            try:
                response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=25)
                if response.status_code == 429:
                    time.sleep(2)
                    continue
                if response.status_code != 200:
                    # Try fallback model
                    if target_model != self.fallback_model:
                        payload["model"] = self.fallback_model
                        fallback_res = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=25)
                        if fallback_res.status_code == 200:
                            return fallback_res.json()["choices"][0]["message"]["content"]
                    response.raise_for_status()

                return response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                if attempt == 2:
                    raise e
                time.sleep(1)

        raise RuntimeError("Groq request failed after retries.")


class OpenRouterFreeClient(BaseLLMClient):
    """OpenRouter Client restricted STRICTLY to verified 100% :free models (Nemotron)"""
    name: str = "openrouter"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        # Verified active free Nemotron model
        self.free_models = [
            "nvidia/nemotron-3.5-lightning:free",
            "nvidia/nemotron-3.5-super-vl:free",
            "google/gemma-2-9b-it:free"
        ]
        self.default_model = self.free_models[0]

    def complete(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None) -> str:
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured.")

        target_model = model or self.default_model
        if not target_model.endswith(":free"):
            target_model = f"{target_model}:free"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://versatile-ai-delta.vercel.app/",
            "X-Title": "VersatileAI",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": target_model,
            "messages": messages
        }

        response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


class NvidiaNemotronClient(BaseLLMClient):
    """Direct NVIDIA NIM Client"""
    name: str = "nvidia"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        self.base_url = "https://integrate.api.nvidia.com/v1"
        self.default_model = "nvidia/llama-3.1-nemotron-70b-instruct"

    def complete(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None) -> str:
        if not self.api_key:
            raise ValueError("NVIDIA_API_KEY is not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1500
        }

        response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


class GeminiClient(BaseLLMClient):
    """Google Gemini Client (Google AI Studio Free Tier)"""
    name: str = "gemini"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai"
        self.default_model = "gemini-2.0-flash"

    def complete(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None) -> str:
        if not self.api_key or not self.api_key.startswith("AIzaSy"):
            raise ValueError("GEMINI_API_KEY must be a valid Google AI Studio key starting with 'AIzaSy'.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": 0.2
        }

        response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=25)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


class ModelRouter:
    """Universal Free Multi-Model Router with Automatic Failover"""
    def __init__(self):
        self.providers: Dict[str, BaseLLMClient] = {}
        
        # Groq (blazing fast LPU)
        if os.getenv("GROQ_API_KEY"):
            self.providers["groq"] = GroqClient()
            
        # OpenRouter (verified free Nemotron)
        if os.getenv("OPENROUTER_API_KEY"):
            self.providers["openrouter"] = OpenRouterFreeClient()

        # NVIDIA direct
        if os.getenv("NVIDIA_API_KEY"):
            self.providers["nvidia"] = NvidiaNemotronClient()

        # Gemini (only if valid AIzaSy key)
        gemini_k = os.getenv("GEMINI_API_KEY", "")
        if gemini_k and gemini_k.startswith("AIzaSy"):
            self.providers["gemini"] = GeminiClient()

    def get_available_providers(self) -> List[str]:
        return list(self.providers.keys())

    def execute(self, prompt: str, system_prompt: Optional[str] = None, preferred: str = "groq", fast: bool = False) -> str:
        """Executes LLM call with automated cascade failover across verified free models"""
        if not self.providers:
            raise RuntimeError("No LLM provider keys configured in .env file.")

        # Determine priority order - Groq first, then OpenRouter (Nemotron free), then others
        order = [preferred] + [p for p in ["groq", "openrouter", "nvidia", "gemini"] if p != preferred]
        
        last_error = None
        for provider_name in order:
            client = self.providers.get(provider_name)
            if not client:
                continue

            try:
                model_override = None
                if fast and isinstance(client, GroqClient):
                    model_override = client.fast_model

                return client.complete(prompt, system_prompt=system_prompt, model=model_override)
            except Exception as e:
                print(f"[ModelRouter] Provider '{provider_name}' notice: {e}. Trying next free model...")
                last_error = e
                continue

        raise RuntimeError(f"All free model providers failed. Last error: {last_error}")
