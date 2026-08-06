"""LLM client wrappers for Google Gemini.

Gemini handles high-volume structural/extraction calls, benchmarking, and reporting.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any
import httpx


from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings

logger = logging.getLogger(__name__)


# ── NVIDIA NIM Client ────────────────────────────────────────────────────────────

class NvidiaNimClient:
    """Async wrapper around NVIDIA NIM (OpenAI compatible) API."""

    def __init__(self):
        self.api_key = settings.nvidia_nim_api_key
        self.model = settings.nvidia_nim_model
        self.base_url = "https://integrate.api.nvidia.com/v1"
        self._total_tokens = 0
        self._semaphore = asyncio.Semaphore(settings.nvidia_max_concurrent_requests)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=120.0
        )

    @retry(
        stop=stop_after_attempt(8),
        wait=wait_exponential(multiplier=2, min=5, max=65),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int | None = 2048,
        response_schema: dict | None = None,
    ) -> str:
        """Send a chat completion request to NVIDIA NIM."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        # We can append JSON instructions manually for Kimi if needed, 
        # or just rely on the system prompt. Some endpoints support response_format.
        if response_schema:
            payload["response_format"] = {"type": "json_object"}

        async with self._semaphore:
            response = await self.client.post("/chat/completions", json=payload)
            
            if response.status_code != 200:
                logger.error(f"NVIDIA NIM API error: {response.text}")
                response.raise_for_status()

            data = response.json()
            if "usage" in data and "total_tokens" in data["usage"]:
                self._total_tokens += data["usage"]["total_tokens"]

            return data["choices"][0]["message"]["content"]

    async def chat_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int | None = 2048,
    ) -> dict | list:
        """Send a chat request and parse the response as JSON."""
        # Check if the last message mentions JSON, if not, append to prompt for Kimi
        last_msg = messages[-1]["content"]
        if "json" not in last_msg.lower():
            messages[-1]["content"] += "\n\nYou must output a valid JSON object."

        response_text = await self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_schema={"type": "json_object"}
        )
        return _extract_json(response_text)

    @property
    def total_tokens(self) -> int:
        return self._total_tokens


# ── Shared utilities ──────────────────────────────────────────────────────────

def _extract_json(text: str) -> dict | list:
    """Extract JSON from a text response, handling markdown code fences."""
    text = text.strip()

    # Strip markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines (fences)
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object/array within the text
        for start_char, end_char in [("{", "}"), ("[", "]")]:
            start_idx = text.find(start_char)
            end_idx = text.rfind(end_char)
            if start_idx != -1 and end_idx > start_idx:
                try:
                    return json.loads(text[start_idx : end_idx + 1])
                except json.JSONDecodeError:
                    continue

        logger.warning(f"Failed to parse JSON from response: {text[:200]}")
        return {"raw_response": text, "parse_error": True}


# ── Singleton instances ───────────────────────────────────────────────────────

_nim_client: NvidiaNimClient | None = None

def get_nim_client() -> NvidiaNimClient:
    """Get or create the NVIDIA NIM client singleton."""
    global _nim_client
    if _nim_client is None:
        _nim_client = NvidiaNimClient()
    return _nim_client
