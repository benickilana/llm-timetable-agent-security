from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class BackendOutput:
    """
    Structured output returned by a model backend.

    raw_text:
        The raw model output.

    answer:
        Parsed natural-language answer shown to the user.

    action:
        Parsed structured action proposed by the assistant.

    parse_error:
        Non-null if the model output could not be parsed as valid structured JSON.
    """
    raw_text: str
    answer: str
    action: Dict[str, Any]
    parse_error: Optional[str] = None


class ModelBackend(ABC):
    name: str

    @abstractmethod
    def generate(
        self,
        prompt: str,
        attack: Dict[str, Any],
        defense_mode: str,
    ) -> BackendOutput:
        raise NotImplementedError
