from __future__ import annotations

import json
import os
from typing import Any


def configured() -> bool:
    return bool(os.getenv("GROQ_API_KEY"))


def choose_action(prompt: str, schema_hint: dict[str, Any] | None = None) -> str:
    """Optional GPT-OSS-120B call for the later stochastic extension.

    Phase-0 core never calls this function.
    """
    from openai import OpenAI

    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is not set")
    base_url = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
    model = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
    temperature = float(os.getenv("LLM_TEMPERATURE", "0"))
    client = OpenAI(api_key=key, base_url=base_url)
    instruction = prompt
    if schema_hint:
        instruction += "\nReturn compact JSON matching this shape:\n" + json.dumps(schema_hint)
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[{"role": "user", "content": instruction}],
    )
    return response.choices[0].message.content or ""
