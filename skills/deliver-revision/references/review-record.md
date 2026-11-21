# Candidate review record

Put an artifact, its review evidence and its review record in a local folder. The record uses this form.

```json
{
  "kind": "film",
  "artifact": {"path": "final.mp4", "sha256": "<64 lowercase hexadecimal characters>"},
  "reviews": {
    "content": {"verdict": "PASS", "sha256": "<artifact SHA-256>", "evidence": "content.md"},
    "visual": {"verdict": "PASS", "sha256": "<artifact SHA-256>", "evidence": "visual.md"}
  }
}
```

Use `kind: "text"` for a complete text. Its required review is `content`. Paths are relative to the record and must resolve to nonempty files inside its folder. Use distinct evidence files for the content and visual decisions. A content review records what was checked against the primary source, the limits of each claim, and any remaining uncertainty. A visual review records what happened at specific timestamps during actual playback and the independent viewer's interpretation. Keep these files with the team.

```sh
python3 -B .agent-workflow-local/check_delivery.py path/to/review.json
```

After a PASS, send the owner a link to the complete candidate and a compact summary of decisions, checks and open issues. On a failed review, revise internally and recheck the new artifact. The review hash identifies the exact candidate examined. Authorization for sampling, publication and changes to project direction stays with the owner.
