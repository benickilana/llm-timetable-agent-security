from pathlib import Path
from typing import Dict, Any

from src.signatures import verify_policy_signature


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def read_text_file(filename: str) -> str:
    path = DATA_DIR / filename
    return path.read_text(encoding="utf-8")


def load_documents() -> Dict[str, Any]:
    return {
        "trusted_policy": read_text_file("trusted_policy.txt"),
        "trusted_policy_verified": verify_policy_signature(),
        "private_teacher_notes": read_text_file("private_teacher_notes.txt"),
        "benign_teacher_requests": read_text_file("benign_teacher_requests.txt"),
        "malicious_teacher_requests": read_text_file("malicious_teacher_requests.txt"),
    }
