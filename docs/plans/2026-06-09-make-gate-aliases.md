# Make Gate Aliases Plan

status: completed

## Context

The repository had a working `make check` static baseline for the legacy
Swift/Xcode scaffold, but did not expose the standard local `make lint`,
`make test`, `make build`, or `make verify` aliases. Xcode is not available in
all automation environments, so the aliases need a deterministic no-Xcode path.

## Objectives

- Add `make lint` as the static baseline alias.
- Add `make test` as the no-Xcode static test metadata alias.
- Add `make build` as the no-Xcode build metadata alias.
- Add `make verify` as the full local verification alias.
- Document the alias behavior in the README, security notes, and vision.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
