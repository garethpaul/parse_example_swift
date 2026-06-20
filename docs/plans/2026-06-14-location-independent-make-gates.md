# Location-Independent Make Gates

status: completed

## Context

The dependency-free structural checker passes from the repository root and by
direct absolute script path, but an absolute Makefile invocation from another
working directory still resolves `scripts/check-baseline.py` against the
caller. Shared automation should use the standard aliases without first
changing directories.

## Requirements

- Derive an override-protected repository root from the Makefile location.
- Invoke the structural checker by its rooted path for `lint`, `test`, `build`,
  `verify`, and `check` without changing alias behavior.
- Preserve the legacy Swift/Xcode compatibility inventory, no-SDK boundary,
  credential-free metadata, workflow, and dependency-free checker.
- Statically reject caller-relative or caller-overridable checker execution.
- Record completed repository-root and external-Makefile verification.

## Scope Boundaries

- Do not change Swift, XCTest, Xcode project, plist, storyboard, asset catalog,
  workflow, deployment target, signing, SDK, dependency, or credential data.
- Do not claim a current Xcode build or simulator result.
- Do not weaken the structural checker or compatibility non-goals.

## Implementation Units

1. Root the Makefile's checker recipe while preserving every existing alias.
2. Extend `scripts/check-baseline.py` to require the rooted recipe, this plan,
   completed evidence, and maintenance documentation.
3. Document the external invocation contract in `README.md` and `CHANGES.md`.

## Verification Plan

- Run every standard alias from the repository root and through the absolute
  Makefile path from `/tmp`, including a caller-supplied root override.
- Compile the checker outside the repository and parse workflow YAML, plists,
  storyboard XML, asset-catalog JSON, and README SVG.
- Run isolated hostile mutations over rooted execution and completed evidence.
- Audit intended paths, unchanged implementation/project surfaces, whitespace,
  generated artifacts, captured identifiers, and secret-like data.

## Work Completed

The Makefile now derives an override-protected absolute repository root from
its own location and invokes the dependency-free structural checker through
that root. Every existing alias still resolves to the same checker, and no
Swift, XCTest, Xcode project, plist, storyboard, asset, workflow, or dependency
surface changed.

## Verification Completed

- `make lint`, `make test`, `make build`, `make verify`, `make check`, and
  `make static-check` passed from the repository root.
- Every alias passed from `/tmp` through the repository's absolute Makefile
  path.
- External `make check` passed with caller-supplied `REPO_ROOT=/tmp`, confirming
  command-line variables cannot redirect checker execution.
- `python3 -m py_compile scripts/check-baseline.py` passed with bytecode routed
  outside the repository; workflow YAML, both plists, storyboard XML,
  README SVG, and both asset-catalog JSON files parsed successfully.
- Nine isolated hostile mutations were rejected across root derivation,
  override resistance, checker invocation, completed evidence, README, and
  change-history contracts.
