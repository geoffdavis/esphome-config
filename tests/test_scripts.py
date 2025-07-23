#!/usr/bin/env python3
"""
Unit tests for individual ESPHome security scripts

Tests the main functionality of each security script including:
- validate_secrets.py
- validate_1password_structure.py
- setup_security.py
- track_secret_rotation.py
- setup_dev_secrets.py
- backup_secrets.py
- rotate_credentials.py
"""

import unittest
import tempfile
import shutil
import os
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch, call

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Import the script modules
import validate_secrets
import validate_1password_structure
import setup_dev_secrets
import backup_secrets
import track_secret_rotation


class TestValidateSecrets(unittest.TestCase):
    """Test validate_secrets.py functionality"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Create a test secrets file
        self.secrets_content = """
wifi_ssid: "TestNetwork"
wifi_password: "testpassword123"
wifi_domain: "example.com"
api_key: "dGVzdF9hcGlfa2V5XzEyMzQ1Njc4OTBhYmNkZWY="
ota_password: "1234567890abcdef1234567890abcdef"
fallback_password: "testpassword"
"""
        with open("secrets.yaml", "w") as f:
            f.write(self.secrets_content)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_secrets_validator_creation(self):
        """Test SecretsValidator can be created"""
        validator = validate_secrets.SecretsValidator()
        self.assertIsNotNone(validator)
        self.assertIsNotNone(validator.logger)
        self.assertIsNotNone(validator.validator)
        self.assertFalse(validator.transition_mode)

    def test_secrets_validator_transition_mode(self):
        """Test SecretsValidator can be created with transition mode"""
        validator = validate_secrets.SecretsValidator(transition_mode=True)
        self.assertIsNotNone(validator)
        self.assertTrue(validator.transition_mode)

    @patch('validate_secrets.OnePasswordManager')
    def test_validate_secrets_file_success(self, mock_op_manager):
        """Test successful secrets file validation"""
        validator = validate_secrets.SecretsValidator()

        # Mock 1Password manager to avoid actual CLI calls
        mock_op_manager.return_value.check_cli_available.return_value = False

        # This should pass basic format validation
        result = validator.check_secrets_file()
        # We expect this to pass basic validation even without 1Password
        self.assertTrue(result)

    def test_transition_mode_with_old_credentials(self):
        """Test transition mode allows old credentials"""
        # Create secrets file with old (exposed) credentials
        old_secrets_content = """
wifi_ssid: "TestNetwork"
wifi_password: "testpassword123"
wifi_domain: "example.com"
api_key: "rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk="
ota_password: "5929ccc1f08289c79aca50ebe0a9b7eb"
fallback_password: "1SXRpeXi7AdU"
"""
        with open("secrets.yaml", "w") as f:
            f.write(old_secrets_content)

        # Test normal mode - should fail with exposed credentials
        validator_normal = validate_secrets.SecretsValidator(transition_mode=False)
        result_normal = validator_normal.validate_credential_formats()
        self.assertFalse(result_normal)  # Should fail due to exposed credentials

        # Test transition mode - should pass with warnings
        validator_transition = validate_secrets.SecretsValidator(transition_mode=True)
        result_transition = validator_transition.validate_credential_formats()
        self.assertTrue(result_transition)  # Should pass in transition mode

    @patch('validate_secrets.OnePasswordManager')
    def test_transition_mode_file_scanning(self, mock_op_manager):
        """Test transition mode handles file scanning correctly"""
        # Mock 1Password manager
        mock_op_manager.return_value.check_cli_available.return_value = False

        # Create a Taskfile.yml with old credentials (simulating our fix)
        taskfile_content = """
version: '3'
tasks:
  security-validate:
    cmds:
      - |
        if grep -q "5929ccc1f08289c79aca50ebe0a9b7eb" secrets.yaml; then
          echo "transition mode"
        fi
"""
        with open("Taskfile.yml", "w") as f:
            f.write(taskfile_content)

        # Test normal mode - should detect exposed credential
        validator_normal = validate_secrets.SecretsValidator(transition_mode=False)
        result_normal = validator_normal.scan_for_exposed_credentials()
        self.assertFalse(result_normal)  # Should fail due to exposed credential in Taskfile

        # Test transition mode - should allow it
        validator_transition = validate_secrets.SecretsValidator(transition_mode=True)
        result_transition = validator_transition.scan_for_exposed_credentials()
        self.assertTrue(result_transition)  # Should pass in transition mode


class TestValidate1PasswordStructure(unittest.TestCase):
    """Test validate_1password_structure.py functionality"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_onepassword_validator_creation(self):
        """Test OnePasswordValidator can be created"""
        validator = validate_1password_structure.OnePasswordValidator()
        self.assertIsNotNone(validator)
        self.assertIsNotNone(validator.logger)
        self.assertIsNotNone(validator.validator)

    @patch('validate_1password_structure.OnePasswordManager')
    def test_check_cli_availability(self, mock_op_manager):
        """Test 1Password CLI availability check"""
        validator = validate_1password_structure.OnePasswordValidator()

        # Mock CLI not available
        mock_op_manager.return_value.check_cli_available.return_value = False

        result = validator.check_cli_availability()
        self.assertFalse(result)


class TestSetupDevSecrets(unittest.TestCase):
    """Test setup_dev_secrets.py functionality"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_dev_secrets_setup_creation(self):
        """Test DevSecretsSetup can be created"""
        setup = setup_dev_secrets.DevSecretsSetup()
        self.assertIsNotNone(setup)
        self.assertIsNotNone(setup.logger)
        self.assertIsNotNone(setup.validator)

    def test_generate_development_credentials(self):
        """Test development credentials generation"""
        setup = setup_dev_secrets.DevSecretsSetup()

        dev_creds = setup.generate_development_credentials()
        self.assertIsNotNone(dev_creds)
        self.assertIn('wifi_ssid', dev_creds)
        self.assertIn('api_key', dev_creds)
        self.assertIn('ota_password', dev_creds)
        self.assertIn('fallback_password', dev_creds)

    def test_generate_test_credentials(self):
        """Test test credentials generation"""
        setup = setup_dev_secrets.DevSecretsSetup()

        test_creds = setup.generate_test_credentials()
        self.assertIsNotNone(test_creds)
        self.assertIn('wifi_ssid', test_creds)
        self.assertIn('api_key', test_creds)
        self.assertIn('ota_password', test_creds)
        self.assertIn('fallback_password', test_creds)

    def test_create_development_secrets_file(self):
        """Test development secrets file creation"""
        setup = setup_dev_secrets.DevSecretsSetup()

        success = setup.create_development_secrets_file()
        self.assertTrue(success)

        # Check file was created
        self.assertTrue(os.path.exists(setup.dev_secrets_file))

        # Check file content
        with open(setup.dev_secrets_file, 'r') as f:
            content = f.read()
        self.assertIn('wifi_ssid', content)
        self.assertIn('api_key', content)


class TestBackupSecrets(unittest.TestCase):
    """Test backup_secrets.py functionality"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Create test files to backup
        with open("secrets.yaml", "w") as f:
            f.write("test_secret: value")
        with open("test.yaml", "w") as f:
            f.write("test: config")

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_secrets_backup_creation(self):
        """Test SecretsBackup can be created"""
        backup = backup_secrets.SecretsBackup()
        self.assertIsNotNone(backup)
        self.assertIsNotNone(backup.logger)

    def test_ensure_backup_directory(self):
        """Test backup directory creation"""
        backup = backup_secrets.SecretsBackup()

        success = backup.ensure_backup_directory()
        self.assertTrue(success)
        self.assertTrue(backup.backup_dir.exists())
        self.assertTrue((backup.backup_dir / ".gitignore").exists())
        self.assertTrue((backup.backup_dir / "README.md").exists())

    def test_get_files_to_backup(self):
        """Test getting list of files to backup"""
        backup = backup_secrets.SecretsBackup()

        files = backup.get_files_to_backup()
        self.assertIsInstance(files, list)
        self.assertGreater(len(files), 0)

        # Check that secrets.yaml is included
        secrets_found = any(f['path'] == 'secrets.yaml' for f in files)
        self.assertTrue(secrets_found)

    def test_create_backup(self):
        """Test backup creation"""
        backup = backup_secrets.SecretsBackup()

        backup_id = backup.create_backup("test")
        self.assertIsNotNone(backup_id)
        self.assertTrue(backup_id.startswith("backup_test_"))

        # Check backup directory was created
        backup_path = backup.backup_dir / backup_id
        self.assertTrue(backup_path.exists())

        # Check manifest was created
        manifest_path = backup.backup_dir / f"{backup_id}_manifest.json"
        self.assertTrue(manifest_path.exists())

    def test_list_backups(self):
        """Test listing backups"""
        backup = backup_secrets.SecretsBackup()

        # Create a backup first
        backup_id = backup.create_backup("test")
        self.assertIsNotNone(backup_id)

        # List backups
        backups = backup.list_backups()
        self.assertIsInstance(backups, list)
        self.assertGreater(len(backups), 0)

        # Check our backup is in the list
        backup_found = any(b['backup_id'] == backup_id for b in backups)
        self.assertTrue(backup_found)


class TestTrackSecretRotation(unittest.TestCase):
    """Test track_secret_rotation.py functionality"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_rotation_tracker_creation(self):
        """Test RotationTracker can be created"""
        tracker = track_secret_rotation.RotationTracker()
        self.assertIsNotNone(tracker)
        self.assertIsNotNone(tracker.logger)
        self.assertIsNotNone(tracker.validator)

    def test_load_rotation_history_empty(self):
        """Test loading empty rotation history"""
        tracker = track_secret_rotation.RotationTracker()

        history = tracker.load_rotation_history()
        self.assertIsInstance(history, list)
        self.assertEqual(len(history), 0)

    def test_add_rotation_entry(self):
        """Test adding rotation entry"""
        tracker = track_secret_rotation.RotationTracker()

        success = tracker.add_rotation_entry(
            "manual",
            "test rotation",
            ["api_key", "ota_password"],
            "manual",
            "test notes"
        )
        self.assertTrue(success)

        # Check history was updated
        history = tracker.load_rotation_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['rotation_type'], 'manual')
        self.assertEqual(history[0]['reason'], 'test rotation')

    def test_get_rotation_statistics(self):
        """Test getting rotation statistics"""
        tracker = track_secret_rotation.RotationTracker()

        # Add a test entry
        tracker.add_rotation_entry(
            "manual",
            "test rotation",
            ["api_key"],
            "manual",
            "test"
        )

        stats = tracker.get_rotation_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_rotations', stats)
        self.assertIn('last_rotation', stats)
        self.assertEqual(stats['total_rotations'], 1)

    def test_generate_markdown_report(self):
        """Test markdown report generation"""
        tracker = track_secret_rotation.RotationTracker()

        # Add a test entry
        tracker.add_rotation_entry(
            "manual",
            "test rotation",
            ["api_key"],
            "manual",
            "test"
        )

        success = tracker.generate_markdown_report()
        self.assertTrue(success)

        # Check report file was created
        self.assertTrue(os.path.exists(tracker.markdown_log_file))

        # Check report content
        with open(tracker.markdown_log_file, 'r') as f:
            content = f.read()
        self.assertIn('Secret Rotation Report', content)
        self.assertIn('test rotation', content)


class TestScriptIntegration(unittest.TestCase):
    """Integration tests for script interactions"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_dev_secrets_and_validation_workflow(self):
        """Test development secrets creation and validation workflow"""
        # Create development secrets
        setup = setup_dev_secrets.DevSecretsSetup()
        success = setup.create_development_secrets_file()
        self.assertTrue(success)

        # Validate the created secrets
        validator = validate_secrets.SecretsValidator()
        # This should work with the development secrets
        result = validator.validate_secrets_file()
        self.assertIsNotNone(result)

    def test_backup_and_restore_workflow(self):
        """Test backup and restore workflow"""
        # Create a test secrets file
        with open("secrets.yaml", "w") as f:
            f.write("test_secret: original_value")

        # Create backup
        backup = backup_secrets.SecretsBackup()
        backup_id = backup.create_backup("test")
        self.assertIsNotNone(backup_id)

        # Modify original file
        with open("secrets.yaml", "w") as f:
            f.write("test_secret: modified_value")

        # Restore from backup
        success = backup.restore_backup(backup_id, force=True)
        self.assertTrue(success)

        # Check file was restored
        with open("secrets.yaml", "r") as f:
            content = f.read()
        self.assertIn("original_value", content)

    def test_rotation_tracking_workflow(self):
        """Test rotation tracking workflow"""
        tracker = track_secret_rotation.RotationTracker()

        # Add multiple rotation entries
        tracker.add_rotation_entry("scheduled", "Regular rotation", ["api_key"], "automated", "")
        tracker.add_rotation_entry("emergency", "Security incident", ["api_key", "ota_password"], "manual", "Urgent")

        # Get statistics
        stats = tracker.get_rotation_statistics()
        self.assertEqual(stats['total_rotations'], 2)

        # Generate report
        success = tracker.generate_markdown_report()
        self.assertTrue(success)

        # Check report contains both entries
        with open(tracker.markdown_log_file, 'r') as f:
            content = f.read()
        self.assertIn("Regular rotation", content)
        self.assertIn("Security incident", content)


if __name__ == '__main__':
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestValidateSecrets,
        TestValidate1PasswordStructure,
        TestSetupDevSecrets,
        TestBackupSecrets,
        TestTrackSecretRotation,
        TestScriptIntegration
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
