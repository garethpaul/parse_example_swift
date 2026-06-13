# Intended Parse Scenario Contract

status: completed

## Context

The repository describes itself as a Parse example but currently contains only
a legacy Swift/Xcode scaffold. Before selecting an SDK version or adding a
service call, the project needs one small, testable scenario that defines what
the sample will demonstrate, what data it may handle, and which security and
compatibility decisions remain deliberately unresolved.

## Priorities

1. Define one credential-free Parse-backed user flow with a minimal owned data
   model and clear success, empty, loading, and failure outcomes.
2. Require a deterministic client boundary and fake-backed tests before any
   Parse SDK or network implementation is added.
3. Keep credentials, endpoints, production data, admin capabilities, SDK
   selection, and Swift modernization outside this documentation-only change.

## Requirements

- R1. Document the current no-SDK/no-service baseline before describing future
  behavior.
- R2. Define a signed-in user's private note flow: authenticate, create a note,
  and list only notes owned by that user.
- R3. Specify the minimum note fields and owner-only access boundary without
  adding real identifiers or payloads.
- R4. Define loading, empty, success, validation, authentication, and network
  failure outcomes.
- R5. Require future Parse integration behind a deterministic application
  boundary that can be tested with a fake before service calls.
- R6. Prohibit master/admin keys, embedded credentials or endpoints, public or
  cross-user queries, production data, analytics, file uploads, push
  notifications, and background synchronization in the initial scenario.
- R7. State that SDK version, installation path, supported Xcode/macOS version,
  and Swift modernization require a separate compatibility decision.
- R8. Enforce the scenario and completed verification evidence through the
  existing static checker without changing Swift sources or Xcode metadata.

## Implementation Units

### U1: Scenario Document

File: `docs/intended-parse-scenario.md`

Document the current baseline, future user flow, data and authorization
contract, observable states, test seam, configuration boundary, and non-goals.

### U2: Repository Guidance

Files: `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`

Link the scenario from operator and contributor guidance, record the security
boundary, and move the scenario backlog item into the maintained priority
contract.

### U3: Static Contract And Evidence

Files: `scripts/check-baseline.py`,
`docs/plans/2026-06-13-intended-parse-scenario.md`

Require the scenario's safety and testability boundaries, unchanged
implementation surfaces, completed plan status, and truthful verification
evidence.

## Verification Plan

- `make lint`
- `make test`
- `make build`
- `make verify`
- `make check`
- run the checker from an external working directory
- parse workflow YAML, plist/storyboard XML, asset-catalog JSON, and README SVG
- run focused hostile mutations against scenario, authorization, testability,
  compatibility, non-goal, and completed-evidence boundaries
- verify Swift sources, tests, Xcode metadata, plists, storyboard, assets, and
  workflow have no diff
- `git diff --check`
- scan intended paths for secrets, captured identifiers, and generated artifacts

## Scope Boundaries

- Do not add or select a Parse SDK, package manager, backend endpoint,
  application ID, client key, master key, test account, or captured payload.
- Do not change Swift sources, tests, Xcode metadata, plists, storyboard,
  assets, signing settings, workflow behavior, or deployment targets.
- Do not claim current Xcode compatibility, simulator behavior, authentication,
  network behavior, or service-backed functionality has been tested.

## Work Completed

Defined one credential-free future Parse scenario covering authenticated
private notes, owner-scoped reads and writes, observable states, sanitized
failures, a deterministic fake-first application boundary, and a separate SDK
compatibility decision without changing project behavior.

## Verification Completed

- `make lint`, `make test`, `make build`, `make verify`, and `make check`
  passed.
- The checker passed from an external working directory.
- The workflow YAML, plist/storyboard XML, asset-catalog JSON, and README SVG
  parsed successfully.
- Thirteen focused hostile mutations rejected weakened scenario, authorization,
  state, testability, compatibility, non-goal, and completed-evidence
  requirements.
- `implementation and project paths had no diff`, including Swift sources,
  tests, Xcode metadata, plists, storyboard, assets, and workflow.
- `git diff --check` passed.
- The `secret, captured-identifier, and generated-artifact scan` passed.
