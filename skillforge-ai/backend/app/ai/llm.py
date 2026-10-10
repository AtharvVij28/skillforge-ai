"""Swappable LLM provider. Live OpenAI is used only when configured; otherwise mock."""

from __future__ import annotations

import json
import re
from typing import Any, Protocol

import httpx

from app.core.config import get_settings


class LLMProvider(Protocol):
    def generate_json(self, prompt: str) -> dict[str, Any]: ...


class MockLLMProvider:
    def generate_json(self, prompt: str) -> dict[str, Any]:
        competency = "this competency"
        match = re.search(r"competency named (.+?)\.", prompt, re.IGNORECASE)
        if match:
            competency = match.group(1).strip()
        return {
            "questions": [
                {
                    "stem": f"Which statement best reflects sound practice in {competency}?",
                    "options": [
                        {"key": "A", "text": f"Apply {competency} methods with documented assumptions and review."},
                        {"key": "B", "text": "Skip validation if the output looks plausible."},
                        {"key": "C", "text": "Prefer undocumented shortcuts over reproducible steps."},
                        {"key": "D", "text": "Ignore metadata because it slows delivery."},
                    ],
                    "correct_option": "A",
                    "explanation": f"Reliable work in {competency} requires documented methods, validation, and review.",
                    "competency_code": competency.split(" ")[0].upper() if " " not in competency else "",
                }
            ]
        }


class OpenAILLMProvider:
    def generate_json(self, prompt: str) -> dict[str, Any]:
        settings = get_settings()
        url = settings.llm_api_base.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.llm_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.llm_model or "gpt-4o-mini",
            "temperature": 0.4,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You generate multiple-choice questions for professional statistical and data skills. "
                        "Return JSON only. For a single question use keys stem, options (A-D as {key, text}), "
                        "correct_option, explanation. For several questions use {\"questions\": [ ...those objects, "
                        "optionally with competency_code ]}. The correct answer must be unambiguously right."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("LLM did not return a JSON object")
        return parsed


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    if settings.uses_live_llm:
        return OpenAILLMProvider()
    return MockLLMProvider()
