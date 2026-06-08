# Parse Swift Baseline Plan

status: completed

## Context

`parse_example_swift` is a minimal early Swift iOS scaffold. It contains an
Xcode project, app delegate, view controller, storyboard, and placeholder
XCTest target, but it does not include a Parse SDK dependency or implemented
backend flow.

## Risks

- The repository name implies a Parse integration that is not implemented.
- Future changes could accidentally commit Parse credentials, application IDs,
  client keys, or production endpoints.
- Local verification depended on Xcode being available, which is not guaranteed
  in this checkout environment.
- Xcode user state, archives, logs, and environment files were not fully
  ignored.

## Work Completed

- Added `make check` and `scripts/check-baseline.py` for dependency-free static
  verification.
- Verified plist and storyboard files parse without invoking Xcode.
- Added static guardrails against checked-in Parse credential or login snippets.
- Documented the legacy Swift/Xcode scaffold status and the absence of a Parse
  SDK integration.
- Expanded ignore rules for Xcode local state, build artifacts, logs,
  temporary files, and environment files.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
