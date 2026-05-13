from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from typing import Protocol

import httpx
from anthropic import AsyncAnthropicVertex
from loguru import logger

from cc_monitor.models import AgentState

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

_LLM_MAX_RETRIES = 3

_ASSISTANT_PREFILL = "<think>\n\n</think>\n```json"

_RESULT_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "state": {"type": "string", "enum": ["working", "idle", "needs_input"]},
        "summary": {"type": "string", "description": "5-15 word task description"},
    },
    "required": ["state", "summary"],
}


@dataclass(frozen=True)
class LLMResult:
    state: AgentState
    summary: str


class LLMProvider(Protocol):
    async def classify(self, system_prompt: str, user_prompt: str) -> LLMResult: ...


def _parse_llm_json(raw: str) -> dict[str, str]:
    """Extract JSON object from raw LLM text, stripping control chars."""
    cleaned = _CONTROL_CHAR_RE.sub("", raw)
    m = _JSON_RE.search(cleaned)
    if m:
        return json.loads(m.group())  # type: ignore[no-any-return]
    return {}


def _validate_state(state: str) -> AgentState:
    if state in ("working", "idle", "needs_input"):
        return state  # type: ignore[return-value]
    return "idle"


class OllamaProvider:
    def __init__(self, model: str, base_url: str | None = None) -> None:
        self.model = model
        self.base_url = base_url or os.environ.get(
            "CC_MONITOR_LLM_BASE_URL", "http://localhost:11434"
        )

    async def classify(self, system_prompt: str, user_prompt: str) -> LLMResult:
        async with httpx.AsyncClient() as client:
            for attempt in range(_LLM_MAX_RETRIES):
                t0 = time.monotonic()
                try:
                    resp = await client.post(
                        f"{self.base_url}/api/chat",
                        json={
                            "model": self.model,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt},
                                {
                                    "role": "assistant",
                                    "content": _ASSISTANT_PREFILL,
                                },
                            ],
                            "stream": False,
                        },
                        timeout=60.0,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    raw = data.get("message", {}).get("content", "").strip()
                    combined = _ASSISTANT_PREFILL + raw
                    result = _parse_llm_json(combined)
                    elapsed_ms = (time.monotonic() - t0) * 1000
                    state = _validate_state(result.get("state", "idle"))
                    summary = result.get("summary", "")
                    logger.debug(
                        "ollama classify -> {} {!r} ({:.0f}ms)",
                        state,
                        summary,
                        elapsed_ms,
                    )
                    return LLMResult(state=state, summary=summary)
                except Exception as e:
                    elapsed_ms = (time.monotonic() - t0) * 1000
                    logger.debug(
                        "ollama attempt {}/{} failed ({:.0f}ms): {}",
                        attempt + 1,
                        _LLM_MAX_RETRIES,
                        elapsed_ms,
                        e,
                    )
        raise RuntimeError(f"OllamaProvider failed after {_LLM_MAX_RETRIES} retries")


class AnthropicVertexProvider:
    def __init__(self, model: str) -> None:
        self.model = model

    async def classify(self, system_prompt: str, user_prompt: str) -> LLMResult:
        client = AsyncAnthropicVertex()
        for attempt in range(_LLM_MAX_RETRIES):
            t0 = time.monotonic()
            try:
                message = await client.messages.create(
                    model=self.model,
                    max_tokens=256,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                raw = message.content[0].text  # type: ignore[union-attr]
                result = _parse_llm_json(raw)
                elapsed_ms = (time.monotonic() - t0) * 1000
                state = _validate_state(result.get("state", "idle"))
                summary = result.get("summary", "")
                logger.debug(
                    "anthropic-vertex classify -> {} {!r} ({:.0f}ms)",
                    state,
                    summary,
                    elapsed_ms,
                )
                return LLMResult(state=state, summary=summary)
            except Exception as e:
                elapsed_ms = (time.monotonic() - t0) * 1000
                logger.debug(
                    "anthropic-vertex attempt {}/{} failed ({:.0f}ms): {}",
                    attempt + 1,
                    _LLM_MAX_RETRIES,
                    elapsed_ms,
                    e,
                )
        raise RuntimeError(
            f"AnthropicVertexProvider failed after {_LLM_MAX_RETRIES} retries"
        )


_PROVIDERS: dict[str, type[OllamaProvider] | type[AnthropicVertexProvider]] = {
    "ollama": OllamaProvider,
    "anthropic-vertex": AnthropicVertexProvider,
}

_DEFAULT_PROVIDER_MODEL = "anthropic-vertex/claude-haiku-4-5@20251001"


def resolve_provider(provider_model_str: str | None = None) -> LLMProvider:
    """Parse 'provider/model_name' and return an LLMProvider instance.

    Examples:
        resolve_provider("ollama/qwen3.5:4b")
        resolve_provider("anthropic-vertex/claude-sonnet-4-20250514")
    """
    raw = provider_model_str or _DEFAULT_PROVIDER_MODEL
    parts = raw.split("/", maxsplit=1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(
            f"Invalid provider/model format: {raw!r}. "
            f"Expected 'provider/model_name' (e.g. 'ollama/qwen3.5:4b')"
        )
    provider_name, model_name = parts
    if provider_name not in _PROVIDERS:
        raise ValueError(
            f"Unknown provider: {provider_name!r}. "
            f"Available: {', '.join(sorted(_PROVIDERS))}"
        )
    cls = _PROVIDERS[provider_name]
    if cls is OllamaProvider:
        return OllamaProvider(model=model_name)
    return AnthropicVertexProvider(model=model_name)
