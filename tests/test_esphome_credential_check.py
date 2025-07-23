#!/usr/bin/env python3
"""
Unit tests for ESPHome credential checker
"""

import unittest
import tempfile
from pathlib import Path
import sys
import os

# Add the .githooks directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.githooks'))

from esphome_credential_check import CredentialChecker


class TestCredentialChecker(unittest.TestCase):
    """Test cases for CredentialChecker"""

    def setUp(self):
        """Set up test fixtures"""
        self.checker = CredentialChecker()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file with given content"""
        file_path = self.temp_path / filename
        file_path.write_text(content)
        return file_path

    def test_api_key_detection(self):
        """Test detection of hardcoded API keys"""
        content = """
esphome:
  name: test-device

api:
  encryption:
    key: "rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk="
"""
        file_path = self.create_test_file("test.yaml", content)
        errors = self.checker.check_file(file_path)

        self.assertEqual(len(errors), 2)  # Should detect both pattern and known exposed
        self.assertTrue(any("API key" in error[0] for error in errors))

    def test_ota_password_detection(self):
        """Test detection of hardcoded OTA passwords"""
        content = """
esphome:
  name: test-device

ota:
  password: "5929ccc1f08289c79aca50ebe0a9b7eb"
"""
        file_path = self.create_test_file("test.yaml", content)
        errors = self.checker.check_file(file_path)

        self.assertEqual(len(errors), 2)  # Should detect both pattern and known exposed
        self.assertTrue(any("OTA password" in error[0] for error in errors))

    def test_fallback_password_detection(self):
        """Test detection of hardcoded fallback passwords"""
        content = """
esphome:
  name: test-device

wifi:
  ssid: "MyWiFi"
  password: "MyPassword"
  ap:
    password: "1SXRpeXi7AdU"
"""
        file_path = self.create_test_file("test.yaml", content)
        errors = self.checker.check_file(file_path)

        self.assertEqual(len(errors), 2)  # Should detect both pattern and known exposed
        self.assertTrue(any("fallback password" in error[0] for error in errors))

    def test_valid_secret_references(self):
        """Test that valid !secret references are not flagged"""
        content = """
esphome:
  name: test-device

api:
  encryption:
    key: !secret api_key

ota:
  password: !secret ota_password

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  ap:
    password: !secret fallback_password
"""
        file_path = self.create_test_file("test.yaml", content)
        errors = self.checker.check_file(file_path)

        self.assertEqual(len(errors), 0)

    def test_non_yaml_files_ignored(self):
        """Test that non-YAML files are ignored"""
        content = "rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk="
        file_path = self.create_test_file("test.txt", content)
        errors = self.checker.check_file(file_path)

        self.assertEqual(len(errors), 0)

    def test_nonexistent_file(self):
        """Test handling of nonexistent files"""
        file_path = self.temp_path / "nonexistent.yaml"
        errors = self.checker.check_file(file_path)

        self.assertEqual(len(errors), 0)

    def test_multiple_files(self):
        """Test checking multiple files"""
        # Create a file with issues
        bad_content = """
api:
  encryption:
    key: "rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk="
"""
        bad_file = self.create_test_file("bad.yaml", bad_content)

        # Create a good file
        good_content = """
api:
  encryption:
    key: !secret api_key
"""
        good_file = self.create_test_file("good.yaml", good_content)

        # Check both files
        exit_code = self.checker.check_files([str(bad_file), str(good_file)])

        self.assertEqual(exit_code, 1)  # Should return error code due to bad file

    def test_all_good_files(self):
        """Test checking multiple good files"""
        good_content = """
api:
  encryption:
    key: !secret api_key
"""
        file1 = self.create_test_file("good1.yaml", good_content)
        file2 = self.create_test_file("good2.yaml", good_content)

        exit_code = self.checker.check_files([str(file1), str(file2)])

        self.assertEqual(exit_code, 0)  # Should return success

    def test_known_exposed_credentials(self):
        """Test detection of all known exposed credentials"""
        known_creds = [
            'rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk=',
            '5929ccc1f08289c79aca50ebe0a9b7eb',
            '1SXRpeXi7AdU'
        ]

        for i, cred in enumerate(known_creds):
            content = f"test: {cred}"
            file_path = self.create_test_file(f"test{i}.yaml", content)
            errors = self.checker.check_file(file_path)

            self.assertGreater(len(errors), 0)
            self.assertTrue(any("Known exposed" in error[0] for error in errors))


if __name__ == '__main__':
    unittest.main()
