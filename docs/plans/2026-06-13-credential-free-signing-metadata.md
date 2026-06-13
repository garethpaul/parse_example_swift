# Credential-free signing metadata

status: completed

## Context

The repository documents a credential-free legacy Xcode scaffold, but the
baseline does not enforce that account-specific signing metadata stays out of
the project file. A committed development team, provisioning profile, signing
certificate, or entitlements path could couple the sample to a real Apple
developer account or disclose account-specific configuration.

## Requirements

- Reject development team identifiers, provisioning profile UUIDs or
  specifiers, and code-signing entitlements paths in project build settings.
- Preserve only the historical generic `iPhone Developer` signing identity;
  reject alternate or account-specific signing identity values.
- Keep Swift sources, targets, deployment settings, plists, storyboards,
  assets, and hosted workflow behavior unchanged.
- Add mutation-sensitive static contracts, documentation, and completed local
  and hosted verification evidence.

## Scope boundaries

- Do not modernize the Swift 1-era scaffold, add a Parse SDK, add credentials,
  change signing behavior, or claim a current Xcode build succeeds.

## Verification

## Work completed

- Added project-file parsing that rejects `DEVELOPMENT_TEAM`,
  `PROVISIONING_PROFILE`, `PROVISIONING_PROFILE_SPECIFIER`, and
  `CODE_SIGN_ENTITLEMENTS` build settings.
- Required exactly the two historical generic `iPhone Developer` signing
  identities and rejected alternate certificate values.
- Updated contributor, security, vision, README, and change documentation for
  the credential-free signing boundary.

## Verification completed

- `make lint`, `make test`, `make build`, `make verify`, and `make check`
  passed the no-Xcode structural baseline.
- Python checker compilation, plist/JSON/XML/project parsing, `git diff --check`,
  generated-artifact scans, and secret scans passed.
- The checker rejected six hostile mutations covering a development team,
  provisioning profile UUID, provisioning profile specifier, entitlements
  path, account-specific signing identity, and removed generic identity.
