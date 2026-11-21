# Candidate review record

Put an artifact, its review evidence and its review record in a local folder. The record uses this form.

```json
{
  "kind": "film",
  "artifact": {"path": "final.mp4", "sha256": "<64 lowercase hexadecimal characters>"},
  "reviews": {
    "content": {
      "verdict": "PASS",
      "sha256": "<artifact SHA-256>",
      "evidence": "content.md",
      "evidence_sha256": "<SHA-256 of content.md>"
    },
    "visual": {
      "verdict": "PASS",
      "sha256": "<artifact SHA-256>",
      "evidence": "visual.md",
      "evidence_sha256": "<SHA-256 of visual.md>"
    }
  }
}
```

Use `kind: "text"` for `.md`, `.txt`, `.rst`, `.html`, `.htm`, `.pdf`, `.docx`, `.odt`, or `.rtf`. It requires a content review. Use `kind: "film"` for `.mp4`, `.mov`, `.m4v`, `.webm`, `.mkv`, or `.avi`. It requires both content and visual reviews. Other formats cannot pass. Paths are relative to the record and must resolve to nonempty files inside its folder.

1. The lead computes the candidate's SHA-256 locally and gives its path and digest to the reviewer.
2. The reviewer inspects that exact candidate. For a film, use an approved local player, such as a desktop player opening a local file. If the agent cannot play the film, assign actual playback to an independent local viewer and have that viewer issue the visual verdict. An agent can check the handoff for completeness. When playback is missing, record BLOCKED.
3. Each reviewer uses a separate UTF-8 evidence file. The first line contains the verdict, a space, and the candidate digest, such as `PASS <artifact SHA-256>`. On later lines, the content reviewer records source checks and limits. The visual reviewer records observations and interpretation at specific timestamps. The lead hashes each completed evidence file and records its digest in `evidence_sha256`.

```sh
python3 -B .agent-workflow-local/check_delivery.py --sha256 path/to/final.mp4
python3 -B .agent-workflow-local/check_delivery.py --sha256 path/to/visual.md
python3 -B .agent-workflow-local/check_delivery.py path/to/review.json
```

If evidence changes, confirm its new verdict and revalidate the record. Update older records only after checking the actual evidence. Keep candidates, screenshots and review records local. Use a local reviewer for private materials rather than attaching them to a hosted agent.

After a PASS, give the owner a local link to the complete candidate and a compact summary of decisions, checks and open issues. On a failed review, revise internally and recheck the new artifact. Authorization for sampling, publication and changes to project direction stays with the owner.
