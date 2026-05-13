# PRD: Pane Content Cache

## Problem

In watch mode, `ccm watch` calls `analyze_sessions()` every N seconds (default 2s). Each call sends every discovered pane's content to the LLM for classification. Most of the time, a pane's content hasn't changed between iterations — the agent is still doing the same thing. This wastes LLM calls (latency + cost) on redundant classification.

## Desired Behavior

If a pane's content hasn't changed since the last iteration, reuse the previous `LLMResult` (state + summary) without calling the LLM. Only call the LLM when the content actually changes.

## Scope

- **Watch mode only** — `ccm status` is one-shot, no caching needed
- **Per-pane granularity** — each tmux target is cached independently
- **Content-based** — cache key is a hash of the pane text, not time-based TTL

## Design

### Cache Data Structure

```python
# keyed by tmux_target, value is (content_hash, cached_result)
_cache: dict[str, tuple[str, LLMResult]] = {}
```

### Cache Lifecycle

- **Created**: in `watch_loop()` before the `while True` loop
- **Passed**: into `analyze_sessions(sessions, cache=pane_cache)`
- **Persists**: across all iterations of the watch loop
- **Destroyed**: when watch mode exits (KeyboardInterrupt)

### Cache Lookup Flow

For each session in `analyze_sessions()`:

1. Capture pane content via `tmux capture-pane`
2. Take last 30 lines (same as what gets sent to LLM)
3. Compute `content_hash = hashlib.md5(tail.encode()).hexdigest()`
4. Lookup `cache.get(tmux_target)`
   - **HIT**: stored hash matches `content_hash` → apply cached `state` + `summary` to session, skip LLM
   - **MISS**: hash differs or key absent → proceed to LLM (or regex fallback)
5. After LLM returns, store `cache[tmux_target] = (content_hash, LLMResult)`

### Interface Change

```python
# current
def analyze_sessions(sessions: list[AgentSession]) -> list[AgentSession]

# new — cache is optional (None = no caching, used by ccm status)
def analyze_sessions(
    sessions: list[AgentSession],
    cache: dict[str, tuple[str, LLMResult]] | None = None,
) -> list[AgentSession]
```

### What Gets Hashed

The last 30 lines of pane content — the same text that gets sent to the LLM as `user_prompt`. This means the hash matches exactly what the LLM would see, so a cache hit guarantees the LLM would produce the same classification.

### Cache Invalidation

- **Automatic**: content changes → hash changes → cache miss → fresh LLM call
- **Session disappears**: pane closes or agent exits → `discover_sessions()` no longer returns it → stale cache entry is harmless (never looked up)
- **No TTL needed**: content-hash comparison is sufficient. If the pane text is identical, the classification is identical.

## Files to Change

| File | Change |
|------|--------|
| `analyzer.py` | Add `cache` param to `analyze_sessions()`. Hash content before LLM call. Check cache, skip LLM on hit, store on miss. |
| `watch.py` | Create cache dict before loop. Pass into `analyze_sessions()`. |
| `cli.py` | No change — `_run_status()` calls `analyze_sessions()` without cache (default `None`). |

## What Does NOT Change

- `llm_provider.py` — providers are unaware of caching
- `discovery.py` — discovery is unaware of caching
- `display.py` — display is unaware of caching
- `models.py` — no new types needed (cache is a plain `dict`)
- Regex fallback — runs every time (cheap, no caching needed)

## Edge Cases

| Case | Behavior |
|------|----------|
| First iteration of watch | All misses, all panes get analyzed (same as today) |
| Pane scrolls but content is same last-30-lines | Cache hit (correct — visible state unchanged) |
| Agent switches task | Content changes → hash changes → cache miss → fresh analysis |
| Pane closes mid-watch | Entry stays in cache, never looked up again, harmless |
| New pane appears | No cache entry → miss → fresh analysis |
| LLM fails, regex fallback used | Regex runs every iteration (cheap) — not cached |

## Success Criteria

- Watch mode makes zero LLM calls for panes whose content hasn't changed
- No behavior change for `ccm status` (one-shot)
- All existing tests pass unchanged
- New tests verify cache hit/miss logic
