# Source Target Membership

status: completed

## Context

The static baseline required Swift filenames to appear somewhere in the Xcode
project file, but it did not prove that each source remained in the correct
native target. Removing a build-file relationship or moving app code into the
test target would still pass the previous string checks.

## Objectives

- Resolve each native target through its `PBXSourcesBuildPhase` entries.
- Resolve source build files through their file references.
- Require the app target to contain exactly `AppDelegate.swift` and
  `ViewController.swift`.
- Require the XCTest target to contain exactly `parse_exampleTests.swift`.
- Keep the check independent of Xcode and compatible with hosted structural
  validation.

## Verification

- `make lint`
- `make test`
- `make build`
- `make verify`
- `make check`
- Mutation: remove `ViewController.swift` from the app Sources phase and
  confirm `make check` fails.
- Mutation: assign `parse_exampleTests.swift` to the app Sources phase and
  confirm `make check` fails.
- `git diff --check`
