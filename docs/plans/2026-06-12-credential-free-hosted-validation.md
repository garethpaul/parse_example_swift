# Credential-free hosted validation

status: completed

## Context

The hosted macOS workflow used pinned, read-only actions but allowed checkout
to persist its repository credential. The baseline also checked workflow
fragments independently, which could accept additional actions or shadowed YAML
settings alongside the required text.

## Decision

1. Configure checkout with `persist-credentials: false`.
2. Enforce the exact workflow contract, including events, permissions,
   concurrency, runner, timeout, action commits, Python version, and command.
3. Require the contributor guidance that protects Parse credentials, legacy
   Xcode settings, and meaningful XCTest coverage.
4. Reject duplicate or unexpected native target names before validating exact
   source membership.

## Verification

- `make check`
- focused hostile mutations for credential persistence, duplicate overrides,
  floating or extra actions, workflow event drift, and Xcode target membership
- `git diff --check`

All hostile mutations must fail the exact workflow contract or structural Xcode
checks before this plan remains `status: completed`.
