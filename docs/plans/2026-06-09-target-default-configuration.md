# Target Default Configuration Plan

status: completed

## Context

The project-level configuration list declared `defaultConfigurationName =
Release`, but the app and XCTest native target configuration lists did not.
Keeping target defaults explicit makes the legacy Xcode metadata easier to
review statically when Xcode is unavailable.

## Objectives

- Add `defaultConfigurationName = Release;` to the app native target
  configuration list.
- Add `defaultConfigurationName = Release;` to the XCTest native target
  configuration list.
- Extend static checks and docs so target default configurations remain
  explicit.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
