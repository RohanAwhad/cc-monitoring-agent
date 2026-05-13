# Mission

## Project: cc-monitor (ccm)

**One-liner:** CLI tool that monitors AI coding agent sessions running in tmux panes.

## Problem

Developers running multiple AI coding agents (Claude Code, OpenCode, Gemini CLI, Codex CLI) across tmux sessions have no unified view of:
- Which agents are actively working vs idle vs waiting for input
- What each agent is currently doing
- Where to find each agent (tmux coordinates)

Constantly switching between panes to check status is disruptive and error-prone.

## Solution

`ccm` scans all tmux panes, identifies AI agent sessions, classifies their state (working/idle/needs_input), and summarizes what they're doing -- displayed as a Rich table or JSON output.

## Core Value Proposition

- **Zero-config discovery**: Automatically finds agents via tmux pane commands and child process inspection
- **State classification**: LLM-based analysis (with regex fallback) determines if an agent is working, idle, or needs user input
- **Tmux coordinates**: Shows exact `session:window.pane` target to jump directly to any agent
- **Two modes**: One-shot `ccm status` and continuous `ccm watch`

## Design Principles

1. **No external dependencies beyond tmux**: Agents are discovered via `tmux list-panes` and `ps` -- no agent-side instrumentation required
2. **Graceful degradation**: LLM analysis falls back to regex heuristics if the LLM is unavailable
3. **Minimal footprint**: Small Python package (~310 LOC), 3 runtime dependencies (loguru, rich, httpx)
4. **Strict typing**: MyPy strict mode, PEP 561 typed package
5. **Observable**: Structured JSON logging to file at DEBUG level

## Non-Goals

- Agent control (sending commands to agents)
- Cross-machine monitoring (local tmux only)
- Historical session tracking / persistence
- Web UI or dashboard
