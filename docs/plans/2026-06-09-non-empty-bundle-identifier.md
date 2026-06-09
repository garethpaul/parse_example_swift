# Non-Empty Bundle Identifier Plan

status: completed

## Context

The scaffold XCTest checked that `NSBundle.mainBundle().bundleIdentifier` was
non-nil, but an empty identifier would still pass that assertion.

## Objectives

- Add an `XCTAssertFalse` assertion for empty bundle identifiers.
- Extend the static checker so the non-empty assertion remains in place.
- Document the stricter scaffold XCTest expectation.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
