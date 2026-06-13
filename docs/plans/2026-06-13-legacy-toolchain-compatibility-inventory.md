# Legacy Toolchain Compatibility Inventory

status: pending

## Context

The intended Parse scenario requires a separate compatibility decision, while
the checked-in project remains an Xcode 6-era iOS 8 scaffold with no dependency
metadata. Contributors need an exact inventory of what the repository proves
before selecting a migration or Parse SDK path.

## Requirements

- Record the project object version, Xcode upgrade marker, deployment target,
  legacy Swift syntax indicators, and absent Swift-version setting.
- Record the absence of Swift Package Manager, CocoaPods, Carthage, and checked-
  in Parse SDK dependency metadata.
- Distinguish static structural validation from a current-Xcode build claim.
- Define the evidence required before choosing a migration and SDK path.
- Add mutation-sensitive static and completed-plan contracts.

## Scope Boundaries

- Do not modify Swift source, the Xcode project, plists, storyboard, assets,
  signing metadata, dependencies, or deployment target.
- Do not claim current Xcode, simulator, Parse backend, or SDK compatibility.

## Work Completed

Pending implementation.

## Verification Completed

Pending implementation and validation.
