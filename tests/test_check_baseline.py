import plistlib
from hashlib import sha256
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


SOURCE_ROOT = Path(__file__).resolve().parents[1]


class BaselineMutationTests(unittest.TestCase):
    def copy_repository(self, temporary_directory):
        destination = Path(temporary_directory) / "repository"
        shutil.copytree(
            SOURCE_ROOT,
            destination,
            ignore=shutil.ignore_patterns(
                ".git",
                ".review",
                "__pycache__",
                ".pytest_cache",
            ),
        )
        integrity_path = destination / "scripts" / "check-integrity.py"
        integrity = integrity_path.read_text(encoding="utf-8")
        for protected_path in [
            "scripts/check-baseline.py",
            "tests/test_check_baseline.py",
        ]:
            protected_digest = sha256(
                (destination / protected_path).read_bytes()
            ).hexdigest()
            integrity, replacements = re.subn(
                rf'("{re.escape(protected_path)}": ")[0-9a-f]{{64}}("[,])',
                rf"\g<1>{protected_digest}\g<2>",
                integrity,
            )
            self.assertEqual(replacements, 1)
        integrity_path.write_text(integrity, encoding="utf-8")
        workflow_path = destination / ".github" / "workflows" / "check.yml"
        workflow = workflow_path.read_text(encoding="utf-8")
        integrity_digest = sha256(integrity_path.read_bytes()).hexdigest()
        workflow, replacements = re.subn(
            r"(?m)^(  INTEGRITY_SHA256: )[0-9a-f]{64}$",
            rf"\g<1>{integrity_digest}",
            workflow,
        )
        self.assertEqual(replacements, 1)
        workflow_path.write_text(workflow, encoding="utf-8")
        return destination

    def run_checker(self, repository):
        integrity_result = self.run_integrity_checker(repository)
        baseline_result = subprocess.run(
            ["python3", "scripts/check-baseline.py"],
            cwd=repository,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        return subprocess.CompletedProcess(
            args=["integrity-and-baseline"],
            returncode=int(
                integrity_result.returncode != 0 or baseline_result.returncode != 0
            ),
            stdout=integrity_result.stdout + baseline_result.stdout,
            stderr=integrity_result.stderr + baseline_result.stderr,
        )

    def run_integrity_checker(self, repository):
        return subprocess.run(
            ["python3", "scripts/check-integrity.py"],
            cwd=repository,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )

    def run_integrity_gate(self, repository):
        return subprocess.run(
            ["make", "static-check"],
            cwd=repository,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )

    def assert_mutation_rejected(self, mutate, expected_diagnostic):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = self.copy_repository(temporary_directory)
            mutate(repository, Path(temporary_directory))
            result = self.run_checker(repository)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(expected_diagnostic, result.stderr)

    def assert_integrity_mutation_rejected(self, mutate, expected_diagnostic):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = self.copy_repository(temporary_directory)
            mutate(repository, Path(temporary_directory))
            result = self.run_integrity_checker(repository)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(expected_diagnostic, result.stderr)

    def assert_gate_mutation_rejected(self, mutate, expected_diagnostic):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = self.copy_repository(temporary_directory)
            mutate(repository, Path(temporary_directory))
            result = self.run_integrity_gate(repository)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(expected_diagnostic, result.stderr)

    def test_clean_repository_passes(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = self.copy_repository(temporary_directory)
            result = self.run_checker(repository)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_unreviewed_parse_configuration(self):
        def mutate(repository, _):
            application_id_key = "PARSE_APPLICATION" + "_ID"
            client_key = "PARSE_CLIENT" + "_KEY"
            (repository / "ParseConfig.plist").write_text(
                f"""<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict>
<key>{application_id_key}</key><string>example-application-id</string>
<key>{client_key}</key><string>example-client-key</string>
<key>SERVER_URL</key><string>http://example.invalid/parse</string>
</dict></plist>
""",
                encoding="utf-8",
            )

        self.assert_mutation_rejected(mutate, "unexpected repository file: ParseConfig.plist")

    def test_rejects_artifact_hidden_in_review_directory(self):
        def mutate(repository, _):
            review_directory = repository / ".review"
            review_directory.mkdir()
            (review_directory / "ParseConfig.plist").write_text(
                "<plist version=\"1.0\"><dict/></plist>\n",
                encoding="utf-8",
            )

        self.assert_mutation_rejected(
            mutate,
            "unexpected repository file: .review/ParseConfig.plist",
        )

    def test_rejects_artifact_hidden_in_python_cache(self):
        def mutate(repository, _):
            cache_directory = repository / "scripts" / "__pycache__"
            cache_directory.mkdir()
            (cache_directory / "credential.pyc").write_bytes(b"hidden")

        self.assert_mutation_rejected(
            mutate,
            "unexpected repository file: scripts/__pycache__/credential.pyc",
        )

    def test_rejects_provisioning_artifact(self):
        def mutate(repository, _):
            (repository / "Developer.mobileprovision").write_bytes(b"not-a-profile")

        self.assert_mutation_rejected(
            mutate,
            "unexpected repository file: Developer.mobileprovision",
        )

    def test_rejects_required_file_symlink(self):
        def mutate(repository, temporary_directory):
            readme = repository / "README.md"
            outside = temporary_directory / "README.md"
            readme.replace(outside)
            readme.symlink_to(outside)

        self.assert_mutation_rejected(mutate, "repository files must not be symlinks: README.md")

    def test_rejects_unreviewed_swift_implementation(self):
        def mutate(repository, _):
            (repository / "parse_example" / "ParseClient.swift").write_text(
                "import Parse\n",
                encoding="utf-8",
            )

        self.assert_mutation_rejected(
            mutate,
            "unexpected repository file: parse_example/ParseClient.swift",
        )

    def test_rejects_app_transport_security_exception(self):
        def mutate(repository, _):
            path = repository / "parse_example" / "Info.plist"
            with path.open("rb") as handle:
                plist = plistlib.load(handle)
            plist["NSAppTransportSecurity"] = {"NSAllowsArbitraryLoads": True}
            with path.open("wb") as handle:
                plistlib.dump(plist, handle)

        self.assert_mutation_rejected(
            mutate,
            "parse_example/Info.plist must not define NSAppTransportSecurity exceptions",
        )

    def test_rejects_parse_credential_key_in_app_plist(self):
        def mutate(repository, _):
            path = repository / "parse_example" / "Info.plist"
            with path.open("rb") as handle:
                plist = plistlib.load(handle)
            plist["PARSE_APPLICATION" + "_ID"] = "example-application-id"
            with path.open("wb") as handle:
                plistlib.dump(plist, handle)

        self.assert_mutation_rejected(
            mutate,
            "parse_example/Info.plist must not contain Parse credential or endpoint keys",
        )

    def test_rejects_runtime_endpoint(self):
        def mutate(repository, _):
            path = repository / "parse_example" / "ViewController.swift"
            path.write_text(
                path.read_text(encoding="utf-8")
                + '\nlet parseEndpoint = "http://example.invalid/parse"\n',
                encoding="utf-8",
            )

        self.assert_mutation_rejected(
            mutate,
            "native source must not contain runtime network endpoints",
        )

    def test_rejects_runtime_network_api_without_literal_endpoint(self):
        def mutate(repository, _):
            path = repository / "parse_example" / "ViewController.swift"
            path.write_text(
                path.read_text(encoding="utf-8")
                + "\nlet session = URLSession.sharedSession()\n",
                encoding="utf-8",
            )

        self.assert_mutation_rejected(
            mutate,
            "structural scaffold must not contain unreviewed network or Parse runtime code: URLSession",
        )

    def test_rejects_assembled_https_data_contents_of_bypass(self):
        def mutate(repository, _):
            path = repository / "parse_example" / "ViewController.swift"
            path.write_text(
                path.read_text(encoding="utf-8")
                + """

func loadRemotePayload() throws -> Data {
    let scheme = ["ht", "tps"].joined()
    let endpoint = URL(string: scheme + "://example.invalid/payload")!
    return try Data(contentsOf: endpoint)
}
""",
                encoding="utf-8",
            )

        self.assert_mutation_rejected(
            mutate,
            "native source integrity mismatch: parse_example/ViewController.swift",
        )

    def test_rejects_network_code_hidden_in_dead_code_and_comments(self):
        def mutate(repository, _):
            path = repository / "parse_example" / "ViewController.swift"
            path.write_text(
                path.read_text(encoding="utf-8")
                + """

// Data(contentsOf: URL(string: assembledScheme)!)
func unreachableFileRead() {
    if false {
        let path = ["/tmp", "/payload"].joined()
        _ = NSData(contentsOfFile: path)
    }
}
""",
                encoding="utf-8",
            )

        self.assert_mutation_rejected(
            mutate,
            "native source integrity mismatch: parse_example/ViewController.swift",
        )

    def test_rejects_native_source_rename(self):
        def mutate(repository, _):
            source = repository / "parse_example" / "ViewController.swift"
            source.rename(repository / "parse_example" / "HomeViewController.swift")

        self.assert_mutation_rejected(
            mutate,
            "expected protected file missing: parse_example/ViewController.swift",
        )

    def test_integrity_checker_rejects_makefile_laundering(self):
        def mutate(repository, _):
            (repository / "Makefile").write_text(
                ".PHONY: check\ncheck:\n\t@true\n",
                encoding="utf-8",
            )

        self.assert_integrity_mutation_rejected(
            mutate,
            "integrity mismatch: Makefile",
        )

    def test_make_gate_rejects_later_single_colon_recipe_replacement(self):
        self.assert_later_makefile_rejected(":")

    def test_make_gate_rejects_later_double_colon_recipe_append(self):
        self.assert_later_makefile_rejected("::")

    def assert_later_makefile_rejected(self, separator):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = self.copy_repository(temporary_directory)
            later_makefile = Path(temporary_directory) / "later.mk"
            marker = Path(temporary_directory) / "later-recipe-ran"
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
                    str(repository / "Makefile"),
                    "-f",
                    str(later_makefile),
                    "check",
                ],
                cwd=repository.parent,
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
            marker_exists = marker.exists()

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertFalse(marker_exists, result.stdout)

    def test_integrity_checker_rejects_native_source_addition(self):
        def mutate(repository, _):
            (repository / "parse_example" / "NetworkClient.swift").write_text(
                "import Foundation\n",
                encoding="utf-8",
            )

        self.assert_integrity_mutation_rejected(
            mutate,
            "unexpected native source file: parse_example/NetworkClient.swift",
        )

    def test_integrity_checker_rejects_executable_protected_file(self):
        def mutate(repository, _):
            path = repository / "Makefile"
            path.chmod(path.stat().st_mode | 0o111)

        self.assert_integrity_mutation_rejected(
            mutate,
            "protected files must not be executable: Makefile",
        )

    def test_integrity_checker_rejects_crlf_rewrite(self):
        def mutate(repository, _):
            path = repository / "parse_example" / "ViewController.swift"
            path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))

        self.assert_integrity_mutation_rejected(
            mutate,
            "native source integrity mismatch: parse_example/ViewController.swift",
        )

    def test_integrity_checker_rejects_policy_tool_laundering(self):
        def mutate(repository, _):
            (repository / "scripts" / "check-baseline.py").write_text(
                "print('baseline checks passed')\n",
                encoding="utf-8",
            )

        self.assert_integrity_mutation_rejected(
            mutate,
            "integrity mismatch: scripts/check-baseline.py",
        )

    def test_integrity_checker_rejects_test_laundering(self):
        def mutate(repository, _):
            path = repository / "tests" / "test_check_baseline.py"
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "self.assertNotEqual(result.returncode, 0, result.stdout)",
                    "self.assertEqual(result.returncode, 0, result.stderr)",
                ),
                encoding="utf-8",
            )

        self.assert_integrity_mutation_rejected(
            mutate,
            "integrity mismatch: tests/test_check_baseline.py",
        )

    def test_integrity_gate_rejects_bootstrap_laundering(self):
        def mutate(repository, _):
            (repository / "scripts" / "check-integrity.py").write_text(
                "print('integrity checks passed')\n",
                encoding="utf-8",
            )

        self.assert_gate_mutation_rejected(
            mutate,
            "integrity bootstrap digest mismatch",
        )

    def test_integrity_checker_rejects_workflow_laundering(self):
        def mutate(repository, _):
            path = repository / ".github" / "workflows" / "check.yml"
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "make check",
                    "true",
                ),
                encoding="utf-8",
            )

        self.assert_integrity_mutation_rejected(
            mutate,
            "integrity workflow contract mismatch",
        )

    def test_rejects_gitlink_hidden_from_working_tree_inventory(self):
        def mutate(repository, _):
            subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
            subprocess.run(["git", "add", "."], cwd=repository, check=True)
            subprocess.run(
                [
                    "git",
                    "update-index",
                    "--add",
                    "--info-only",
                    "--cacheinfo",
                    "160000,1111111111111111111111111111111111111111,vendor/HiddenSDK",
                ],
                cwd=repository,
                check=True,
            )

        self.assert_mutation_rejected(
            mutate,
            "tracked repository entries must be regular non-executable files: "
            "160000 vendor/HiddenSDK",
        )

    def test_rejects_oversized_repository_file(self):
        def mutate(repository, _):
            path = repository / "README.md"
            path.write_text("x" * 1_048_577, encoding="utf-8")

        self.assert_mutation_rejected(
            mutate,
            "repository file exceeds 1048576-byte limit: README.md",
        )

    def test_rejects_private_key_material_in_allowed_file(self):
        def mutate(repository, _):
            marker = "-----BEGIN " + "PRIVATE KEY-----"
            path = repository / "CHANGES.md"
            path.write_text(
                path.read_text(encoding="utf-8") + f"\n{marker}\nredacted\n",
                encoding="utf-8",
            )

        self.assert_mutation_rejected(
            mutate,
            "repository must not contain private-key material: CHANGES.md",
        )


if __name__ == "__main__":
    unittest.main()
