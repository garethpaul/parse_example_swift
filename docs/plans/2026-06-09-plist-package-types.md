# Plist Package Types Plan

status: completed

## Context

The static checker parsed the app and test `Info.plist` files, but it did not
assert the package type values that distinguish the runnable app from the test
bundle.

## Objectives

- Preserve `CFBundlePackageType` as `APPL` for the app target.
- Preserve `CFBundlePackageType` as `BNDL` for the XCTest target.
- Extend `make check` and docs so plist package types stay visible during
  scaffold maintenance.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
