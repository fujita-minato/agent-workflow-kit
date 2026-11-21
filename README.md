# Agent Workflow Kit

A project-local starter for teams that use Claude Code, Codex, or both. Use seven agent roles and seven skills to split project coordination from research, turn decisions into executable briefs, and give the owner the complete revision after review.

## Quick start

Requires Python 3.11 or newer. The tools use the standard library.

1. Run `./scripts/verify` in this repository.
2. From this repository, run `python3 scripts/install.py /path/to/your-project --runtime both`. Use `claude` or `codex` to install one runtime. The target must already exist.
3. Start the agent in the target project, using its coordinator role or the `coordinate-work` skill. Give it a real request and the project folder where it should find the latest handoff. [Walk through a fictional example](examples/run.md).

The installer writes project-local skills, role definitions and verification scripts. It keeps existing files, reports conflicts before writing, and can be rerun to check or add an installation. It does not create accounts, configure browser profiles or install integrations.

| Role | Responsibility |
| --- | --- |
| Coordinator | Set priorities, assign a project lead, and collect decisions and evidence. |
| Research lead | Choose a skill, inspect original sources, and use workers to search and deduplicate in batches. |
| Project lead | Turn intent into a brief, supervise the revision, and confirm review of the complete version. |
| Worker | Implement a scoped brief and report results with evidence. |
| Reviewer | Inspect the exact candidate independently and return a verdict with specific evidence. |
| Motion designer | Develop the storyboard, motion approach and sample for an approved script. |
| Workflow auditor | Compare completion claims and queue state with actual evidence. |

The roles can run as separate agents or as explicit stages handled by a smaller team. Assign a single writer per artifact. Run independent review separately from implementation where possible.

## Review and handoff

Use a single versioned review record for the candidate. For a film, content and visuals each need a PASS and an evidence reference tied to that artifact. For revised text, content needs a PASS. A project's first-sample approval and publication permissions are separate decisions. [Review record format](skills/deliver-revision/references/review-record.md)

The delivery checker verifies the candidate format, the artifact's SHA-256 and the SHA-256 of each review evidence file. It also checks that each evidence file names the exact candidate and records PASS. A reviewer still judges the work. Use independent local playback for a film if the agent cannot play it.

Use [feedback regression checks](skills/coordinate-work/references/feedback-checks.md) for recurring corrections. Rerun the installer to add the checker to an existing installation. Wire it into your project's verification entry point so each check must reject a known bad example and accept the current candidate.

## Adapting the kit

- Choose tools, browser profile aliases, project directories and access limits in your own environment. Open only the intended project's profile and verify it before accessing signed-in sites.
- Keep credentials, account mappings, transcripts, screenshots, active deliverables and review evidence local. Use a local reviewer for private material and keep it out of hosted tools and public repositories. `python3 scripts/privacy_check.py .` checks the release tree for common privacy leaks. Inspect the diff and Git metadata before sharing.
- The kit provides project-local role templates and checks. Configure any scheduling, browser integration or publishing integration in your own environment according to its permissions.

[MIT License](LICENSE)
