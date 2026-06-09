# Main Storyboard Plist Plan

status: completed

## Context

The storyboard already declares an initial view controller, but the app plist is
the launch contract that tells iOS which storyboard to open. If
`UIMainStoryboardFile` drifts away from `Main`, the checked-in launch scene can
stop being used even though the storyboard XML still looks valid.

## Objectives

- Require `parse_example/Info.plist` to keep `UIMainStoryboardFile` set to
  `Main`.
- Add scaffold XCTest coverage for the main storyboard plist entry.
- Extend the static checker and docs so launch metadata remains visible.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
