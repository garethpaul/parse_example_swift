# Safe Make Root

## Problem

Caller-controlled Make metadata could redirect the integrity trust chain outside
the frozen legacy checkout.

## Change

- Resolve the Makefile directory with POSIX-safe absolute path handling.
- Reject non-file `MAKEFILE_LIST` origins and ignore caller `REPO_ROOT` values.
- Shell-quote the resolved root once before any recipe uses it.
- Add dependency-free dry-run and live command-substitution regressions.

## Validation

- Refresh protected Makefile and baseline hashes, then the workflow bootstrap.
- Run integrity, static, hostile mutation, and root-policy gates.
- Confirm hosted macOS validation and CodeQL pass at the exact PR head.
