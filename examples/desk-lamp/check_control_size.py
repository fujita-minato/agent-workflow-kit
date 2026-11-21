"""Check a fictional tutorial layout against its agreed target size."""
import json
from pathlib import Path
import sys


def main():
    try:
        target = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["switch_target"]
        width, height = target["width"], target["height"]
        if type(width) is not int or type(height) is not int:
            raise ValueError("Target dimensions must be integers")
    except (IndexError, KeyError, OSError, TypeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    if min(width, height) < 44:
        print("FAIL")
        print(f"Switch target is only {width} by {height} pixels")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
