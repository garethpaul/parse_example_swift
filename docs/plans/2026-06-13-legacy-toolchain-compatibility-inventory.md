# Legacy Toolchain Compatibility Inventory

status: completed

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

- Added an exact checked-in inventory covering project format, Xcode upgrade
  marker, deployment target, legacy Swift syntax, absent Swift-version setting,
  and absent package-manager or Parse SDK metadata.
- Documented what structural validation proves, what it cannot prove, and the
  evidence required before selecting a modern Xcode, Swift, deployment target,
  dependency manager, or Parse SDK path.
- Added current contributor/security guidance and mutation-sensitive project,
  source, dependency-absence, documentation, and completed-plan contracts.

## Verification Completed

- `make lint`, `make test`, `make build`, `make verify`, and `make check`
- Ran the baseline checker from an external working directory.
- Parsed the workflow YAML, Python checker, plist files, storyboard XML,
  README SVG, asset-catalog JSON, and inventoried project metadata.
- Confirmed focused hostile mutations to project facts, dependency absence,
  current documentation, and completed-plan evidence are rejected.
- `git diff --check`
- The intended-path secret and generated-artifact scan passed; Swift source,
  Xcode project, plists, storyboard, assets, signing metadata, dependency
  metadata, and deployment target had no diff.
