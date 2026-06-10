#!/usr/bin/env python3
"""Static baseline checks for the Parse Swift example scaffold."""

from pathlib import Path
import json
import plistlib
import re
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PLAN = "docs/plans/2026-06-08-parse-swift-baseline.md"
STORYBOARD_PLAN = "docs/plans/2026-06-09-storyboard-initial-view-controller.md"
HOSTED_VALIDATION_PLAN = "docs/plans/2026-06-10-hosted-structural-validation.md"
SOURCE_MEMBERSHIP_PLAN = "docs/plans/2026-06-10-source-target-membership.md"
REQUIRED = [
    ".github/workflows/check.yml",
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
    "docs/plans/2026-06-10-plist-executable-name-tokens.md",
    HOSTED_VALIDATION_PLAN,
    SOURCE_MEMBERSHIP_PLAN,
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


def pbx_section(project, name):
    match = re.search(
        rf"/\* Begin {re.escape(name)} section \*/(.*?)/\* End {re.escape(name)} section \*/",
        project,
        re.DOTALL,
    )
    return match.group(1) if match else ""


def pbx_objects(project, section_name):
    section = pbx_section(project, section_name)
    return {
        object_id: body
        for object_id, body in re.findall(
            r"^\t\t([A-F0-9]{24})(?: /\*.*?\*/)? = \{(.*?)\};\s*$",
            section,
            re.DOTALL | re.MULTILINE,
        )
    }


def pbx_list_ids(body, field):
    match = re.search(rf"\b{re.escape(field)} = \((.*?)\);", body, re.DOTALL)
    return re.findall(r"\b[A-F0-9]{24}\b", match.group(1)) if match else []


def pbx_field(body, field):
    match = re.search(rf"\b{re.escape(field)} = (?:\"([^\"]+)\"|([^;]+));", body)
    return (match.group(1) or match.group(2)).strip() if match else None


def pbx_id_field(body, field):
    match = re.search(rf"\b{re.escape(field)} = ([A-F0-9]{{24}})\b", body)
    return match.group(1) if match else None


def target_source_paths(project):
    build_files = pbx_objects(project, "PBXBuildFile")
    file_references = pbx_objects(project, "PBXFileReference")
    source_phases = pbx_objects(project, "PBXSourcesBuildPhase")
    native_targets = pbx_objects(project, "PBXNativeTarget")

    file_paths = {
        object_id: pbx_field(body, "path")
        for object_id, body in file_references.items()
    }
    build_file_paths = {
        object_id: file_paths.get(pbx_id_field(body, "fileRef"))
        for object_id, body in build_files.items()
    }
    phase_paths = {
        object_id: {
            build_file_paths.get(build_file_id) or f"<unresolved:{build_file_id}>"
            for build_file_id in pbx_list_ids(body, "files")
        }
        for object_id, body in source_phases.items()
    }

    targets = {}
    for body in native_targets.values():
        target_name = pbx_field(body, "name")
        source_phase_ids = [
            phase_id
            for phase_id in pbx_list_ids(body, "buildPhases")
            if phase_id in source_phases
        ]
        target_paths = set()
        for phase_id in source_phase_ids:
            target_paths.update(phase_paths[phase_id])
        targets[target_name] = target_paths
    return targets


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

    workflow = read(".github/workflows/check.yml")
    for expected in [
        "permissions:\n  contents: read",
        "cancel-in-progress: true",
        "runs-on: macos-15",
        "timeout-minutes: 10",
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
        "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
        'python-version: "3.12"',
        "run: make check",
    ]:
        if expected not in workflow:
            failures.append(f"Check workflow must keep {expected}")

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
        if plist.get("CFBundleExecutable") != "${EXECUTABLE_NAME}":
            failures.append(f"{path} must keep CFBundleExecutable=${{EXECUTABLE_NAME}}")
        if plist.get("CFBundleName") != "${PRODUCT_NAME}":
            failures.append(f"{path} must keep CFBundleName=${{PRODUCT_NAME}}")
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
    expected_target_sources = {
        "parse_example": {"AppDelegate.swift", "ViewController.swift"},
        "parse_exampleTests": {"parse_exampleTests.swift"},
    }
    actual_target_sources = target_source_paths(pbxproj)
    for target_name, expected_sources in expected_target_sources.items():
        actual_sources = actual_target_sources.get(target_name)
        if actual_sources != expected_sources:
            failures.append(
                f"{target_name} Sources phase must contain exactly "
                f"{sorted(expected_sources)}; found {sorted(actual_sources or set())}"
            )

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
        "plist executable and product-name tokens",
        "storyboard initial view controller",
        "main storyboard plist entry",
        "target default configurations",
        "asset catalog metadata",
        "make lint",
        "make test",
        "make build",
        "make verify",
        "hosted macOS",
        "structural validation",
        "source target membership",
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
    plist_token_plan = read("docs/plans/2026-06-10-plist-executable-name-tokens.md")
    if (
        "status: completed" not in plist_token_plan
        or "CFBundleExecutable" not in plist_token_plan
        or "CFBundleName" not in plist_token_plan
    ):
        failures.append("plist executable/name token plan must record completed status and verification")
    hosted_validation_plan = read(HOSTED_VALIDATION_PLAN)
    if "status: completed" not in hosted_validation_plan or "make check" not in hosted_validation_plan:
        failures.append("hosted structural validation plan must record completed status and verification")
    source_membership_plan = read(SOURCE_MEMBERSHIP_PLAN)
    if "status: completed" not in source_membership_plan or "PBXSourcesBuildPhase" not in source_membership_plan:
        failures.append("source target membership plan must record completed status and verification")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("parse_example_swift baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
