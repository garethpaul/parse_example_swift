# Non-Placeholder XCTest

status: completed

## Context

The legacy test target still contained generated placeholder XCTest methods:
`testExample()` asserted `true`, and `testPerformanceExample()` measured an
empty block. Those methods did not verify any part of the app scaffold.

## Objectives

- Preserve the legacy XCTest target.
- Replace generated placeholder tests with a small scaffold assertion.
- Verify that the app bundle identifier is configured with
  `testAppBundleIdentifierIsConfigured`.
- Extend `make check` and docs so placeholder tests do not return.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`

Full Xcode test execution still requires macOS with a compatible Xcode version.
