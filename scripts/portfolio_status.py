#!/usr/bin/env python3
"""
Portfolio-wide repository status generator.

Scans the 13 permanent Cyber Port repositories, measures basic
completeness signals, and emits Markdown/JSON reports which help drive the
continuous development loop.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


REPOSITORIES: list[dict[str, str]] = [
    {"name": "honeypot-foundry", "url": "https://github.com/hiagokinlevi/honeypot-foundry.git"},
    {"name": "dfir-attack-lab", "url": "https://github.com/hiagokinlevi/dfir-attack-lab.git"},
    {"name": "waf-defense-rulepacks", "url": "https://github.com/hiagokinlevi/waf-defense-rulepacks.git"},
    {"name": "secure-pipeline-blueprints", "url": "https://github.com/hiagokinlevi/secure-pipeline-blueprints.git"},
    {"name": "ai-security-guardrails", "url": "https://github.com/hiagokinlevi/ai-security-guardrails.git"},
    {"name": "iam-audit-lab", "url": "https://github.com/hiagokinlevi/iam-audit-lab.git"},
    {"name": "cloud-posture-watch", "url": "https://github.com/hiagokinlevi/cloud-posture-watch.git"},
    {"name": "secret-leak-sentinel", "url": "https://github.com/hiagokinlevi/secret-leak-sentinel.git"},
    {"name": "phishing-surface-monitor", "url": "https://github.com/hiagokinlevi/phishing-surface-monitor.git"},
    {"name": "container-defense-stack", "url": "https://github.com/hiagokinlevi/container-defense-stack.git"},
    {"name": "ir-playbooks-automation", "url": "https://github.com/hiagokinlevi/ir-playbooks-automation.git"},
    {"name": "cryptologik", "url": "https://github.com/hiagokinlevi/cryptologik.git"},
    {"name": "offensive-gvuln", "url": "https://github.com/hiagokinlevi/offensive-gvuln.git"},
]

REQUIRED_FILES = [
    "README.md",
    "ROADMAP.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
]

UNCHECKED_PATTERN = re.compile(r"(?m)^- \[ \] (.+)$")
CYCLE_PATTERN = re.compile(r"Cycle (\d+)", re.IGNORECASE)


@dataclass
class RepoStatus:
    """Snapshot of a single repository's basic portfolio health."""

    name: str
    path: str
    latest_commit: str
    latest_commit_date: str
    latest_commit_message: str
    latest_cycle: int | None
    required_files_present: int
    required_files_total: int
    missing_required_files: list[str]
    open_roadmap_items: int
    open_roadmap_preview: list[str]
    test_file_count: int
    prompt_doc_count: int
    python_module_count: int
    completion_band: str
    target_track: str
    priority_rank: int = 0


def run_git(repo_path: Path, *args: str) -> str:
    """Run a git command and return stripped stdout."""
    result = subprocess.run(
        ["git", "-C", str(repo_path), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def parse_open_roadmap_items(text: str) -> list[str]:
    """Extract unchecked roadmap checklist items."""
    return [match.strip() for match in UNCHECKED_PATTERN.findall(text)]


def classify_completion_band(open_items: int, missing_required_files: int) -> str:
    """Map simple repository signals to a readable completion band."""
    if missing_required_files > 0:
        return "foundation-gap"
    if open_items <= 5:
        return "near-complete"
    if open_items <= 12:
        return "advanced"
    if open_items <= 20:
        return "active"
    return "expanding"


def classify_target_track(open_items: int, missing_required_files: int) -> str:
    """Map repository state to a practical delivery track."""
    if missing_required_files > 0:
        return "foundation-first"
    if open_items == 0:
        return "beyond-ready"
    if open_items <= 10:
        return "complete-now"
    if open_items <= 20:
        return "complete-next"
    return "expand-then-complete"


def ensure_repo_checkout(repo: dict[str, str], base_dir: Path, cache_dir: Path, clone_missing: bool) -> Path:
    """Resolve a repository path, cloning to cache when required."""
    local_path = base_dir / repo["name"]
    if (local_path / ".git").exists():
        return local_path

    cached_path = cache_dir / repo["name"]
    if (cached_path / ".git").exists():
        return cached_path

    if not clone_missing:
        raise FileNotFoundError(f"Repository not found locally: {repo['name']}")

    cached_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--depth", "1", repo["url"], str(cached_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return cached_path


def collect_repo_status(repo: dict[str, str], repo_path: Path) -> RepoStatus:
    """Collect status data for one repository."""
    latest_commit = run_git(repo_path, "log", "-1", "--pretty=format:%h")
    latest_commit_date = run_git(repo_path, "log", "-1", "--date=short", "--pretty=format:%cs")
    latest_commit_message = run_git(repo_path, "log", "-1", "--pretty=format:%s")

    cycle_match = CYCLE_PATTERN.search(latest_commit_message)
    latest_cycle = int(cycle_match.group(1)) if cycle_match else None

    missing_required_files = [name for name in REQUIRED_FILES if not (repo_path / name).exists()]
    required_files_present = len(REQUIRED_FILES) - len(missing_required_files)

    roadmap_path = repo_path / "ROADMAP.md"
    open_items: list[str] = []
    if roadmap_path.exists():
        open_items = parse_open_roadmap_items(roadmap_path.read_text(encoding="utf-8"))

    test_file_count = len(list(repo_path.rglob("tests/test_*.py")))
    prompt_doc_count = len(list((repo_path / "docs").rglob("prompts/*.md"))) if (repo_path / "docs").exists() else 0
    python_module_count = len(
        [
            path for path in repo_path.rglob("*.py")
            if ".venv" not in path.parts and ".git" not in path.parts and "__pycache__" not in path.parts
        ]
    )

    return RepoStatus(
        name=repo["name"],
        path=str(repo_path),
        latest_commit=latest_commit,
        latest_commit_date=latest_commit_date,
        latest_commit_message=latest_commit_message,
        latest_cycle=latest_cycle,
        required_files_present=required_files_present,
        required_files_total=len(REQUIRED_FILES),
        missing_required_files=missing_required_files,
        open_roadmap_items=len(open_items),
        open_roadmap_preview=open_items[:3],
        test_file_count=test_file_count,
        prompt_doc_count=prompt_doc_count,
        python_module_count=python_module_count,
        completion_band=classify_completion_band(len(open_items), len(missing_required_files)),
        target_track=classify_target_track(len(open_items), len(missing_required_files)),
    )


def render_markdown(statuses: Iterable[RepoStatus]) -> str:
    """Render a Markdown portfolio status report."""
    items = sorted(statuses, key=lambda status: (status.open_roadmap_items, status.name))
    total_open = sum(status.open_roadmap_items for status in items)
    near_complete = sum(1 for status in items if status.completion_band == "near-complete")
    foundation_gap = [status.name for status in items if status.completion_band == "foundation-gap"]

    lines = [
        "# Portfolio Status",
        "",
        "Generated by `scripts/portfolio_status.py`.",
        "",
        "## Summary",
        "",
        f"- Repositories scanned: **{len(items)}**",
        f"- Total open roadmap items: **{total_open}**",
        f"- Near-complete repositories: **{near_complete}**",
        f"- Repositories with missing core files: **{len(foundation_gap)}**",
    ]

    if foundation_gap:
        lines.append(f"- Core file gaps: {', '.join(foundation_gap)}")

    lines.extend(
        [
            "",
            "## Completion-First Order",
            "",
            "| Priority | Repository | Track | Open Roadmap Items |",
            "|----------|------------|-------|--------------------|",
        ]
    )

    for status in items:
        lines.append(
            f"| {status.priority_rank} | {status.name} | {status.target_track} | {status.open_roadmap_items} |"
        )

    lines.extend(
        [
            "",
            "## Matrix",
            "",
            "| Repository | Latest Cycle | Open Roadmap Items | Core Files | Tests | Python Files | Band | Track |",
            "|------------|--------------|--------------------|------------|-------|--------------|------|-------|",
        ]
    )

    for status in items:
        lines.append(
            f"| {status.name} | {status.latest_cycle or '-'} | {status.open_roadmap_items} | "
            f"{status.required_files_present}/{status.required_files_total} | {status.test_file_count} | "
            f"{status.python_module_count} | {status.completion_band} | {status.target_track} |"
        )

    lines.extend(["", "## Priority Backlog", ""])
    for status in items:
        lines.append(f"### {status.name}")
        lines.append("")
        lines.append(f"- Latest commit: `{status.latest_commit}` on {status.latest_commit_date}")
        lines.append(f"- Latest message: {status.latest_commit_message}")
        if status.missing_required_files:
            lines.append(f"- Missing core files: {', '.join(status.missing_required_files)}")
        if status.open_roadmap_preview:
            lines.append("- Next visible roadmap gaps:")
            for item in status.open_roadmap_preview:
                lines.append(f"  - {item}")
        else:
            lines.append("- No unchecked roadmap items were found.")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Generate cross-portfolio status reports.")
    parser.add_argument("--base-dir", type=Path, default=Path.cwd().parent, help="Directory containing local repository clones.")
    parser.add_argument("--cache-dir", type=Path, default=Path(".cache/portfolio-status"), help="Directory used when cloning missing repositories.")
    parser.add_argument("--clone-missing", action="store_true", help="Clone repositories into the cache dir when they do not exist locally.")
    parser.add_argument("--output-md", type=Path, default=Path("PORTFOLIO_STATUS.md"), help="Markdown report output path.")
    parser.add_argument("--output-json", type=Path, default=Path("portfolio-status.json"), help="JSON report output path.")
    return parser.parse_args()


def main() -> int:
    """Generate reports and write them to disk."""
    args = parse_args()
    statuses: list[RepoStatus] = []

    for repo in REPOSITORIES:
        repo_path = ensure_repo_checkout(repo, args.base_dir, args.cache_dir, args.clone_missing)
        statuses.append(collect_repo_status(repo, repo_path))

    ordered = sorted(statuses, key=lambda status: (status.open_roadmap_items, status.name))
    for index, status in enumerate(ordered, start=1):
        status.priority_rank = index

    args.output_md.write_text(render_markdown(statuses), encoding="utf-8")
    args.output_json.write_text(
        json.dumps([asdict(status) for status in statuses], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
