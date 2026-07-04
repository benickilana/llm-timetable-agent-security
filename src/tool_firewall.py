import re
from typing import List


SUSPICIOUS_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above|prior)\s+instructions",
    r"system\s+override",
    r"developer\s+message",
    r"system\s+message",
    r"admin\s+override",
    r"validation\s*=\s*false",
    r"disable\s+validation",
    r"skip\s+validation",
    r"bypass\s+validation",
    r"reveal\s+private",
    r"private\s+teacher\s+notes",
    r"confidential\s+teacher\s+notes",
    r"treat\s+.*\s+as\s+signed",
    r"signed_trusted_policy",
    r"this\s+is\s+now\s+a\s+hard\s+constraint",
    r"must\s+override\s+the\s+signed\s+policy",
    r"copy\s+.*\s+private\s+notes",
    r"export\s+.*\s+private\s+notes",
    r"operator\s+may\s+manually\s+place",
]


def is_suspicious_line(line: str) -> bool:
    normalized = line.lower()

    return any(
        re.search(pattern, normalized, flags=re.IGNORECASE)
        for pattern in SUSPICIOUS_PATTERNS
    )


def sanitize_tool_result(text: str) -> str:
    """
    Sanitizes untrusted tool output before it is shown to the model.

    The firewall is intentionally simple:
    - It preserves ordinary scheduling facts.
    - It removes lines that look like instructions to the model.
    - It labels the result as sanitized and untrusted.

    This is not meant to be a complete defense. It is a small prototype of a
    tool-output firewall for indirect prompt-injection experiments.
    """
    kept_lines: List[str] = []
    removed_count = 0

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if is_suspicious_line(line):
            removed_count += 1
            continue

        # Remove HTML/comment wrappers but keep benign content.
        line = re.sub(r"<!--|-->", "", line).strip()

        if line:
            kept_lines.append(line)

    if not kept_lines:
        kept_lines.append("[No scheduling-relevant content remained after sanitization.]")

    header = [
        "[SANITIZED UNTRUSTED TOOL RESULT]",
        f"[Removed suspicious instruction-like lines: {removed_count}]",
    ]

    return "\n".join(header + kept_lines)


def maybe_sanitize_tool_result(text: str, enabled: bool) -> str:
    if not enabled:
        return text

    return sanitize_tool_result(text)
