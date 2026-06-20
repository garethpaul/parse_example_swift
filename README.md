# parse_example_swift

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/parse_example_swift` is an Apple platform application or Objective-C/Swift sample. Swift Parse Example

This is a legacy Swift/Xcode scaffold. It does not currently include the Parse
SDK, Parse credentials, or an implemented backend login/data flow.

The intended first integration is a signed-in user's private-note flow with
owner-scoped reads and writes, fake-backed application tests, and no privileged
client capability. See
[`docs/intended-parse-scenario.md`](docs/intended-parse-scenario.md) for the
data, authorization, state, compatibility, and non-goal contract.

The checked-in Xcode 6-era, iOS 8, legacy Swift metadata and absent dependency
declarations are inventoried in
[`docs/legacy-toolchain-compatibility.md`](docs/legacy-toolchain-compatibility.md).
Structural validation is not a current-Xcode build or Parse SDK compatibility
claim.

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: Swift (3), C/C++ headers (1).

## Repository Contents

- `parse_example` - source or example code
- `parse_example.xcodeproj` - Xcode project file
- `parse_exampleTests` - source or example code
- `Makefile` - local static verification entry point
- `CHANGES.md` - baseline change log
- `docs/plans/2026-06-08-parse-swift-baseline.md` - completed baseline plan
- `scripts/check-integrity.py` - SHA-256 trust-chain and frozen-source checks
- `scripts/check-baseline.py` - static baseline checks used by `make check`
- `tests/test_check_baseline.py` - hostile mutation coverage for structural policy
- `SECURITY.md` - security reporting and disclosure guidance
- `VISION.md` - project direction and maintenance guardrails
- `docs/intended-parse-scenario.md` - future Parse flow and safety contract

Additional scan context:

- Source directories: parse_example, parse_exampleTests
- Dependency and build manifests: Makefile
- Entry points or build surfaces: parse_example.xcodeproj, Makefile
- Test-looking files: parse_exampleTests/Info.plist, parse_exampleTests/parse_exampleTests.swift

## Getting Started

### Prerequisites

- Git
- macOS with Xcode for building Apple platform projects

### Setup

```bash
git clone https://github.com/garethpaul/parse_example_swift.git
cd parse_example_swift
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- Open `parse_example.xcodeproj` in Xcode, choose the app or sample scheme, and run it on the matching simulator/device.
- Run `make check`, `make lint`, `make test`, `make build`, or `make verify`
  before changing the project scaffold, plist/storyboard files, or Parse
  integration assumptions.
- The test target keeps a non-placeholder XCTest that verifies the app bundle
  identifier is configured as a non-empty bundle identifier.
- Static checks preserve plist bundle identifiers and plist package types:
  `APPL` for the app and `BNDL` for the XCTest bundle.
- Static checks preserve plist executable and product-name tokens:
  `CFBundleExecutable` stays `${EXECUTABLE_NAME}` and `CFBundleName` stays
  `${PRODUCT_NAME}` for the app and XCTest targets.
- The storyboard initial view controller must stay connected to the checked-in
  `ViewController` Swift class.
- The main storyboard plist entry must keep `UIMainStoryboardFile` pointed at
  `Main`.
- Xcode project and native target default configurations stay explicit so the
  app and XCTest target default configurations remain deterministic.
- Static checks resolve source target membership through Xcode build phases so
  app and XCTest Swift files cannot silently move between targets.
- Asset catalog metadata for `AppIcon` and `LaunchImage` stays parseable and
  aligned with the Xcode project compiler settings.
- Any future Parse implementation must preserve the documented private-note
  ownership boundary and deterministic fake-first test seam before service
  calls are added.

## Testing and Verification

- `make check`
- `make lint`
- `make test`
- `make build`
- `make verify`
- `python3 scripts/check-integrity.py`
- `python3 scripts/check-baseline.py`
- Xcode's test action or `xcodebuild test` with the appropriate scheme and destination when Xcode is available

`make check` first verifies the workflow-pinned integrity bootstrap, then checks
SHA-256 digests for the exact native source, Xcode project inputs, Make policy,
baseline checker, and hostile tests before running the static baseline and
mutation suite. This freezes the intended legacy scaffold: alternate network or
path APIs, assembled strings, comments or dead code, source renames or additions,
and isolated Make/checker/test laundering all fail closed. The remaining Make
aliases stay usable on machines without Xcode.

Pinned hosted macOS structural validation independently verifies the integrity
bootstrap before running the same `make check` contract on Python 3.12. It does
not claim that this Swift 1-era iOS 8 project builds or that XCTest runs on
current Xcode.

The integrity gate hashes canonical file bytes, so line-ending rewrites change
the digest. On Git checkouts it also requires every tracked entry to be a
regular, non-executable `100644` file, rejecting executable-bit changes,
symlinks, Gitlinks/submodules, unmerged index stages, hidden tracked paths, and
unexpected tracked files. Exported source archives without `.git` still receive
the closed working-tree inventory, symlink, UTF-8, size, and byte-digest checks,
but cannot prove Git index modes or entry types.

### Updating the frozen baseline

Treat any baseline update as a review boundary, not routine hash regeneration:

1. Review the intended source/project/policy diff and update the corresponding
   entry in `PROTECTED_FILE_SHA256` in `scripts/check-integrity.py`.
2. If the baseline checker or mutation suite changes, update their protected
   digests only after the final code and tests are fixed.
3. Recompute `INTEGRITY_SHA256` from the final bytes of
   `scripts/check-integrity.py` and update `.github/workflows/check.yml` last.
4. Run `make check`, the hostile mode/type/path/line-ending mutations,
   `git diff --check`, the changed-tree secret scan, and hosted checks.

This is repository-local tamper evidence. A single reviewed change can rewrite
the bootstrap, workflow digest, and protected hashes together, so it does not
provide external attestation or make maintainer review unnecessary. It is
designed to reject isolated drift and partial validation laundering.

Hosted checkout credentials are not persisted, and the baseline enforces the
complete workflow contract so extra actions, events, permissions, or shadowed
YAML settings cannot silently weaken validation.

Credential-free signing metadata is also enforced: the Xcode project must not
contain a development team, provisioning profile, entitlements path, or
account-specific signing identity.

The structural repository inventory is exact and bounded. Required files must
be regular files smaller than 1 MiB, and unreviewed source, configuration,
framework, signing, or generated artifacts fail validation.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.
- Do not commit Parse credentials, application IDs, client keys, production
  endpoints, or captured user data.

## Security and Privacy Notes

- Review changes touching network requests, sockets, or service endpoints; examples from the scan include parse_example/Info.plist, parse_exampleTests/Info.plist.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include parse_example/Info.plist, parse_exampleTests/Info.plist.

## Maintenance Notes

- Standard Make aliases resolve the structural checker from `Makefile`, so an
  absolute Makefile path works from another directory without changing scope.
- This looks like an Apple platform project or sample. Xcode, Swift, CocoaPods, and deployment target versions may need to match the original project era.
- Keep non-placeholder XCTest coverage in place before adding Parse SDK calls or
  service-backed flows.
- Keep the non-empty bundle identifier assertion in place for scaffold changes.
- Keep plist bundle identifiers and plist package types intact when editing app
  or test target metadata.
- Keep plist executable and product-name tokens intact when editing app or test
  target metadata.
- Keep the storyboard initial view controller bound to `ViewController` when
  editing Interface Builder files.
- Keep the main storyboard plist entry aligned with the checked-in `Main`
  storyboard.
- Keep target default configurations explicit when editing Xcode project
  metadata.
- Keep asset catalog metadata intact when editing app icon or launch image
  assets.
- See `CHANGES.md` and `docs/plans/2026-06-08-parse-swift-baseline.md` for
  the current static baseline.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
