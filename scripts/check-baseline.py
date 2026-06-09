#!/usr/bin/env python3
"""Static baseline checks for the Parse Swift example scaffold."""

from pathlib import Path
import plistlib
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PLAN = "docs/plans/2026-06-08-parse-swift-baseline.md"
REQUIRED = [
    ".gitignore",
    "CHANGES.md",
    "Makefile",
    "README.md",
    "SECURITY.md",
    "VISION.md",
    "Swift.h",
    "docs/readme-overview.svg",
    PLAN,
    "docs/plans/2026-06-09-non-placeholder-xctest.md",
    "docs/plans/2026-06-09-non-empty-bundle-identifier.md",
    "docs/plans/2026-06-09-plist-package-types.md",
    "parse_example.xcodeproj/project.pbxproj",
    "parse_example/AppDelegate.swift",
    "parse_example/ViewController.swift",
    "parse_example/Base.lproj/Main.storyboard",
    "parse_example/Info.plist",
    "parse_exampleTests/Info.plist",
    "parse_exampleTests/parse_exampleTests.swift",
    "scripts/check-baseline.py",
]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8", errors="replace")


def main():
    failures = []
    for path in REQUIRED:
        if not (ROOT / path).is_file():
            failures.append(f"required file missing: {path}")

    makefile = read("Makefile")
    if "python3 scripts/check-baseline.py" not in makefile:
        failures.append("Makefile must expose the static checker")

    gitignore = read(".gitignore")
    for phrase in ["DerivedData", "*.xcuserstate", ".env", "*.log", "tmp/"]:
        if phrase not in gitignore:
            failures.append(f".gitignore must include {phrase}")

    plists = {}
    for path in ["parse_example/Info.plist", "parse_exampleTests/Info.plist"]:
        try:
            with (ROOT / path).open("rb") as handle:
                plists[path] = plistlib.load(handle)
        except Exception as error:
            failures.append(f"{path} must parse as a plist: {error}")

    if plists.get("parse_example/Info.plist", {}).get("CFBundlePackageType") != "APPL":
        failures.append("app Info.plist must keep CFBundlePackageType as APPL")
    if plists.get("parse_exampleTests/Info.plist", {}).get("CFBundlePackageType") != "BNDL":
        failures.append("test Info.plist must keep CFBundlePackageType as BNDL")

    for path in ["parse_example/Base.lproj/Main.storyboard", "docs/readme-overview.svg"]:
        try:
            ET.parse(ROOT / path)
        except ET.ParseError as error:
            failures.append(f"{path} must parse as XML: {error}")

    pbxproj = read("parse_example.xcodeproj/project.pbxproj")
    for phrase in ["parse_example", "parse_exampleTests", "AppDelegate.swift", "ViewController.swift"]:
        if phrase not in pbxproj:
            failures.append(f"project.pbxproj must reference {phrase}")

    app_delegate = read("parse_example/AppDelegate.swift")
    view_controller = read("parse_example/ViewController.swift")
    tests = read("parse_exampleTests/parse_exampleTests.swift")
    if "UIApplicationDelegate" not in app_delegate:
        failures.append("AppDelegate.swift must define the app delegate")
    if "UIViewController" not in view_controller:
        failures.append("ViewController.swift must define the view controller")
    if "XCTestCase" not in tests:
        failures.append("parse_exampleTests.swift must keep an XCTestCase")
    if "testExample" in tests or "testPerformanceExample" in tests:
        failures.append("placeholder XCTest methods must be replaced")
    if "testAppBundleIdentifierIsConfigured" not in tests or "XCTAssertNotNil" not in tests:
        failures.append("XCTest target must verify the scaffold bundle identifier")
    if "XCTAssertFalse(identifier.isEmpty" not in tests:
        failures.append("XCTest target must reject an empty bundle identifier")

    source_text = "\n".join(read(path) for path in [
        "parse_example/AppDelegate.swift",
        "parse_example/ViewController.swift",
        "parse_exampleTests/parse_exampleTests.swift",
        "README.md",
        "SECURITY.md",
        "VISION.md",
    ])
    for forbidden in [
        "Parse.setApplicationId",
        "applicationId:",
        "clientKey:",
        "PFUser.logIn",
        "BEGIN PRIVATE KEY",
    ]:
        if forbidden in source_text:
            failures.append(f"repository must not include live Parse credential or login snippet: {forbidden}")

    docs = "\n".join(read(path) for path in ["README.md", "SECURITY.md", "VISION.md"])
    for phrase in [
        "make check",
        "legacy Swift",
        "no Parse SDK",
        "Parse credentials",
        "Xcode",
        "non-placeholder XCTest",
        "non-empty bundle identifier",
        "plist package types",
    ]:
        if phrase.lower() not in docs.lower():
            failures.append(f"docs must mention {phrase}")

    plan = read(PLAN)
    if "status: completed" not in plan or "make check" not in plan:
        failures.append("plan must record completed status and verification")
    test_plan = read("docs/plans/2026-06-09-non-placeholder-xctest.md")
    if "status: completed" not in test_plan or "testAppBundleIdentifierIsConfigured" not in test_plan:
        failures.append("XCTest plan must record completed status and verification")
    bundle_plan = read("docs/plans/2026-06-09-non-empty-bundle-identifier.md")
    if "status: completed" not in bundle_plan or "XCTAssertFalse" not in bundle_plan:
        failures.append("bundle identifier plan must record completed status and verification")
    package_plan = read("docs/plans/2026-06-09-plist-package-types.md")
    if "status: completed" not in package_plan or "CFBundlePackageType" not in package_plan:
        failures.append("plist package type plan must record completed status and verification")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("parse_example_swift baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
