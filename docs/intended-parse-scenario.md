# Intended Parse Scenario

Review date: 2026-06-13

## Current Baseline

The current repository has no Parse SDK, runtime configuration, authentication,
network request, or service-backed behavior. Opening the Xcode project shows a
legacy scaffold only. This document defines a future scenario; it does not make
the sample operational or claim compatibility with current Xcode or Parse SDK
releases.

## User Goal

The initial sample should demonstrate one signed-in user managing a private
note:

1. The user authenticates against an operator-controlled development backend.
2. The app lists only notes owned by the current user.
3. The user creates a note with a non-empty title.
4. The new note appears in the same owner-scoped list after the save succeeds.

Authentication screens may support development-only sign-up when the selected
backend policy permits it. The initial scenario does not include password
recovery, social login, account administration, or privileged user management.

## Data And Authorization Contract

Use one conceptual `Note` record with the minimum fields needed for the flow:

- `title`: trimmed, non-empty user text with a documented length limit
- `owner`: an immutable relation to the authenticated user
- platform-managed creation timestamp for deterministic ordering

Every created note must use owner-only access. Every list query must query only
records owned by the current user and order them deterministically. A missing
user session must fail before any note query or write. The initial scenario has
no public or cross-user query, shared note, role ACL, admin path, or migration of
production records.

Examples and tests must use clearly fake users and payloads. Do not put account
identifiers, session tokens, application credentials, backend endpoints, or
captured user records in source, fixtures, logs, screenshots, or documentation.

## Observable States

The future UI and application boundary must distinguish:

- signed out and authentication required
- authentication in progress and authentication failure
- note list loading
- empty note list
- loaded owner-scoped notes
- invalid or empty note title
- save in progress and save success
- save failure or list failure with a retry path

Failure text must be useful without repeating credentials, session tokens,
backend responses, or private note contents.

## Testability Boundary

Define a small application boundary for authentication, owner-scoped listing,
and note creation before importing a Parse SDK into view-controller code. Unit
tests must use a deterministic fake to cover state transitions, title
validation, owner scoping, ordering, retry behavior, and sanitized failures
without a network or credential.

The real adapter may be added only after the fake-backed contract is reviewed.
Runtime-supplied configuration must stay outside version control and fail
closed when absent. No master or admin key belongs in a client application.

## Compatibility Decision Required

The SDK version and installation path, supported Xcode and macOS versions,
deployment target, Swift migration approach, and backend compatibility require
a separate compatibility decision. That work must identify primary-source
support evidence, lock dependency resolution where the selected package manager
allows it, and preserve this scenario's tests and credential boundaries.

## Initial Non-Goals

- no SDK dependency or service call in this documentation change
- no public or cross-user query
- no master/admin capability or production backend
- no file uploads, geolocation, analytics, push notifications, or background
  synchronization
- no broad UI redesign, Swift modernization, signing change, or Xcode project
  rewrite

No Swift or Xcode project changes are part of this scenario-definition unit.
