# Storyboard Initial View Controller Plan

status: completed

## Context

The static checker parsed `Main.storyboard` as XML, but it did not verify that
the initial scene still points at the checked-in `ViewController` class. A
storyboard edit could accidentally disconnect the launch scene while the
project, plist, and XML checks still passed.

## Objectives

- Require `Main.storyboard` to declare an initial view controller.
- Verify that the initial controller resolves to the `ViewController` Swift
  class.
- Keep the storyboard binding documented as part of the legacy scaffold
  contract.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
