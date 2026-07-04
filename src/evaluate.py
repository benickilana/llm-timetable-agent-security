import argparse
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.assistant import TimetableAgent
from src.attacks import ATTACKS
from src.backends.registry import get_backend
from src.defenses import DEFENSE_MODES
from src.monitor import inspect_response


DEFAULT_RESULTS_DIR = Path("results")


def unique_issue_codes(issues):
    codes = []
    for code, _ in issues:
        if code not in codes:
            codes.append(code)
    return codes


def parse_csv_arg(value: Optional[str]) -> Optional[List[str]]:
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def select_attacks(attack_ids: Optional[List[str]]) -> List[Dict[str, Any]]:
    if attack_ids is None:
        return ATTACKS

    wanted = set(attack_ids)
    selected = [attack for attack in ATTACKS if attack["attack_id"] in wanted]

    missing = wanted - {attack["attack_id"] for attack in selected}
    if missing:
        raise ValueError(f"Unknown attack ids: {', '.join(sorted(missing))}")

    return selected


def select_defense_modes(defense_modes: Optional[List[str]]) -> List[str]:
    if defense_modes is None:
        return DEFENSE_MODES

    wanted = set(defense_modes)
    available = set(DEFENSE_MODES)

    missing = wanted - available
    if missing:
        raise ValueError(f"Unknown defense modes: {', '.join(sorted(missing))}")

    return defense_modes


def run_single_attack(
    agent: TimetableAgent,
    attack: Dict[str, Any],
    defense_mode: str,
) -> Dict[str, Any]:
    result = agent.respond(attack, defense_mode)

    decision = inspect_response(
        action=result.action,
        answer=result.answer,
        defense_mode=defense_mode,
    )

    issue_codes = unique_issue_codes(decision.issues)

    attack_success = (
        not decision.blocked
        and attack["expected_issue"] in issue_codes
    )

    unsafe_output = (
        not decision.blocked
        and len(issue_codes) > 0
    )

    return {
        "backend": result.backend_name,
        "attack_id": attack["attack_id"],
        "attack_type": attack["attack_type"],
        "defense_mode": defense_mode,
        "expected_issue": attack["expected_issue"],
        "detected_issues": ";".join(issue_codes),
        "blocked": decision.blocked,
        "attack_success": attack_success,
        "unsafe_output": unsafe_output,
        "parse_error": result.parse_error or "",
        "assistant_answer": decision.final_answer,
        "raw_model_output": result.raw_model_output,
    }


def write_csv(rows: List[Dict[str, Any]], results_path: Path) -> None:
    results_path.parent.mkdir(parents=True, exist_ok=True)

    with results_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "backend",
                "attack_id",
                "attack_type",
                "defense_mode",
                "expected_issue",
                "detected_issues",
                "blocked",
                "attack_success",
                "unsafe_output",
                "parse_error",
                "assistant_answer",
                "raw_model_output",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def write_summary(
    rows: List[Dict[str, Any]],
    defense_modes: List[str],
    summary_path: Path,
) -> None:
    if not rows:
        summary_path.write_text("# Attack Evaluation Summary\n\nNo rows.\n", encoding="utf-8")
        return

    backend = rows[0]["backend"]
    parse_failures = sum(1 for row in rows if row["parse_error"])

    lines = []
    lines.append("# Attack Evaluation Summary")
    lines.append("")
    lines.append(f"Backend: `{backend}`")
    lines.append(f"Parse failures: `{parse_failures}`")
    lines.append("")
    lines.append("| Defense mode | Targeted attacks | Unsafe unblocked outputs | Blocked outputs | Total attacks |")
    lines.append("|---|---:|---:|---:|---:|")

    for defense_mode in defense_modes:
        subset = [row for row in rows if row["defense_mode"] == defense_mode]
        targeted = sum(1 for row in subset if row["attack_success"] == "True" or row["attack_success"] is True)
        unsafe = sum(1 for row in subset if row["unsafe_output"] == "True" or row["unsafe_output"] is True)
        blocked = sum(1 for row in subset if row["blocked"] == "True" or row["blocked"] is True)
        total = len(subset)
        lines.append(f"| `{defense_mode}` | {targeted}/{total} | {unsafe}/{total} | {blocked}/{total} | {total} |")

    lines.append("")
    lines.append("## Detailed Results")
    lines.append("")
    lines.append("| Attack | Type | Defense | Detected issues | Blocked | Targeted success | Unsafe output | Parse error |")
    lines.append("|---|---|---|---|---:|---:|---:|---|")

    for row in rows:
        parse_error = "yes" if row["parse_error"] else ""
        lines.append(
            f"| {row['attack_id']} | {row['attack_type']} | `{row['defense_mode']}` | "
            f"{row['detected_issues']} | {row['blocked']} | {row['attack_success']} | "
            f"{row['unsafe_output']} | {parse_error} |"
        )

    summary_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate prompt-injection attacks against the timetable agent."
    )
    parser.add_argument(
        "--backend",
        default="simulated",
        help="Model backend to use. Supported: simulated, ollama.",
    )
    parser.add_argument(
        "--attack-ids",
        default=None,
        help="Comma-separated attack ids to run, e.g. A1,A2. Default: all.",
    )
    parser.add_argument(
        "--defense-modes",
        default=None,
        help=(
            "Comma-separated defense modes to run, e.g. "
            "no_defense,signed_policy_hierarchy_validator. Default: all."
        ),
    )
    parser.add_argument(
        "--run-name",
        default=None,
        help="Optional run name used for output files, e.g. simulated_full or ollama_subset.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    backend = get_backend(args.backend)
    agent = TimetableAgent(backend=backend)

    selected_attacks = select_attacks(parse_csv_arg(args.attack_ids))
    selected_defense_modes = select_defense_modes(parse_csv_arg(args.defense_modes))

    rows: List[Dict[str, Any]] = []

    for attack in selected_attacks:
        for defense_mode in selected_defense_modes:
            rows.append(run_single_attack(agent, attack, defense_mode))

    run_name = args.run_name or args.backend
    results_path = DEFAULT_RESULTS_DIR / f"{run_name}_attack_results.csv"
    summary_path = DEFAULT_RESULTS_DIR / f"{run_name}_summary.md"

    write_csv(rows, results_path)
    write_summary(rows, selected_defense_modes, summary_path)

    print(f"Wrote results to {results_path}")
    print(f"Wrote summary to {summary_path}")
    print()
    print(f"Backend: {backend.name}")

    parse_failures = sum(1 for row in rows if row["parse_error"])
    print(f"Parse failures: {parse_failures}")
    print()
    print("Summary:")

    for defense_mode in selected_defense_modes:
        subset = [row for row in rows if row["defense_mode"] == defense_mode]
        targeted = sum(1 for row in subset if row["attack_success"])
        unsafe = sum(1 for row in subset if row["unsafe_output"])
        blocked = sum(1 for row in subset if row["blocked"])
        print(
            f"{defense_mode}: targeted={targeted}/{len(subset)}, "
            f"unsafe_unblocked={unsafe}/{len(subset)}, blocked={blocked}/{len(subset)}"
        )


if __name__ == "__main__":
    main()
