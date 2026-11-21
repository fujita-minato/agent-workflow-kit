#!/usr/bin/env python3
"""Check that the required reviews refer to the exact deliverable."""
import argparse
import hashlib
import json
from pathlib import Path

REQUIRED = {"text": ("content",), "film": ("content", "visual")}
SUPPORTED_SUFFIXES = {
    "text": {".md", ".txt", ".rst", ".html", ".htm", ".pdf", ".docx", ".odt", ".rtf"},
    "film": {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi"},
}


def file_sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def local_file(directory, name):
    given = Path(name)
    path = (directory / given).resolve()
    if given.is_absolute() or not path.is_relative_to(directory):
        raise ValueError("Artifact and evidence must stay inside the review folder")
    if not path.is_file() or not path.stat().st_size:
        raise ValueError("Artifact and evidence must be nonempty files")
    return path


def check(record):
    directory = record.parent.resolve()
    data = json.loads(record.read_text(encoding="utf-8"))
    kind = data["kind"]
    artifact = local_file(directory, data["artifact"]["path"])
    if artifact.suffix.lower() not in SUPPORTED_SUFFIXES[kind]:
        raise ValueError(f"Unsupported {kind} format: {artifact.suffix or '(no extension)'}")
    digest = file_sha256(artifact)
    if digest != data["artifact"]["sha256"]:
        raise ValueError("Artifact hash no longer matches the review record")

    seen = {record.resolve(), artifact}
    for name in REQUIRED[kind]:
        review = data["reviews"][name]
        if review["verdict"] != "PASS" or review["sha256"] != digest:
            raise ValueError(f"{name} must have a PASS for this artifact hash")
        evidence = local_file(directory, review["evidence"])
        if evidence in seen:
            raise ValueError(f"{name} must reference its own evidence file")
        evidence_bytes = evidence.read_bytes()
        if hashlib.sha256(evidence_bytes).hexdigest() != review.get("evidence_sha256"):
            raise ValueError(f"{name} evidence hash is missing or no longer matches the review record")
        header, _, notes = evidence_bytes.decode("utf-8").partition("\n")
        if header.rstrip("\r") != f"PASS {digest}":
            raise ValueError(f"{name} evidence must record PASS for this artifact hash")
        if not notes.strip():
            raise ValueError(f"{name} evidence must include review notes")
        seen.add(evidence)
    return artifact


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Review record, or a local file with --sha256")
    parser.add_argument("--sha256", action="store_true", help="Print the SHA-256 of a local file")
    args = parser.parse_args()
    try:
        if args.sha256:
            print(file_sha256(args.path))
            return
        artifact = check(args.path)
    except (OSError, RuntimeError, TypeError, ValueError, KeyError) as error:
        parser.exit(1, f"REVISE: {error}\n")
    print(f"PASS: {artifact.name}")


if __name__ == "__main__":
    main()
