# Parse Swift Deep-Review Hardening

status: completed

## Classification

The repository is a structural/archive baseline. It contains a Swift 1-era iOS
8 scaffold, but no Parse SDK, dependency manifest, credential configuration,
endpoint, service call, or implemented private-note flow.

## Root Cause

The stacked structural checker validated only known required files. A change
could add an unreviewed Parse configuration, insecure endpoint, provisioning
artifact, additional Swift implementation, or symlink without affecting any
existing check. The same checker had no executable mutation suite, so its
documented hostile checks were not rerunnable.

## Work Completed

- Enforced an exact repository file inventory with a 1 MiB per-file limit.
- Rejected symlinks before reading or parsing repository files.
- Rejected ATS exceptions, Parse credential/endpoint plist keys, runtime URLs,
  and unreviewed network or Parse runtime markers.
- Added thirteen executable unit and hostile mutation tests.
- Made `make check` run both structural and mutation gates from any directory.
- Updated checkout to the immutable official v7.0.0 release commit while
  retaining read-only permissions and `persist-credentials: false`.
- Corrected security documentation that previously implied runtime networking.
- Recorded the actual Xcode 26.0.1 compatibility probe and its unsupported
  Swift-version failure without changing the historical project.

## Verification Completed

- `make check`, `make verify`, `make lint`, `make test`, and `make build`
- absolute Makefile invocation from `/tmp`
- `python3 -W error -m py_compile scripts/check-baseline.py`
- thirteen executable unit and hostile mutation tests
- `actionlint .github/workflows/check.yml`
- plist, storyboard XML, README SVG, and asset-catalog parsing through the gate
- `xcodebuild -list -project parse_example.xcodeproj`
- unsigned Xcode 26.0.1 simulator build probe, expected to fail because the
  absent legacy Swift version is unsupported
- current-tree and full-history credential scans with values redacted
- `git diff --check`

No Parse service, backend, credential, signing identity, archive, or upload was
used during review.
