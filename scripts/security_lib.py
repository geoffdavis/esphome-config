#!/usr/bin/env python3
"""
ESPHome Security Library

Shared security utilities for credential validation, 1Password integration,
file handling, and logging across all ESPHome security scripts.
"""

import os
import sys
import subprocess
import secrets
import base64
import re
import shutil
import time
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging


# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================

def load_env_file(env_file: str = ".env") -> None:
    """Load environment variables from .env file if it exists"""
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    os.environ[key] = value

# Load .env file at module import
load_env_file()


# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================

class SecurityConfig:
    """Security configuration constants"""

    # 1Password configuration - load from environment
    @staticmethod
    def get_onepassword_account() -> str:
        """Get 1Password account from environment"""
        account = os.getenv('OP_ACCOUNT')
        if not account:
            raise ValueError("OP_ACCOUNT environment variable not set. Please set it in .env file or environment.")
        return account

    AUTOMATION_VAULT = "Automation"
    SHARED_VAULT = "Shared"
    ESPHOME_ITEM = "ESPHome"
    HOME_IOT_ITEM = "Home IoT"

    # Known exposed credentials that must be detected
    EXPOSED_CREDENTIALS = {
        'api_key': 'rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk=',  # pragma: allowlist secret
        'ota_password': '5929ccc1f08289c79aca50ebe0a9b7eb',  # pragma: allowlist secret
        'fallback_password': '1SXRpeXi7AdU',  # pragma: allowlist secret
        # Additional transition credentials used in Taskfile.yml
        'ota_password_2': '3a11021250d483c5e78d0ff3e93779e3',  # pragma: allowlist secret
        'ota_password_3': '55977e01702437af44c5544c565fb451',  # pragma: allowlist secret
        'fallback_password_2': 'E4GPbKApzm6Qe.3k'  # pragma: allowlist secret
    }

    # Credential format patterns
    API_KEY_PATTERN = r'^[A-Za-z0-9+/]{43}=$'
    OTA_PASSWORD_PATTERN = r'^[a-fA-F0-9]{32}$'
    FALLBACK_PASSWORD_PATTERN = r'^[A-Za-z0-9]+$'

    # File patterns
    YAML_EXTENSIONS = ['.yaml', '.yml']
    BACKUP_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"


# =============================================================================
# LOGGING AND OUTPUT
# =============================================================================

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color


class SecurityLogger:
    """Enhanced logging with colors and formatting for security operations"""

    def __init__(self, name: str = "security", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create console handler if not already exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def info(self, message: str):
        """Log info message with blue color"""
        print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

    def success(self, message: str):
        """Log success message with green color"""
        print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

    def warning(self, message: str):
        """Log warning message with yellow color"""
        print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

    def error(self, message: str):
        """Log error message with red color"""
        print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

    def step(self, message: str):
        """Log step header with formatting"""
        print()
        print("=" * 60)
        print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.NC}")
        print("=" * 60)

    def header(self, title: str, width: int = 50):
        """Log header with formatting"""
        print("=" * width)
        print(title)
        print("=" * width)
        print()


# =============================================================================
# CREDENTIAL GENERATION
# =============================================================================

class CredentialGenerator:
    """Generates secure credentials according to ESPHome requirements"""

    @staticmethod
    def generate_api_key() -> str:
        """Generate 32-byte base64 encoded API key"""
        return base64.b64encode(secrets.token_bytes(32)).decode('utf-8')

    @staticmethod
    def generate_ota_password() -> str:
        """Generate 32-character hexadecimal OTA password"""
        return secrets.token_hex(16)

    @staticmethod
    def generate_fallback_password() -> str:
        """Generate 12-character alphanumeric fallback password"""
        # Generate more bytes than needed and filter to alphanumeric
        while True:
            raw = base64.b64encode(secrets.token_bytes(16)).decode('utf-8')
            # Remove non-alphanumeric characters
            clean = re.sub(r'[^A-Za-z0-9]', '', raw)
            if len(clean) >= 12:
                return clean[:12]

    @classmethod
    def generate_all_credentials(cls) -> Dict[str, str]:
        """Generate all ESPHome credentials"""
        return {
            'api_key': cls.generate_api_key(),
            'ota_password': cls.generate_ota_password(),
            'fallback_password': cls.generate_fallback_password()
        }


# =============================================================================
# CREDENTIAL VALIDATION
# =============================================================================

class CredentialValidator:
    """Validates credential formats and security"""

    @staticmethod
    def validate_api_key(api_key: str) -> Tuple[bool, str]:
        """Validate API key format and security"""
        # Check for exposed credential first
        if api_key == SecurityConfig.EXPOSED_CREDENTIALS['api_key']:
            return False, "API key is the known exposed credential - must be rotated!"

        # Check length
        if len(api_key) != 44:
            return False, "API key must be exactly 44 characters"

        # Check base64 format
        if not re.match(SecurityConfig.API_KEY_PATTERN, api_key):
            return False, "API key must be valid base64 with padding"

        # Validate it's actually decodable base64
        try:
            decoded = base64.b64decode(api_key)
            if len(decoded) != 32:
                return False, "API key must be valid base64 encoding 32 bytes"
        except Exception:
            return False, "API key must be valid base64 with padding"

        return True, "API key format is valid"

    @staticmethod
    def validate_ota_password(ota_password: str) -> Tuple[bool, str]:
        """Validate OTA password format and security"""
        # Check for exposed credential first
        if ota_password == SecurityConfig.EXPOSED_CREDENTIALS['ota_password']:
            return False, "OTA password is the known exposed credential - must be rotated!"

        # Check length and format together for better error messages
        if len(ota_password) != 32:
            if not re.match(r'^[a-fA-F0-9]*$', ota_password):
                return False, "OTA password must be exactly 32 hexadecimal characters"
            return False, "OTA password must be exactly 32 characters"

        if not re.match(SecurityConfig.OTA_PASSWORD_PATTERN, ota_password):
            return False, "OTA password must be hexadecimal only"

        return True, "OTA password format is valid"

    @staticmethod
    def validate_fallback_password(fallback_password: str) -> Tuple[bool, str]:
        """Validate fallback password format and security"""
        if len(fallback_password) < 12:
            return False, "Fallback password must be at least 12 characters"

        if not re.match(SecurityConfig.FALLBACK_PASSWORD_PATTERN, fallback_password):
            return False, "Fallback password must be alphanumeric only"

        if fallback_password == SecurityConfig.EXPOSED_CREDENTIALS['fallback_password']:
            return False, "Fallback password is the known exposed credential - must be rotated!"

        return True, "Fallback password format is valid"

    @staticmethod
    def validate_wifi_credentials(wifi_ssid: str, wifi_password: str, wifi_domain: str = "") -> Tuple[bool, List[str]]:
        """Validate WiFi credentials"""
        errors = []

        if not wifi_ssid:
            errors.append("WiFi SSID not found")
        elif len(wifi_ssid) > 32:
            errors.append("WiFi SSID too long (max 32 characters)")

        if not wifi_password:
            errors.append("WiFi password not found")
        elif len(wifi_password) < 8 or len(wifi_password) > 63:
            errors.append("WiFi password length invalid (must be 8-63 characters)")

        if wifi_domain and not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', wifi_domain):
            errors.append("WiFi domain format may be invalid")

        return len(errors) == 0, errors

    @classmethod
    def validate_all_credentials(cls, credentials: Dict[str, str]) -> Tuple[bool, Dict[str, str]]:
        """Validate all credentials and return results"""
        results = {}
        all_valid = True

        if 'api_key' in credentials:
            valid, msg = cls.validate_api_key(credentials['api_key'])
            results['api_key'] = msg
            all_valid = all_valid and valid

        if 'ota_password' in credentials:
            valid, msg = cls.validate_ota_password(credentials['ota_password'])
            results['ota_password'] = msg
            all_valid = all_valid and valid

        if 'fallback_password' in credentials:
            valid, msg = cls.validate_fallback_password(credentials['fallback_password'])
            results['fallback_password'] = msg
            all_valid = all_valid and valid

        return all_valid, results


# =============================================================================
# 1PASSWORD INTEGRATION
# =============================================================================

class OnePasswordManager:
    """Manages 1Password CLI operations"""

    def __init__(self, account: Optional[str] = None):
        self.account = account or SecurityConfig.get_onepassword_account()
        self.logger = SecurityLogger("1password")

    def check_cli_available(self) -> bool:
        """Check if 1Password CLI is available and authenticated"""
        try:
            subprocess.run(['op', 'account', 'list'],
                         check=True, capture_output=True, text=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def check_account_access(self) -> bool:
        """Check if we can access the configured account"""
        try:
            result = subprocess.run([
                'op', 'account', 'list', f'--account={self.account}'
            ], check=True, capture_output=True, text=True)
            return self.account in result.stdout
        except subprocess.CalledProcessError:
            return False

    def check_vault_access(self, vault_name: str) -> bool:
        """Check if we can access a specific vault"""
        try:
            result = subprocess.run([
                'op', 'vault', 'list', f'--account={self.account}'
            ], check=True, capture_output=True, text=True)
            return vault_name in result.stdout
        except subprocess.CalledProcessError:
            return False

    def check_item_access(self, vault_name: str, item_name: str) -> bool:
        """Check if we can access a specific item"""
        try:
            subprocess.run([
                'op', 'item', 'get', item_name, f'--vault={vault_name}',
                f'--account={self.account}'
            ], check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def get_item_field(self, vault_name: str, item_name: str, field_name: str) -> Optional[str]:
        """Get a specific field from an item"""
        try:
            result = subprocess.run([
                'op', 'item', 'get', item_name, f'--vault={vault_name}',
                f'--fields={field_name}', '--reveal', f'--account={self.account}'
            ], check=True, capture_output=True, text=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def update_item_field(self, vault_name: str, item_name: str, field_name: str, value: str) -> bool:
        """Update a specific field in an item"""
        try:
            subprocess.run([
                'op', 'item', 'edit', item_name, f'--vault={vault_name}',
                f'{field_name}={value}', f'--account={self.account}'
            ], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to update {field_name}: {e}")
            return False

    def get_esphome_credentials(self) -> Optional[Dict[str, str]]:
        """Get all ESPHome credentials from 1Password"""
        credentials = {}

        for field in ['api_key', 'ota_password', 'fallback_password']:
            value = self.get_item_field(SecurityConfig.AUTOMATION_VAULT,
                                      SecurityConfig.ESPHOME_ITEM, field)
            if value is None:
                return None
            credentials[field] = value

        return credentials

    def get_wifi_credentials(self) -> Optional[Dict[str, str]]:
        """Get WiFi credentials from 1Password"""
        credentials = {}
        field_mapping = {
            'wifi_ssid': 'network name',
            'wifi_password': 'wireless network password',  # pragma: allowlist secret
            'wifi_domain': 'domain name'
        }

        for key, field in field_mapping.items():  # pragma: allowlist secret
            value = self.get_item_field(SecurityConfig.SHARED_VAULT,
                                      SecurityConfig.HOME_IOT_ITEM, field)
            if value is None and key != 'wifi_domain':  # domain is optional
                return None
            credentials[key] = value or ""

        return credentials

    def update_esphome_credentials(self, api_key: str, ota_password: str, fallback_password: str) -> bool:
        """Update ESPHome credentials in 1Password"""
        updates = [
            ('api_key', api_key),
            ('ota_password', ota_password),
            ('fallback_password', fallback_password)
        ]

        for field, value in updates:
            if not self.update_item_field(SecurityConfig.AUTOMATION_VAULT,
                                        SecurityConfig.ESPHOME_ITEM, field, value):
                return False

        return True

    def verify_credentials(self) -> bool:
        """Verify credentials were stored correctly in 1Password"""
        try:
            result = subprocess.run([
                'op', 'item', 'get', SecurityConfig.ESPHOME_ITEM,
                f'--vault={SecurityConfig.AUTOMATION_VAULT}',
                '--fields=api_key,ota_password,fallback_password',
                f'--account={self.account}'
            ], check=True, capture_output=True, text=True)

            self.logger.info("1Password credentials verified:")
            for line in result.stdout.strip().split('\n'):
                if line:
                    self.logger.info(f"  {line}")
            return True
        except subprocess.CalledProcessError:
            return False


# =============================================================================
# FILE OPERATIONS
# =============================================================================

class SecureFileHandler:
    """Secure file operations for secrets and configuration files"""

    def __init__(self):
        self.logger = SecurityLogger("filehandler")

    def backup_file(self, file_path: str, backup_suffix: str = None) -> Optional[str]:
        """Create a backup of a file with timestamp"""
        if not os.path.exists(file_path):
            return None

        if backup_suffix is None:
            timestamp = datetime.now().strftime(SecurityConfig.BACKUP_TIMESTAMP_FORMAT)
            backup_suffix = f"backup.{timestamp}"

        backup_path = f"{file_path}.{backup_suffix}"
        shutil.copy2(file_path, backup_path)
        self.logger.success(f"Backed up {file_path} to {backup_path}")
        return backup_path

    def read_yaml_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Safely read a YAML file"""
        try:
            with open(file_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to read YAML file {file_path}: {e}")
            return None

    def write_yaml_file(self, file_path: str, data: Dict[str, Any]) -> bool:
        """Safely write a YAML file"""
        try:
            with open(file_path, 'w') as f:
                yaml.safe_dump(data, f, default_flow_style=False)
            return True
        except Exception as e:
            self.logger.error(f"Failed to write YAML file {file_path}: {e}")
            return False

    def read_secrets_file(self, file_path: str = "secrets.yaml") -> Optional[Dict[str, str]]:
        """Read secrets from secrets.yaml file"""
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Parse secrets manually to handle the simple key: "value" format
            secrets = {}
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        secrets[key] = value

            return secrets
        except Exception as e:
            self.logger.error(f"Failed to read secrets file {file_path}: {e}")
            return None

    def write_secrets_file(self, secrets: Dict[str, str], file_path: str = "secrets.yaml") -> bool:
        """Write secrets to secrets.yaml file"""
        try:
            content = "# ESPHome secrets file\n"
            content += "# This file is auto-generated. DO NOT EDIT MANUALLY.\n\n"

            # Group secrets logically
            if 'wifi_ssid' in secrets:
                content += "# WiFi credentials\n"
                content += f'wifi_ssid: "{secrets["wifi_ssid"]}"\n'
                if 'wifi_password' in secrets:
                    content += f'wifi_password: "{secrets["wifi_password"]}"\n'
                if 'wifi_domain' in secrets:
                    content += f'wifi_domain: "{secrets["wifi_domain"]}"\n'
                content += "\n"

            # ESPHome credentials
            if 'api_key' in secrets:
                content += "# API key\n"
                content += f'api_key: "{secrets["api_key"]}"\n\n'

            if 'fallback_password' in secrets:
                content += "# Fallback hotspot password\n"
                content += f'fallback_password: "{secrets["fallback_password"]}"\n\n'

            if 'ota_password' in secrets:
                content += "# OTA password\n"
                content += f'ota_password: "{secrets["ota_password"]}"\n'

            with open(file_path, 'w') as f:
                f.write(content)

            self.logger.success(f"Secrets written to {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write secrets file {file_path}: {e}")
            return False

    def cleanup_temporary_files(self, temp_files: List[str]) -> None:
        """Clean up temporary files"""
        for file_path in temp_files:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.success(f"Removed temporary file: {file_path}")


# =============================================================================
# SECURITY SCANNING
# =============================================================================

class SecurityScanner:
    """Security scanning utilities for detecting exposed credentials"""

    def __init__(self):
        self.logger = SecurityLogger("scanner")

    def scan_file_for_credentials(self, file_path: str) -> List[str]:
        """Scan a single file for exposed credentials"""
        issues = []

        if not os.path.exists(file_path):
            return issues

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Check for each exposed credential
            for cred_type, cred_value in SecurityConfig.EXPOSED_CREDENTIALS.items():
                if cred_value in content:
                    issues.append(f"Exposed {cred_type} found in {file_path}")

            # Check for credential patterns
            if re.search(SecurityConfig.API_KEY_PATTERN, content):
                # Make sure it's not the exposed one we already checked
                matches = re.findall(SecurityConfig.API_KEY_PATTERN, content)
                for match in matches:
                    if match != SecurityConfig.EXPOSED_CREDENTIALS['api_key']:
                        issues.append(f"Potential hardcoded API key found in {file_path}")
                        break

            if re.search(SecurityConfig.OTA_PASSWORD_PATTERN, content):
                matches = re.findall(SecurityConfig.OTA_PASSWORD_PATTERN, content)
                for match in matches:
                    if match != SecurityConfig.EXPOSED_CREDENTIALS['ota_password']:
                        issues.append(f"Potential hardcoded OTA password found in {file_path}")
                        break

        except Exception as e:
            self.logger.warning(f"Failed to scan {file_path}: {e}")

        return issues

    def scan_directory_for_credentials(self, directory: str = ".",
                                     extensions: List[str] = None) -> List[str]:
        """Scan directory for exposed credentials"""
        if extensions is None:
            extensions = SecurityConfig.YAML_EXTENSIONS + ['.py', '.sh', '.js', '.ts', '.json', '.md']

        issues = []

        for root, dirs, files in os.walk(directory):
            # Skip certain directories
            dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.githooks']

            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    file_issues = self.scan_file_for_credentials(file_path)
                    issues.extend(file_issues)

        return issues

    def scan_for_exposed_credentials(self, directory: str = ".") -> List[str]:
        """Scan for exposed credentials (alias for scan_directory_for_credentials)"""
        return self.scan_directory_for_credentials(directory)

    def test_security_hooks(self, hook_path: str = ".githooks/esphome-credential-check.sh") -> bool:
        """Test that security hooks properly detect exposed credentials"""
        if not os.path.exists(hook_path):
            self.logger.error(f"Security hook not found: {hook_path}")
            return False

        test_files = {
            'test_old_api.yaml': f'api_key: "{SecurityConfig.EXPOSED_CREDENTIALS["api_key"]}"',
            'test_old_ota.yaml': f'ota_password: "{SecurityConfig.EXPOSED_CREDENTIALS["ota_password"]}"',
            'test_old_fallback.yaml': f'fallback_password: "{SecurityConfig.EXPOSED_CREDENTIALS["fallback_password"]}"'
        }

        all_detected = True

        for filename, content in test_files.items():
            # Create test file
            with open(filename, 'w') as f:
                f.write(content)

            try:
                # Test security hook
                result = subprocess.run([hook_path, filename], capture_output=True, text=True)

                if result.returncode != 0:
                    self.logger.success(f"Security hook correctly detected exposed credential in {filename}")
                else:
                    self.logger.error(f"Security hook failed to detect exposed credential in {filename}")
                    all_detected = False
            except Exception as e:
                self.logger.error(f"Failed to test security hook on {filename}: {e}")
                all_detected = False
            finally:
                # Clean up test file
                if os.path.exists(filename):
                    os.remove(filename)

        return all_detected


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def check_required_tools(tools: List[str]) -> Tuple[bool, List[str]]:
    """Check if required tools are available in PATH"""
    missing_tools = []

    for tool in tools:
        if not shutil.which(tool):
            missing_tools.append(tool)

    return len(missing_tools) == 0, missing_tools


def run_command(cmd: List[str], check: bool = True, capture_output: bool = True,
                timeout: Optional[int] = None) -> subprocess.CompletedProcess:
    """Run a command with proper error handling"""
    try:
        return subprocess.run(
            cmd,
            check=check,
            capture_output=capture_output,
            text=True,
            timeout=timeout
        )
    except subprocess.TimeoutExpired as e:
        raise subprocess.CalledProcessError(1, cmd, "Command timed out")
    except subprocess.CalledProcessError as e:
        if not check:
            return e
        raise


def get_device_list(directory: str = ".") -> List[str]:
    """Get list of ESPHome device names from YAML files"""
    devices = []

    try:
        for file in os.listdir(directory):
            if (file.endswith('.yaml') and
                not file.endswith('-minimal.yaml') and
                not file.endswith('-full.yaml') and
                file != 'secrets.yaml'):
                device = file.replace('.yaml', '')
                devices.append(device)
    except Exception:
        pass

    return sorted(devices)


# =============================================================================
# MAIN LIBRARY INITIALIZATION
# =============================================================================

# Initialize logger for the library
_library_logger = SecurityLogger("security_lib")

# Verify environment setup on import
try:
    SecurityConfig.get_onepassword_account()
    _library_logger.info("Security library initialized successfully")
except ValueError as e:
    _library_logger.warning(f"Security library initialization warning: {e}")
