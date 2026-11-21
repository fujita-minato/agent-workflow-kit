#!/usr/bin/env python3
"""Check release files for private paths, identifiers, secrets and local artifacts."""
import argparse
from pathlib import Path
import re

RULES = (
    ("personal path", re.compile(r"(?:/(?:Users|home)/|[A-Z]:\\Users\\)[^\s/\\]+")),
    ("session identifier", re.compile(r"\blocal_[0-9a-f]{8}-[0-9a-f-]{27,}\b", re.I)),
    ("email address", re.compile(r"[\w.+-]+@(?!example\.(?:com|org|net)\b)[\w.-]+\.[a-z]{2,}", re.I)),
    ("credential-shaped string", re.compile(
        r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16})\b"
        r"|-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----")),
    ("account handle", re.compile(r"(?:instagram\.com/|tiktok\.com/@|youtube\.com/@)[\w.-]+", re.I)),
)
PRIVATE_NAMES = {".agent-workflow-local", ".DS_Store", "__pycache__", "captains.json"}


def scan(root, private_patterns=()):
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if relative.parts[0] == ".git":
            continue
        if path.is_symlink():
            yield relative, "symbolic link"
            continue
        if path.name in PRIVATE_NAMES or path.name.startswith(".env") or path.suffix in {".jsonl", ".log", ".pyc"}:
            yield relative, "local artifact"
            continue
        if path.is_dir():
            continue
        if not path.is_file():
            yield relative, "special file"
            continue
        try:
            contents = path.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            yield relative, "binary or unreadable file"
            continue
        if "\0" in contents:
            yield relative, "binary file"
            continue
        searchable = f"{relative.as_posix()}\n{contents}"
        for label, pattern in (*RULES, *private_patterns):
            match = pattern.search(searchable)
            if match:
                line = searchable.count("\n", 0, match.start())
                yield relative, f"{label} at line {line}" if line else f"{label} in path"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--private-rules", type=Path, help="Optional local regex list kept outside the release")
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error("root must be a directory")
    private = []
    if args.private_rules:
        try:
            for pattern in args.private_rules.read_text(encoding="utf-8").splitlines():
                if pattern.strip():
                    private.append(("private deny-list match", re.compile(pattern, re.I)))
        except (OSError, re.error) as error:
            parser.error(f"Cannot load private rules: {error}")
    findings = list(scan(args.root, private))
    for path, reason in findings:
        print(f"REVISE: {path}: {reason}")
    if findings:
        return 1
    print("PASS: release privacy scan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
