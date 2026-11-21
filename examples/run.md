# Fictional walkthrough

An owner asks, “Make the desk-lamp setup guide easier to follow. Show me the revised guide when it's ready.”

1. The coordinator assigns one project lead. The brief specifies a first-time reader, the current guide and the fictional device instructions.
2. The research lead tests the source for the controls. A worker checks for ambiguous wording and compares examples without editing the guide.
3. The project lead assigns one writer. The reviewer opens the actual revised document, then records the exact question the guide answers and the checked conditions.
4. Run the delivery gate on [this complete example](desk-lamp/review.json).

```sh
python3 -B scripts/check_delivery.py examples/desk-lamp/review.json
```

The reviewed [complete guide](desk-lamp/final.md) goes to the owner with a short summary. The example's source and evidence are fictional. The visual-review skill would be used on the exact exported candidate if the deliverable were a film.

## Keep a correction from recurring

The owner also wants the switch shown in a fictional interactive tutorial to be large enough to tap. The team agrees on a 44 by 44 pixel minimum for this example and records it under `lamp-control-size`. The [old layout](desk-lamp/layout-before.json) has a 24 by 24 target. The [revised layout](desk-lamp/layout-after.json) has a 48 by 48 target. Run the same check on both through the [feedback manifest](desk-lamp/feedback.json).

```sh
python3 -B scripts/check_feedback.py examples/desk-lamp/feedback.json
```

The gate passes once the old layout fails and the revised layout passes. If the target shrinks again, the project verification reports the feedback ID.
