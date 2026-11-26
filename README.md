# most

Grok bridge: a Mistral Workflow that sends a question to xAI Grok
(`https://api.x.ai/v1`) and returns the answer.

## Setup

1. Create a workspace secret `xai_api_key` in Mistral Studio with your xAI API key.
2. Deploy the worker: `deploy/docker/Dockerfile.worker` (build context = repo root).

## Run

```python
execute_workflow(
    workflow_identifier="ask-grok",
    input={"message": "Привет! Кто ты?"},
)
```

Optional fields: `system` (system prompt), `history` (prior turns), `model`
(default `grok-4.7`, override with the `XAI_DEFAULT_MODEL` env var).
