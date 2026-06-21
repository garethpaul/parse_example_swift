#!/usr/bin/env python3
"""Static baseline checks for the Parse Swift example scaffold."""

from pathlib import Path
import json
import plistlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PLAN = "docs/plans/2026-06-08-parse-swift-baseline.md"
STORYBOARD_PLAN = "docs/plans/2026-06-09-storyboard-initial-view-controller.md"
HOSTED_VALIDATION_PLAN = "docs/plans/2026-06-10-hosted-structural-validation.md"
SOURCE_MEMBERSHIP_PLAN = "docs/plans/2026-06-10-source-target-membership.md"
CREDENTIAL_FREE_PLAN = "docs/plans/2026-06-12-credential-free-hosted-validation.md"
SIGNING_METADATA_PLAN = "docs/plans/2026-06-13-credential-free-signing-metadata.md"
SCENARIO_PLAN = "docs/plans/2026-06-13-intended-parse-scenario.md"
COMPATIBILITY_PLAN = "docs/plans/2026-06-13-legacy-toolchain-compatibility-inventory.md"
LOCATION_INDEPENDENT_MAKE_PLAN = "docs/plans/2026-06-14-location-independent-make-gates.md"
SAFE_MAKE_ROOT_PLAN = "docs/plans/2026-06-21-safe-make-root.md"
REQUIRED = [
    ".github/workflows/check.yml",
    "AGENTS.md",
    ".gitignore",
    "CHANGES.md",
    "Makefile",
    "README.md",
    "SECURITY.md",
    "VISION.md",
    "Swift.h",
    "docs/readme-overview.svg",
    "docs/intended-parse-scenario.md",
    "docs/legacy-toolchain-compatibility.md",
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
    CREDENTIAL_FREE_PLAN,
    SIGNING_METADATA_PLAN,
    SCENARIO_PLAN,
    COMPATIBILITY_PLAN,
    LOCATION_INDEPENDENT_MAKE_PLAN,
    SAFE_MAKE_ROOT_PLAN,
    "docs/plans/2026-06-19-deep-review-hardening.md",
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
    "scripts/check-integrity.py",
    "scripts/test-makefile-root.py",
    "tests/test_check_baseline.py",
]
EXPECTED_REPOSITORY_FILES = set(REQUIRED) | {
    "parse_example.xcodeproj/project.xcworkspace/contents.xcworkspacedata",
}
IGNORED_PATH_PARTS = {".git"}
MAX_REPOSITORY_FILE_BYTES = 1_048_576

EXPECTED_WORKFLOW_TEMPLATE = """name: Check
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


def read(path):
    return (ROOT / path).read_text(encoding="utf-8", errors="replace")


def markdown_section(text, heading):
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


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
    duplicate_target_names = set()
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
        if target_name in targets:
            duplicate_target_names.add(target_name)
        targets[target_name] = target_paths
    return targets, duplicate_target_names


def main():
    failures = []
    repository_files = set()
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if any(part in IGNORED_PATH_PARTS for part in relative.parts):
            continue
        relative_path = relative.as_posix()
        if path.is_symlink():
            failures.append(
                f"repository files must not be symlinks: {relative_path}"
            )
            repository_files.add(relative_path)
            continue
        if not path.is_file():
            continue
        repository_files.add(relative_path)
        if path.stat().st_size > MAX_REPOSITORY_FILE_BYTES:
            failures.append(
                "repository file exceeds "
                f"{MAX_REPOSITORY_FILE_BYTES}-byte limit: {relative_path}"
            )
            continue
        try:
            repository_text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failures.append(f"repository files must be UTF-8 text: {relative_path}")
            continue
        if re.search(
            r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----",
            repository_text,
        ):
            failures.append(
                f"repository must not contain private-key material: {relative_path}"
            )

    for path in sorted(repository_files - EXPECTED_REPOSITORY_FILES):
        failures.append(f"unexpected repository file: {path}")
    for path in sorted(EXPECTED_REPOSITORY_FILES - repository_files):
        failures.append(f"expected repository file missing: {path}")

    git_metadata = ROOT / ".git"
    if git_metadata.exists():
        tracked = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "--stage", "-z"],
            capture_output=True,
            check=False,
        )
        if tracked.returncode != 0:
            failures.append("unable to inspect tracked repository entry types")
        else:
            tracked_paths = set()
            for record in tracked.stdout.split(b"\0"):
                if not record:
                    continue
                metadata, separator, raw_path = record.partition(b"\t")
                fields = metadata.split()
                if not separator or len(fields) != 3:
                    failures.append("malformed tracked repository entry metadata")
                    continue
                mode, _, stage = fields
                try:
                    tracked_path = raw_path.decode("utf-8")
                except UnicodeDecodeError:
                    failures.append("tracked repository paths must be UTF-8")
                    continue
                tracked_paths.add(tracked_path)
                if mode != b"100644" or stage != b"0":
                    failures.append(
                        "tracked repository entries must be regular "
                        f"non-executable files: {mode.decode()} {tracked_path}"
                    )
            for path in sorted(tracked_paths - EXPECTED_REPOSITORY_FILES):
                failures.append(f"unexpected tracked repository entry: {path}")
            for path in sorted(EXPECTED_REPOSITORY_FILES - tracked_paths):
                failures.append(f"expected tracked repository entry missing: {path}")

    for path in REQUIRED:
        if not (ROOT / path).is_file():
            failures.append(f"required file missing: {path}")

    makefile = read("Makefile")
    for phrase in [
        "ifneq ($(origin MAKEFILE_LIST),file)",
        "$(error MAKEFILE_LIST must not be overridden)",
        "override REPO_ROOT := $(shell path=",
        'CDPATH= cd -- "$$directory" && /bin/pwd -P)',
        'python3 "$(REPO_ROOT)/scripts/check-baseline.py"',
        'PYTHONDONTWRITEBYTECODE=1 python3 "$(REPO_ROOT)/scripts/test-makefile-root.py"',
        "check: static-check mutation-test root-test",
        "lint: static-check",
        "test: mutation-test",
        "build: static-check",
        "verify: check",
        "mutation-test:",
        "python3 -m unittest discover",
    ]:
        if phrase not in makefile:
            failures.append(f"Makefile must include {phrase}")

    workflow = read(".github/workflows/check.yml")
    normalized_workflow, digest_count = re.subn(
        r"(?m)^(  INTEGRITY_SHA256: )[0-9a-f]{64}$",
        r"\1__INTEGRITY_SHA256__",
        workflow,
    )
    if digest_count != 1 or normalized_workflow != EXPECTED_WORKFLOW_TEMPLATE:
        failures.append(
            "Check workflow must exactly preserve the pinned, credential-free "
            "macOS integrity and structural validation contract"
        )

    agents = read("AGENTS.md")
    for phrase in [
        "make check",
        "Do not commit Parse credentials",
        "preserve legacy Xcode project settings",
        "non-placeholder XCTest coverage",
        "credential-free signing metadata",
    ]:
        if phrase.lower() not in agents.lower():
            failures.append(f"AGENTS.md must preserve the guardrail: {phrase}")

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
    if app_plist and "NSAppTransportSecurity" in app_plist:
        failures.append(
            "parse_example/Info.plist must not define NSAppTransportSecurity exceptions"
        )
    forbidden_plist_keys = {
        "parseapplicationid",
        "parseclientkey",
        "parsemasterkey",
        "parseserverurl",
        "serverurl",
    }
    for path, plist in plists.items():
        present_forbidden_keys = sorted(
            str(key)
            for key in plist
            if re.sub(r"[^a-z0-9]", "", str(key).lower()) in forbidden_plist_keys
        )
        if present_forbidden_keys:
            failures.append(
                f"{path} must not contain Parse credential or endpoint keys: "
                + ", ".join(present_forbidden_keys)
            )
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
    signing_settings = []
    for line in pbxproj.splitlines():
        match = re.match(
            r'^\s*"?([A-Z][A-Z0-9_]*)(?:\[[^]]+\])?"?\s*=\s*(.*?);\s*$',
            line,
        )
        if match:
            signing_settings.append(match.groups())

    forbidden_signing_settings = {
        "CODE_SIGN_ENTITLEMENTS",
        "DEVELOPMENT_TEAM",
        "PROVISIONING_PROFILE",
        "PROVISIONING_PROFILE_SPECIFIER",
    }
    present_forbidden_settings = sorted(
        name for name, _ in signing_settings if name in forbidden_signing_settings
    )
    if present_forbidden_settings:
        failures.append(
            "Xcode project must not contain account-specific signing settings: "
            + ", ".join(present_forbidden_settings)
        )
    signing_identities = [
        value for name, value in signing_settings if name == "CODE_SIGN_IDENTITY"
    ]
    if signing_identities != ['"iPhone Developer"', '"iPhone Developer"']:
        failures.append(
            "Xcode project must retain only the two historical generic "
            "iPhone Developer signing identities"
        )
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
    for phrase in [
        "objectVersion = 46;",
        "LastUpgradeCheck = 0600;",
        'compatibilityVersion = "Xcode 3.2";',
    ]:
        if phrase not in pbxproj:
            failures.append(f"project.pbxproj compatibility inventory must keep {phrase}")
    if pbxproj.count("IPHONEOS_DEPLOYMENT_TARGET = 8.0;") != 2:
        failures.append(
            "project.pbxproj must keep exactly two inventoried iOS 8.0 deployment settings"
        )
    if "SWIFT_VERSION" in pbxproj:
        failures.append("legacy project must not gain an unreviewed SWIFT_VERSION setting")
    expected_target_sources = {
        "parse_example": {"AppDelegate.swift", "ViewController.swift"},
        "parse_exampleTests": {"parse_exampleTests.swift"},
    }
    actual_target_sources, duplicate_target_names = target_source_paths(pbxproj)
    if duplicate_target_names:
        failures.append(
            "project.pbxproj must not define duplicate native target names: "
            f"{sorted(duplicate_target_names)}"
        )
    if set(actual_target_sources) != set(expected_target_sources):
        failures.append(
            "project.pbxproj must define exactly the expected native targets; "
            f"found {sorted(name for name in actual_target_sources if name)}"
        )
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
    native_source = "\n".join([app_delegate, view_controller, tests])
    if re.search(r"(?i)\bhttps?://", native_source):
        failures.append("native source must not contain runtime network endpoints")
    for marker in [
        "URLSession",
        "URLRequest",
        "NSURLSession",
        "NSURLConnection",
        "CFNetwork",
        "NWConnection",
        "PFObject",
        "PFQuery",
        "PFUser",
    ]:
        if marker in native_source:
            failures.append(
                f"structural scaffold must not contain unreviewed network or Parse runtime code: {marker}"
            )
    if "UIApplicationDelegate" not in app_delegate:
        failures.append("AppDelegate.swift must define the app delegate")
    for phrase in [
        "@UIApplicationMain",
        "application(application: UIApplication, didFinishLaunchingWithOptions",
    ]:
        if phrase not in app_delegate:
            failures.append(f"legacy Swift compatibility inventory must keep {phrase}")
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
        "docs/intended-parse-scenario.md",
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

    dependency_markers = [
        "Package.swift",
        "Package.resolved",
        "Podfile",
        "Podfile.lock",
        "Cartfile",
        "Cartfile.resolved",
    ]
    present_dependency_markers = [
        path for path in dependency_markers if (ROOT / path).exists()
    ]
    if present_dependency_markers:
        failures.append(
            "legacy compatibility inventory must not gain dependency metadata without review: "
            + ", ".join(present_dependency_markers)
        )
    if re.search(r"(?m)^\s*import\s+Parse\w*\s*$", native_source):
        failures.append("legacy Swift source must not gain an unreviewed Parse import")

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
        "credential-free signing metadata",
        "owner-scoped",
        "deterministic fake",
        "Xcode 6-era",
        "iOS 8",
        "compatibility inventory",
        "absolute Makefile path works from another directory",
        "repository-local tamper evidence",
        "not external attestation",
        "100644",
        "Gitlinks/submodules",
        "Updating the frozen baseline",
    ]:
        if phrase.lower() not in docs.lower():
            failures.append(f"docs must mention {phrase}")

    compatibility_claims = {
        "README.md": "Structural validation is not a current-Xcode build or Parse SDK compatibility claim",
        "SECURITY.md": "compatibility inventory, not proof that current Xcode or a Parse SDK builds",
        "VISION.md": "Xcode 6-era iOS 8 compatibility inventory explicit",
        "CHANGES.md": "must precede any modern toolchain or Parse SDK compatibility claim",
    }
    for path, phrase in compatibility_claims.items():
        if phrase not in " ".join(read(path).split()):
            failures.append(f"{path} must include {phrase}")
    changes = " ".join(read("CHANGES.md").split())
    if "external absolute-Makefile calls" not in changes:
        failures.append(
            "CHANGES.md must record external absolute-Makefile calls"
        )

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
    credential_free_plan = read(CREDENTIAL_FREE_PLAN)
    credential_free_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", credential_free_plan
    )
    credential_free_work = markdown_section(credential_free_plan, "Work Completed")
    credential_free_verification = markdown_section(
        credential_free_plan, "Verification Completed"
    )
    if credential_free_status != ["completed"] or not credential_free_work:
        failures.append(
            "credential-free hosted validation plan must record one completed status and completed work"
        )
    if not credential_free_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", credential_free_verification
    ):
        failures.append(
            "credential-free hosted validation plan must record finished verification without pending markers"
        )
    for evidence in [
        "persist-credentials: false",
        "make check",
        "make verify",
        "make lint",
        "make test",
        "make build",
        "python3 -W error scripts/check-baseline.py",
        "git diff --check",
        "Twelve focused hostile mutations",
        "27390789152",
        "27390794889",
        "44affc3f1806bcc1ebee102594a9396779704674",
        "df4cb1c069e1874edd31b4311f1884172cec0e10",
        "a309ff8b426b58ec0e2a45f0f869d46889d02405",
        "PBXSourcesBuildPhase",
        "AppDelegate.swift",
        "ViewController.swift",
        "parse_exampleTests.swift",
    ]:
        if evidence not in credential_free_verification:
            failures.append(
                f"credential-free hosted validation plan must preserve verification evidence: {evidence}"
            )

    signing_metadata_plan = read(SIGNING_METADATA_PLAN)
    for phrase in [
        "status: completed",
        "make check",
        "six hostile mutations",
        "DEVELOPMENT_TEAM",
        "PROVISIONING_PROFILE_SPECIFIER",
        "CODE_SIGN_ENTITLEMENTS",
    ]:
        if phrase not in signing_metadata_plan:
            failures.append(
                f"credential-free signing metadata plan must record {phrase}"
            )

    scenario = " ".join(read("docs/intended-parse-scenario.md").split())
    for phrase in [
        "Review date: 2026-06-13",
        "current repository has no Parse SDK",
        "signed-in user managing a private note",
        "lists only notes owned by the current user",
        "owner-only access",
        "query only records owned by the current user",
        "missing user session must fail before any note query or write",
        "signed out and authentication required",
        "empty note list",
        "save failure or list failure with a retry path",
        "small application boundary",
        "deterministic fake",
        "Runtime-supplied configuration must stay outside version control",
        "No master or admin key belongs in a client application",
        "SDK version and installation path",
        "separate compatibility decision",
        "no public or cross-user query",
        "no file uploads, geolocation, analytics, push notifications",
        "No Swift or Xcode project changes",
    ]:
        if phrase not in scenario:
            failures.append(f"intended Parse scenario must include {phrase}")

    scenario_plan = read(SCENARIO_PLAN)
    scenario_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", scenario_plan)
    scenario_work = markdown_section(scenario_plan, "Work Completed")
    scenario_verification = markdown_section(scenario_plan, "Verification Completed")
    if scenario_status != ["completed"] or not scenario_work:
        failures.append(
            "intended Parse scenario plan must record one completed status and completed work"
        )
    if not scenario_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", scenario_verification
    ):
        failures.append(
            "intended Parse scenario plan must record completed verification"
        )
    for evidence in [
        "make lint",
        "make test",
        "make build",
        "make verify",
        "make check",
        "external working directory",
        "workflow YAML",
        "plist/storyboard XML",
        "asset-catalog JSON",
        "README SVG",
        "hostile mutations rejected",
        "implementation and project paths had no diff",
        "git diff --check",
        "secret, captured-identifier, and generated-artifact scan",
    ]:
        if evidence not in scenario_verification:
            failures.append(
                f"intended Parse scenario verification must record {evidence}"
            )

    compatibility = " ".join(
        read("docs/legacy-toolchain-compatibility.md").split()
    )
    for phrase in [
        "objectVersion = 46",
        "LastUpgradeCheck = 0600",
        'compatibilityVersion = "Xcode 3.2"',
        "IPHONEOS_DEPLOYMENT_TARGET = 8.0",
        "no explicit `SWIFT_VERSION`",
        "@UIApplicationMain",
        "no `Package.swift`",
        "`Podfile`",
        "`Cartfile`",
        "no Parse import",
        "do not invoke an Xcode build",
        "Passing structural validation does not prove compatibility",
        "Parse SDK version and primary-source platform support evidence",
        "simulator build and XCTest commands",
    ]:
        if phrase not in compatibility:
            failures.append(f"legacy compatibility inventory must include {phrase}")

    compatibility_plan = read(COMPATIBILITY_PLAN)
    compatibility_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", compatibility_plan
    )
    compatibility_work = markdown_section(compatibility_plan, "Work Completed")
    compatibility_verification = markdown_section(
        compatibility_plan, "Verification Completed"
    )
    if compatibility_status != ["completed"] or not compatibility_work:
        failures.append(
            "legacy compatibility plan must record completed status and work"
        )
    if not compatibility_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", compatibility_verification
    ):
        failures.append("legacy compatibility plan must record completed verification")
    for evidence in [
        "make lint",
        "make test",
        "make build",
        "make verify",
        "make check",
        "external working directory",
        "workflow YAML",
        "project metadata",
        "hostile mutations",
        "git diff --check",
        "secret and generated-artifact scan",
    ]:
        if evidence not in compatibility_verification:
            failures.append(f"legacy compatibility verification must record {evidence}")

    location_make_plan = read(LOCATION_INDEPENDENT_MAKE_PLAN)
    location_make_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", location_make_plan
    )
    location_make_work = markdown_section(location_make_plan, "Work Completed")
    location_make_verification = markdown_section(
        location_make_plan, "Verification Completed"
    )
    if location_make_status != ["completed"] or not location_make_work:
        failures.append(
            "location-independent Make plan must record one completed status "
            "and completed work"
        )
    if not location_make_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", location_make_verification
    ):
        failures.append(
            "location-independent Make plan must record completed verification"
        )
    for evidence in [
        "make lint",
        "make test",
        "make build",
        "make verify",
        "make check",
        "make static-check",
        "from `/tmp`",
        "absolute",
        "caller-supplied `REPO_ROOT=/tmp`",
        "python3 -m py_compile scripts/check-baseline.py",
        "workflow YAML",
        "both plists",
        "storyboard XML",
        "README SVG",
        "asset-catalog JSON",
        "Nine isolated hostile mutations were rejected",
    ]:
        if evidence not in location_make_verification:
            failures.append(
                f"location-independent Make verification must record {evidence}"
            )

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("parse_example_swift baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
