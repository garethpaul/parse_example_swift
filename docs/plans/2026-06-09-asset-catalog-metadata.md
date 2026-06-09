# Asset Catalog Metadata

status: completed

## Context

The Xcode project references the `AppIcon` and `LaunchImage` asset catalogs, but
the static baseline only checked plist, storyboard, and project metadata. The
checked-in asset catalog `Contents.json` files should remain parseable and keep
the core launch/icon slots expected by the project settings.

## Objectives

- Add `AppIcon` and `LaunchImage` asset catalog metadata to required files.
- Parse the asset catalog JSON in the static baseline.
- Check the Xcode metadata block and representative iPhone/iPad icon and
  launch image slots.
- Keep project compiler settings aligned with the named asset catalogs.
- Document the asset catalog metadata guard.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
