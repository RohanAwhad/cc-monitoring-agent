# Roadmap

## Current State (v0.2.0)

- Core pipeline functional: discover -> analyze -> display
- LLM-based analysis with async retry/concurrency + regex fallback
- Supports: Claude Code, OpenCode, Gemini CLI, Codex CLI
- Two output modes: one-shot status, continuous watch
- 107 tests, 97% coverage, mypy strict, eval score 1.0
- Factory autonomous improvement system: 23 experiments, 16 kept

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

## Factory System Status

- **Mode**: improve (build phase complete)
- **Eval threshold**: 0.56 (weighted composite)
- **Keep rate**: 55% overall (improving: cycles 5-7 at 100%)
- **Strategy**: backlog cleared, research-driven hypothesis generation
