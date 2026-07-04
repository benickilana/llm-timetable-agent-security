import json
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ParsedModelOutput:
    answer: str
    action: Dict[str, Any]
    error: Optional[str] = None


def _strip_markdown_fence(text: str) -> str:
    stripped = text.strip()

    if stripped.startswith("```"):
        lines = stripped.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]

        return "\n".join(lines).strip()

    return stripped


def _extract_json_object(text: str) -> str:
    """
    Extract the first plausible JSON object from raw model output.
    This is useful because real LLMs sometimes wrap JSON in prose or markdown.
    """
    text = _strip_markdown_fence(text)

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model output.")

    return text[start : end + 1]


def parse_model_output(raw_text: str) -> ParsedModelOutput:
    """
    Parse model output into the expected structure:

    {
      "answer": "...",
      "action": {...}
    }

    If parsing fails, return the raw text as the answer and an empty action.
    """
    try:
        json_text = _extract_json_object(raw_text)
        data = json.loads(json_text)

        answer = data.get("answer")
        action = data.get("action")

        if not isinstance(answer, str):
            raise ValueError("Field 'answer' must be a string.")

        if not isinstance(action, dict):
            raise ValueError("Field 'action' must be an object/dictionary.")

        return ParsedModelOutput(answer=answer, action=action)

    except Exception as exc:
        return ParsedModelOutput(
            answer=raw_text,
            action={},
            error=str(exc),
        )
