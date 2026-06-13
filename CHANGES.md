# Changes

## 2026-06-13

- Defined the intended credential-free Parse scenario: authenticated private
  notes, owner-scoped reads and writes, explicit UI outcomes, a deterministic
  fake-first application boundary, and separate SDK compatibility work.
- Added a structural guard for credential-free signing metadata that rejects
  Apple development teams, provisioning profiles, entitlements paths, and
  account-specific signing identities in the Xcode project.

## 2026-06-12

- Disabled persisted checkout credentials in hosted macOS validation and made
  the baseline enforce the exact pinned workflow contract.
- Added contributor-safety checks and rejected duplicate or unexpected Xcode
  native targets in source membership validation.

## 2026-06-09

- Added stable `make lint`, `make test`, `make build`, and `make verify`
  aliases for the no-Xcode static baseline.
- Added a static app plist guard that requires `UIMainStoryboardFile` to point
  at the checked-in `Main` storyboard.
- Added a static storyboard guard that requires the initial scene to resolve to
  the checked-in `ViewController` class.
- Added static asset catalog metadata checks for the app icon and launch image
  slots referenced by the Xcode project.

## 2026-06-10

- Added pinned, read-only hosted macOS structural validation for the legacy
  Swift/Xcode scaffold.
- Added static plist checks for the executable and product-name substitution
  tokens used by the app and XCTest targets.
- Added structured source target membership checks for app and XCTest build
  phases in the Xcode project.

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
- Added explicit Release default configurations for the app and XCTest target
  metadata.
