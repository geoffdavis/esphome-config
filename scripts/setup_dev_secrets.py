#!/usr/bin/env python3
"""
ESPHome Development Secrets Setup Script

Sets up development environment with test credentials for local development
and testing. Creates safe test credentials that don't interfere with production.
"""

import sys
import os
from pathlib import Path

# Add the scripts directory to the path to import security_lib
sys.path.insert(0, str(Path(__file__).parent))

from security_lib import (
    SecurityLogger,
    CredentialGenerator,
    CredentialValidator,
    SecureFileHandler
)


class DevSecretsSetup:
    """Development secrets setup and management"""
    
    def __init__(self):
        self.logger = SecurityLogger("dev_secrets")
        self.generator = CredentialGenerator()
        self.validator = CredentialValidator()
        self.file_handler = SecureFileHandler()
        self.dev_secrets_file = "secrets.dev.yaml"
        self.test_secrets_file = "secrets.test.yaml"
    
    def generate_dev_credentials(self) -> dict:
        """Generate development credentials"""
        self.logger.info("Generating development credentials...")
        
        credentials = {
            'wifi_ssid': 'ESPHome-Dev-Network',
            'wifi_password': 'dev-password-12345678',
            'wifi_domain': 'dev.local',
            'api_key': self.generator.generate_api_key(),
            'ota_password': self.generator.generate_ota_password(),
            'fallback_password': self.generator.generate_fallback_password()
        }
        
        # Validate generated credentials
        for cred_type in ['api_key', 'ota_password', 'fallback_password']:
            if cred_type == 'api_key':
                valid, msg = self.validator.validate_api_key(credentials[cred_type])
            elif cred_type == 'ota_password':
                valid, msg = self.validator.validate_ota_password(credentials[cred_type])
            elif cred_type == 'fallback_password':
                valid, msg = self.validator.validate_fallback_password(credentials[cred_type])
            
            if valid:
                self.logger.success(f"Generated valid {cred_type}")
            else:
                self.logger.error(f"Generated invalid {cred_type}: {msg}")
                return {}
        
        return credentials
    
    def generate_test_credentials(self) -> dict:
        """Generate test credentials for unit testing"""
        self.logger.info("Generating test credentials...")
        
        # Use fixed test credentials for reproducible tests
        credentials = {
            'wifi_ssid': 'ESPHome-Test-Network',
            'wifi_password': 'test-password-87654321',
            'wifi_domain': 'test.local',
            'api_key': 'dGVzdF9hcGlfa2V5XzEyMzQ1Njc4OTBhYmNkZWY=',  # test_api_key_1234567890abcdef (base64)
            'ota_password': 'abcdef1234567890abcdef1234567890',  # 32 char hex
            'fallback_password': 'TestPass1234'  # 12 char alphanumeric
        }
        
        # Validate test credentials
        for cred_type in ['api_key', 'ota_password', 'fallback_password']:
            if cred_type == 'api_key':
                valid, msg = self.validator.validate_api_key(credentials[cred_type])
            elif cred_type == 'ota_password':
                valid, msg = self.validator.validate_ota_password(credentials[cred_type])
            elif cred_type == 'fallback_password':
                valid, msg = self.validator.validate_fallback_password(credentials[cred_type])
            
            if valid:
                self.logger.success(f"Test {cred_type} is valid")
            else:
                self.logger.error(f"Test {cred_type} is invalid: {msg}")
                return {}
        
        return credentials
    
    def create_dev_secrets_file(self, credentials: dict) -> bool:
        """Create development secrets file"""
        self.logger.info(f"Creating {self.dev_secrets_file}...")
        
        content = f"""# ESPHome Development Secrets
# This file contains development credentials for local testing
# DO NOT USE IN PRODUCTION - FOR DEVELOPMENT ONLY

# WiFi credentials (development network)
wifi_ssid: "{credentials['wifi_ssid']}"
wifi_password: "{credentials['wifi_password']}"
wifi_domain: "{credentials['wifi_domain']}"

# ESPHome credentials (development)
api_key: "{credentials['api_key']}"
ota_password: "{credentials['ota_password']}"
fallback_password: "{credentials['fallback_password']}"

# Development notes:
# - These credentials are for development/testing only
# - Use 'cp {self.dev_secrets_file} secrets.yaml' to use for development
# - Never commit secrets.yaml to version control
# - For production, use: ./scripts/generate_secrets.sh
"""
        
        try:
            with open(self.dev_secrets_file, 'w') as f:
                f.write(content)
            self.logger.success(f"Created {self.dev_secrets_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create {self.dev_secrets_file}: {e}")
            return False
    
    def create_test_secrets_file(self, credentials: dict) -> bool:
        """Create test secrets file for unit testing"""
        self.logger.info(f"Creating {self.test_secrets_file}...")
        
        content = f"""# ESPHome Test Secrets
# This file contains fixed test credentials for unit testing
# DO NOT USE IN PRODUCTION - FOR TESTING ONLY

# WiFi credentials (test network)
wifi_ssid: "{credentials['wifi_ssid']}"
wifi_password: "{credentials['wifi_password']}"
wifi_domain: "{credentials['wifi_domain']}"

# ESPHome credentials (test)
api_key: "{credentials['api_key']}"
ota_password: "{credentials['ota_password']}"
fallback_password: "{credentials['fallback_password']}"

# Test notes:
# - These are fixed credentials for reproducible unit tests
# - Used by test suites to validate credential handling
# - Safe to commit to version control (test credentials only)
"""
        
        try:
            with open(self.test_secrets_file, 'w') as f:
                f.write(content)
            self.logger.success(f"Created {self.test_secrets_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create {self.test_secrets_file}: {e}")
            return False
    
    def create_dev_env_file(self) -> bool:
        """Create development .env file"""
        dev_env_file = ".env.dev"
        self.logger.info(f"Creating {dev_env_file}...")
        
        content = """# ESPHome Development Environment Variables
# Copy this to .env for development use

# 1Password Configuration (for development)
OP_ACCOUNT=your-dev-1password-account

# Development Settings
ESPHOME_DEV_MODE=true
ESPHOME_LOG_LEVEL=DEBUG
ESPHOME_SKIP_VALIDATION=false

# Test Settings
ESPHOME_TEST_MODE=false
ESPHOME_USE_TEST_CREDENTIALS=false
"""
        
        try:
            with open(dev_env_file, 'w') as f:
                f.write(content)
            self.logger.success(f"Created {dev_env_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create {dev_env_file}: {e}")
            return False
    
    def update_gitignore(self) -> bool:
        """Update .gitignore to exclude development files"""
        gitignore_path = Path(".gitignore")
        
        dev_entries = [
            "# Development secrets",
            "secrets.dev.yaml",
            ".env.dev",
            ".env",
            "",
            "# Test artifacts", 
            "test_*.yaml",
            "*.test.yaml",
            ""
        ]
        
        try:
            # Read existing .gitignore
            existing_content = ""
            if gitignore_path.exists():
                with open(gitignore_path, 'r') as f:
                    existing_content = f.read()
            
            # Check if dev entries already exist
            needs_update = False
            for entry in dev_entries:
                if entry.strip() and entry not in existing_content:
                    needs_update = True
                    break
            
            if needs_update:
                with open(gitignore_path, 'a') as f:
                    f.write('\n'.join(dev_entries))
                self.logger.success("Updated .gitignore with development entries")
            else:
                self.logger.info(".gitignore already contains development entries")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to update .gitignore: {e}")
            return False
    
    def create_dev_readme(self) -> bool:
        """Create development README"""
        readme_file = "DEV_SECRETS_README.md"
        self.logger.info(f"Creating {readme_file}...")
        
        content = f"""# ESPHome Development Secrets

This directory contains development and test credentials for ESPHome development.

## Files

- `{self.dev_secrets_file}` - Development credentials for local testing
- `{self.test_secrets_file}` - Fixed test credentials for unit tests
- `.env.dev` - Development environment variables template

## Usage

### Development Setup

1. Copy development secrets for local use:
   ```bash
   cp {self.dev_secrets_file} secrets.yaml
   ```

2. Copy development environment:
   ```bash
   cp .env.dev .env
   ```

3. Edit `.env` with your actual 1Password account name

### Testing

The test credentials in `{self.test_secrets_file}` are used by unit tests and are safe to commit to version control.

### Production

For production use, always generate secrets from 1Password:
```bash
./scripts/generate_secrets.sh
```

## Security Notes

- **NEVER** commit `secrets.yaml` or `.env` to version control
- Development credentials are for local testing only
- Test credentials are fixed and safe for version control
- Production credentials must come from 1Password

## Credential Validation

All generated credentials are validated for format and security:
- API keys: 44-character base64 encoded
- OTA passwords: 32-character hexadecimal
- Fallback passwords: 12+ character alphanumeric

## Scripts

- `python3 scripts/setup_dev_secrets.py` - Generate development credentials
- `python3 scripts/validate_secrets.py` - Validate current secrets
- `python3 scripts/validate_1password_structure.py` - Validate 1Password setup
"""
        
        try:
            with open(readme_file, 'w') as f:
                f.write(content)
            self.logger.success(f"Created {readme_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create {readme_file}: {e}")
            return False
    
    def run_setup(self, include_test: bool = True) -> bool:
        """Run complete development secrets setup"""
        self.logger.header("ESPHome Development Secrets Setup")
        
        success = True
        
        # Generate and create development credentials
        dev_credentials = self.generate_dev_credentials()
        if dev_credentials:
            if not self.create_dev_secrets_file(dev_credentials):
                success = False
        else:
            success = False
        
        # Generate and create test credentials if requested
        if include_test:
            test_credentials = self.generate_test_credentials()
            if test_credentials:
                if not self.create_test_secrets_file(test_credentials):
                    success = False
            else:
                success = False
        
        # Create supporting files
        if not self.create_dev_env_file():
            success = False
        
        if not self.update_gitignore():
            success = False
        
        if not self.create_dev_readme():
            success = False
        
        # Print results
        print()
        print("=" * 50)
        if success:
            self.logger.success("Development secrets setup completed!")
            print("=" * 50)
            print()
            print("Next steps:")
            print(f"1. Copy development secrets: cp {self.dev_secrets_file} secrets.yaml")
            print("2. Copy development environment: cp .env.dev .env")
            print("3. Edit .env with your 1Password account name")
            print("4. Start developing with safe test credentials")
            print()
            print("Files created:")
            print(f"• {self.dev_secrets_file} - Development credentials")
            if include_test:
                print(f"• {self.test_secrets_file} - Test credentials")
            print("• .env.dev - Development environment template")
            print("• DEV_SECRETS_README.md - Documentation")
            print()
            print("⚠️  Remember: Never commit secrets.yaml or .env to version control!")
        else:
            self.logger.error("Development secrets setup failed!")
            print("=" * 50)
        
        return success


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("""
ESPHome Development Secrets Setup Script

This script sets up development environment with safe test credentials.

Usage:
    python3 scripts/setup_dev_secrets.py [options]

Options:
    --no-test       Skip creating test credentials
    --dev-only      Create only development credentials
    --help, -h      Show this help message

The script will:
1. Generate safe development credentials
2. Create test credentials for unit testing
3. Set up development environment files
4. Update .gitignore to protect secrets
5. Create documentation

Files created:
- secrets.dev.yaml - Development credentials
- secrets.test.yaml - Test credentials (fixed for reproducible tests)
- .env.dev - Development environment template
- DEV_SECRETS_README.md - Documentation

For production use, always use: ./scripts/generate_secrets.sh
        """)
        return
    
    include_test = True
    if len(sys.argv) > 1:
        if '--no-test' in sys.argv or '--dev-only' in sys.argv:
            include_test = False
    
    setup = DevSecretsSetup()
    success = setup.run_setup(include_test=include_test)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()