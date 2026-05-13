# Roadmap

## Current State (v0.3.1)

- Core pipeline functional: discover -> analyze -> display
- Protocol-based LLM provider abstraction (Ollama + Anthropic Vertex)
- Default model: `anthropic-vertex/claude-haiku-4-5@20251001`
- Supports: Claude Code, OpenCode, Gemini CLI, Codex CLI
- Two output modes: one-shot status, continuous watch
- 96 tests, 93% coverage, mypy strict

## Completed Milestones

### v0.1.0 (Build Phase)
- [x] Core data model (`AgentSession`)
- [x] Tmux pane discovery via `list-panes` + process verification
- [x] Regex-based state detection (working/idle/needs_input)
- [x] Rich table display
- [x] CLI with argparse (`ccm status`, `ccm watch`)
- [x] Structured logging (loguru, file + stderr)
- [x] JSON output mode (`--json`)

### v0.2.0 (Improve Phase)
- [x] LLM-based pane analysis (Ollama integration)
- [x] Async HTTP with retry and concurrency control (semaphore=4)
- [x] Graceful LLM -> regex fallback
- [x] Debug logging for all uninstrumented functions
- [x] Gemini CLI and Codex CLI detection
- [x] Watch mode with Rich Live
- [x] Version bump and stabilization

### v0.3.0 (Provider Abstraction)
- [x] `LLMProvider` Protocol (`typing.Protocol`) with `classify()` method
- [x] `LLMResult` frozen dataclass as shared return type
- [x] `OllamaProvider` — httpx async, retries, JSON parsing
- [x] `AnthropicVertexProvider` — AsyncAnthropicVertex SDK
- [x] `resolve_provider("provider/model_name")` factory function
- [x] `CC_MONITOR_LLM_MODEL` env var accepts `"provider/model"` format
- [x] Canonical `AgentState` type alias moved to `models.py`
- [x] Default model: `anthropic-vertex/claude-haiku-4-5@20251001`
- [x] `anthropic[vertex]` added as dependency

### v0.3.1 (Bugfix)
- [x] Fix `RuntimeError: Event loop is closed` — AsyncAnthropicVertex client not closed
- [x] Wrap `AsyncAnthropicVertex()` in `async with` context manager
- [x] Prevents GC `__del__` from scheduling cleanup on dead event loop

## In Progress

### v0.4.0 — Pane content cache for watch mode
- [ ] Hash last 30 lines of pane content (md5) per tmux target
- [ ] Cache `LLMResult` keyed by `(tmux_target, content_hash)` — plain `dict` in `watch_loop()` scope
- [ ] Skip LLM call on cache hit (content unchanged since last iteration)
- [ ] `analyze_sessions()` gets optional `cache` param (`None` = no caching)
- [ ] `watch.py` creates cache before loop, passes into `analyze_sessions()`
- [ ] `ccm status` (one-shot) does not use cache — calls without `cache` arg
- [ ] Cache only applies to LLM path — regex fallback is cheap, no caching
- [ ] PRD: `.dingllm/prd/pane-content-cache.md`

## Potential Future Work

### Near-term
- [ ] macOS notifications when agent needs input
- [ ] Token/cost estimation per session
- [ ] Configurable LLM prompt templates
- [ ] Sound alerts for state transitions (needs_input)

### Medium-term
- [ ] Plugin system for custom agent type detection
- [ ] Session history / state change timeline
- [ ] Multi-machine support via SSH + tmux
- [ ] Web dashboard (optional, lightweight)

### Long-term
- [ ] Agent orchestration (send commands to agents)
- [ ] OTel-based observability integration
- [ ] Integration with task management systems
