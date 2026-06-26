# Make Invocation Authority

status: completed

## Summary

Keep repository verification authoritative when callers provide additional
Makefiles or GNU Make modes that suppress execution or ignore errors.

## Problem

The root Makefile rejected direct `MAKEFILE_LIST` overrides but used ordinary
single-colon recipes. A caller could load a later Makefile that replaced every
leaf recipe; the aggregate dependency graph remained present, yet each leaf
only ran attacker-controlled success commands. Dry-run, touch, question, and
ignore-error modes could likewise return a false-green result.

## Design

Use double-colon public targets and attach a repository-owned authority
prerequisite through secondary expansion. A later single-colon replacement is
invalid because GNU Make forbids mixing rule kinds; a later double-colon append
still inherits the authority prerequisite, which rejects the expanded
`MAKEFILE_LIST` before target recipes execute. Reject `MAKEFILES`, caller
`MAKEFLAGS`, and GNU Make's non-executing or error-ignoring modes at parse time.

An in-recipe guard was rejected because the later file can replace that recipe.
A new wrapper command was rejected because it would abandon the documented
Make interface instead of fixing its ownership boundary.

## Implementation

- Converted all public targets to double-colon rules.
- Added the `__repository-make-authority` prerequisite and exact Makefile-list
  comparison.
- Rejected preloaded Makefiles, command-line `MAKEFLAGS`, and short/long
  non-executing or error-ignoring modes.
- Added live minimal-fixture target executions plus later-recipe and mode
  regressions.
- Updated the static checker, repository guidance, and integrity digests.

## Verification Completed

- All seven Make root tests passed with real target execution.
- All 27 baseline mutations passed, including single-colon replacement and
  double-colon append rejection before the attacker marker was created.
- All ten non-executing and error-ignoring modes were rejected with the
  documented diagnostic.
- `make check` passed from the repository root.
- Absolute-Make verification passed from an external working directory.
- Frozen integrity verification passed after reviewing and updating the exact
  Makefile, checker, and test digests.
- `git diff --check`, Python compilation, generated-artifact, conflict-marker,
  and secret-shaped-content audits passed.
