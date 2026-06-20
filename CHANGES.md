# Changes

## 2026-06-19

- Pinned the intended native source and Xcode project inputs with SHA-256
  digests, retaining the exact closed-world repository inventory so assembled
  networking, alternate file APIs, comments, dead code, source renames, and
  source additions cannot evade validation.
- Added a workflow-pinned integrity bootstrap that protects Make policy, the
  structural checker, and hostile tests from isolated laundering, with
  executable mutations for each trust-chain layer.
- Added executable hostile mutation coverage and an exact bounded repository
  inventory that rejects symlinks, unexpected implementation/configuration,
  signing artifacts, ATS exceptions, runtime endpoints, and oversized files.
- Updated the immutable checkout pin to the official `actions/checkout` v7.0.0
  release while retaining read-only permissions and disabled credential
  persistence.
- Recorded that Xcode 26.0.1 can enumerate the legacy targets but cannot build
  the project because its absent Swift language version is unsupported.

## 2026-06-14

- Made every standard Make alias resolve the structural checker from the
  repository root, including external absolute-Makefile calls.

## 2026-06-13

- Recorded the exact Xcode 6-era, iOS 8, legacy Swift, and absent dependency
  metadata that must precede any modern toolchain or Parse SDK compatibility
  claim.
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
