#!/usr/bin/env python3
"""
ESPHome Security Setup Script
Simplified setup for single-user repository
"""

import sys
import subprocess
import platform
import tempfile
import shutil
from pathlib import Path
from typing import List


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


class SecuritySetup:
    """Main class for ESPHome security setup"""

    def __init__(self):
        self.repo_root = Path.cwd()

    def log_info(self, message: str) -> None:
        """Log info message with blue color"""
        print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

    def log_success(self, message: str) -> None:
        """Log success message with green color"""
        print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

    def log_warning(self, message: str) -> None:
        """Log warning message with yellow color"""
        print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

    def log_error(self, message: str) -> None:
        """Log error message with red color"""
        print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

    def run_command(self, cmd: List[str], check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
        """Run a command with proper error handling"""
        try:
            result = subprocess.run(
                cmd,
                check=check,
                capture_output=capture_output,
                text=True,
                cwd=self.repo_root
            )
            return result
        except subprocess.CalledProcessError as e:
            if not check:
                return e
            raise

    def command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH"""
        return shutil.which(command) is not None

    def check_git_repo(self) -> None:
        """Check if we're in a git repository"""
        try:
            self.run_command(['git', 'rev-parse', '--git-dir'], capture_output=True)
            self.log_success("Git repository detected")
        except subprocess.CalledProcessError:
            self.log_error("This script must be run from within a git repository")
            sys.exit(1)

    def install_git_secrets(self) -> None:
        """Install git-secrets based on the operating system"""
        self.log_info("Installing git-secrets...")

        if self.command_exists('git-secrets'):
            self.log_success("git-secrets is already installed")
            return

        system = platform.system().lower()

        if system == 'darwin':  # macOS
            if self.command_exists('brew'):
                self.log_info("Installing git-secrets via Homebrew...")
                self.run_command(['brew', 'install', 'git-secrets'])
            else:
                self.log_error("Homebrew not found. Please install Homebrew first or install git-secrets manually")
                self.log_info("Manual installation: https://github.com/awslabs/git-secrets#installing-git-secrets")
                sys.exit(1)

        elif system == 'linux':
            self.log_info("Installing git-secrets from source...")
            if not self.command_exists('make'):
                self.log_error("make is required but not installed. Please install build-essential or equivalent")
                sys.exit(1)

            # Clone and install git-secrets
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                self.run_command(['git', 'clone', 'https://github.com/awslabs/git-secrets.git'], cwd=temp_path)
                secrets_dir = temp_path / 'git-secrets'
                self.run_command(['make', 'install'], cwd=secrets_dir)

        else:
            self.log_error(f"Unsupported operating system: {system}")
            self.log_info("Please install git-secrets manually: https://github.com/awslabs/git-secrets#installing-git-secrets")
            sys.exit(1)

        self.log_success("git-secrets installed successfully")

    def install_pre_commit(self) -> None:
        """Install pre-commit using pip"""
        self.log_info("Installing pre-commit...")

        if self.command_exists('pre-commit'):
            self.log_success("pre-commit is already installed")
            return

        # Try pip3 first, then pip
        pip_cmd = 'pip3' if self.command_exists('pip3') else 'pip' if self.command_exists('pip') else None

        if not pip_cmd:
            self.log_error("pip or pip3 not found. Please install Python and pip first")
            sys.exit(1)

        self.run_command([pip_cmd, 'install', 'pre-commit'])
        self.log_success("pre-commit installed successfully")

    def configure_git_secrets(self) -> None:
        """Configure git-secrets with ESPHome patterns"""
        self.log_info("Configuring git-secrets...")

        # Install git-secrets hooks
        self.run_command(['git', 'secrets', '--install', '--force'])

        # Register AWS provider (includes common patterns)
        self.run_command(['git', 'secrets', '--register-aws'])

        # Add ESPHome-specific patterns from .gitsecrets file
        gitsecrets_file = self.repo_root / '.gitsecrets'
        if gitsecrets_file.exists():
            self.log_info("Adding ESPHome-specific patterns from .gitsecrets...")
            with open(gitsecrets_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        try:
                            self.run_command(['git', 'secrets', '--add', line])
                        except subprocess.CalledProcessError:
                            self.log_warning(f"Failed to add pattern: {line}")
        else:
            self.log_warning(".gitsecrets file not found, adding basic ESPHome patterns...")

            # Add basic ESPHome patterns manually
            patterns = [
                '[A-Za-z0-9+/]{43}=',  # API keys
                r'\b[a-fA-F0-9]{32}\b',  # OTA passwords
                r'\b[A-Za-z0-9]{12}\b',  # Fallback passwords
                # Known exposed credentials
                'rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk=',  # pragma: allowlist secret
                '5929ccc1f08289c79aca50ebe0a9b7eb',  # pragma: allowlist secret
                '1SXRpeXi7AdU'  # pragma: allowlist secret
            ]

            for pattern in patterns:
                try:
                    self.run_command(['git', 'secrets', '--add', pattern])
                except subprocess.CalledProcessError:
                    self.log_warning(f"Failed to add pattern: {pattern}")

        # Add allowed patterns
        allowed_patterns = [
            r'!secret\s+[A-Za-z0-9_]+',  # Allow !secret references
            r'op\s+read\s+["\']?op://[^"\'\s]+["\']?',  # Allow op read commands
            'EXAMPLE_[A-Z_]+',  # Allow example placeholders
            'YOUR_[A-Z_]+_HERE',  # Allow placeholder text
            'test_[a-z_]+'  # Allow test values
        ]

        for pattern in allowed_patterns:
            try:
                self.run_command(['git', 'secrets', '--add', '--allowed', pattern])
            except subprocess.CalledProcessError:
                self.log_warning(f"Failed to add allowed pattern: {pattern}")

        self.log_success("git-secrets configured with ESPHome patterns")

    def create_essential_hooks(self) -> None:
        """Create essential git hooks"""
        self.log_info("Creating essential git hooks...")

        githooks_dir = self.repo_root / '.githooks'
        githooks_dir.mkdir(exist_ok=True)

        # Create ESPHome credential checker (will be converted to Python next)
        esphome_hook = githooks_dir / 'esphome_credential_check.py'
        git_secrets_hook = githooks_dir / 'git_secrets_scan.py'

        # For now, create Python wrappers that call the existing shell scripts
        # These will be replaced with full Python implementations
        esphome_wrapper = '''#!/usr/bin/env python3
"""ESPHome credential check wrapper - temporary until full Python implementation"""
import subprocess
import sys
import os

script_path = os.path.join(os.path.dirname(__file__), 'esphome-credential-check.sh')
if os.path.exists(script_path):
    result = subprocess.run([script_path] + sys.argv[1:])
    sys.exit(result.returncode)
else:
    print("ERROR: esphome-credential-check.sh not found")
    sys.exit(1)
'''

        git_secrets_wrapper = '''#!/usr/bin/env python3
"""Git-secrets scan wrapper - temporary until full Python implementation"""
import subprocess
import sys
import os

script_path = os.path.join(os.path.dirname(__file__), 'git-secrets-scan.sh')
if os.path.exists(script_path):
    result = subprocess.run([script_path] + sys.argv[1:])
    sys.exit(result.returncode)
else:
    print("ERROR: git-secrets-scan.sh not found")
    sys.exit(1)
'''

        # Write the wrapper files
        with open(esphome_hook, 'w') as f:
            f.write(esphome_wrapper)
        with open(git_secrets_hook, 'w') as f:
            f.write(git_secrets_wrapper)

        # Make hooks executable
        esphome_hook.chmod(0o755)
        git_secrets_hook.chmod(0o755)

        self.log_success("Essential git hooks created in .githooks/")

    def install_pre_commit_hooks(self) -> None:
        """Install pre-commit hooks"""
        self.log_info("Installing pre-commit hooks...")

        precommit_config = self.repo_root / '.pre-commit-config.yaml'
        if not precommit_config.exists():
            self.log_error(".pre-commit-config.yaml not found")
            sys.exit(1)

        self.run_command(['pre-commit', 'install'])
        self.log_success("Pre-commit hooks installed")

    def create_secrets_baseline(self) -> None:
        """Create secrets baseline for detect-secrets"""
        self.log_info("Creating secrets baseline for detect-secrets...")

        if self.command_exists('detect-secrets'):
            self.run_command(['detect-secrets', 'scan', '--baseline', '.secrets.baseline'])
            self.log_success("Secrets baseline created")
        else:
            self.log_warning("detect-secrets not found, skipping baseline creation")
            self.log_info("Install with: pip install detect-secrets")

    def run_initial_scan(self) -> None:
        """Run initial security scan"""
        self.log_info("Running initial security scan...")

        # Run git-secrets scan
        if self.command_exists('git-secrets'):
            self.log_info("Running git-secrets scan...")
            try:
                self.run_command(['git', 'secrets', '--scan-history'])
                self.log_success("git-secrets scan completed - no issues found")
            except subprocess.CalledProcessError:
                self.log_warning("git-secrets found potential issues - review the output above")

        # Run pre-commit on all files
        self.log_info("Running pre-commit on all files...")
        try:
            self.run_command(['pre-commit', 'run', '--all-files'])
            self.log_success("Pre-commit checks passed")
        except subprocess.CalledProcessError:
            self.log_warning("Pre-commit found issues - review the output above")

    def main(self) -> None:
        """Main execution function"""
        print("=" * 50)
        print("ESPHome Security Setup Script (Python)")
        print("=" * 50)
        print()

        # Pre-flight checks
        self.check_git_repo()

        # Install tools
        self.install_git_secrets()
        self.install_pre_commit()

        # Configure security
        self.configure_git_secrets()
        self.create_essential_hooks()
        self.install_pre_commit_hooks()
        self.create_secrets_baseline()

        # Run initial scan
        self.run_initial_scan()

        print()
        print("=" * 50)
        self.log_success("Security setup completed successfully!")
        print("=" * 50)
        print()
        print("Next steps:")
        print("1. Review any warnings or issues reported above")
        print("2. Run 'git secrets --scan' to scan for secrets")
        print("3. Run 'pre-commit run --all-files' to validate all files")
        print("4. Commit your changes to activate the hooks")
        print()
        print("The following security measures are now active:")
        print("• git-secrets: Scans for hardcoded credentials")
        print("• pre-commit hooks: Validates code before commits")
        print("• ESPHome credential validator: Checks YAML files for secrets")
        print()
        print("For more information, see the simplified security documentation")


if __name__ == '__main__':
    setup = SecuritySetup()
    try:
        setup.main()
    except KeyboardInterrupt:
        setup.log_error("Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        setup.log_error(f"Setup failed: {e}")
        sys.exit(1)
