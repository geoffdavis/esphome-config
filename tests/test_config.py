#!/usr/bin/env python3
"""
Test configuration and utilities for ESPHome Security Framework tests

Provides common test fixtures, mock data, and utility functions
used across multiple test modules.
"""

import tempfile
import shutil
import os
from pathlib import Path
from typing import Dict, Any


class TestConfig:
    """Configuration constants for tests"""

    # Test credentials (safe for testing)
    TEST_CREDENTIALS = {
        'wifi_ssid': 'TestNetwork',
        'wifi_password': 'testpassword123',
        'wifi_domain': 'test.example.com',
        'api_key': 'dGVzdF9hcGlfa2V5XzEyMzQ1Njc4OTBhYmNkZWY=',  # test_api_key_1234567890abcdef
        'ota_password': '1234567890abcdef1234567890abcdef',
        'fallback_password': 'testpassword'
    }

    # Invalid test credentials
    INVALID_CREDENTIALS = {
        'api_key_short': 'short',
        'api_key_invalid': 'not-base64!@#',
        'ota_password_short': 'short',
        'ota_password_invalid': 'not-hex-ZZZZ',
        'fallback_password_short': 'short',
        'fallback_password_invalid': 'invalid-chars!@#'
    }

    # Test file contents
    TEST_SECRETS_YAML = """
# Test secrets file
wifi_ssid: "TestNetwork"
wifi_password: "testpassword123"
wifi_domain: "test.example.com"
api_key: "dGVzdF9hcGlfa2V5XzEyMzQ1Njc4OTBhYmNkZWY="
ota_password: "1234567890abcdef1234567890abcdef"
fallback_password: "testpassword"
"""

    TEST_ENV_FILE = """
# Test environment file
OP_ACCOUNT=test-account
TEST_VAR=test_value
"""

    TEST_GITIGNORE = """
# Test .gitignore
secrets.yaml
.env
*.backup
"""


class TestFixtures:
    """Common test fixtures and utilities"""

    @staticmethod
    def create_temp_directory() -> str:
        """Create a temporary directory for testing"""
        return tempfile.mkdtemp()

    @staticmethod
    def cleanup_temp_directory(temp_dir: str):
        """Clean up a temporary directory"""
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

    @staticmethod
    def create_test_secrets_file(temp_dir: str, content: str = None) -> str:
        """Create a test secrets.yaml file"""
        content = content or TestConfig.TEST_SECRETS_YAML
        secrets_file = os.path.join(temp_dir, "secrets.yaml")
        with open(secrets_file, 'w') as f:
            f.write(content)
        return secrets_file

    @staticmethod
    def create_test_env_file(temp_dir: str, content: str = None) -> str:
        """Create a test .env file"""
        content = content or TestConfig.TEST_ENV_FILE
        env_file = os.path.join(temp_dir, ".env")
        with open(env_file, 'w') as f:
            f.write(content)
        return env_file

    @staticmethod
    def create_test_config_files(temp_dir: str) -> Dict[str, str]:
        """Create a set of test configuration files"""
        files = {}

        # Create secrets.yaml
        files['secrets'] = TestFixtures.create_test_secrets_file(temp_dir)

        # Create .env
        files['env'] = TestFixtures.create_test_env_file(temp_dir)

        # Create .gitignore
        gitignore_file = os.path.join(temp_dir, ".gitignore")
        with open(gitignore_file, 'w') as f:
            f.write(TestConfig.TEST_GITIGNORE)
        files['gitignore'] = gitignore_file

        # Create test YAML files
        test_files = [
            ("device1.yaml", "esphome:\n  name: device1\n"),
            ("device2.yaml", "esphome:\n  name: device2\n"),
            ("test.yaml", "test: configuration\n")
        ]

        for filename, content in test_files:
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
            files[filename] = file_path

        return files

    @staticmethod
    def create_test_rotation_history() -> list:
        """Create test rotation history data"""
        return [
            {
                "timestamp": "2024-01-01T12:00:00",
                "rotation_type": "scheduled",
                "reason": "Regular rotation",
                "credentials_rotated": ["api_key", "ota_password"],
                "method": "automated",
                "notes": "Automated monthly rotation",
                "validation_status": "passed",
                "validation_timestamp": "2024-01-01T12:05:00",
                "validation_notes": "All credentials validated successfully"
            },
            {
                "timestamp": "2024-01-15T14:30:00",
                "rotation_type": "emergency",
                "reason": "Security incident",
                "credentials_rotated": ["api_key", "ota_password", "fallback_password"],
                "method": "manual",
                "notes": "Emergency rotation due to potential exposure",
                "validation_status": "passed",
                "validation_timestamp": "2024-01-15T14:35:00",
                "validation_notes": "Emergency validation completed"
            }
        ]

    @staticmethod
    def create_test_backup_manifest() -> Dict[str, Any]:
        """Create test backup manifest data"""
        return {
            "backup_id": "backup_test_20240101_120000",
            "timestamp": "2024-01-01T12:00:00",
            "date": "2024-01-01",
            "time": "12:00:00",
            "created_by": "test_user",
            "total_files": 3,
            "files": [
                {
                    "path": "secrets.yaml",
                    "type": "core",
                    "hash": "abc123",
                    "backup_path": "secrets.yaml",
                    "backup_hash": "abc123"
                },
                {
                    "path": "device1.yaml",
                    "type": "config",
                    "hash": "def456",
                    "backup_path": "device1.yaml",
                    "backup_hash": "def456"
                },
                {
                    "path": ".env",
                    "type": "core",
                    "hash": "ghi789",
                    "backup_path": ".env",
                    "backup_hash": "ghi789"
                }
            ],
            "backup_type": "full",
            "compression": "none",
            "encryption": "none",
            "onepassword_available": False
        }


class MockOnePasswordManager:
    """Mock 1Password manager for testing"""

    def __init__(self, available=True, account="test-account"):
        self.available = available
        self.account = account
        self._items = {
            ("Automation", "ESPHome"): {
                "api_key": TestConfig.TEST_CREDENTIALS['api_key'],
                "ota_password": TestConfig.TEST_CREDENTIALS['ota_password'],
                "fallback_password": TestConfig.TEST_CREDENTIALS['fallback_password']
            },
            ("Shared", "Home IoT"): {
                "network name": TestConfig.TEST_CREDENTIALS['wifi_ssid'],
                "wireless network password": TestConfig.TEST_CREDENTIALS['wifi_password'],
                "domain name": TestConfig.TEST_CREDENTIALS['wifi_domain']
            }
        }

    def check_cli_available(self) -> bool:
        return self.available

    def check_vault_access(self, vault_name: str) -> bool:
        return self.available

    def check_item_access(self, vault_name: str, item_name: str) -> bool:
        return self.available and (vault_name, item_name) in self._items

    def get_item_field(self, vault_name: str, item_name: str, field_name: str) -> str:
        if not self.available:
            raise Exception("1Password CLI not available")

        key = (vault_name, item_name)
        if key in self._items and field_name in self._items[key]:
            return self._items[key][field_name]

        raise Exception(f"Field {field_name} not found")

    def update_item_field(self, vault_name: str, item_name: str, field_name: str, value: str) -> bool:
        if not self.available:
            return False

        key = (vault_name, item_name)
        if key not in self._items:
            self._items[key] = {}

        self._items[key][field_name] = value
        return True

    def update_esphome_credentials(self, api_key: str, ota_password: str, fallback_password: str) -> bool:
        if not self.available:
            return False

        key = ("Automation", "ESPHome")
        self._items[key] = {
            "api_key": api_key,
            "ota_password": ota_password,
            "fallback_password": fallback_password
        }
        return True


class TestEnvironment:
    """Test environment manager"""

    def __init__(self):
        self.temp_dir = None
        self.original_cwd = None
        self.files = {}

    def setup(self):
        """Set up test environment"""
        self.temp_dir = TestFixtures.create_temp_directory()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        self.files = TestFixtures.create_test_config_files(self.temp_dir)
        return self

    def teardown(self):
        """Clean up test environment"""
        if self.original_cwd:
            os.chdir(self.original_cwd)
        if self.temp_dir:
            TestFixtures.cleanup_temp_directory(self.temp_dir)

    def __enter__(self):
        return self.setup()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()

    def get_file_path(self, filename: str) -> str:
        """Get path to a test file"""
        if filename in self.files:
            return self.files[filename]
        return os.path.join(self.temp_dir, filename)

    def create_file(self, filename: str, content: str) -> str:
        """Create a new file in the test environment"""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'w') as f:
            f.write(content)
        self.files[filename] = file_path
        return file_path
