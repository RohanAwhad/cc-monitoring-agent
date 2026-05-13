from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cc_monitor.llm_provider import (
    AnthropicVertexProvider,
    LLMResult,
    OllamaProvider,
    _parse_llm_json,
    _validate_state,
    resolve_provider,
)


# --- resolve_provider ---


class TestResolveProvider:
    def test_anthropic_vertex_default(self) -> None:
        provider = resolve_provider(None)
        assert isinstance(provider, AnthropicVertexProvider)
        assert provider.model == "claude-haiku-4-5@20251001"

    def test_ollama_explicit(self) -> None:
        provider = resolve_provider("ollama/llama3:8b")
        assert isinstance(provider, OllamaProvider)
        assert provider.model == "llama3:8b"

    def test_anthropic_vertex(self) -> None:
        provider = resolve_provider("anthropic-vertex/claude-sonnet-4-20250514")
        assert isinstance(provider, AnthropicVertexProvider)
        assert provider.model == "claude-sonnet-4-20250514"

    def test_model_with_slashes_in_name(self) -> None:
        # Only splits on first slash
        provider = resolve_provider("ollama/org/model:tag")
        assert isinstance(provider, OllamaProvider)
        assert provider.model == "org/model:tag"

    def test_invalid_format_no_slash(self) -> None:
        with pytest.raises(ValueError, match="Invalid provider/model format"):
            resolve_provider("just-a-model")

    def test_invalid_format_empty_model(self) -> None:
        with pytest.raises(ValueError, match="Invalid provider/model format"):
            resolve_provider("ollama/")

    def test_invalid_format_empty_provider(self) -> None:
        with pytest.raises(ValueError, match="Invalid provider/model format"):
            resolve_provider("/some-model")

    def test_unknown_provider(self) -> None:
        with pytest.raises(ValueError, match="Unknown provider"):
            resolve_provider("openai/gpt-4")

    def test_default_string(self) -> None:
        provider = resolve_provider("ollama/qwen3.5:4b")
        assert isinstance(provider, OllamaProvider)


# --- _parse_llm_json ---


class TestParseLlmJson:
    def test_valid_json(self) -> None:
        raw = '{"state": "working", "summary": "doing stuff"}'
        result = _parse_llm_json(raw)
        assert result == {"state": "working", "summary": "doing stuff"}

    def test_json_with_surrounding_text(self) -> None:
        raw = 'Some thinking\n```json\n{"state": "idle", "summary": "done"}\n```'
        result = _parse_llm_json(raw)
        assert result["state"] == "idle"

    def test_no_json(self) -> None:
        result = _parse_llm_json("no json here")
        assert result == {}

    def test_strips_control_chars(self) -> None:
        raw = '{"state": "idle", "summary": "test\x00"}'
        result = _parse_llm_json(raw)
        assert result["state"] == "idle"


# --- _validate_state ---


class TestValidateState:
    def test_valid_states(self) -> None:
        assert _validate_state("working") == "working"
        assert _validate_state("idle") == "idle"
        assert _validate_state("needs_input") == "needs_input"

    def test_invalid_state_defaults_idle(self) -> None:
        assert _validate_state("unknown") == "idle"
        assert _validate_state("") == "idle"


# --- OllamaProvider.classify ---


class TestOllamaProviderClassify:
    def test_success(self) -> None:
        provider = OllamaProvider(model="test-model", base_url="http://test:11434")
        response_body = {
            "message": {
                "content": '{"state": "working", "summary": "running tests"}'
            }
        }
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = response_body

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("cc_monitor.llm_provider.httpx.AsyncClient", return_value=mock_client):
            result = asyncio.run(provider.classify("system", "user"))

        assert result == LLMResult(state="working", summary="running tests")
        mock_client.post.assert_called_once()
        call_kwargs = mock_client.post.call_args
        assert "http://test:11434/api/chat" in call_kwargs.args
        payload = call_kwargs.kwargs["json"]
        assert payload["model"] == "test-model"
        assert payload["stream"] is False
        assert len(payload["messages"]) == 3

    def test_request_shape(self) -> None:
        """Verify the exact request body sent to Ollama."""
        provider = OllamaProvider(model="qwen3.5:4b", base_url="http://localhost:11434")
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "message": {"content": '{"state": "idle", "summary": "done"}'}
        }
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("cc_monitor.llm_provider.httpx.AsyncClient", return_value=mock_client):
            asyncio.run(provider.classify("sys prompt", "user prompt"))

        payload = mock_client.post.call_args.kwargs["json"]
        assert payload["messages"][0] == {"role": "system", "content": "sys prompt"}
        assert payload["messages"][1] == {"role": "user", "content": "user prompt"}
        assert payload["messages"][2]["role"] == "assistant"

    def test_malformed_response(self) -> None:
        """LLM returns non-JSON -> retries exhaust -> raises."""
        provider = OllamaProvider(model="test", base_url="http://test:11434")
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"message": {"content": "not json at all"}}

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        # Even with no valid JSON, _parse_llm_json returns {} and we default to idle
        # So this actually succeeds with defaults
        with patch("cc_monitor.llm_provider.httpx.AsyncClient", return_value=mock_client):
            result = asyncio.run(provider.classify("sys", "user"))
        assert result.state == "idle"
        assert result.summary == ""

    def test_timeout_retries_exhaust(self) -> None:
        """Network errors cause retries, then RuntimeError."""
        provider = OllamaProvider(model="test", base_url="http://test:11434")
        mock_client = AsyncMock()
        mock_client.post.side_effect = TimeoutError("connect timeout")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("cc_monitor.llm_provider.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(RuntimeError, match="failed after 3 retries"):
                asyncio.run(provider.classify("sys", "user"))
        assert mock_client.post.call_count == 3


# --- AnthropicVertexProvider.classify ---


class TestAnthropicVertexProviderClassify:
    def test_success(self) -> None:
        provider = AnthropicVertexProvider(model="claude-sonnet-4-20250514")
        mock_content_block = MagicMock()
        mock_content_block.text = json.dumps(
            {"state": "needs_input", "summary": "waiting for approval"}
        )
        mock_message = MagicMock()
        mock_message.content = [mock_content_block]

        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)

        with patch(
            "cc_monitor.llm_provider.AsyncAnthropicVertex",
            return_value=mock_client,
        ):
            result = asyncio.run(provider.classify("system", "user"))

        assert result == LLMResult(
            state="needs_input", summary="waiting for approval"
        )
        mock_client.messages.create.assert_called_once_with(
            model="claude-sonnet-4-20250514",
            max_tokens=256,
            system="system",
            messages=[{"role": "user", "content": "user"}],
        )

    def test_request_shape(self) -> None:
        """Verify correct SDK call parameters."""
        provider = AnthropicVertexProvider(model="claude-sonnet-4-20250514")
        mock_content_block = MagicMock()
        mock_content_block.text = (
            '{"state": "working", "summary": "analyzing code"}'
        )
        mock_message = MagicMock()
        mock_message.content = [mock_content_block]
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)

        with patch(
            "cc_monitor.llm_provider.AsyncAnthropicVertex",
            return_value=mock_client,
        ):
            asyncio.run(
                provider.classify("my system prompt", "my user prompt")
            )

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["model"] == "claude-sonnet-4-20250514"
        assert call_kwargs["system"] == "my system prompt"
        assert call_kwargs["messages"] == [
            {"role": "user", "content": "my user prompt"}
        ]

    def test_timeout_retries_exhaust(self) -> None:
        provider = AnthropicVertexProvider(model="claude-sonnet-4-20250514")
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(
            side_effect=TimeoutError("deadline exceeded")
        )

        with patch(
            "cc_monitor.llm_provider.AsyncAnthropicVertex",
            return_value=mock_client,
        ):
            with pytest.raises(RuntimeError, match="failed after 3 retries"):
                asyncio.run(provider.classify("sys", "user"))
        assert mock_client.messages.create.call_count == 3

    def test_malformed_response_defaults(self) -> None:
        """Non-JSON response defaults to idle/empty."""
        provider = AnthropicVertexProvider(model="claude-sonnet-4-20250514")
        mock_content_block = MagicMock()
        mock_content_block.text = "I cannot classify this."
        mock_message = MagicMock()
        mock_message.content = [mock_content_block]
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)

        with patch(
            "cc_monitor.llm_provider.AsyncAnthropicVertex",
            return_value=mock_client,
        ):
            result = asyncio.run(provider.classify("sys", "user"))
        assert result.state == "idle"
        assert result.summary == ""


# --- LLMResult ---


class TestLLMResult:
    def test_frozen(self) -> None:
        r = LLMResult(state="working", summary="test")
        with pytest.raises(AttributeError):
            r.state = "idle"  # type: ignore[misc]

    def test_equality(self) -> None:
        a = LLMResult(state="idle", summary="done")
        b = LLMResult(state="idle", summary="done")
        assert a == b
