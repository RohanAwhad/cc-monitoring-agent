# Tech Stack

## Runtime

| Component | Choice | Notes |
|-----------|--------|-------|
| Language | Python >= 3.11 | src layout, PEP 561 typed |
| Package manager | uv | lockfile: `uv.lock` |
| Build system | setuptools >= 68.0 | `setuptools.build_meta` backend |
| CLI framework | argparse | Subcommands: `status`, `watch` |
| Terminal UI | rich | Tables + Live mode |
| HTTP client | httpx | Async, for LLM API calls |
| Logging | loguru | stderr + file sink (JSON serialized) |

## External Integrations

| System | How | Config |
|--------|-----|--------|
| tmux | `subprocess.run` (`list-panes`, `capture-pane`) | No config needed |
| Ollama (LLM) | httpx async POST to `/api/chat` | `CC_MONITOR_LLM_BASE_URL` (default: `localhost:11434`), `CC_MONITOR_LLM_MODEL` (default: `qwen3.5:4b`) |
| OS processes | `subprocess.run` (`ps -eo pid,ppid,comm`) | For Claude child-process verification |

## Dev Toolchain

| Tool | Purpose | Config |
|------|---------|--------|
| pytest | Testing | `tests/`, `--cov=cc_monitor`, `fail_under=80` |
| mypy | Type checking | `strict=true`, `ignore_missing_imports=true` |
| ruff | Linting + formatting | `py311`, rules `E, F, I, W` |
| pytest-cov | Coverage | `source_pkgs = ["cc_monitor"]` |

## Environment Variables

| Variable | Module | Default | Purpose |
|----------|--------|---------|---------|
| `CC_MONITOR_LLM_BASE_URL` | analyzer.py | `http://localhost:11434` | Ollama API endpoint |
| `CC_MONITOR_LLM_MODEL` | analyzer.py | `qwen3.5:4b` | LLM model for pane analysis |
| `LOGGING_LEVEL` | logging.py | `INFO` | Stderr log verbosity |

## Module Inventory

| Module | LOC | Role |
|--------|-----|------|
| `models.py` | 26 | `AgentSession` dataclass (central data object) |
| `discovery.py` | ~80 | Tmux pane scanning, agent classification, process verification |
| `analyzer.py` | ~80 | LLM + regex state detection, pane content capture |
| `display.py` | ~60 | Rich table rendering (one-shot) |
| `watch.py` | ~60 | Rich Live continuous monitoring loop |
| `cli.py` | 90 | CLI entry point, argparse, subcommand dispatch |
| `logging.py` | 27 | Loguru configuration (stderr + file) |
| `__main__.py` | 3 | `python -m cc_monitor` support |

## Key Constants

| Constant | File | Value |
|----------|------|-------|
| `_LLM_MAX_RETRIES` | analyzer.py | 3 |
| `_LLM_CONCURRENCY` | analyzer.py | 4 (semaphore) |
| LLM timeout | analyzer.py | 60s per request |
| Log rotation | logging.py | 10MB per file |
| Watch default interval | watch.py | 2.0s |
