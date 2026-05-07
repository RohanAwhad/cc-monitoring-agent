# Research Report — cc-monitoring-agent (Cycle 6)

## Project Summary

cc-monitoring-agent (`ccm`) is a Python CLI tool that scans tmux panes, detects Claude Code and OpenCode sessions, analyzes agent state (idle/working/needs_input), and displays a Rich table dashboard. Architecture: discover → analyze → display pipeline. Stack: argparse + subprocess + rich + loguru. Current state: 107 tests, 97% coverage, mypy strict, project eval 1.0, factory composite 0.575. Backlog is empty — all 3 cycle 5 items (filtering, summary, notifications) delivered and merged.

**Key differentiator**: Zero-config passive pane scraping — works with any terminal agent (Claude Code, OpenCode) without hooks, plugins, or daemon setup.

## Backlog Assessment

Backlog is empty. All 13 GitHub issues are closed/delivered. The project is functionally complete for its original scope. This research focuses on identifying high-value new features informed by the competitive landscape.

## Prior Knowledge (Archive)

### Competitive Landscape (from cycle 3)

- **claude-tmux**: SQLite + hooks, TUI dashboard, worktree isolation — heavier but richer state
- **tmux-orche**: Inter-agent communication control plane
- **pylumbergh**: Web dashboard for supervising Claude Code sessions
- **claude-code-tools**: Programmatic tmux control

ccm's differentiation was established as: lightweight, zero-config, passive monitoring, works with any agent.

### Key Patterns Validated
- No-new-files strategy for factory eval compatibility
- `mypy_path = "src"` for src-layout projects
- Rich Live for flicker-free watch mode (no Textual dependency needed)
- argparse subparsers sufficient for <5 subcommands

## External Research Findings

### 1. Competitive Landscape — Explosive Growth (May 2026)

The Claude Code monitoring space has exploded since cycle 3. Multiple new tools have emerged:

**Hook-Based Monitoring (structured events, rich metadata)**

- **[ATM (Agent Tmux Manager)](https://github.com/damelLP/agent-tmux-manager)**: Rust TUI + daemon. Claude Code hooks → Unix socket → real-time dashboard. Captures model, context usage bars, cost tracking, live terminal capture. Agent control CLI (spawn, kill, interrupt, send text, auto-approve). Workspace layouts (solo/pair/squad/grid). Currently Claude Code-only.

- **[claude-code-hooks-multi-agent-observability](https://github.com/disler/claude-code-hooks-multi-agent-observability)** (920 stars): Hook scripts intercept all 12 Claude Code lifecycle events → HTTP → Bun server → SQLite → WebSocket → Vue dashboard. Live pulse chart, agent swim lanes, MCP tool detection, security blocking. Full multi-agent orchestration with builder/validator agent roles.

- **[agents-observe](https://github.com/simple10/agents-observe)**: Claude plugin (`claude plugin install agents-observe`). Hook events → API server (SQLite) → React dashboard. Subagent relationship tracking, filtering/search. Docker-based.

- **[Claude Code Agent Monitor](https://github.com/hoangsonww/Claude-Code-Agent-Monitor)**: Node.js + React + SQLite. Activity feed with pause/resume, token usage analytics, activity heatmap, agent orchestration DAGs, Sankey diagrams.

**TUI-Based Monitoring (pane scraping, multi-agent)**

- **[TmuxCC](https://github.com/nyanko3141592/tmuxcc)**: Rust TUI. Supports Claude Code, OpenCode, Codex CLI, Gemini CLI. Interactive approval management (y/n from dashboard), batch approve/reject, subagent tracking, live pane preview. 500ms polling. Installed via `cargo install tmuxcc`.

- **[Agent Deck](https://github.com/asheshgoplani/agent-deck)**: Multi-agent TUI with Telegram bridge and Slack bridge for mobile/channel-based monitoring.

- **[Workmux](https://github.com/raine/workmux)**: Git worktrees + tmux windows, with agent status overview across all sessions.

**OTel-Based Monitoring (enterprise, metrics/cost)**

- **[claude-code-otel](https://github.com/ColeMurray/claude-code-otel)**: Full Grafana stack (OTel Collector → Prometheus + Loki → Grafana). Tracks session count, cost by model, token usage, LOC changes, commits, PRs. DAU/WAU/MAU. 30s refresh dashboards.

- **[Datadog AI Agents Console](https://www.datadoghq.com/blog/claude-code-monitoring/)**: Enterprise Claude Code monitoring — adoption tracking, performance trends, cost/ROI analysis.

- **[Dynatrace Claude Code Monitoring](https://www.dynatrace.com/hub/detail/claude-code-agent-monitoring/)**: End-to-end visibility via OTel. Dashboards for total users, cost, tokens, sessions, active time.

- **[Sentry AI Monitoring](https://sentry.io/cookbook/monitor-claude-code-with-sentry/)**: Token usage, API costs, tool activity per session.

**Key Shift**: Claude Code now has native OpenTelemetry support (metrics, events, distributed tracing in beta), with `TRACEPARENT` propagation to subprocesses. This makes hook-based and OTel-based approaches first-class, while pane scraping remains the lightweight alternative.

### 2. ccm's Position in the New Landscape

**What ccm does uniquely well:**
- Zero-config: no hooks, no plugins, no daemon, no Docker, no Rust toolchain
- Agent-agnostic: works with OpenCode out of the box (most competitors are Claude-only)
- Fast: ~50ms per scan, Python-only, pip-installable
- Composable: `--json` output for scripting, `ccm summary` for status bars

**Where ccm is falling behind:**
- No interactive approval management (TmuxCC, ATM offer this)
- No cost/token tracking (OTel-based tools and ATM provide this)
- No subagent/hierarchy visibility
- No persistent history or analytics
- No remote monitoring (Agent Deck has Telegram/Slack bridges)

### 3. High-Value Feature Opportunities

Based on competitive analysis and gaps, ranked by value-to-effort ratio:

#### A. `ccm attach <target>` — Quick Jump (LOW effort, HIGH daily value)
Shortcut to switch to a specific agent's tmux pane. Already identified in cycle 3 research. Every competitor (TmuxCC, ATM, Workmux) offers this. Single function, minimal code.

#### B. Context/Cost Display (MEDIUM effort, HIGH value)
Read Claude Code's JSONL conversation files (`~/.claude/projects/*/conversations/*.jsonl`) to extract token counts and estimate costs. No hooks needed — just file reading. Would close the biggest feature gap vs ATM and OTel-based tools. OpenCode equivalent: read session files if available.

#### C. Session History / Timeline (MEDIUM effort, MEDIUM value)
Log state transitions to a local SQLite or JSONL file during `watch` mode. Enable `ccm history` to show recent sessions, durations, and state changes. Useful for "what happened while I was away?" scenarios. Simple append-only log.

#### D. Approval Count / Pending Action Badge (LOW effort, MEDIUM value)
Detect pending approval prompts (❯ with specific patterns) and surface a count in the status table. Doesn't do the approval (that requires sending keystrokes) but flags "3 agents need attention."

#### E. Gemini CLI / Codex CLI Support (MEDIUM effort, MEDIUM value)
TmuxCC already supports 4 agent types. Adding Gemini CLI and Codex CLI detection to ccm would strengthen the agent-agnostic differentiator. Requires discovering their terminal patterns (command names, status indicators).

#### F. tmux Status Bar Widget (LOW effort, LOW-MEDIUM value)
Already have `ccm summary`. Document and optimize the `set -g status-right '#(ccm summary)'` pattern. Ensure output has no ANSI codes, fits in status bar width, and refreshes efficiently.

#### G. Remote Notifications — Slack/Telegram (HIGH effort, MEDIUM value)
Agent Deck offers Telegram and Slack bridges. Could add `--notify-slack` or `--notify-telegram` for remote monitoring. Higher complexity due to auth/tokens, but high value for users managing agents on remote machines.

### 4. Claude Code Native Monitoring Capabilities

Claude Code now exports telemetry via OpenTelemetry:
- 8 metrics including `claude_code.token.usage` (by type and model) and `claude_code.session.count`
- Active time tracking (excludes idle time)
- Distributed tracing with `TRACEPARENT` propagation to subprocesses
- Privacy: prompt text redacted by default, configurable via env vars

This is relevant because ccm could optionally consume OTel data for richer metrics without requiring hook setup — just reading the metrics endpoint.

### 5. OpenCode Ecosystem Update

OpenCode (150k+ GitHub stars) now has:
- **opencode-plugin-otel**: OTel exporter mirroring Claude Code's telemetry signals
- Client/server architecture (headless server + multiple frontends)
- Agent system with plan/build modes
- LSP integration for code intelligence
- Non-interactive scripting mode

This reinforces ccm's value proposition: OpenCode and Claude Code are converging on similar architectures, and ccm is one of the few tools that monitors both.

## Recommended Focus Areas

### Tier 1: Quick Wins (embed in existing modules, no new files)

1. **`ccm attach <target>`** — Add to `cli.py`, ~15 lines. Direct `tmux select-window`/`select-pane`. Every competitor has this.

2. **Pending approval detection** — Enhance `analyzer.py` state detection to flag pending approvals. Add an `approvals_pending: int` field or refine the `needs_input` state. ~20 lines.

3. **tmux status bar docs/optimization** — Ensure `ccm summary` output is clean for status bar embedding. Add `--no-color` flag if not already present.

### Tier 2: Differentiating Features (moderate effort, high value)

4. **Token/cost estimation from conversation files** — Read Claude Code's local JSONL conversation logs, extract token usage. Add `--costs` flag to status output. Would be unique among pane-scraping tools (getting hook-level data without hooks).

5. **Gemini CLI + Codex CLI detection** — Extend `discovery.py` and `analyzer.py` with new agent type patterns. Strengthen "works with any agent" positioning.

### Tier 3: Larger Features (consider for future cycles)

6. **Session history log** — Append state transitions to JSONL during watch mode. `ccm history` subcommand.

7. **Remote notification bridges** — Slack webhook or Telegram bot integration for `--notify`.

## References

- [ATM - Agent Tmux Manager](https://github.com/damelLP/agent-tmux-manager)
- [TmuxCC - TUI Dashboard](https://github.com/nyanko3141592/tmuxcc)
- [claude-code-hooks-multi-agent-observability](https://github.com/disler/claude-code-hooks-multi-agent-observability)
- [agents-observe](https://github.com/simple10/agents-observe)
- [Claude Code Agent Monitor](https://github.com/hoangsonww/Claude-Code-Agent-Monitor)
- [Agent Deck](https://github.com/asheshgoplani/agent-deck)
- [Workmux](https://github.com/raine/workmux)
- [claude-code-otel](https://github.com/ColeMurray/claude-code-otel)
- [Claude Code Monitoring Docs](https://code.claude.com/docs/en/monitoring-usage)
- [Datadog AI Agents Console](https://www.datadoghq.com/blog/claude-code-monitoring/)
- [Dynatrace Claude Code Monitoring](https://www.dynatrace.com/hub/detail/claude-code-agent-monitoring/)
- [Sentry Claude Code Monitoring](https://sentry.io/cookbook/monitor-claude-code-with-sentry/)
- [Sesh - Smart tmux Session Manager](https://github.com/joshmedeski/sesh)
- [tmux-ls](https://github.com/waystid/tmux-ls)
- [TmuxAI](https://tmuxai.dev/)
- [OpenCode](https://opencode.ai/)
- [Agent Flow - Real-time Visualization](https://github.com/patoles/agent-flow)
