"""LLM client wrappers for NVIDIA NIM and Google Gemini.

NIM (Nemotron) handles high-volume structural/extraction calls.
Gemini handles reasoning + web-grounded benchmark lookups.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings

logger = logging.getLogger(__name__)


# ── NVIDIA NIM Client ─────────────────────────────────────────────────────────

class NIMClient:
    """Async wrapper around NVIDIA NIM API (OpenAI-compatible)."""

    def __init__(self):
        self.client = AsyncOpenAI(
            base_url=settings.nvidia_base_url,
            api_key=settings.nvidia_api_key,
        )
        self.model = settings.nvidia_model
        self._total_tokens = 0

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 4096,
        response_format: dict | None = None,
    ) -> str:
        """Send a chat completion request to NIM.

        Args:
            messages: List of {"role": "...", "content": "..."} dicts
            temperature: Sampling temperature (low for structured output)
            max_tokens: Max response tokens
            response_format: Optional {"type": "json_object"} for JSON mode

        Returns:
            The assistant's response text.
        """
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format:
            kwargs["response_format"] = response_format

        try:
            response = await self.client.chat.completions.create(**kwargs)
            self._total_tokens += response.usage.total_tokens if response.usage else 0
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"NIM API error: {e}")
            raise

    async def chat_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> dict | list:
        """Send a chat request and parse the response as JSON.

        Returns:
            Parsed JSON response.
        """
        # Request JSON output format
        response = await self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        # Try to parse JSON from the response
        return _extract_json(response)

    @property
    def total_tokens(self) -> int:
        return self._total_tokens


# ── Google Gemini Client ──────────────────────────────────────────────────────

class GeminiClient:
    """Wrapper around Google Gemini API with optional web grounding."""

    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model
        self._total_tokens = 0

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def chat(
        self,
        prompt: str,
        system_instruction: str | None = None,
        use_web_grounding: bool = False,
        temperature: float = 0.2,
    ) -> str:
        """Send a request to Gemini.

        Args:
            prompt: The user prompt
            system_instruction: Optional system instruction
            use_web_grounding: If True, enables Google Search grounding
            temperature: Sampling temperature

        Returns:
            The model's response text.
        """
        tools = []
        if use_web_grounding:
            tools = [types.Tool(google_search=types.GoogleSearch())]

        config = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=system_instruction,
        )
        if tools:
            config.tools = tools

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
            if response.usage_metadata:
                self._total_tokens += (
                    response.usage_metadata.prompt_token_count +
                    response.usage_metadata.candidates_token_count
                )
            return response.text or ""
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def chat_json(
        self,
        prompt: str,
        system_instruction: str | None = None,
        use_web_grounding: bool = False,
        temperature: float = 0.1,
    ) -> dict | list:
        """Send a request and parse the response as JSON.

        Returns:
            Parsed JSON response.
        """
        json_prompt = prompt + "\n\nRespond with valid JSON only, no markdown code fences."

        response_text = await self.chat(
            prompt=json_prompt,
            system_instruction=system_instruction,
            use_web_grounding=use_web_grounding,
            temperature=temperature,
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

_nim_client: NIMClient | None = None
_gemini_client: GeminiClient | None = None


def get_nim_client() -> NIMClient:
    """Get or create the NIM client singleton."""
    global _nim_client
    if _nim_client is None:
        _nim_client = NIMClient()
    return _nim_client


def get_gemini_client() -> GeminiClient:
    """Get or create the Gemini client singleton."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
