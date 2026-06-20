import plistlib
from pathlib import Path
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
        return destination

    def run_checker(self, repository):
        return subprocess.run(
            ["python3", "scripts/check-baseline.py"],
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
