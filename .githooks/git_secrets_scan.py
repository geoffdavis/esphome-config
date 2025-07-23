#!/usr/bin/env python3
"""
Git-secrets scan wrapper
Provides a Python interface to git-secrets with graceful fallback
"""

import sys
import subprocess
import shutil
from typing import List


class GitSecretsScanner:
    """Wrapper for git-secrets scanning functionality"""

    def __init__(self):
        self.git_secrets_available = shutil.which('git-secrets') is not None

    def scan_files(self, file_paths: List[str]) -> int:
        """
        Scan files using git-secrets
        Returns exit code (0 = success, 1 = issues found)
        """
        if not self.git_secrets_available:
            print("WARNING: git-secrets not found, skipping scan")
            return 0

        try:
            # Run git secrets --scan with the provided files
            cmd = ['git', 'secrets', '--scan'] + file_paths
            result = subprocess.run(cmd, check=False)
            return result.returncode

        except subprocess.SubprocessError as e:
            print(f"ERROR: Failed to run git-secrets: {e}")
            return 1

    def scan_history(self) -> int:
        """
        Scan git history using git-secrets
        Returns exit code (0 = success, 1 = issues found)
        """
        if not self.git_secrets_available:
            print("WARNING: git-secrets not found, skipping history scan")
            return 0

        try:
            result = subprocess.run(['git', 'secrets', '--scan-history'], check=False)
            return result.returncode

        except subprocess.SubprocessError as e:
            print(f"ERROR: Failed to run git-secrets history scan: {e}")
            return 1

    def is_available(self) -> bool:
        """Check if git-secrets is available"""
        return self.git_secrets_available


def main() -> int:
    """Main entry point"""
    scanner = GitSecretsScanner()

    if len(sys.argv) < 2:
        # No files provided, scan history
        return scanner.scan_history()
    else:
        # Files provided, scan them
        return scanner.scan_files(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main())
