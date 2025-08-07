#!/usr/bin/env python3
"""
Unit tests for the credential rotation script.

Tests all components of the credential rotation process including:
- Credential generation and validation
- 1Password integration
- Deployment management
- Security validation
"""

import unittest
import tempfile
import os
import sys
import shutil
import subprocess
from unittest.mock import Mock, patch
from pathlib import Path

# Add the scripts directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from rotate_credentials import (
    CredentialGenerator,
    CredentialValidator,
    OnePasswordManager,
    DeploymentManager,
    SecurityValidator,
    CredentialRotator
)


class TestCredentialGenerator(unittest.TestCase):
    """Test credential generation functionality"""

    def setUp(self):
        self.generator = CredentialGenerator()

    def test_generate_api_key(self):
        """Test API key generation"""
        api_key = self.generator.generate_api_key()

        # Should be 44 characters long
        self.assertEqual(len(api_key), 44)

        # Should end with =
        self.assertTrue(api_key.endswith('='))

        # Should be valid base64
        import base64
        try:
            decoded = base64.b64decode(api_key)
            self.assertEqual(len(decoded), 32)  # 32 bytes
        except Exception:
            self.fail("Generated API key is not valid base64")

    def test_generate_ota_password(self):
        """Test OTA password generation"""
        ota_password = self.generator.generate_ota_password()

        # Should be 32 characters long
        self.assertEqual(len(ota_password), 32)

        # Should be hexadecimal
        try:
            int(ota_password, 16)
        except ValueError:
            self.fail("Generated OTA password is not valid hexadecimal")

    def test_generate_fallback_password(self):
        """Test fallback password generation"""
        fallback_password = self.generator.generate_fallback_password()

        # Should be 12 characters long
        self.assertEqual(len(fallback_password), 12)

        # Should be alphanumeric only
        self.assertTrue(fallback_password.isalnum())

    def test_multiple_generations_are_different(self):
        """Test that multiple generations produce different results"""
        api_keys = [self.generator.generate_api_key() for _ in range(5)]
        ota_passwords = [self.generator.generate_ota_password() for _ in range(5)]
        fallback_passwords = [self.generator.generate_fallback_password() for _ in range(5)]

        # All should be unique
        self.assertEqual(len(set(api_keys)), 5)
        self.assertEqual(len(set(ota_passwords)), 5)
        self.assertEqual(len(set(fallback_passwords)), 5)


class TestCredentialValidator(unittest.TestCase):
    """Test credential validation functionality"""

    def setUp(self):
        self.validator = CredentialValidator()

    def test_validate_api_key_valid(self):
        """Test validation of valid API key"""
        # Use a properly generated base64 key (32 bytes = 44 chars with padding)
        import base64
        import secrets
        valid_key = base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
        valid, msg = self.validator.validate_api_key(valid_key)
        self.assertTrue(valid)
        self.assertIn("valid", msg)

    def test_validate_api_key_wrong_length(self):
        """Test validation of API key with wrong length"""
        short_key = "short="
        valid, msg = self.validator.validate_api_key(short_key)
        self.assertFalse(valid)
        self.assertIn("44 characters", msg)

    def test_validate_api_key_invalid_format(self):
        """Test validation of API key with invalid format"""
        # Use exactly 44 characters that's not valid base64 (contains invalid chars)
        invalid_key = "1234567890123456789012345678901234567890!@#="
        valid, msg = self.validator.validate_api_key(invalid_key)
        self.assertFalse(valid)
        self.assertIn("valid base64", msg)

    def test_validate_api_key_exposed(self):
        """Test validation detects exposed API key"""
        exposed_key = "rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk="  # pragma: allowlist secret
        valid, msg = self.validator.validate_api_key(exposed_key)
        self.assertFalse(valid)
        self.assertIn("exposed", msg)

    def test_validate_ota_password_valid(self):
        """Test validation of valid OTA password"""
        valid_password = "1234567890abcdef1234567890abcdef"
        valid, msg = self.validator.validate_ota_password(valid_password)
        self.assertTrue(valid)
        self.assertIn("valid", msg)

    def test_validate_ota_password_wrong_length(self):
        """Test validation of OTA password with wrong length"""
        short_password = "short"
        valid, msg = self.validator.validate_ota_password(short_password)
        self.assertFalse(valid)
        # The message could be either format depending on whether it's hex or not
        self.assertTrue("32" in msg and "characters" in msg)

    def test_validate_ota_password_invalid_format(self):
        """Test validation of OTA password with invalid format"""
        # Use a 32-character string that's not valid hex
        invalid_password = "not-hex-format-contains-invalid-gh"
        valid, msg = self.validator.validate_ota_password(invalid_password)
        self.assertFalse(valid)
        self.assertIn("hexadecimal", msg)

    def test_validate_ota_password_exposed(self):
        """Test validation detects exposed OTA password"""
        exposed_password = "5929ccc1f08289c79aca50ebe0a9b7eb"  # pragma: allowlist secret
        valid, msg = self.validator.validate_ota_password(exposed_password)
        self.assertFalse(valid)
        self.assertIn("exposed", msg)

    def test_validate_fallback_password_valid(self):
        """Test validation of valid fallback password"""
        valid_password = "AbC123XyZ789"
        valid, msg = self.validator.validate_fallback_password(valid_password)
        self.assertTrue(valid)
        self.assertIn("valid", msg)

    def test_validate_fallback_password_too_short(self):
        """Test validation of fallback password that's too short"""
        short_password = "short"
        valid, msg = self.validator.validate_fallback_password(short_password)
        self.assertFalse(valid)
        self.assertIn("12 characters", msg)

    def test_validate_fallback_password_invalid_chars(self):
        """Test validation of fallback password with invalid characters"""
        invalid_password = "invalid-password!"
        valid, msg = self.validator.validate_fallback_password(invalid_password)
        self.assertFalse(valid)
        self.assertIn("alphanumeric", msg)

    def test_validate_fallback_password_exposed(self):
        """Test validation detects exposed fallback password"""
        exposed_password = "1SXRpeXi7AdU"  # pragma: allowlist secret
        valid, msg = self.validator.validate_fallback_password(exposed_password)
        self.assertFalse(valid)
        self.assertIn("exposed", msg)


class TestOnePasswordManager(unittest.TestCase):
    """Test 1Password integration functionality"""

    def setUp(self):
        self.op_manager = OnePasswordManager()

    @patch('subprocess.run')
    def test_check_cli_available_success(self, mock_run):
        """Test successful CLI availability check"""
        mock_run.return_value = Mock(returncode=0)

        result = self.op_manager.check_cli_available()

        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ['op', 'account', 'list'],
            check=True, capture_output=True, text=True
        )

    @patch('subprocess.run')
    def test_check_cli_available_failure(self, mock_run):
        """Test CLI availability check failure"""
        mock_run.side_effect = FileNotFoundError()

        result = self.op_manager.check_cli_available()

        self.assertFalse(result)

    @patch('subprocess.run')
    def test_update_esphome_credentials_success(self, mock_run):
        """Test successful credential update"""
        mock_run.return_value = Mock(returncode=0)

        result = self.op_manager.update_esphome_credentials(
            "test_api_key", "test_ota_password", "test_fallback_password"
        )

        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 3)  # Three update calls

    @patch('subprocess.run')
    def test_update_esphome_credentials_failure(self, mock_run):
        """Test credential update failure"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'op')

        result = self.op_manager.update_esphome_credentials(
            "test_api_key", "test_ota_password", "test_fallback_password"
        )

        self.assertFalse(result)

    @patch('subprocess.run')
    def test_verify_credentials_success(self, mock_run):
        """Test successful credential verification"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="api_key: test\nota_password: test\nfallback_password: test"
        )

        result = self.op_manager.verify_credentials()

        self.assertTrue(result)

    @patch('subprocess.run')
    def test_verify_credentials_failure(self, mock_run):
        """Test credential verification failure"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'op')

        result = self.op_manager.verify_credentials()

        self.assertFalse(result)


class TestDeploymentManager(unittest.TestCase):
    """Test deployment management functionality"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        self.deployment = DeploymentManager()

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    def test_backup_secrets_exists(self):
        """Test backing up existing secrets file"""
        # Create a test secrets file
        with open("secrets.yaml", "w") as f:
            f.write("test: content")

        backup_file = self.deployment.backup_secrets()

        self.assertIsNotNone(backup_file)
        self.assertTrue(os.path.exists(backup_file))
        self.assertTrue(backup_file.startswith("secrets.yaml.backup."))

    def test_backup_secrets_not_exists(self):
        """Test backup when secrets file doesn't exist"""
        backup_file = self.deployment.backup_secrets()

        self.assertIsNone(backup_file)

    @patch('subprocess.run')
    def test_create_old_credentials_file_success(self, mock_run):
        """Test successful creation of old credentials file"""
        # Mock 1Password reads
        mock_run.side_effect = [
            Mock(stdout="test_ssid", returncode=0),
            Mock(stdout="test_password", returncode=0),
            Mock(stdout="test_domain", returncode=0)
        ]

        result = self.deployment.create_old_credentials_file()

        self.assertTrue(result)
        self.assertTrue(os.path.exists("secrets.yaml.old"))

        # Check file contents
        with open("secrets.yaml.old", "r") as f:
            content = f.read()
            self.assertIn("test_ssid", content)
            self.assertIn("rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk=", content)  # pragma: allowlist secret

    @patch('subprocess.run')
    def test_create_old_credentials_file_failure(self, mock_run):
        """Test failure in creating old credentials file"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'op')

        result = self.deployment.create_old_credentials_file()

        self.assertFalse(result)

    @patch('subprocess.run')
    def test_generate_new_secrets_success(self, mock_run):
        """Test successful new secrets generation"""
        mock_run.return_value = Mock(returncode=0)

        result = self.deployment.generate_new_secrets()

        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ['./scripts/generate_secrets.sh'],
            check=True, capture_output=True, text=True
        )

    @patch('subprocess.run')
    def test_generate_new_secrets_failure(self, mock_run):
        """Test failure in new secrets generation"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'script')

        result = self.deployment.generate_new_secrets()

        self.assertFalse(result)

    def test_get_device_list(self):
        """Test getting device list from YAML files"""
        # Create test YAML files
        test_files = [
            "device1.yaml",
            "device2.yaml",
            "device3-minimal.yaml",
            "device3-full.yaml",
            "not_yaml.txt"
        ]

        for file in test_files:
            with open(file, "w") as f:
                f.write("test: content")

        devices = self.deployment._get_device_list()

        # Should only include main device files, not minimal/full variants
        expected_devices = ["device1", "device2"]
        self.assertEqual(sorted(devices), sorted(expected_devices))

    def test_cleanup_temporary_files(self):
        """Test cleanup of temporary files"""
        # Create temporary files
        with open("secrets.yaml.old", "w") as f:
            f.write("temp content")

        self.deployment.cleanup_temporary_files()

        self.assertFalse(os.path.exists("secrets.yaml.old"))


class TestSecurityValidator(unittest.TestCase):
    """Test security validation functionality"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        self.security = SecurityValidator()

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    @patch('subprocess.run')
    def test_test_security_hooks_success(self, mock_run):
        """Test successful security hook testing"""
        # Mock security hook returning error (which means it detected the credential)
        mock_run.return_value = Mock(returncode=1)  # Error means detection worked

        result = self.security.test_security_hooks()

        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 3)  # Three test files

    @patch('subprocess.run')
    def test_test_security_hooks_failure(self, mock_run):
        """Test security hook testing failure"""
        # Mock security hook returning success (which means it failed to detect)
        mock_run.return_value = Mock(returncode=0)  # Success means detection failed

        result = self.security.test_security_hooks()

        self.assertFalse(result)

    @patch('subprocess.run')
    def test_scan_for_exposed_credentials_clean(self, mock_run):
        """Test scanning for exposed credentials with clean result"""
        # Mock grep returning no matches (exit code 1)
        mock_run.return_value = Mock(returncode=1)

        result = self.security.scan_for_exposed_credentials()

        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 3)  # Three credentials to check

    @patch('subprocess.run')
    def test_scan_for_exposed_credentials_found(self, mock_run):
        """Test scanning for exposed credentials with findings"""
        # Mock grep returning matches (exit code 0)
        mock_run.return_value = Mock(returncode=0, stdout="file.yaml:exposed_cred")

        result = self.security.scan_for_exposed_credentials()

        self.assertFalse(result)


class TestCredentialRotator(unittest.TestCase):
    """Test the main credential rotator orchestrator"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Create mock components
        self.rotator = CredentialRotator()
        self.rotator.generator = Mock()
        self.rotator.validator = Mock()
        self.rotator.onepassword = Mock()
        self.rotator.deployment = Mock()
        self.rotator.security = Mock()

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    @patch('shutil.which')
    def test_check_prerequisites_success(self, mock_which):
        """Test successful prerequisites check"""
        mock_which.return_value = "/usr/bin/tool"
        self.rotator.onepassword.check_cli_available.return_value = True

        # Create security hook file
        os.makedirs('.githooks', exist_ok=True)
        with open('.githooks/esphome-credential-check.sh', 'w') as f:
            f.write("#!/bin/bash\necho test")

        result = self.rotator.check_prerequisites()

        self.assertTrue(result)

    @patch('shutil.which')
    def test_check_prerequisites_missing_tool(self, mock_which):
        """Test prerequisites check with missing tool"""
        mock_which.return_value = None

        result = self.rotator.check_prerequisites()

        self.assertFalse(result)

    def test_generate_and_validate_credentials_success(self):
        """Test successful credential generation and validation"""
        # Mock generation
        self.rotator.generator.generate_api_key.return_value = "test_api_key="
        self.rotator.generator.generate_ota_password.return_value = "test_ota_password"
        self.rotator.generator.generate_fallback_password.return_value = "test_fallback"

        # Mock validation
        self.rotator.validator.validate_api_key.return_value = (True, "valid")
        self.rotator.validator.validate_ota_password.return_value = (True, "valid")
        self.rotator.validator.validate_fallback_password.return_value = (True, "valid")

        result = self.rotator.generate_and_validate_credentials()

        self.assertTrue(result)
        self.assertIn('api_key', self.rotator.new_credentials)
        self.assertIn('ota_password', self.rotator.new_credentials)
        self.assertIn('fallback_password', self.rotator.new_credentials)

    def test_generate_and_validate_credentials_validation_failure(self):
        """Test credential generation with validation failure"""
        # Mock generation
        self.rotator.generator.generate_api_key.return_value = "invalid_key"
        self.rotator.generator.generate_ota_password.return_value = "invalid_password"
        self.rotator.generator.generate_fallback_password.return_value = "invalid"

        # Mock validation failure
        self.rotator.validator.validate_api_key.return_value = (False, "invalid")

        result = self.rotator.generate_and_validate_credentials()

        self.assertFalse(result)

    def test_update_1password_success(self):
        """Test successful 1Password update"""
        self.rotator.new_credentials = {
            'api_key': 'test_api',
            'ota_password': 'test_ota',
            'fallback_password': 'test_fallback'
        }

        self.rotator.onepassword.update_esphome_credentials.return_value = True
        self.rotator.onepassword.verify_credentials.return_value = True

        result = self.rotator.update_1password()

        self.assertTrue(result)
        self.rotator.onepassword.update_esphome_credentials.assert_called_once()
        self.rotator.onepassword.verify_credentials.assert_called_once()

    def test_update_1password_failure(self):
        """Test 1Password update failure"""
        self.rotator.new_credentials = {
            'api_key': 'test_api',
            'ota_password': 'test_ota',
            'fallback_password': 'test_fallback'
        }

        self.rotator.onepassword.update_esphome_credentials.return_value = False

        result = self.rotator.update_1password()

        self.assertFalse(result)

    @patch('shutil.copy2')
    def test_execute_two_stage_deployment_success(self, mock_copy):
        """Test successful two-stage deployment"""
        self.rotator.deployment.backup_secrets.return_value = "backup_file"
        self.rotator.deployment.create_old_credentials_file.return_value = True
        self.rotator.deployment.run_security_validation.return_value = True
        self.rotator.deployment.deploy_two_stage.return_value = True
        self.rotator.deployment.generate_new_secrets.return_value = True

        result = self.rotator.execute_two_stage_deployment()

        self.assertTrue(result)
        # Verify the sequence of calls
        self.rotator.deployment.backup_secrets.assert_called_once()
        self.rotator.deployment.create_old_credentials_file.assert_called_once()
        self.assertEqual(self.rotator.deployment.deploy_two_stage.call_count, 2)

    @patch('shutil.copy2')
    def test_execute_two_stage_deployment_stage1_failure(self, mock_copy):
        """Test two-stage deployment with Stage 1 failure"""
        self.rotator.deployment.backup_secrets.return_value = "backup_file"
        self.rotator.deployment.create_old_credentials_file.return_value = True
        self.rotator.deployment.run_security_validation.return_value = True
        self.rotator.deployment.deploy_two_stage.return_value = False  # Stage 1 fails

        result = self.rotator.execute_two_stage_deployment()

        self.assertFalse(result)

    def test_verify_rotation_success(self):
        """Test successful rotation verification"""
        self.rotator.deployment.test_device_connectivity.return_value = {
            'device1': True,
            'device2': True,
            'device3': False
        }
        self.rotator.security.test_security_hooks.return_value = True
        self.rotator.security.scan_for_exposed_credentials.return_value = True

        result = self.rotator.verify_rotation()

        self.assertTrue(result)

    def test_verify_rotation_security_failure(self):
        """Test rotation verification with security failure"""
        self.rotator.deployment.test_device_connectivity.return_value = {'device1': True}
        self.rotator.security.test_security_hooks.return_value = False

        result = self.rotator.verify_rotation()

        self.assertFalse(result)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete rotation process"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    def test_credential_generation_and_validation_integration(self):
        """Test that generated credentials pass validation"""
        generator = CredentialGenerator()
        validator = CredentialValidator()

        # Generate credentials
        api_key = generator.generate_api_key()
        ota_password = generator.generate_ota_password()
        fallback_password = generator.generate_fallback_password()

        # Validate them
        api_valid, api_msg = validator.validate_api_key(api_key)
        ota_valid, ota_msg = validator.validate_ota_password(ota_password)
        fallback_valid, fallback_msg = validator.validate_fallback_password(fallback_password)

        self.assertTrue(api_valid, f"API key validation failed: {api_msg}")
        self.assertTrue(ota_valid, f"OTA password validation failed: {ota_msg}")
        self.assertTrue(fallback_valid, f"Fallback password validation failed: {fallback_msg}")

    def test_exposed_credential_detection(self):
        """Test that all exposed credentials are properly detected"""
        validator = CredentialValidator()

        # Test all exposed credentials are detected
        exposed_api = "rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk="  # pragma: allowlist secret
        exposed_ota = "5929ccc1f08289c79aca50ebe0a9b7eb"  # pragma: allowlist secret
        exposed_fallback = "1SXRpeXi7AdU"  # pragma: allowlist secret

        api_valid, api_msg = validator.validate_api_key(exposed_api)
        ota_valid, ota_msg = validator.validate_ota_password(exposed_ota)
        fallback_valid, fallback_msg = validator.validate_fallback_password(exposed_fallback)

        self.assertFalse(api_valid, "Exposed API key should be detected")
        self.assertFalse(ota_valid, "Exposed OTA password should be detected")
        self.assertFalse(fallback_valid, "Exposed fallback password should be detected")

        self.assertIn("exposed", api_msg.lower())
        self.assertIn("exposed", ota_msg.lower())
        self.assertIn("exposed", fallback_msg.lower())


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestCredentialGenerator,
        TestCredentialValidator,
        TestOnePasswordManager,
        TestDeploymentManager,
        TestSecurityValidator,
        TestCredentialRotator,
        TestIntegration
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
