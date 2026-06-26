# Changes

## 2026-06-26 13:51:31 PDT - P1 - Make repository verification authoritative

### Summary

Closed a Make invocation bypass that allowed a later caller-controlled
Makefile to replace every verification recipe and return success without
running integrity, structural, mutation, or root tests.

### Work completed

- Converted public targets to guarded double-colon rules with a repository
  authority prerequisite.
- Rejected later single-colon replacement, later double-colon append,
  preloaded Makefiles, caller `MAKEFLAGS`, and ten non-executing or
  error-ignoring modes.
- Replaced dry-run-only root assertions with live minimal-fixture executions.
- Extended frozen static contracts and hostile regressions.

### Threads

- None; the focused Make authority work was completed directly.

### Files changed

- `Makefile` — enforce one authoritative executable verification graph.
- `scripts/test-makefile-root.py` — cover replacement, append, mode, override,
  and live path behavior.
- `scripts/check-baseline.py`, `scripts/check-integrity.py`, and
  `.github/workflows/check.yml` — freeze the reviewed authority boundary.
- `README.md`, `SECURITY.md`, `VISION.md`, `AGENTS.md`, and
  `docs/plans/2026-06-26-make-invocation-authority.md` — document behavior and
  evidence.

### Validation

- Full structural, mutation, Make authority, external-directory, integrity,
  and diff checks — recorded in the completed plan.

### Bugs / findings

- P1 fixed: a later `-f` file could replace all leaf recipes, preserve the
  aggregate dependency graph, and return exit 0 without running any check.
- P1 fixed: `-n`, `-t`, `-q`, and `-i` families could report success while
  suppressing execution or errors.

### Blockers

- Current-Xcode and Parse SDK compatibility remain intentionally unclaimed.

### Next action

- Make the separate compatibility decision before adding any Parse SDK or
  private-note implementation.

## 2026-06-21

- Made absolute Makefile verification safe for spaces, apostrophes, quotes,
  backticks, and shell metacharacters,
  ignored caller-provided `REPO_ROOT` values, and rejected command-line or
  environment `MAKEFILE_LIST` injection before the integrity trust chain runs.
- Added live command-substitution regressions and refreshed protected-file and
  bootstrap hashes.

## 2026-06-19

- Pinned the intended native source and Xcode project inputs with SHA-256
  digests, retaining the exact closed-world repository inventory so assembled
  networking, alternate file APIs, comments, dead code, source renames, and
  source additions cannot evade validation.
- Added a workflow-pinned integrity bootstrap that protects Make policy, the
  structural checker, and hostile tests from isolated laundering, with
  executable mutations for each trust-chain layer.
- Rejected executable tracked files, Gitlinks/submodules, unmerged index stages,
  hidden tracked paths, and unexpected tracked entries; documented canonical
  byte/line-ending behavior, the deliberate hash-update order, archive limits,
  and the repository-local rather than externally attested trust boundary.
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
