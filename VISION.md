## Parse Example Swift Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

Parse Example Swift is a minimal early Swift iOS project scaffold intended to
demonstrate where a Parse-backed app integration would start.

The repository is useful as a historical Xcode and Swift sample: it shows a
small app delegate, view controller, storyboard, tests, and project structure
from the original era.

The goal is to preserve the scaffold while making clear that meaningful Parse
behavior still needs to be documented and implemented before the project is a
working integration sample.

Current baseline: `make check` performs static validation of the legacy Swift
project structure, plist/storyboard XML, and documentation guardrails. The
repository currently has no Parse SDK, Parse credentials, or implemented
backend data flow. `make lint`, `make test`, `make build`, and `make verify`
are stable aliases for the no-Xcode static baseline.

The current focus is:

Priority:

- Preserve the Xcode project and Swift source layout
- Keep the empty app behavior easy to inspect
- Document SDK and Swift version assumptions before adding Parse calls
- Avoid committing app credentials or service keys
- Keep static checks green while Xcode is unavailable in automation
- Keep non-placeholder XCTest coverage for the scaffold
- Keep the bundle identifier XCTest checking for non-empty values
- Keep plist bundle identifiers and plist package types explicit for the app
  and XCTest target
- Keep plist executable and product-name tokens explicit for the app and XCTest
  target
- Keep the no-Xcode structural validation gate running on pinned hosted macOS
- Keep hosted checkout credential-free and reject workflow drift structurally
- Keep credential-free signing metadata free of Apple account, provisioning,
  entitlements, and certificate-specific values
- Keep the storyboard initial view controller bound to the checked-in
  `ViewController` class
- Keep the main storyboard plist entry aligned with the checked-in `Main`
  storyboard
- Keep target default configurations explicit in Xcode project metadata
- Keep source target membership aligned with app and XCTest build phases
- Keep asset catalog metadata aligned with app icon and launch image settings
- Keep `make lint`, `make test`, `make build`, `make verify`, and `make check`
  available as no-Xcode local verification gates
- Keep the intended Parse scenario limited to authenticated owner-scoped
  private notes behind a deterministic fake-first application boundary
- Keep the Xcode 6-era iOS 8 compatibility inventory explicit until a selected
  Swift, Xcode, deployment-target, and Parse SDK configuration builds and tests

Next priorities:

- Select and prove an exact Parse SDK version and installation path in a
  dedicated compatibility decision
- Add tests around any future Parse-backed behavior before service calls
- Add a small model or login example only with testable behavior
- Update the Swift syntax in a dedicated modernization pass

Contribution rules:

- One PR = one focused project, SDK, example, or documentation change.
- Do not commit service credentials.
- Keep sample flows small and reproducible.
- Include simulator or Xcode version notes for app changes.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Backend app samples often require credentials and user data. Any future Parse
integration should keep secrets out of source control and use clearly fake data
for examples and tests.

## What We Will Not Merge (For Now)

- Checked-in Parse keys or production endpoints
- Broad UI work before the sample scenario is defined
- SDK migrations without setup notes
- Untested service calls
- Public, cross-user, or admin-capable behavior in the initial note scenario

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
