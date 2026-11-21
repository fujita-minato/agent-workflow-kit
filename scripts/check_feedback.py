#!/usr/bin/env python3
"""Run each recorded feedback check against a known bad case and the candidate."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys


def project_file(root, name):
    path = Path(name)
    resolved = (root / path).resolve()
    if path.is_absolute() or not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError(f"Expected a file relative to the manifest directory: {name}")
    return resolved


def load_checks(manifest):
    root = manifest.parent.resolve()
    entries = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(entries, list) or not entries:
        raise ValueError("The manifest must contain at least one feedback check")

    checks = []
    seen = set()
    for entry in entries:
        check_id = entry["id"]
        if not isinstance(check_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", check_id):
            raise ValueError("Feedback IDs must use lowercase letters, digits and hyphens")
        if check_id in seen:
            raise ValueError(f"Duplicate feedback ID: {check_id}")
        seen.add(check_id)
        requirement = entry["requirement"]
        if not isinstance(requirement, str) or not requirement.strip():
            raise ValueError(f"{check_id}: missing feedback requirement")
        checker = project_file(root, entry["check"])
        if checker.suffix != ".py":
            raise ValueError(f"{check_id}: the check must be a Python script")
        known_bad = project_file(root, entry["known_bad"])
        candidate = project_file(root, entry["candidate"])
        if known_bad == candidate:
            raise ValueError(f"{check_id}: known_bad and candidate must be different files")
        checks.append((check_id, checker, known_bad, candidate))
    return checks


def run_check(root, check_id, checker, path, label, verdict, status):
    try:
        result = subprocess.run(
            [sys.executable, "-B", str(checker), str(path)],
            cwd=root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        raise ValueError(f"{check_id} {label}: check timed out") from None
    first_line = result.stdout.partition(b"\n")[0].rstrip(b"\r")
    if result.returncode != status or first_line != verdict.encode("ascii"):
        raise ValueError(
            f"{check_id} {label}: expected {verdict} and exit {status}; checker exited {result.returncode}"
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        manifest = args.manifest.resolve()
        for check_id, checker, known_bad, candidate in load_checks(manifest):
            run_check(manifest.parent, check_id, checker, known_bad, "known_bad", "FAIL", 1)
            run_check(manifest.parent, check_id, checker, candidate, "candidate", "PASS", 0)
            print(f"PASS {check_id}: known bad case rejected and candidate passed")
    except (KeyError, OSError, RuntimeError, TypeError, ValueError) as error:
        parser.exit(1, f"REVISE: {error}\n")


if __name__ == "__main__":
    main()
