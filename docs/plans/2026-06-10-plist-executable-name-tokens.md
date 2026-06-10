# Plist Executable Name Tokens

status: completed

## Context

The app and XCTest `Info.plist` files already keep bundle identifiers and
package types under static review. They also rely on Xcode substitution tokens
for `CFBundleExecutable` and `CFBundleName`; hard-coding either value would
make target metadata drift harder to review without Xcode.

## Objectives

- Require app and XCTest plists to keep `CFBundleExecutable` set to
  `${EXECUTABLE_NAME}`.
- Require app and XCTest plists to keep `CFBundleName` set to
  `${PRODUCT_NAME}`.
- Extend docs and the static baseline for plist executable and product-name
  tokens.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
