#!/usr/bin/env python3
"""Check that the required reviews refer to the exact deliverable."""
import argparse
import hashlib
import json
from pathlib import Path

REQUIRED = {"text": ("content",), "film": ("content", "visual")}
VIDEO_SUFFIXES = {".mp4", ".mov", ".m4v", ".webm"}


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
    if kind == "film" and artifact.suffix.lower() not in VIDEO_SUFFIXES:
        raise ValueError("Film review must reference a video file")
    if kind == "text" and artifact.suffix.lower() in VIDEO_SUFFIXES:
        raise ValueError("Video files require the film review")
    with artifact.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
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
        seen.add(evidence)
    return artifact


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        artifact = check(args.record)
    except (OSError, RuntimeError, TypeError, ValueError, KeyError) as error:
        parser.exit(1, f"REVISE: {error}\n")
    print(f"PASS: {artifact.name}")


if __name__ == "__main__":
    main()
