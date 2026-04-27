"""Groq LLM client wrapper used by ArchMind agents."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL_NAME = "llama-3.3-70b-versatile"

_client: Groq | None = None


def _get_client() -> Groq:
    """Lazily build and cache a Groq client using GROQ_API_KEY."""
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to your .env file."
            )
        _client = Groq(api_key=api_key)
    return _client


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Call the Groq chat completion API and return the response text.

    Args:
        system_prompt: Instructions that shape the assistant's behavior.
        user_prompt: The user-provided content to act on.

    Returns:
        The assistant's response as plain text.

    Raises:
        RuntimeError: If the API key is missing or the API call fails.
    """
    try:
        client = _get_client()
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = completion.choices[0].message.content
        return content or ""
    except RuntimeError:
        raise
    except Exception as exc:  # noqa: BLE001 - surface provider errors uniformly
        raise RuntimeError(f"Groq API call failed: {exc}") from exc
