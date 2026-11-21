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
