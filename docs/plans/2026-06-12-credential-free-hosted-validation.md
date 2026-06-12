# Credential-free hosted validation

status: completed

## Context

The hosted macOS workflow used pinned, read-only actions but allowed checkout
to persist its repository credential. The baseline also checked workflow
fragments independently, which could accept additional actions or shadowed YAML
settings alongside the required text.

## Decision

1. Configure checkout with `persist-credentials: false`.
2. Enforce the exact workflow contract, including events, permissions,
   concurrency, runner, timeout, action commits, Python version, and command.
3. Require the contributor guidance that protects Parse credentials, legacy
   Xcode settings, and meaningful XCTest coverage.
4. Reject duplicate or unexpected native target names before validating exact
   source membership.

## Work Completed

- Disabled checkout credential persistence while retaining the immutable
  checkout and setup-python action commits.
- Enforced the complete workflow structure, including triggers, read-only
  permissions, concurrency, runner, timeout, Python version, and `make check`.
- Required exactly the `parse_example` and `parse_exampleTests` native targets
  with their expected Swift source membership.
- Preserved repository guidance that forbids Parse credentials and protects
  the legacy Xcode and XCTest contracts.

## Verification Completed

- Local `make check`, `make verify`, `make lint`, `make test`, and `make build`
  passed the complete structural baseline.
- `python3 -W error scripts/check-baseline.py` and `git diff --check` passed.
- Twelve focused hostile mutations were rejected, covering credential
  persistence, duplicate overrides, floating and extra actions, event and
  permission drift, missing and misplaced sources, duplicate and unexpected
  native targets, removed contributor guidance, and incomplete plan status.
- GitHub Actions push run `27390789152` and pull-request run `27390794889`
  completed successfully on exact implementation head
  `44affc3f1806bcc1ebee102594a9396779704674` using `macos-15` and Python 3.12.
- The workflow preserves `persist-credentials: false`, checkout commit
  `df4cb1c069e1874edd31b4311f1884172cec0e10`, and setup-python commit
  `a309ff8b426b58ec0e2a45f0f869d46889d02405`.
- The project parser requires `PBXSourcesBuildPhase`, target `parse_example`
  with `AppDelegate.swift` and `ViewController.swift`, and target
  `parse_exampleTests` with `parse_exampleTests.swift`.
