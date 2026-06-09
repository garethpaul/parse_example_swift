# Changes

## 2026-06-08

- Added `make check` with static project, plist, storyboard, and documentation
  checks that do not require Xcode.
- Documented that the repository is a legacy Swift/Xcode scaffold with no
  checked-in Parse SDK, Parse credentials, or implemented backend flow.
- Added a completed baseline plan under `docs/plans/`.
- Expanded local ignore rules for Xcode user state, archives, logs, temporary
  files, and environment files.
- Replaced generated placeholder XCTest methods with a scaffold bundle
  identifier check.
- Tightened the scaffold XCTest to reject an empty bundle identifier.
- Added static plist bundle identifier and package type checks for the app and
  XCTest targets.
