#!/usr/bin/env python3
"""Install project-local skills, role definitions and the delivery checker."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIMES = {"claude": Path(".claude"), "codex": Path(".codex")}


def install(target, runtime):
    target = target.resolve(strict=True)
    if not target.is_dir():
        raise ValueError("The target must be an existing project directory")
    sources = {}
    for name in RUNTIMES if runtime == "both" else (runtime,):
        config = RUNTIMES[name]
        skills = Path(".agents/skills") if name == "codex" else config / "skills"
        for src in (ROOT / "skills").rglob("*"):
            if src.is_file():
                sources[skills / src.relative_to(ROOT / "skills")] = src
        for src in (ROOT / "agents" / name).iterdir():
            sources[config / "agents" / src.name] = src
    sources[Path(".agent-workflow-local/check_delivery.py")] = ROOT / "scripts/check_delivery.py"

    pending = {}
    for rel, src in sorted(sources.items()):
        path = target / rel
        parents = (target / parent for parent in rel.parents if parent != Path("."))
        if path.is_symlink() or any(p.is_symlink() or (p.exists() and not p.is_dir()) for p in parents):
            raise ValueError(f"Conflicting path: {rel}")
        content = src.read_bytes()
        if path.exists():
            if not path.is_file() or path.read_bytes() != content:
                raise ValueError(f"Existing file differs: {rel}")
        else:
            pending[path] = content

    created = []
    try:
        for path, content in pending.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as handle:
                created.append(path)
                handle.write(content)
    except OSError:
        for path in reversed(created):
            path.unlink(missing_ok=True)
        raise
    return len(created)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("--runtime", choices=(*RUNTIMES, "both"), required=True)
    args = parser.parse_args()
    try:
        count = install(args.target, args.runtime)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Installation stopped: {error}\n")
    print(f"Installed {count} files. Matching existing files were kept.")


if __name__ == "__main__":
    main()
