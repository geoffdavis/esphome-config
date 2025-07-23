#!/usr/bin/env python3
"""
Unit tests for the ESPHome Security Library

Tests all components of the shared security library including:
- SecurityLogger
- CredentialGenerator
- CredentialValidator
- OnePasswordManager
- SecureFileHandler
- SecurityScanner
"""

import unittest
import tempfile
import shutil
import os
import sys
import json
import base64
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from security_lib import (
    SecurityLogger,
    SecurityConfig,
    CredentialGenerator,
    CredentialValidator,
    OnePasswordManager,
    SecureFileHandler,
    SecurityScanner,
    load_env_file
)


class TestSecurityConfig(unittest.TestCase):
    """Test SecurityConfig constants and configuration"""

    def test_exposed_credentials_exist(self):
        """Test that exposed credentials are defined"""
        self.assertIn('api_key', SecurityConfig.EXPOSED_CREDENTIALS)
        self.assertIn('ota_password', SecurityConfig.EXPOSED_CREDENTIALS)
        self.assertIn('fallback_password', SecurityConfig.EXPOSED_CREDENTIALS)

    def test_patterns_defined(self):
        """Test that validation patterns are defined"""
        self.assertTrue(hasattr(SecurityConfig, 'API_KEY_PATTERN'))
        self.assertTrue(hasattr(SecurityConfig, 'OTA_PASSWORD_PATTERN'))
        self.assertTrue(hasattr(SecurityConfig, 'FALLBACK_PASSWORD_PATTERN'))

    def test_vault_names_defined(self):
        """Test that vault names are defined"""
        self.assertTrue(hasattr(SecurityConfig, 'AUTOMATION_VAULT'))
        self.assertTrue(hasattr(SecurityConfig, 'SHARED_VAULT'))
        self.assertTrue(hasattr(SecurityConfig, 'ESPHOME_ITEM'))
        self.assertTrue(hasattr(SecurityConfig, 'HOME_IOT_ITEM'))


class TestSecurityLogger(unittest.TestCase):
    """Test SecurityLogger functionality"""

    def setUp(self):
        self.logger = SecurityLogger("test")

    @patch('builtins.print')
    def test_info_logging(self, mock_print):
        """Test info level logging"""
        self.logger.info("Test message")
        mock_print.assert_called_once()
        args = mock_print.call_args[0][0]
        self.assertIn("[INFO]", args)
        self.assertIn("Test message", args)

    @patch('builtins.print')
    def test_error_logging(self, mock_print):
        """Test error level logging"""
        self.logger.error("Error message")
        mock_print.assert_called_once()
        args = mock_print.call_args[0][0]
        self.assertIn("[ERROR]", args)
        self.assertIn("Error message", args)

    @patch('builtins.print')
    def test_success_logging(self, mock_print):
        """Test success level logging"""
        self.logger.success("Success message")
        mock_print.assert_called_once()
        args = mock_print.call_args[0][0]
        self.assertIn("[SUCCESS]", args)
        self.assertIn("Success message", args)

    @patch('builtins.print')
    def test_warning_logging(self, mock_print):
        """Test warning level logging"""
        self.logger.warning("Warning message")
        mock_print.assert_called_once()
        args = mock_print.call_args[0][0]
        self.assertIn("[WARNING]", args)
        self.assertIn("Warning message", args)

    @patch('builtins.print')
    def test_step_logging(self, mock_print):
        """Test step level logging"""
        self.logger.step("Step message")
        # Step logging calls print multiple times (header, message, footer)
        self.assertTrue(mock_print.called)
        # Check that the step message appears in one of the calls
        calls = [str(call) for call in mock_print.call_args_list]
        step_found = any("Step message" in call for call in calls)
        self.assertTrue(step_found)


class TestCredentialGenerator(unittest.TestCase):
    """Test CredentialGenerator functionality"""

    def setUp(self):
        self.generator = CredentialGenerator()

    def test_generate_api_key(self):
        """Test API key generation"""
        api_key = self.generator.generate_api_key()

        # Check length (44 characters for base64 encoded 32 bytes)
        self.assertEqual(len(api_key), 44)

        # Check it's valid base64
        try:
            decoded = base64.b64decode(api_key)
            self.assertEqual(len(decoded), 32)
        except Exception:
            self.fail("Generated API key is not valid base64")

        # Check it ends with =
        self.assertTrue(api_key.endswith('='))

    def test_generate_ota_password(self):
        """Test OTA password generation"""
        ota_password = self.generator.generate_ota_password()

        # Check length (32 characters)
        self.assertEqual(len(ota_password), 32)

        # Check it's hexadecimal
        try:
            int(ota_password, 16)
        except ValueError:
            self.fail("Generated OTA password is not valid hexadecimal")

    def test_generate_fallback_password(self):
        """Test fallback password generation"""
        fallback_password = self.generator.generate_fallback_password()

        # Check minimum length (12 characters)
        self.assertGreaterEqual(len(fallback_password), 12)

        # Check it's alphanumeric
        self.assertTrue(fallback_password.isalnum())

    def test_credentials_are_unique(self):
        """Test that generated credentials are unique"""
        api_keys = [self.generator.generate_api_key() for _ in range(10)]
        ota_passwords = [self.generator.generate_ota_password() for _ in range(10)]
        fallback_passwords = [self.generator.generate_fallback_password() for _ in range(10)]

        # Check uniqueness
        self.assertEqual(len(set(api_keys)), 10)
        self.assertEqual(len(set(ota_passwords)), 10)
        self.assertEqual(len(set(fallback_passwords)), 10)


class TestCredentialValidator(unittest.TestCase):
    """Test CredentialValidator functionality"""

    def setUp(self):
        self.validator = CredentialValidator()

    def test_validate_api_key_valid(self):
        """Test API key validation with valid key"""
        # Generate a valid API key
        generator = CredentialGenerator()
        api_key = generator.generate_api_key()

        valid, msg = self.validator.validate_api_key(api_key)
        self.assertTrue(valid)
        self.assertIn("valid", msg.lower())

    def test_validate_api_key_exposed(self):
        """Test API key validation with exposed credential"""
        exposed_key = SecurityConfig.EXPOSED_CREDENTIALS['api_key']

        valid, msg = self.validator.validate_api_key(exposed_key)
        self.assertFalse(valid)
        self.assertIn("exposed", msg.lower())

    def test_validate_api_key_invalid_length(self):
        """Test API key validation with invalid length"""
        invalid_key = "short"

        valid, msg = self.validator.validate_api_key(invalid_key)
        self.assertFalse(valid)
        self.assertIn("44 characters", msg)

    def test_validate_ota_password_valid(self):
        """Test OTA password validation with valid password"""
        generator = CredentialGenerator()
        ota_password = generator.generate_ota_password()

        valid, msg = self.validator.validate_ota_password(ota_password)
        self.assertTrue(valid)
        self.assertIn("valid", msg.lower())

    def test_validate_ota_password_exposed(self):
        """Test OTA password validation with exposed credential"""
        exposed_password = SecurityConfig.EXPOSED_CREDENTIALS['ota_password']

        valid, msg = self.validator.validate_ota_password(exposed_password)
        self.assertFalse(valid)
        self.assertIn("exposed", msg.lower())

    def test_validate_ota_password_invalid_length(self):
        """Test OTA password validation with invalid length"""
        invalid_password = "short"

        valid, msg = self.validator.validate_ota_password(invalid_password)
        self.assertFalse(valid)
        self.assertIn("32", msg)

    def test_validate_fallback_password_valid(self):
        """Test fallback password validation with valid password"""
        generator = CredentialGenerator()
        fallback_password = generator.generate_fallback_password()

        valid, msg = self.validator.validate_fallback_password(fallback_password)
        self.assertTrue(valid)
        self.assertIn("valid", msg.lower())

    def test_validate_fallback_password_exposed(self):
        """Test fallback password validation with exposed credential"""
        exposed_password = SecurityConfig.EXPOSED_CREDENTIALS['fallback_password']

        valid, msg = self.validator.validate_fallback_password(exposed_password)
        self.assertFalse(valid)
        self.assertIn("exposed", msg.lower())

    def test_validate_fallback_password_too_short(self):
        """Test fallback password validation with too short password"""
        short_password = "short"

        valid, msg = self.validator.validate_fallback_password(short_password)
        self.assertFalse(valid)
        self.assertIn("12 characters", msg)

    def test_validate_wifi_credentials(self):
        """Test WiFi credentials validation"""
        # Valid credentials
        valid, errors = self.validator.validate_wifi_credentials(
            "TestNetwork", "validpassword123", "example.com"
        )
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

        # Invalid SSID (too long)
        valid, errors = self.validator.validate_wifi_credentials(
            "A" * 33, "validpassword123", "example.com"
        )
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

        # Invalid password (too short)
        valid, errors = self.validator.validate_wifi_credentials(
            "TestNetwork", "short", "example.com"
        )
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)


class TestSecureFileHandler(unittest.TestCase):
    """Test SecureFileHandler functionality"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.handler = SecureFileHandler()
        self.test_file = os.path.join(self.temp_dir, "test.yaml")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_backup_file(self):
        """Test file backup functionality"""
        # Create a test file
        with open(self.test_file, 'w') as f:
            f.write("test content")

        # Backup the file
        backup_path = self.handler.backup_file(self.test_file)

        # Check backup was created
        self.assertIsNotNone(backup_path)
        self.assertTrue(os.path.exists(backup_path))

        # Check backup content
        with open(backup_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, "test content")

    def test_read_secrets_file(self):
        """Test reading secrets file"""
        # Create a test secrets file
        secrets_content = """
wifi_ssid: "TestNetwork"
wifi_password: "testpassword"
api_key: "testkey"
"""
        with open(self.test_file, 'w') as f:
            f.write(secrets_content)

        # Read the secrets
        secrets = self.handler.read_secrets_file(self.test_file)

        self.assertIsNotNone(secrets)
        self.assertEqual(secrets['wifi_ssid'], 'TestNetwork')
        self.assertEqual(secrets['wifi_password'], 'testpassword')
        self.assertEqual(secrets['api_key'], 'testkey')

    def test_write_secrets_file(self):
        """Test writing secrets file"""
        secrets = {
            'wifi_ssid': 'TestNetwork',
            'wifi_password': 'testpassword',
            'api_key': 'testkey'
        }

        # Write the secrets
        success = self.handler.write_secrets_file(secrets, self.test_file)
        self.assertTrue(success)

        # Verify the file was created
        self.assertTrue(os.path.exists(self.test_file))

        # Read back and verify content
        read_secrets = self.handler.read_secrets_file(self.test_file)
        self.assertEqual(read_secrets['wifi_ssid'], 'TestNetwork')
        self.assertEqual(read_secrets['wifi_password'], 'testpassword')
        self.assertEqual(read_secrets['api_key'], 'testkey')


class TestSecurityScanner(unittest.TestCase):
    """Test SecurityScanner functionality"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.scanner = SecurityScanner()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_scan_for_exposed_credentials(self):
        """Test scanning for exposed credentials"""
        # Create a file with exposed credentials
        test_file = os.path.join(self.temp_dir, "test.yaml")
        with open(test_file, 'w') as f:
            f.write(f"api_key: \"{SecurityConfig.EXPOSED_CREDENTIALS['api_key']}\"")

        # Scan for exposed credentials
        issues = self.scanner.scan_for_exposed_credentials(self.temp_dir)

        # Should find the exposed credential
        self.assertGreater(len(issues), 0)
        # Check for either "api key" or "api_key" in the issue message
        self.assertTrue(any("api" in issue.lower() for issue in issues))

    def test_scan_clean_files(self):
        """Test scanning files without exposed credentials"""
        # Create a file with clean credentials
        test_file = os.path.join(self.temp_dir, "test.yaml")
        with open(test_file, 'w') as f:
            f.write("api_key: \"clean_api_key_here\"")

        # Scan for exposed credentials
        issues = self.scanner.scan_for_exposed_credentials(self.temp_dir)

        # Should not find any issues
        self.assertEqual(len(issues), 0)


class TestOnePasswordManager(unittest.TestCase):
    """Test OnePasswordManager functionality"""

    def setUp(self):
        # Mock the environment variable
        self.env_patcher = patch.dict(os.environ, {'OP_ACCOUNT': 'test-account'})
        self.env_patcher.start()
        self.op_manager = OnePasswordManager()

    def tearDown(self):
        self.env_patcher.stop()

    @patch('subprocess.run')
    def test_check_cli_available_success(self, mock_run):
        """Test 1Password CLI availability check - success"""
        mock_run.return_value = Mock(returncode=0)

        result = self.op_manager.check_cli_available()
        self.assertTrue(result)

    @patch('subprocess.run')
    def test_check_cli_available_failure(self, mock_run):
        """Test 1Password CLI availability check - failure"""
        mock_run.side_effect = FileNotFoundError()

        result = self.op_manager.check_cli_available()
        self.assertFalse(result)

    @patch('subprocess.run')
    def test_get_item_field_success(self, mock_run):
        """Test getting item field - success"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="test_value"
        )

        result = self.op_manager.get_item_field("vault", "item", "field")
        self.assertEqual(result, "test_value")

    @patch('subprocess.run')
    def test_get_item_field_failure(self, mock_run):
        """Test getting item field - failure"""
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(1, ['op'], "Command failed")

        result = self.op_manager.get_item_field("vault", "item", "field")
        self.assertIsNone(result)


class TestLoadEnvFile(unittest.TestCase):
    """Test environment file loading"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.env_file = os.path.join(self.temp_dir, ".env")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_env_file_success(self):
        """Test loading environment file successfully"""
        # Create a test .env file
        with open(self.env_file, 'w') as f:
            f.write("TEST_VAR=test_value\n")
            f.write("ANOTHER_VAR=another_value\n")

        # Change to temp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)

            # Clear any existing env vars
            if 'TEST_VAR' in os.environ:
                del os.environ['TEST_VAR']
            if 'ANOTHER_VAR' in os.environ:
                del os.environ['ANOTHER_VAR']

            # Load the env file
            load_env_file()

            # Check variables were loaded
            self.assertEqual(os.environ.get('TEST_VAR'), 'test_value')
            self.assertEqual(os.environ.get('ANOTHER_VAR'), 'another_value')
        finally:
            os.chdir(original_cwd)

    def test_load_env_file_not_found(self):
        """Test loading non-existent environment file"""
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            # Should not raise an exception
            load_env_file()
        finally:
            os.chdir(original_cwd)


class TestIntegration(unittest.TestCase):
    """Integration tests for the security framework"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.generator = CredentialGenerator()
        self.validator = CredentialValidator()
        self.handler = SecureFileHandler()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_and_validate_workflow(self):
        """Test the complete generate and validate workflow"""
        # Generate credentials
        api_key = self.generator.generate_api_key()
        ota_password = self.generator.generate_ota_password()
        fallback_password = self.generator.generate_fallback_password()

        # Validate all credentials
        api_valid, api_msg = self.validator.validate_api_key(api_key)
        ota_valid, ota_msg = self.validator.validate_ota_password(ota_password)
        fallback_valid, fallback_msg = self.validator.validate_fallback_password(fallback_password)

        # All should be valid
        self.assertTrue(api_valid, f"API key validation failed: {api_msg}")
        self.assertTrue(ota_valid, f"OTA password validation failed: {ota_msg}")
        self.assertTrue(fallback_valid, f"Fallback password validation failed: {fallback_msg}")

    def test_secrets_file_workflow(self):
        """Test the complete secrets file workflow"""
        # Generate credentials
        secrets = {
            'wifi_ssid': 'TestNetwork',
            'wifi_password': 'testpassword123',
            'wifi_domain': 'example.com',
            'api_key': self.generator.generate_api_key(),
            'ota_password': self.generator.generate_ota_password(),
            'fallback_password': self.generator.generate_fallback_password()
        }

        # Write secrets file
        secrets_file = os.path.join(self.temp_dir, "secrets.yaml")
        success = self.handler.write_secrets_file(secrets, secrets_file)
        self.assertTrue(success)

        # Read secrets file back
        read_secrets = self.handler.read_secrets_file(secrets_file)
        self.assertIsNotNone(read_secrets)

        # Validate all credentials from file
        for key in ['api_key', 'ota_password', 'fallback_password']:
            self.assertEqual(secrets[key], read_secrets[key])

        # Validate credentials
        api_valid, _ = self.validator.validate_api_key(read_secrets['api_key'])
        ota_valid, _ = self.validator.validate_ota_password(read_secrets['ota_password'])
        fallback_valid, _ = self.validator.validate_fallback_password(read_secrets['fallback_password'])

        self.assertTrue(api_valid)
        self.assertTrue(ota_valid)
        self.assertTrue(fallback_valid)


if __name__ == '__main__':
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestSecurityConfig,
        TestSecurityLogger,
        TestCredentialGenerator,
        TestCredentialValidator,
        TestSecureFileHandler,
        TestSecurityScanner,
        TestOnePasswordManager,
        TestLoadEnvFile,
        TestIntegration
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
