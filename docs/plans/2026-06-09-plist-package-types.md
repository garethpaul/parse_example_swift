# Plist Package Types Plan

status: completed

## Context

The static checker parsed the app and test `Info.plist` files, but it did not
assert the identity metadata that distinguishes the runnable app from the test
bundle.

## Objectives

- Preserve `CFBundlePackageType` as `APPL` for the app target.
- Preserve `CFBundlePackageType` as `BNDL` for the XCTest target.
- Require non-empty plist bundle identifiers that keep the product-name token.
- Extend `make check` and docs so plist bundle identifiers and package types
  stay visible during scaffold maintenance.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
