#!/usr/bin/env python3
"""
Integration tests for Hardstop Read Hook v1.3.0

Tests the Read tool protection: credential detection, path normalization,
pattern matching, and skip mechanism.

Run: python -m pytest tests/test_read_hook.py -v
Or:  python tests/test_read_hook.py
"""

import sys
import os
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Tuple
from unittest import TestCase, main as unittest_main
from unittest.mock import patch

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "hooks"))

from pre_read import (
    check_dangerous_patterns,
    check_sensitive_patterns,
    check_safe_patterns,
    normalize_path,
    is_skip_enabled,
    STATE_DIR,
    SKIP_FILE,
    DANGEROUS_READ_PATTERNS,
    SENSITIVE_READ_PATTERNS,
    SAFE_READ_PATTERNS,
)


class TestDangerousPatterns(TestCase):
    """Test detection of dangerous credential files."""

    def test_ssh_private_key_rsa(self):
        is_dangerous, reason = check_dangerous_patterns("/home/user/.ssh/id_rsa")
        self.assertTrue(is_dangerous)
        self.assertIn("SSH", reason)

    def test_ssh_private_key_ed25519(self):
        is_dangerous, reason = check_dangerous_patterns("/home/user/.ssh/id_ed25519")
        self.assertTrue(is_dangerous)
        self.assertIn("SSH", reason)

    def test_ssh_pem_file(self):
        is_dangerous, reason = check_dangerous_patterns("/home/user/.ssh/mykey.pem")
        self.assertTrue(is_dangerous)

    def test_ssh_config(self):
        is_dangerous, reason = check_dangerous_patterns("/home/user/.ssh/config")
        self.assertTrue(is_dangerous)

    def test_aws_credentials(self):
        is_dangerous, reason = check_dangerous_patterns("/home/user/.aws/credentials")
        self.assertTrue(is_dangerous)
        self.assertIn("AWS", reason)

    def test_aws_config(self):
        is_dangerous, reason = check_dangerous_patterns("/home/user/.aws/config")
        self.assertTrue(is_dangerous)

    def test_env_file(self):
        is_dangerous, reason = check_dangerous_patterns("/project/.env")
        self.assertTrue(is_dangerous)
        self.assertIn("Environment", reason)

    def test_env_production(self):
        is_dangerous, reason = check_dangerous_patterns("/project/.env.production")
        self.assertTrue(is_dangerous)

    def test_env_local(self):
        is_dangerous, reason = check_dangerous_patterns("/project/.env.local")
        self.assertTrue(is_dangerous)

    def test_kube_config(self):
        is_dangerous, reason = check_dangerous_patterns("/home/user/.kube/config")
        self.assertTrue(is_dangerous)
        self.assertIn("Kubernetes", reason)

    def test_docker_config(self):
        is_dangerous, reason = check_dangerous_patterns("/home/user/.docker/config.json")
        self.assertTrue(is_dangerous)

    def test_netrc(self):
        is_dangerous, reason = check_dangerous_patterns("/home/user/.netrc")
        self.assertTrue(is_dangerous)

    def test_npmrc(self):
        is_dangerous, reason = check_dangerous_patterns("/home/user/.npmrc")
        self.assertTrue(is_dangerous)

    def test_pypirc(self):
        is_dangerous, reason = check_dangerous_patterns("/home/user/.pypirc")
        self.assertTrue(is_dangerous)

    def test_credentials_json(self):
        is_dangerous, reason = check_dangerous_patterns("/project/credentials.json")
        self.assertTrue(is_dangerous)

    def test_secrets_yaml(self):
        is_dangerous, reason = check_dangerous_patterns("/project/secrets.yaml")
        self.assertTrue(is_dangerous)

    def test_gitconfig(self):
        is_dangerous, reason = check_dangerous_patterns("/home/user/.gitconfig")
        self.assertTrue(is_dangerous)

    def test_git_credentials(self):
        is_dangerous, reason = check_dangerous_patterns("/home/user/.git-credentials")
        self.assertTrue(is_dangerous)

    def test_pgpass(self):
        is_dangerous, reason = check_dangerous_patterns("/home/user/.pgpass")
        self.assertTrue(is_dangerous)

    def test_gcloud_credentials(self):
        is_dangerous, reason = check_dangerous_patterns("/home/user/.config/gcloud/credentials.db")
        self.assertTrue(is_dangerous)

    def test_azure_credentials(self):
        is_dangerous, reason = check_dangerous_patterns("/home/user/.azure/credentials")
        self.assertTrue(is_dangerous)


class TestSafePatterns(TestCase):
    """Test that safe files are allowed."""

    def test_python_file(self):
        self.assertTrue(check_safe_patterns("/project/main.py"))

    def test_javascript_file(self):
        self.assertTrue(check_safe_patterns("/project/index.js"))

    def test_typescript_file(self):
        self.assertTrue(check_safe_patterns("/project/app.ts"))

    def test_readme(self):
        self.assertTrue(check_safe_patterns("/project/README.md"))

    def test_package_json(self):
        self.assertTrue(check_safe_patterns("/project/package.json"))

    def test_requirements_txt(self):
        self.assertTrue(check_safe_patterns("/project/requirements.txt"))

    def test_env_example(self):
        # .env.example should be safe (it's a template)
        self.assertTrue(check_safe_patterns("/project/.env.example"))

    def test_env_template(self):
        self.assertTrue(check_safe_patterns("/project/.env.template"))

    def test_env_sample(self):
        self.assertTrue(check_safe_patterns("/project/.env.sample"))

    def test_dockerfile(self):
        self.assertTrue(check_safe_patterns("/project/Dockerfile"))

    def test_gitignore(self):
        self.assertTrue(check_safe_patterns("/project/.gitignore"))

    def test_html_file(self):
        self.assertTrue(check_safe_patterns("/project/index.html"))

    def test_css_file(self):
        self.assertTrue(check_safe_patterns("/project/styles.css"))

    def test_makefile(self):
        self.assertTrue(check_safe_patterns("/project/Makefile"))

    def test_cargo_toml(self):
        self.assertTrue(check_safe_patterns("/project/Cargo.toml"))

    def test_go_mod(self):
        self.assertTrue(check_safe_patterns("/project/go.mod"))


class TestSensitivePatterns(TestCase):
    """Test detection of sensitive (but not blocked) files."""

    def test_config_json(self):
        is_sensitive, reason = check_sensitive_patterns("/project/config.json")
        self.assertTrue(is_sensitive)

    def test_config_yaml(self):
        is_sensitive, reason = check_sensitive_patterns("/project/config.yaml")
        self.assertTrue(is_sensitive)

    def test_settings_json(self):
        is_sensitive, reason = check_sensitive_patterns("/project/settings.json")
        self.assertTrue(is_sensitive)

    def test_env_backup(self):
        is_sensitive, reason = check_sensitive_patterns("/project/.env.bak")
        self.assertTrue(is_sensitive)

    def test_file_with_password_in_name(self):
        is_sensitive, reason = check_sensitive_patterns("/project/database_password.txt")
        self.assertTrue(is_sensitive)

    def test_file_with_secret_in_name(self):
        is_sensitive, reason = check_sensitive_patterns("/project/my_secret_file.txt")
        self.assertTrue(is_sensitive)


class TestPathNormalization(TestCase):
    """Test path normalization for cross-platform matching."""

    def test_tilde_expansion(self):
        normalized = normalize_path("~/.ssh/id_rsa", "/")
        self.assertIn(".ssh", normalized)
        self.assertNotIn("~", normalized)

    def test_relative_path(self):
        normalized = normalize_path("config.json", "/home/user/project")
        self.assertIn("project", normalized)
        self.assertIn("config.json", normalized)

    def test_forward_slashes(self):
        # Windows paths should be normalized to forward slashes
        normalized = normalize_path("C:\\Users\\john\\.aws\\credentials", "C:\\")
        self.assertIn("/", normalized)
        # Should not contain backslashes
        self.assertNotIn("\\", normalized)

    def test_double_dots_resolved(self):
        normalized = normalize_path("/project/subdir/../config.json", "/")
        # .. should be resolved
        self.assertNotIn("..", normalized)


class TestWindowsPaths(TestCase):
    """Test Windows-specific path patterns."""

    def test_windows_aws_credentials(self):
        is_dangerous, _ = check_dangerous_patterns("C:/Users/john/.aws/credentials")
        self.assertTrue(is_dangerous)

    def test_windows_ssh_key(self):
        is_dangerous, _ = check_dangerous_patterns("C:/Users/john/.ssh/id_rsa")
        self.assertTrue(is_dangerous)

    def test_windows_env_file(self):
        is_dangerous, _ = check_dangerous_patterns("C:/Projects/myapp/.env")
        self.assertTrue(is_dangerous)

    def test_windows_kube_config(self):
        is_dangerous, _ = check_dangerous_patterns("C:/Users/john/.kube/config")
        self.assertTrue(is_dangerous)


class TestNonMatchingFiles(TestCase):
    """Test that normal files are not flagged."""

    def test_random_text_file(self):
        is_dangerous, _ = check_dangerous_patterns("/project/notes.txt")
        self.assertFalse(is_dangerous)

    def test_image_file(self):
        is_dangerous, _ = check_dangerous_patterns("/project/logo.png")
        self.assertFalse(is_dangerous)

    def test_data_csv(self):
        is_dangerous, _ = check_dangerous_patterns("/project/data.csv")
        self.assertFalse(is_dangerous)

    def test_sql_file(self):
        is_dangerous, _ = check_dangerous_patterns("/project/schema.sql")
        self.assertFalse(is_dangerous)

    def test_lock_file(self):
        is_dangerous, _ = check_dangerous_patterns("/project/package-lock.json")
        self.assertFalse(is_dangerous)


class TestSkipMechanism(TestCase):
    """Test the skip_next one-time bypass."""

    def setUp(self):
        # Ensure clean state
        if SKIP_FILE.exists():
            SKIP_FILE.unlink()

    def tearDown(self):
        # Clean up
        if SKIP_FILE.exists():
            SKIP_FILE.unlink()

    def test_skip_not_enabled_by_default(self):
        self.assertFalse(is_skip_enabled())

    def test_skip_enabled_when_file_exists(self):
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        SKIP_FILE.touch()
        self.assertTrue(is_skip_enabled())

    def test_skip_file_consumed_after_check(self):
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        SKIP_FILE.touch()
        is_skip_enabled()  # Should consume the file
        self.assertFalse(SKIP_FILE.exists())

    def test_skip_only_works_once(self):
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        SKIP_FILE.touch()
        self.assertTrue(is_skip_enabled())  # First call consumes it
        self.assertFalse(is_skip_enabled())  # Second call returns False


class TestIntegration(TestCase):
    """Integration tests running the actual hook script."""

    @classmethod
    def setUpClass(cls):
        cls.hook_script = Path(__file__).parent.parent / "hooks" / "pre_read.py"

    def run_hook(self, file_path: str, cwd: str = "/project") -> Tuple[int, str, str]:
        """Run the hook script and return (exit_code, stdout, stderr)."""
        input_data = json.dumps({
            "tool_name": "Read",
            "tool_input": {"file_path": file_path},
            "cwd": cwd
        })

        result = subprocess.run(
            [sys.executable, str(self.hook_script)],
            input=input_data,
            capture_output=True,
            text=True
        )

        return result.returncode, result.stdout, result.stderr

    def test_blocks_ssh_key(self):
        exit_code, stdout, stderr = self.run_hook("~/.ssh/id_rsa")
        self.assertEqual(exit_code, 2)
        self.assertIn("BLOCKED", stderr)

    def test_blocks_aws_credentials(self):
        exit_code, stdout, stderr = self.run_hook("~/.aws/credentials")
        self.assertEqual(exit_code, 2)
        self.assertIn("BLOCKED", stderr)

    def test_blocks_env_file(self):
        exit_code, stdout, stderr = self.run_hook(".env")
        self.assertEqual(exit_code, 2)
        self.assertIn("BLOCKED", stderr)

    def test_allows_python_file(self):
        exit_code, stdout, stderr = self.run_hook("main.py")
        self.assertEqual(exit_code, 0)

    def test_allows_readme(self):
        exit_code, stdout, stderr = self.run_hook("README.md")
        self.assertEqual(exit_code, 0)

    def test_allows_package_json(self):
        exit_code, stdout, stderr = self.run_hook("package.json")
        self.assertEqual(exit_code, 0)

    def test_allows_env_example(self):
        exit_code, stdout, stderr = self.run_hook(".env.example")
        self.assertEqual(exit_code, 0)


class TestPatternCounts(TestCase):
    """Verify pattern counts for documentation."""

    def test_dangerous_pattern_count(self):
        # Should have ~35 dangerous patterns
        self.assertGreater(len(DANGEROUS_READ_PATTERNS), 30)

    def test_sensitive_pattern_count(self):
        # Should have ~15 sensitive patterns
        self.assertGreater(len(SENSITIVE_READ_PATTERNS), 10)

    def test_safe_pattern_count(self):
        # Should have ~25 safe patterns
        self.assertGreater(len(SAFE_READ_PATTERNS), 20)


if __name__ == "__main__":
    unittest_main()
