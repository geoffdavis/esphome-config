#!/usr/bin/env python3
"""
ESPHome-specific credential validation
Checks YAML files for hardcoded credentials and known exposed secrets
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple


class CredentialChecker:
    """ESPHome credential validation checker"""

    def __init__(self):
        # Define credential patterns
        self.patterns = [
            # API keys (44-char base64)
            (r'[A-Za-z0-9+/]{43}=',
             "Potential hardcoded API key found",
             "Use !secret api_key instead"),

            # OTA passwords (32-char hex)
            (r'\b[a-fA-F0-9]{32}\b',
             "Potential hardcoded OTA password found",
             "Use !secret ota_password instead"),

            # Fallback passwords (12-char alphanumeric)
            (r'\b[A-Za-z0-9]{12}\b',
             "Potential hardcoded fallback password found",
             "Use !secret fallback_password instead"),
        ]

        # Known exposed credentials
        self.known_exposed = [
            'rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk=',  # pragma: allowlist secret
            '5929ccc1f08289c79aca50ebe0a9b7eb',  # pragma: allowlist secret
            '1SXRpeXi7AdU'
        ]

    def check_file(self, file_path: Path) -> List[Tuple[str, str]]:
        """
        Check a single file for credential issues
        Returns list of (error_message, suggestion) tuples
        """
        if not file_path.exists() or not file_path.is_file():
            return []

        # Only check YAML files
        if file_path.suffix.lower() not in ['.yaml', '.yml']:
            return []

        # Skip files that legitimately contain secrets or are in excluded paths
        if file_path.name in ['.pre-commit-config.yaml', 'secrets.yaml']:
            return []

        # Skip virtual environment and build directories
        if '.venv' in str(file_path) or '.esphome' in str(file_path):
            return []

        errors = []

        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, IOError) as e:
            errors.append((f"Failed to read {file_path}: {e}", ""))
            return errors

        # Check for pattern matches with context
        for pattern, error_msg, suggestion in self.patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                matched_text = match.group()

                # Skip common English words that match the pattern
                common_words = [
                    'representing', 'markdownlint', 'configuration', 'temperature',
                    'cn105climate', 'environments', 'overwhelming', 'production',
                    'disconnected'
                ]
                if matched_text.lower() in common_words:
                    continue

                # Skip if it's part of a comment or documentation
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                if line_end == -1:
                    line_end = len(content)
                line_content = content[line_start:line_end]

                if line_content.strip().startswith('#'):
                    continue

                errors.append((
                    f"ERROR: {error_msg} in {file_path}",
                    suggestion
                ))
                break  # Only report first match per pattern to avoid spam

        # Check for known exposed credentials
        for exposed_cred in self.known_exposed:
            if exposed_cred in content:
                if exposed_cred == 'rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk=':  # pragma: allowlist secret
                    errors.append((
                        f"ERROR: Known exposed API key found in {file_path}",
                        ""
                    ))
                elif exposed_cred == '5929ccc1f08289c79aca50ebe0a9b7eb':  # pragma: allowlist secret
                    errors.append((
                        f"ERROR: Known exposed OTA password found in {file_path}",
                        ""
                    ))
                elif exposed_cred == '1SXRpeXi7AdU':
                    errors.append((
                        f"ERROR: Known exposed fallback password found in {file_path}",
                        ""
                    ))

        return errors

    def check_files(self, file_paths: List[str]) -> int:
        """
        Check multiple files for credential issues
        Returns exit code (0 = success, 1 = issues found)
        """
        exit_code = 0

        for file_path_str in file_paths:
            file_path = Path(file_path_str)
            errors = self.check_file(file_path)

            for error_msg, suggestion in errors:
                print(error_msg)
                if suggestion:
                    print(suggestion)
                exit_code = 1

        return exit_code


def main() -> int:
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: esphome_credential_check.py <file1> [file2] ...")
        return 1

    checker = CredentialChecker()
    return checker.check_files(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main())
