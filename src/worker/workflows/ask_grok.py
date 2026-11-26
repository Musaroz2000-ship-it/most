"""grok-bridge — ask xAI Grok a question and return its answer.

Env vars:
  XAI_API_KEY       xAI API key (bind the workspace secret xai_api_key)
  XAI_API_BASE      xAI API base URL (default https://api.x.ai/v1)
  XAI_DEFAULT_MODEL model used when input.model is not set (default grok-4.7)
"""
from __future__ import annotations

import os
from datetime import timedelta
from typing import Optional

import httpx
from pydantic import BaseModel, Field

import mistralai.workflows as workflows

DEFAULT_MODEL = os.getenv("XAI_DEFAULT_MODEL", "grok-4.7")


class AskGrokInput(BaseModel):
    message: str = Field(description="The question to send to Grok")
    system: str = Field(default="", description="Optional system prompt")
    history: Optional[list[dict[str, str]]] = Field(
        default=None,
        description="Optional prior turns as [{\"role\": \"user\"|\"assistant\", \"content\": \"...\"}]",
    )
    model: str = Field(default=DEFAULT_MODEL, description="xAI model id")


class AskGrokOutput(BaseModel):
    answer: str
    model: str


@workflows.activity(
    start_to_close_timeout=timedelta(minutes=5),
    retry_policy_max_attempts=2,
)
async def call_grok(message: str, system: str, history: Optional[list[dict[str, str]]], model: str) -> AskGrokOutput:
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "XAI_API_KEY is not set: create the workspace secret xai_api_key in "
            "Studio and bind it to the grok-bridge deployment"
        )
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": message})

    base_url = os.getenv("XAI_API_BASE", "https://api.x.ai/v1")
    async with httpx.AsyncClient(timeout=240) as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages},
        )
        response.raise_for_status()
        data = response.json()

    answer = data["choices"][0]["message"]["content"]
    return AskGrokOutput(answer=answer, model=model)


@workflows.workflow.define(
    name="ask-grok",
    workflow_display_name="Ask Grok",
    workflow_description="Sends a message to xAI Grok via the xAI API and returns its answer.",
)
class AskGrok:
    @workflows.workflow.entrypoint
    async def run(self, params: AskGrokInput) -> AskGrokOutput:
        return await call_grok(params.message, params.system, params.history, params.model)
