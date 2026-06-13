# Credential-free signing metadata

status: planned

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

- Run all Make gates, Python checker compilation, project parsing, hostile
  signing-metadata mutations, diff checks, generated-artifact scans, and secret
  scans.
