#!/usr/bin/env python3
"""Static baseline checks for the Parse Swift example scaffold."""

from pathlib import Path
import json
import plistlib
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PLAN = "docs/plans/2026-06-08-parse-swift-baseline.md"
STORYBOARD_PLAN = "docs/plans/2026-06-09-storyboard-initial-view-controller.md"
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
    STORYBOARD_PLAN,
    "docs/plans/2026-06-09-target-default-configuration.md",
    "docs/plans/2026-06-09-main-storyboard-plist.md",
    "docs/plans/2026-06-09-make-gate-aliases.md",
    "docs/plans/2026-06-09-asset-catalog-metadata.md",
    "parse_example.xcodeproj/project.pbxproj",
    "parse_example/AppDelegate.swift",
    "parse_example/ViewController.swift",
    "parse_example/Base.lproj/Main.storyboard",
    "parse_example/Images.xcassets/AppIcon.appiconset/Contents.json",
    "parse_example/Images.xcassets/LaunchImage.launchimage/Contents.json",
    "parse_example/Info.plist",
    "parse_exampleTests/Info.plist",
    "parse_exampleTests/parse_exampleTests.swift",
    "scripts/check-baseline.py",
]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8", errors="replace")


def has_image(images, **expected):
    return any(
        all(image.get(key) == value for key, value in expected.items())
        for image in images
    )


def main():
    failures = []
    for path in REQUIRED:
        if not (ROOT / path).is_file():
            failures.append(f"required file missing: {path}")

    makefile = read("Makefile")
    for phrase in [
        "python3 scripts/check-baseline.py",
        "lint: static-check",
        "test: static-check",
        "build: static-check",
        "verify: check",
    ]:
        if phrase not in makefile:
            failures.append(f"Makefile must include {phrase}")

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

    expected_package_types = {
        "parse_example/Info.plist": "APPL",
        "parse_exampleTests/Info.plist": "BNDL",
    }
    for path, package_type in expected_package_types.items():
        plist = plists.get(path)
        if not plist:
            continue
        bundle_identifier = str(plist.get("CFBundleIdentifier", "")).strip()
        if not bundle_identifier:
            failures.append(f"{path} must define a non-empty CFBundleIdentifier")
        if "${PRODUCT_NAME:rfc1034identifier}" not in bundle_identifier:
            failures.append(f"{path} must keep the product-name bundle identifier token")
        if plist.get("CFBundlePackageType") != package_type:
            failures.append(f"{path} must keep CFBundlePackageType={package_type}")
    app_plist = plists.get("parse_example/Info.plist")
    if app_plist and app_plist.get("UIMainStoryboardFile") != "Main":
        failures.append("parse_example/Info.plist must launch the Main storyboard")

    asset_catalogs = {}
    for path in [
        "parse_example/Images.xcassets/AppIcon.appiconset/Contents.json",
        "parse_example/Images.xcassets/LaunchImage.launchimage/Contents.json",
    ]:
        try:
            asset_catalogs[path] = json.loads(read(path))
        except json.JSONDecodeError as error:
            failures.append(f"{path} must parse as JSON: {error}")
    for path, catalog in asset_catalogs.items():
        info = catalog.get("info", {})
        if info.get("version") != 1 or info.get("author") != "xcode":
            failures.append(f"{path} must keep Xcode asset catalog info metadata")
    app_icon_images = asset_catalogs.get(
        "parse_example/Images.xcassets/AppIcon.appiconset/Contents.json", {}
    ).get("images", [])
    if not has_image(app_icon_images, idiom="iphone", size="60x60", scale="2x"):
        failures.append("AppIcon asset catalog must keep the iPhone 60x60@2x icon slot")
    if not has_image(app_icon_images, idiom="ipad", size="76x76", scale="2x"):
        failures.append("AppIcon asset catalog must keep the iPad 76x76@2x icon slot")
    launch_images = asset_catalogs.get(
        "parse_example/Images.xcassets/LaunchImage.launchimage/Contents.json", {}
    ).get("images", [])
    if not has_image(launch_images, idiom="iphone", subtype="retina4", scale="2x"):
        failures.append("LaunchImage asset catalog must keep the iPhone retina4 launch slot")
    if not has_image(launch_images, idiom="ipad", orientation="landscape", scale="2x"):
        failures.append("LaunchImage asset catalog must keep the iPad landscape@2x launch slot")

    storyboard_tree = None
    for path in ["parse_example/Base.lproj/Main.storyboard", "docs/readme-overview.svg"]:
        try:
            tree = ET.parse(ROOT / path)
            if path == "parse_example/Base.lproj/Main.storyboard":
                storyboard_tree = tree
        except ET.ParseError as error:
            failures.append(f"{path} must parse as XML: {error}")

    if storyboard_tree is not None:
        storyboard_root = storyboard_tree.getroot()
        initial_view_controller = storyboard_root.get("initialViewController")
        if not initial_view_controller:
            failures.append("Main.storyboard must declare an initial view controller")
        else:
            initial_controller = storyboard_root.find(
                f".//viewController[@id='{initial_view_controller}']"
            )
            if initial_controller is None:
                failures.append("Main.storyboard initial view controller must resolve to a scene")
            else:
                if initial_controller.get("customClass") != "ViewController":
                    failures.append("Main.storyboard initial scene must use ViewController")
                if initial_controller.get("customModuleProvider") != "target":
                    failures.append("Main.storyboard ViewController must use the target module provider")

    pbxproj = read("parse_example.xcodeproj/project.pbxproj")
    for phrase in [
        "parse_example",
        "parse_exampleTests",
        "AppDelegate.swift",
        "ViewController.swift",
        "ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;",
        "ASSETCATALOG_COMPILER_LAUNCHIMAGE_NAME = LaunchImage;",
    ]:
        if phrase not in pbxproj:
            failures.append(f"project.pbxproj must reference {phrase}")
    if pbxproj.count("defaultConfigurationName = Release;") < 3:
        failures.append("project.pbxproj must keep Release as the default configuration for project and native targets")

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
    if "testAppUsesMainStoryboard" not in tests or "UIMainStoryboardFile" not in tests:
        failures.append("XCTest target must verify the main storyboard plist entry")
    if 'XCTAssertEqual(storyboardName, "Main"' not in tests:
        failures.append("XCTest target must require the Main storyboard")

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
        "plist bundle identifiers",
        "plist package types",
        "storyboard initial view controller",
        "main storyboard plist entry",
        "target default configurations",
        "asset catalog metadata",
        "make lint",
        "make test",
        "make build",
        "make verify",
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
    storyboard_plan = read(STORYBOARD_PLAN)
    if "status: completed" not in storyboard_plan or "initial view controller" not in storyboard_plan:
        failures.append("storyboard plan must record completed status and verification")
    default_config_plan = read("docs/plans/2026-06-09-target-default-configuration.md")
    if "status: completed" not in default_config_plan or "defaultConfigurationName" not in default_config_plan:
        failures.append("target default configuration plan must record completed status and verification")
    main_storyboard_plan = read("docs/plans/2026-06-09-main-storyboard-plist.md")
    if "status: completed" not in main_storyboard_plan or "UIMainStoryboardFile" not in main_storyboard_plan:
        failures.append("main storyboard plist plan must record completed status and verification")
    aliases_plan = read("docs/plans/2026-06-09-make-gate-aliases.md")
    for phrase in ["status: completed", "make lint", "make test", "make build", "make verify"]:
        if phrase not in aliases_plan:
            failures.append(f"make gate alias plan must record {phrase}")
    asset_catalog_plan = read("docs/plans/2026-06-09-asset-catalog-metadata.md")
    if "status: completed" not in asset_catalog_plan or "asset catalog metadata" not in asset_catalog_plan:
        failures.append("asset catalog metadata plan must record completed status and verification")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("parse_example_swift baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
