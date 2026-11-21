# Feedback regression checks

Record a recurring correction in a local manifest. Give it a stable ID, describe the expected behavior, and keep a small fixture that shows the original failure. Point the candidate field at the current project's output. Rebuild or refresh that output before running the check.

```json
[
  {
    "id": "lamp-control-size",
    "requirement": "The fictional switch target is at least 44 pixels wide and high.",
    "check": "checks/check_control_size.py",
    "known_bad": "fixtures/layout-before.json",
    "candidate": "build/layout.json"
  }
]
```

Paths are relative to the manifest directory. The runner calls the same project-owned Python check twice, with one file path as its only argument. The first line of standard output must be `FAIL` with exit status 1 for a reproduced defect, or `PASS` with exit status 0 for a valid candidate. Invalid inputs or inability to inspect the result should return exit status 2. A crash, timeout, missing file, or a check that accepts the old fixture blocks the gate. Run a failing checker directly to see its notes.

```sh
python3 -B .agent-workflow-local/check_feedback.py feedback.json
```

Run only manifests and check scripts trusted by your project. Keep real outputs and feedback records local. Use synthetic inputs for shared examples. Judgment about the quality of writing, motion, or design stays with the reviewer unless a specific test can reliably measure it.
