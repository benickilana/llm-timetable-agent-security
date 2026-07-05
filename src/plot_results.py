import argparse
import csv
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np


DEFENSE_ORDER = [
    "no_defense",
    "context_separation",
    "policy_hierarchy",
    "signed_policy_hierarchy",
    "signed_policy_hierarchy_tool_firewall",
    "validator",
    "policy_hierarchy_validator",
    "signed_policy_hierarchy_validator",
    "signed_policy_hierarchy_tool_firewall_validator",
]

ATTACK_TYPE_ORDER = [
    "constraint_violation",
    "privacy_leak",
    "objective_manipulation",
    "tool_misuse",
    "unsigned_policy_override",
    "authority_impersonation",
    "indirect_prompt_injection",
    "tool_result_injection",
    "adaptive_indirect_prompt_injection",
    "preference_manipulation",
]

DISPLAY_LABELS = {
    "no_defense": "No defense",
    "context_separation": "Context separation",
    "policy_hierarchy": "Policy hierarchy",
    "signed_policy_hierarchy": "Signed policy",
    "validator": "Validator",
    "policy_hierarchy_validator": "Policy + validator",
    "signed_policy_hierarchy_validator": "Signed policy + validator",
    "constraint_violation": "Constraint\nviolation",
    "privacy_leak": "Privacy\nleak",
    "objective_manipulation": "Objective\nmanipulation",
    "tool_misuse": "Tool\nmisuse",
    "unsigned_policy_override": "Unsigned policy\noverride",
    "authority_impersonation": "Authority\nimpersonation",
    "indirect_prompt_injection": "Indirect prompt\ninjection",
    "tool_result_injection": "Tool-result\ninjection",
    "adaptive_indirect_prompt_injection": "Adaptive indirect\nprompt injection",
    "preference_manipulation": "Preference\nmanipulation",
}

COLORS = {
    "no_defense": "#9B1C31",
    "context_separation": "#C65D2E",
    "policy_hierarchy": "#D9922B",
    "signed_policy_hierarchy": "#D7B248",
    "validator": "#4C956C",
    "policy_hierarchy_validator": "#2F7D62",
    "signed_policy_hierarchy_validator": "#1F5F4A",
    "signed_policy_hierarchy_tool_firewall": "#496DDB",
    "signed_policy_hierarchy_tool_firewall_validator": "#24439A",
}


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() == "true"


def read_rows(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ordered_unique(values: List[str], preferred_order: List[str]) -> List[str]:
    present = set(values)
    ordered = [value for value in preferred_order if value in present]
    remaining = sorted(present - set(ordered))
    return ordered + remaining


def label(value: str) -> str:
    return DISPLAY_LABELS.get(value, value.replace("_", " ").replace("answer action", "answer/action").capitalize())


def rate_by_key(rows: List[Dict[str, str]], group_key: str, metric_key: str):
    counts = defaultdict(lambda: {"positive": 0, "total": 0})

    for row in rows:
        key = row[group_key]
        counts[key]["total"] += 1
        if parse_bool(row[metric_key]):
            counts[key]["positive"] += 1

    result = {}
    for key, values in counts.items():
        total = values["total"]
        positive = values["positive"]
        rate = positive / total if total else 0.0
        result[key] = (positive, total, rate)

    return result


def save_figure(fig, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path.with_suffix(".png"), dpi=300, bbox_inches="tight")
    fig.savefig(output_path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def plot_attack_success_by_defense(rows: List[Dict[str, str]], output_path: Path) -> None:
    defenses = ordered_unique([row["defense_mode"] for row in rows], DEFENSE_ORDER)
    rates = rate_by_key(rows, "defense_mode", "attack_success")

    y_labels = [label(defense) for defense in defenses]
    values = [rates[defense][2] * 100 for defense in defenses]

    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    bars = ax.barh(
        y_labels,
        values,
        color=[COLORS.get(defense, "#4C78A8") for defense in defenses],
        edgecolor="black",
        linewidth=0.6,
    )

    ax.set_xlabel("Attack success rate (%)")
    ax.set_title("Attack Success by Defense", pad=14)
    ax.set_xlim(0, 100)
    ax.grid(axis="x", linestyle="--", alpha=0.35)

    for bar, defense, value in zip(bars, defenses, values):
        success, total, _ = rates[defense]
        ax.text(
            min(value + 2, 96),
            bar.get_y() + bar.get_height() / 2,
            f"{success}/{total} ({value:.0f}%)",
            va="center",
            fontsize=10,
        )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    save_figure(fig, output_path)



def plot_horizontal_rate_by_defense(
    rows,
    metric_key: str,
    title: str,
    output_path: Path,
) -> None:
    defenses = ordered_unique([row["defense_mode"] for row in rows], DEFENSE_ORDER)
    rates = rate_by_key(rows, "defense_mode", metric_key)

    y_labels = [label(defense) for defense in defenses]
    values = [rates[defense][2] * 100 for defense in defenses]

    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    bars = ax.barh(
        y_labels,
        values,
        color=[COLORS.get(defense, "#4C78A8") for defense in defenses],
        edgecolor="black",
        linewidth=0.6,
    )

    ax.set_xlabel("Rate (%)")
    ax.set_title(title, pad=14)
    ax.set_xlim(0, 100)
    ax.grid(axis="x", linestyle="--", alpha=0.35)

    for bar, defense, value in zip(bars, defenses, values):
        positive, total, _ = rates[defense]
        ax.text(
            min(value + 2, 96),
            bar.get_y() + bar.get_height() / 2,
            f"{positive}/{total} ({value:.0f}%)",
            va="center",
            fontsize=10,
        )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    save_figure(fig, output_path)

def plot_heatmap_by_type_and_defense(rows: List[Dict[str, str]], output_path: Path) -> None:
    attack_types = ordered_unique([row["attack_type"] for row in rows], ATTACK_TYPE_ORDER)
    defenses = ordered_unique([row["defense_mode"] for row in rows], DEFENSE_ORDER)

    counts = defaultdict(lambda: {"success": 0, "total": 0})

    for row in rows:
        key = (row["attack_type"], row["defense_mode"])
        counts[key]["total"] += 1
        if parse_bool(row["attack_success"]):
            counts[key]["success"] += 1

    matrix = np.zeros((len(attack_types), len(defenses)))

    for i, attack_type in enumerate(attack_types):
        for j, defense in enumerate(defenses):
            data = counts[(attack_type, defense)]
            total = data["total"]
            matrix[i, j] = 100 * data["success"] / total if total else 0

    fig_width = max(8.5, len(defenses) * 2.0)
    fig_height = max(5.2, len(attack_types) * 0.65)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    im = ax.imshow(matrix, aspect="auto", vmin=0, vmax=100)

    ax.set_xticks(range(len(defenses)))
    ax.set_yticks(range(len(attack_types)))
    ax.set_xticklabels([label(d) for d in defenses], rotation=25, ha="right")
    ax.set_yticklabels([label(t) for t in attack_types])

    ax.set_title("Attack Success Rate by Attack Type and Defense", pad=14)

    for i in range(len(attack_types)):
        for j in range(len(defenses)):
            value = matrix[i, j]
            text_color = "white" if value > 55 else "black"
            ax.text(j, i, f"{value:.0f}%", ha="center", va="center", color=text_color, fontsize=9)

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Attack success rate (%)")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    save_figure(fig, output_path)


def plot_issue_frequency(rows: List[Dict[str, str]], output_path: Path) -> None:
    issue_counts = Counter()

    for row in rows:
        for issue in row["detected_issues"].split(";"):
            issue = issue.strip()
            if issue:
                issue_counts[issue] += 1

    if not issue_counts:
        return

    issues = [issue for issue, _ in issue_counts.most_common()]
    values = [issue_counts[issue] for issue in issues]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh([label(issue) for issue in issues], values, color="#4C78A8", edgecolor="black", linewidth=0.6)

    ax.set_xlabel("Number of detections")
    ax.set_title("Runtime Monitor Detections Across Model Outputs", pad=14)
    ax.grid(axis="x", linestyle="--", alpha=0.35)

    for bar, value in zip(bars, values):
        ax.text(value + 0.2, bar.get_y() + bar.get_height() / 2, str(value), va="center", fontsize=10)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    save_figure(fig, output_path)


def write_plot_summary(rows: List[Dict[str, str]], output_path: Path) -> None:
    by_defense_success = rate_by_key(rows, "defense_mode", "attack_success")
    by_defense_block = rate_by_key(rows, "defense_mode", "blocked")
    defenses = ordered_unique([row["defense_mode"] for row in rows], DEFENSE_ORDER)

    lines = []
    lines.append("# Plot Summary")
    lines.append("")
    lines.append("## By defense mode")
    lines.append("")
    has_unsafe = rows and "unsafe_output" in rows[0]

    if has_unsafe:
        by_defense_unsafe = rate_by_key(rows, "defense_mode", "unsafe_output")
        lines.append("| Defense mode | Targeted attack success | Unsafe unblocked outputs | Block rate | Total rows |")
        lines.append("|---|---:|---:|---:|---:|")
    else:
        lines.append("| Defense mode | Attack success | Block rate | Total rows |")
        lines.append("|---|---:|---:|---:|")

    for defense in defenses:
        success_count, total, success_rate = by_defense_success[defense]
        block_count, _, block_rate = by_defense_block[defense]
        if has_unsafe:
            unsafe_count, _, unsafe_rate = by_defense_unsafe[defense]
            lines.append(
                f"| `{defense}` | {success_count}/{total} ({success_rate:.0%}) | "
                f"{unsafe_count}/{total} ({unsafe_rate:.0%}) | "
                f"{block_count}/{total} ({block_rate:.0%}) | {total} |"
            )
        else:
            lines.append(
                f"| `{defense}` | {success_count}/{total} ({success_rate:.0%}) | "
                f"{block_count}/{total} ({block_rate:.0%}) | {total} |"
            )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot attack evaluation results.")
    parser.add_argument("--input", required=True, help="Input attack_results CSV file.")
    parser.add_argument("--run-name", required=True, help="Run name for output plots.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    run_name = args.run_name
    rows = read_rows(input_path)

    plots_dir = Path("results") / "plots"

    plot_attack_success_by_defense(
        rows,
        plots_dir / f"{run_name}_attack_success_by_defense_pretty",
    )

    if rows and "unsafe_output" in rows[0]:
        plot_horizontal_rate_by_defense(
            rows,
            metric_key="unsafe_output",
            title="Unsafe Unblocked Outputs by Defense",
            output_path=plots_dir / f"{run_name}_unsafe_unblocked_by_defense",
        )

    plot_heatmap_by_type_and_defense(
        rows,
        plots_dir / f"{run_name}_attack_success_heatmap",
    )

    plot_issue_frequency(
        rows,
        plots_dir / f"{run_name}_issue_frequency",
    )

    write_plot_summary(
        rows,
        Path("results") / f"{run_name}_plot_summary.md",
    )

    print(f"Wrote high-quality plots to {plots_dir}")
    print(f"Wrote plot summary to results/{run_name}_plot_summary.md")


if __name__ == "__main__":
    main()
