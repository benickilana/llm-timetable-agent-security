from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from src.validator import security_check


VALIDATOR_DEFENSE_MODES = {
    "validator",
    "policy_hierarchy_validator",
    "signed_policy_hierarchy_validator",
    "signed_policy_hierarchy_tool_firewall_validator",
}


Issue = Tuple[str, str]


@dataclass
class SecurityDecision:
    blocked: bool
    issues: List[Issue]
    final_answer: str


def _deduplicate_issues(issues: List[Issue]) -> List[Issue]:
    seen = set()
    unique: List[Issue] = []

    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            unique.append(issue)

    return unique


def inspect_response(
    action: Dict[str, Any],
    answer: str,
    defense_mode: str,
) -> SecurityDecision:
    issues = _deduplicate_issues(security_check(action, answer))

    uses_validator = defense_mode in VALIDATOR_DEFENSE_MODES
    blocked = uses_validator and bool(issues)

    if blocked:
        final_answer = "BLOCKED by security layer: " + " | ".join(
            message for _, message in issues
        )
    else:
        final_answer = answer

    return SecurityDecision(
        blocked=blocked,
        issues=issues,
        final_answer=final_answer,
    )
