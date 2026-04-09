# Completion Strategy

## Goal

Move every permanent Cyber Port repository from active development into a genuinely complete and then beyond-complete state, without shipping shallow filler.

## What "Complete" Means

A repository is considered **complete** only when all of the following are true:

- Its visible roadmap checklist is fully closed
- Core repository files are present and current
- The local install and primary test workflow run successfully
- The CLI or main entrypoints are usable and documented
- The repository has meaningful tests, not placeholder coverage
- Documentation explains what the project does, how to run it, and its limitations
- The project is still strictly defensive and safe for public GitHub publication

## What "Beyond" Means

After a repository reaches complete status, the next phase is **beyond**:

- Stronger interoperability with other k1N repositories
- Better export formats, dashboards, and automation hooks
- Higher operational maturity
- Reference deployments and richer training content
- Better reporting, packaging, governance, and maintenance workflows

## Execution Model

The portfolio now uses a **completion-first** order instead of a simple round-robin loop:

1. Finish repositories with the fewest remaining roadmap gaps first
2. Stabilize them with tests, packaging, and documentation
3. Re-rank the whole portfolio after every cycle
4. Once a repository is complete, shift it into the beyond queue

## Priority Rule

The default priority order is generated from `PORTFOLIO_STATUS.md` and should prefer:

- Near-complete repositories first
- Then advanced repositories
- Then active repositories
- Then expanding repositories

Within the same band, fewer open roadmap items come first.
