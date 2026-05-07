---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# AnthropicVertex Python SDK (Issue #23)

## Key Findings

- Import: `from anthropic import AnthropicVertex`
- Install: `uv add "anthropic[vertex]"` (pulls in `google-cloud-aiplatform`)
- Recommended model: `claude-sonnet-4-5@20250929` (small/fast for pane summarization)

## Credential Mapping (User's Env)

- `ANTHROPIC_VERTEX_PROJECT_ID` — user has `itpc-gcp-ai-eng-claude`
- `VERTEX_LOCATION` — user has `"global"`, but SDK expects `CLOUD_ML_REGION` — **mismatch**
- `VERTEX_ACCESS_TOKEN` — user has a pre-cached token refresh system in `.zshrc`

## Recommended Client Init

```python
client = AnthropicVertex(
    project_id=os.environ["ANTHROPIC_VERTEX_PROJECT_ID"],
    region=os.environ.get("VERTEX_LOCATION", "global"),
    access_token=os.environ.get("VERTEX_ACCESS_TOKEN"),
)
```

## Implementation Plan

- New module: `src/cc_monitor/llm.py` with `analyze_pane(text: str) -> str`
- If credentials missing, return heuristic summary (no crash)
- Adds ~5 capability_surface units

## Sources

- [SDK example](https://github.com/anthropics/anthropic-sdk-python/blob/main/examples/vertex.py)
- [SDK README](https://github.com/anthropics/anthropic-sdk-python)
- [Vertex AI docs](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai)
