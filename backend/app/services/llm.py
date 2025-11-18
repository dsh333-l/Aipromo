from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


@dataclass
class LLMResponse:
    content: str
    raw: Dict[str, Any]


class LLMClient:
    """Lightweight wrapper around OpenAI-compatible chat completion API."""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.timeout = float(os.getenv("OPENAI_TIMEOUT", "45"))

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> LLMResponse:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY 未配置，无法调用真实模型。")

        url = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.model, "messages": messages, "temperature": temperature}

        response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return LLMResponse(content=content, raw=data)


def extract_json_block(text: str) -> str:
    """Return first JSON object found in the response text."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    return text.strip()


llm_client = LLMClient()
