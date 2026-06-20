# Legacy Toolchain Compatibility Inventory

Review date: 2026-06-13

## Checked-In Evidence

The repository is an Xcode 6-era iOS 8 scaffold, not a current toolchain
sample. The checked-in project records:

- project `objectVersion = 46`
- `LastUpgradeCheck = 0600`, corresponding to the Xcode 6 project era
- `compatibilityVersion = "Xcode 3.2"`
- `IPHONEOS_DEPLOYMENT_TARGET = 8.0` for the app and test configurations
- no explicit `SWIFT_VERSION` build setting

The Swift source uses legacy syntax including `@UIApplicationMain` and the
pre-modern `application(application:didFinishLaunchingWithOptions:)` delegate
signature. Those facts are inventory evidence only; they do not identify a
currently supported compiler capable of building the project unchanged.

## Dependency Inventory

The repository has no `Package.swift`, `Package.resolved`, `Podfile`,
`Podfile.lock`, `Cartfile`, `Cartfile.resolved`, or checked-in Parse SDK
framework. The Xcode project and Swift source contain no Parse import or linked
Parse product. There is therefore no selected Parse SDK version, installation
path, or reproducible dependency graph to audit.

## What Validation Proves

`make check` and hosted macOS validation parse and inspect repository structure,
project metadata, plists, storyboard XML, asset-catalog JSON, target membership,
credential boundaries, and documentation contracts. They do not invoke an
Xcode build, simulator, Swift compiler, Parse SDK, or backend.

Passing structural validation does not prove compatibility with current Xcode,
current Swift, a current iOS deployment target, or any Parse SDK release.

On 2026-06-19, Xcode 26.0.1 could enumerate the app and XCTest targets, but an
unsigned simulator build failed before source compilation because the project
has no supported `SWIFT_VERSION`. Xcode also warned that iOS 8.0 is below its
supported simulator deployment range. This confirms that the repository is an
inventory, not a current-Xcode buildable sample.

## Required Compatibility Decision

Before implementation begins, a dedicated migration unit must record:

1. the supported Xcode and macOS versions used for validation
2. the selected iOS deployment target and Swift language mode
3. the Parse SDK version and primary-source platform support evidence
4. the dependency manager, exact resolution, and lockfile policy
5. the Swift and Xcode project migration sequence
6. simulator build and XCTest commands on the exact selected toolchain
7. preservation of credential-free signing and the fake-first owner-scoped
   scenario contract

The migration must be reviewed separately from adding Parse behavior. No
compatibility claim should be added until the exact selected configuration
builds and tests successfully.
