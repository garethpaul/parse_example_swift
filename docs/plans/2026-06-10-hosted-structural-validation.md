# Hosted Structural Validation

status: completed

## Context

The repository is a Swift 1-era iOS 8 scaffold with no checked-in Parse SDK.
Its maintained gate validates project metadata, plists, storyboard wiring,
asset catalogs, and XCTest source structure without requiring Xcode to compile
obsolete Swift syntax. No hosted validation currently runs that contract.

## Priorities

1. Run the canonical structural gate for pushes and pull requests.
2. Use a fixed macOS runner while keeping the gate independent of Xcode builds.
3. Pin actions, Python, permissions, timeout, and concurrency.
4. Keep credentials, Parse services, signing, and runtime tests out of CI.
5. Enforce the workflow contract from `scripts/check-baseline.py`.

## Implementation Units

Files:

- `.github/workflows/check.yml`
- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`

Add a commit-pinned, read-only Python 3.12 job on `macos-15` that runs
`make check`. Document the distinction between structural validation and a
future Swift/Xcode compatibility migration.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- workflow YAML parse
- `git diff --check`
- successful hosted macOS `Check` workflow for the pushed commit

## Boundaries

- Do not modernize Swift syntax or deployment targets in this pass.
- Do not add Parse credentials, SDK binaries, signing, or live service calls.
- Do not claim current Xcode build or XCTest compatibility.
