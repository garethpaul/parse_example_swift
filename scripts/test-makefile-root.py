#!/usr/bin/env python3
import os
import hashlib
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class MakefileRootTests(unittest.TestCase):
    def run_make(self, *arguments, environment=None):
        with tempfile.TemporaryDirectory(prefix="Parse Swift's [gate] ") as directory:
            checkout = Path(directory)
            scripts = checkout / "scripts"
            tests = checkout / "tests"
            workflow_directory = checkout / ".github" / "workflows"
            scripts.mkdir()
            tests.mkdir()
            workflow_directory.mkdir(parents=True)
            makefile = checkout / "Makefile"
            makefile.write_text((ROOT / "Makefile").read_text(encoding="utf-8"), encoding="utf-8")
            integrity_source = "print('integrity fixture passed')\n"
            (scripts / "check-integrity.py").write_text(
                integrity_source,
                encoding="utf-8",
            )
            (scripts / "check-baseline.py").write_text(
                "print('baseline fixture passed')\n",
                encoding="utf-8",
            )
            (scripts / "test-makefile-root.py").write_text(
                "print('root fixture passed')\n",
                encoding="utf-8",
            )
            (tests / "test_fixture.py").write_text(
                "import unittest\n\nclass FixtureTest(unittest.TestCase):\n"
                "    def test_fixture(self):\n        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            integrity_digest = hashlib.sha256(integrity_source.encode()).hexdigest()
            (workflow_directory / "check.yml").write_text(
                f"env:\n  INTEGRITY_SHA256: {integrity_digest}\n",
                encoding="utf-8",
            )
            env = {"PATH": os.environ.get("PATH", "")}
            if environment:
                env.update(environment)
            result = subprocess.run(
                ["make", "--no-print-directory", "-f", str(makefile), *arguments],
                cwd=checkout.parent, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, check=False, env=env,
            )
            return result, shlex.quote(str(checkout.resolve()))

    def assert_live_root_path_is_literal(self, checkout_name, marker_name):
        with tempfile.TemporaryDirectory() as parent:
            checkout = Path(parent) / checkout_name
            scripts = checkout / "scripts"
            scripts.mkdir(parents=True)
            makefile = checkout / "Makefile"
            makefile.write_text((ROOT / "Makefile").read_text(encoding="utf-8"), encoding="utf-8")
            (scripts / "test-makefile-root.py").write_text(
                "print('live root stub passed')\n", encoding="utf-8"
            )
            result = subprocess.run(
                ["make", "--no-print-directory", "-f", str(makefile), "root-test"],
                cwd=checkout.parent, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, check=False, env={"PATH": os.environ.get("PATH", "")},
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertFalse((checkout.parent / marker_name).exists(), result.stdout)
            self.assertIn("live root stub passed", result.stdout)

    def test_all_targets_preserve_spaced_absolute_makefile_path(self):
        targets = ("build", "check", "integrity-check", "lint", "mutation-test", "root-test", "static-check", "test", "verify")
        for target in targets:
            for name, arguments, environment in (
                ("none", (target,), None),
                ("command", (target, "REPO_ROOT=/tmp/attacker-root"), None),
                ("environment", (target,), {"REPO_ROOT": "/tmp/attacker-root"}),
            ):
                with self.subTest(target=target, override=name):
                    result, expected_root = self.run_make(*arguments, environment=environment)
                    self.assertEqual(result.returncode, 0, result.stdout)
                    self.assertNotIn("/tmp/attacker-root", result.stdout)
                    self.assertIn(expected_root, result.stdout)

    def test_command_line_makefile_list_override_fails_closed(self):
        result, _ = self.run_make("verify", "MAKEFILE_LIST=/tmp/untrusted")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MAKEFILE_LIST must not be overridden", result.stdout)

    def test_environment_makefile_list_override_fails_closed(self):
        result, _ = self.run_make("-e", "verify", environment={"MAKEFILE_LIST": "/tmp/untrusted"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MAKEFILE_LIST must not be overridden", result.stdout)

    def test_command_line_makeflags_override_fails_closed(self):
        result, _ = self.run_make("check", "MAKEFLAGS=-n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MAKEFLAGS must not be overridden", result.stdout)

    def test_later_makefile_cannot_replace_or_append_public_recipes(self):
        for separator in (":", "::"):
            with self.subTest(separator=separator), tempfile.TemporaryDirectory() as directory:
                checkout = Path(directory) / "checkout"
                checkout.mkdir()
                makefile = checkout / "Makefile"
                makefile.write_text(
                    (ROOT / "Makefile").read_text(encoding="utf-8"),
                    encoding="utf-8",
                )
                later_makefile = checkout / "later.mk"
                marker = checkout / "later-recipe-ran"
                later_makefile.write_text(
                    (
                        "build check integrity-check lint mutation-test root-test "
                        f"static-check test verify{separator}\n"
                        f"\t@touch '{marker}'\n"
                    ),
                    encoding="utf-8",
                )

                result = subprocess.run(
                    [
                        "make",
                        "--no-print-directory",
                        "-f",
                        str(makefile),
                        "-f",
                        str(later_makefile),
                        "check",
                    ],
                    cwd=checkout.parent,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    check=False,
                    env={"PATH": os.environ.get("PATH", "")},
                )

                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertFalse(marker.exists(), result.stdout)

    def test_non_executing_and_error_ignoring_modes_fail_closed(self):
        for flag in (
            "-n",
            "--just-print",
            "--dry-run",
            "--recon",
            "-t",
            "--touch",
            "-q",
            "--question",
            "-i",
            "--ignore-errors",
        ):
            with self.subTest(flag=flag):
                result, _ = self.run_make(flag, "check")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(
                    "non-executing or error-ignoring MAKEFLAGS are not supported",
                    result.stdout,
                )

    def test_live_root_path_does_not_execute_shell_metacharacters(self):
        for checkout_name, marker_name in (
            ("Parse backtick `touch BACKTICK_PWNED` case", "BACKTICK_PWNED"),
            ('Parse quote " ; touch QUOTE_PWNED ; echo " case', "QUOTE_PWNED"),
        ):
            with self.subTest(checkout_name=checkout_name):
                self.assert_live_root_path_is_literal(checkout_name, marker_name)

if __name__ == "__main__":
    unittest.main()
