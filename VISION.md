## Parse Example Swift Vision

Parse Example Swift is a minimal early Swift iOS project scaffold intended to
demonstrate where a Parse-backed app integration would start.

The repository is useful as a historical Xcode and Swift sample: it shows a
small app delegate, view controller, storyboard, tests, and project structure
from the original era.

The goal is to preserve the scaffold while making clear that meaningful Parse
behavior still needs to be documented and implemented before the project is a
working integration sample.

The current focus is:

Priority:

- Preserve the Xcode project and Swift source layout
- Keep the empty app behavior easy to inspect
- Document SDK and Swift version assumptions before adding Parse calls
- Avoid committing app credentials or service keys

Next priorities:

- Add a README that explains the intended Parse scenario
- Identify the required Parse SDK version and installation path
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

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
