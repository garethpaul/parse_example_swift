#!/usr/bin/env python3
"""Verify the frozen legacy sample and its validation trust chain."""

from hashlib import sha256
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).relative_to(ROOT).as_posix()
NATIVE_SOURCE_PATHS = {
    "parse_example/AppDelegate.swift",
    "parse_example/ViewController.swift",
    "parse_exampleTests/parse_exampleTests.swift",
}
PROTECTED_FILE_SHA256 = {
    "Makefile": "7241f294ea6a3c9a7864a5f2b8864a9e776c16f4cff86c4fe8e4eba7a69618d5",
    "Swift.h": "7737e349ab30c8ea78cd760b12bb1e43af61b2cfcd4e51580ac7cbaf998ab068",
    "parse_example.xcodeproj/project.pbxproj": "138a0fa6ef66983c94ab7f1e3478c6b38a644db7eaaea7c0035830f963e6c527",
    "parse_example.xcodeproj/project.xcworkspace/contents.xcworkspacedata": "4dcd57608e0289e1e510ed6da77eb11278f65482b1bba03e8ed2ba6c5d0f9721",
    "parse_example/AppDelegate.swift": "d03c2ba7242a7b9fce2278107dd23e86ab90a1dd87e4d10f54421c5358c7245e",
    "parse_example/ViewController.swift": "4428f581f7db8ac9ef03e9bf690823b303e6a69c37075450e8f9bfb20e40e0b8",
    "parse_example/Base.lproj/Main.storyboard": "65717a4733ca991a4f4c46f8692dce1bd42229657f67777224a5618b529686fc",
    "parse_example/Images.xcassets/AppIcon.appiconset/Contents.json": "af6d955a3bd0a5b11f4b195d224d1fb831cd1257938e5e31291d0f516a1dcb8e",
    "parse_example/Images.xcassets/LaunchImage.launchimage/Contents.json": "482db227c3fffad967a554080da10abbc2902f85ec62a6f819d452a335a71a47",
    "parse_example/Info.plist": "a83724f00327b342bac26641e2a91647a7b897c714d90e8eddf9bd45e82339eb",
    "parse_exampleTests/Info.plist": "ec09c3ddaec1a2711168f725d53813cc59e40a6b9ff59fd855beb832d2e5e5db",
    "parse_exampleTests/parse_exampleTests.swift": "c35adf82b4e1ff833d876354d4f7d1d107fc022456b15283f38d6d2670532741",
    "scripts/check-baseline.py": "2654e20cf587ee1a4c57ce65f888aa907dc3c6302521e72911e1dc6ec8ceae52",
    "scripts/test-makefile-root.py": "b2d4f308805efc356c7988222a766c78756ec90afeef65fb3bb85aa8b11d0b42",
    "tests/test_check_baseline.py": "472601b178e85e9980b63fb5b03724fb4928f15ec895092f159b869b4e656c00",
}
WORKFLOW_TEMPLATE = """name: Check
on:
  pull_request:
  push:
  workflow_dispatch:
permissions:
  contents: read
env:
  INTEGRITY_SHA256: __INTEGRITY_SHA256__
concurrency:
  group: check-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
jobs:
  structural:
    runs-on: macos-15
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0
        with:
          persist-credentials: false
      - uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405
        with:
          python-version: "3.12"
      - name: Verify integrity bootstrap
        run: |
          actual="$(python3 -c 'import hashlib; print(hashlib.sha256(open("scripts/check-integrity.py", "rb").read()).hexdigest())')"
          test "$actual" = "$INTEGRITY_SHA256" || { echo "integrity bootstrap digest mismatch" >&2; exit 1; }
          python3 scripts/check-integrity.py
      - run: make check
"""


def file_sha256(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    failures = []
    workflow_path = ROOT / ".github/workflows/check.yml"
    workflow = workflow_path.read_text(encoding="utf-8")
    digest_matches = re.findall(
        r"(?m)^  INTEGRITY_SHA256: ([0-9a-f]{64})$",
        workflow,
    )
    normalized_workflow = re.sub(
        r"(?m)^(  INTEGRITY_SHA256: )[0-9a-f]{64}$",
        r"\1__INTEGRITY_SHA256__",
        workflow,
    )
    if len(digest_matches) != 1 or normalized_workflow != WORKFLOW_TEMPLATE:
        failures.append("integrity workflow contract mismatch")
    elif digest_matches[0] != file_sha256(ROOT / SELF):
        failures.append("integrity bootstrap digest mismatch in .github/workflows/check.yml")

    actual_native_source_paths = {
        path.relative_to(ROOT).as_posix()
        for directory in (ROOT / "parse_example", ROOT / "parse_exampleTests")
        for path in directory.rglob("*.swift")
    }
    for relative_path in sorted(actual_native_source_paths - NATIVE_SOURCE_PATHS):
        failures.append(f"unexpected native source file: {relative_path}")

    for relative_path, expected_digest in sorted(PROTECTED_FILE_SHA256.items()):
        path = ROOT / relative_path
        if not path.is_file() or path.is_symlink():
            failures.append(f"expected protected file missing: {relative_path}")
            continue
        if path.stat().st_mode & 0o111:
            failures.append(
                f"protected files must not be executable: {relative_path}"
            )
        if file_sha256(path) == expected_digest:
            continue
        if relative_path in NATIVE_SOURCE_PATHS:
            failures.append(f"native source integrity mismatch: {relative_path}")
        else:
            failures.append(f"integrity mismatch: {relative_path}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("parse_example_swift integrity checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
