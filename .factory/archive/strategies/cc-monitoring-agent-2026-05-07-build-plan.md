---
tags:
  - factory
  - strategy
  - cc-monitoring-agent
date: 2026-05-07
source: factory-archivist
---

# Strategy: cc-monitoring-agent — 2026-05-07 (Build Plan Approved)

## Phase: Build Plan — CEO APPROVED

### Decision
CEO reviewed the 7-phase build plan from strategist and issued PROCEED verdict. No issues found. Plan closely follows research recommendations.

### Approved Build Phases (Sequential)

1. **Phase 1: Project scaffold + eval harness** (FIX, high priority)
   - pyproject.toml, package structure, argparse CLI, trivial test
   - Goal: all 5 eval dimensions green (composite 1.0)
   - Must complete before any feature work

2. **Phase 2: Data model + tmux discovery** (EXPLORE, high priority)
   - AgentSession dataclass, tmux list-panes parsing, two-tier detection
   - classify_pane() fast path + verify_claude_candidate() child process check
   - Unit tests with mocked subprocess

3. **Phase 3: Pane content capture + state detection** (EXPLORE, high priority)
   - tmux capture-pane, detect_claude_state(), detect_opencode_state()
   - Markers: ❯ prompt, ⏺ tool markers, ✻ completion, timer patterns
   - Tests with representative pane content samples

4. **Phase 4: Activity summarization** (EXPLORE, high priority)
   - summarize_activity() — recap lines, tool calls, fallback heuristics
   - analyze_sessions() orchestrator
   - No LLM — heuristic parsing only

5. **Phase 5: Rich table display + CLI wiring** (EXPLORE, high priority)
   - rich.table.Table with color-coded states
   - --json flag, ccm entry point
   - Full pipeline: discover → analyze → display

6. **Phase 6: Structured logging** (EXPLOIT, medium priority)
   - loguru with stderr + file sinks
   - LOGGING_LEVEL env var, logs/ directory
   - Debug logging in discovery + analyzer

7. **Phase 7: Integration tests + validation** (EXPLOIT, medium priority)
   - Full pipeline test with mocked subprocess
   - CLI tests: --help, --json, empty results
   - All eval dimensions passing

### Growth Dimensions Covered
- **capability_surface**: Phases 2-5 (+0.3, +0.3, +0.2, +0.2)
- **observability**: Phase 6 (0.0 → 0.7)
- **factory_effectiveness**: Phase 1 (all evals green), Phase 7 (+0.2)

### Anti-Patterns Documented
- No libtmux — subprocess sufficient for 2 commands
- No hardcoded version strings — use regex
- No scrollback capture — visible content only
- No daemon/TUI/persistence — snapshot MVP
- No LLM summarization — heuristic parsing

### CEO Instructions
- Execute phases sequentially
- Phase 1 must get all eval dimensions green before feature work
- Each phase is one PR's worth of work
