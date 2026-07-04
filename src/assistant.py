from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.backends.base import ModelBackend
from src.defenses import build_prompt
from src.retrieve import load_documents


@dataclass
class AssistantResult:
    backend_name: str
    prompt: str
    raw_model_output: str
    answer: str
    action: Dict[str, Any]
    parse_error: Optional[str]


class TimetableAgent:
    def __init__(self, backend: ModelBackend):
        self.backend = backend

    def respond(
        self,
        attack: Dict[str, Any],
        defense_mode: str,
    ) -> AssistantResult:
        documents = load_documents()

        prompt = build_prompt(
            question=attack["question"],
            malicious_context=attack["malicious_context"],
            documents=documents,
            defense_mode=defense_mode,
        )

        backend_output = self.backend.generate(
            prompt=prompt,
            attack=attack,
            defense_mode=defense_mode,
        )

        return AssistantResult(
            backend_name=self.backend.name,
            prompt=prompt,
            raw_model_output=backend_output.raw_text,
            answer=backend_output.answer,
            action=backend_output.action,
            parse_error=backend_output.parse_error,
        )
