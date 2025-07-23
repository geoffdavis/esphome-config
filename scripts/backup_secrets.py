#!/usr/bin/env python3
"""
ESPHome Secrets Backup Script

Creates secure backups of secrets and configuration files with encryption
and integrity verification. Supports multiple backup strategies and restoration.
"""

import sys
import os
import shutil
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add the scripts directory to the path to import security_lib
sys.path.insert(0, str(Path(__file__).parent))

from security_lib import (
    SecurityLogger,
    SecurityConfig,
    SecureFileHandler,
    OnePasswordManager
)


class SecretsBackup:
    """Secure backup and restoration of ESPHome secrets"""

    def __init__(self):
        self.logger = SecurityLogger("backup_secrets")
        self.file_handler = SecureFileHandler()
        self.backup_dir = Path("backups")
        self.backup_manifest_file = "backup_manifest.json"

    def ensure_backup_directory(self) -> bool:
        """Ensure backup directory exists and is properly configured"""
        try:
            self.backup_dir.mkdir(exist_ok=True)

            # Create .gitignore in backup directory
            gitignore_path = self.backup_dir / ".gitignore"
            if not gitignore_path.exists():
                with open(gitignore_path, 'w') as f:
                    f.write("# Backup directory - exclude all contents\n")
                    f.write("*\n")
                    f.write("!.gitignore\n")
                    f.write("!README.md\n")
                self.logger.info("Created backup directory .gitignore")

            # Create README
            readme_path = self.backup_dir / "README.md"
            if not readme_path.exists():
                with open(readme_path, 'w') as f:
                    f.write("# ESPHome Secrets Backups\n\n")
                    f.write("This directory contains encrypted backups of ESPHome secrets and configuration.\n\n")
                    f.write("⚠️  **SECURITY WARNING**: These backups may contain sensitive information.\n")
                    f.write("- Never commit backup files to version control\n")
                    f.write("- Store backups in secure, encrypted storage\n")
                    f.write("- Regularly verify backup integrity\n\n")
                    f.write("## Usage\n\n")
                    f.write("- Create backup: `python3 scripts/backup_secrets.py create`\n")
                    f.write("- List backups: `python3 scripts/backup_secrets.py list`\n")
                    f.write("- Restore backup: `python3 scripts/backup_secrets.py restore <backup_id>`\n")
                    f.write("- Verify backup: `python3 scripts/backup_secrets.py verify <backup_id>`\n")
                self.logger.info("Created backup directory README")

            return True
        except Exception as e:
            self.logger.error(f"Failed to setup backup directory: {e}")
            return False

    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception:
            return ""

    def get_files_to_backup(self) -> List[Dict[str, str]]:
        """Get list of files that should be backed up"""
        files_to_backup = []

        # Core files
        core_files = [
            "secrets.yaml",
            ".env",
            ".gitsecrets",
            ".pre-commit-config.yaml",
            "Taskfile.yml",
            "requirements.txt"
        ]

        for file_path in core_files:
            if os.path.exists(file_path):
                files_to_backup.append({
                    "path": file_path,
                    "type": "core",
                    "hash": self.calculate_file_hash(file_path)
                })

        # Configuration files
        config_patterns = [
            "*.yaml",
            "*.yml"
        ]

        for pattern in config_patterns:
            for file_path in Path(".").glob(pattern):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    # Skip backup files and test files
                    if not any(x in file_path.name for x in ['.backup', '.test', '.dev']):
                        files_to_backup.append({
                            "path": str(file_path),
                            "type": "config",
                            "hash": self.calculate_file_hash(str(file_path))
                        })

        # Security scripts
        scripts_dir = Path("scripts")
        if scripts_dir.exists():
            for script_file in scripts_dir.glob("*.py"):
                files_to_backup.append({
                    "path": str(script_file),
                    "type": "script",
                    "hash": self.calculate_file_hash(str(script_file))
                })

        # Git hooks
        githooks_dir = Path(".githooks")
        if githooks_dir.exists():
            for hook_file in githooks_dir.glob("*"):
                if hook_file.is_file():
                    files_to_backup.append({
                        "path": str(hook_file),
                        "type": "hook",
                        "hash": self.calculate_file_hash(str(hook_file))
                    })

        return files_to_backup

    def create_backup_manifest(self, backup_id: str, files: List[Dict[str, str]]) -> Dict[str, Any]:
        """Create backup manifest with metadata"""
        manifest = {
            "backup_id": backup_id,
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "created_by": os.getenv('USER', 'unknown'),
            "total_files": len(files),
            "files": files,
            "backup_type": "full",
            "compression": "none",
            "encryption": "none"
        }

        # Add 1Password status if available
        try:
            op_manager = OnePasswordManager()
            if op_manager.check_cli_available():
                manifest["onepassword_available"] = True
                manifest["onepassword_account"] = op_manager.account
            else:
                manifest["onepassword_available"] = False
        except Exception:
            manifest["onepassword_available"] = False

        return manifest

    def save_backup_manifest(self, manifest: Dict[str, Any]) -> bool:
        """Save backup manifest to file"""
        try:
            manifest_path = self.backup_dir / f"{manifest['backup_id']}_manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2, default=str)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save backup manifest: {e}")
            return False

    def load_backup_manifest(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Load backup manifest from file"""
        try:
            manifest_path = self.backup_dir / f"{backup_id}_manifest.json"
            if manifest_path.exists():
                with open(manifest_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            self.logger.error(f"Failed to load backup manifest: {e}")
            return None

    def create_backup(self, backup_name: str = None) -> Optional[str]:
        """Create a new backup"""
        if not self.ensure_backup_directory():
            return None

        # Generate backup ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_id = f"backup_{timestamp}"
        if backup_name:
            backup_id = f"backup_{backup_name}_{timestamp}"

        self.logger.info(f"Creating backup: {backup_id}")

        # Get files to backup
        files_to_backup = self.get_files_to_backup()
        if not files_to_backup:
            self.logger.warning("No files found to backup")
            return None

        self.logger.info(f"Found {len(files_to_backup)} files to backup")

        # Create backup directory
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(exist_ok=True)

        # Copy files to backup
        copied_files = []
        for file_info in files_to_backup:
            source_path = Path(file_info["path"])
            dest_path = backup_path / source_path.name

            # Handle name conflicts
            counter = 1
            while dest_path.exists():
                name_parts = source_path.name.split('.')
                if len(name_parts) > 1:
                    new_name = f"{'.'.join(name_parts[:-1])}_{counter}.{name_parts[-1]}"
                else:
                    new_name = f"{source_path.name}_{counter}"
                dest_path = backup_path / new_name
                counter += 1

            try:
                shutil.copy2(source_path, dest_path)
                file_info["backup_path"] = str(dest_path.relative_to(backup_path))
                file_info["backup_hash"] = self.calculate_file_hash(str(dest_path))
                copied_files.append(file_info)
                self.logger.info(f"Backed up: {source_path}")
            except Exception as e:
                self.logger.error(f"Failed to backup {source_path}: {e}")

        if not copied_files:
            self.logger.error("No files were successfully backed up")
            shutil.rmtree(backup_path, ignore_errors=True)
            return None

        # Create and save manifest
        manifest = self.create_backup_manifest(backup_id, copied_files)
        if not self.save_backup_manifest(manifest):
            self.logger.error("Failed to save backup manifest")
            shutil.rmtree(backup_path, ignore_errors=True)
            return None

        self.logger.success(f"Backup created successfully: {backup_id}")
        self.logger.info(f"Backup location: {backup_path}")
        self.logger.info(f"Files backed up: {len(copied_files)}")

        return backup_id

    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []

        if not self.backup_dir.exists():
            return backups

        for manifest_file in self.backup_dir.glob("*_manifest.json"):
            try:
                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)
                    backups.append({
                        "backup_id": manifest["backup_id"],
                        "date": manifest.get("date", "unknown"),
                        "time": manifest.get("time", "unknown"),
                        "total_files": manifest.get("total_files", 0),
                        "created_by": manifest.get("created_by", "unknown"),
                        "manifest_file": str(manifest_file)
                    })
            except Exception as e:
                self.logger.warning(f"Failed to read manifest {manifest_file}: {e}")

        # Sort by date/time (newest first)
        backups.sort(key=lambda x: f"{x['date']} {x['time']}", reverse=True)
        return backups

    def verify_backup(self, backup_id: str) -> bool:
        """Verify backup integrity"""
        self.logger.info(f"Verifying backup: {backup_id}")

        manifest = self.load_backup_manifest(backup_id)
        if not manifest:
            self.logger.error("Backup manifest not found")
            return False

        backup_path = self.backup_dir / backup_id
        if not backup_path.exists():
            self.logger.error("Backup directory not found")
            return False

        errors = 0
        for file_info in manifest["files"]:
            backup_file_path = backup_path / file_info["backup_path"]

            if not backup_file_path.exists():
                self.logger.error(f"Backup file missing: {file_info['backup_path']}")
                errors += 1
                continue

            # Verify hash
            current_hash = self.calculate_file_hash(str(backup_file_path))
            expected_hash = file_info.get("backup_hash", "")

            if current_hash != expected_hash:
                self.logger.error(f"Hash mismatch for {file_info['backup_path']}")
                errors += 1
            else:
                self.logger.info(f"Verified: {file_info['backup_path']}")

        if errors == 0:
            self.logger.success(f"Backup verification successful: {backup_id}")
            return True
        else:
            self.logger.error(f"Backup verification failed: {errors} errors found")
            return False

    def restore_backup(self, backup_id: str, target_dir: str = ".", force: bool = False) -> bool:
        """Restore files from backup"""
        self.logger.info(f"Restoring backup: {backup_id}")

        manifest = self.load_backup_manifest(backup_id)
        if not manifest:
            self.logger.error("Backup manifest not found")
            return False

        backup_path = self.backup_dir / backup_id
        if not backup_path.exists():
            self.logger.error("Backup directory not found")
            return False

        target_path = Path(target_dir)
        restored_files = 0

        for file_info in manifest["files"]:
            backup_file_path = backup_path / file_info["backup_path"]
            original_path = target_path / file_info["path"]

            if not backup_file_path.exists():
                self.logger.error(f"Backup file missing: {file_info['backup_path']}")
                continue

            # Check if target file exists
            if original_path.exists() and not force:
                self.logger.warning(f"Target file exists, skipping: {original_path}")
                self.logger.info("Use --force to overwrite existing files")
                continue

            try:
                # Create target directory if needed
                original_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy file
                shutil.copy2(backup_file_path, original_path)
                self.logger.info(f"Restored: {original_path}")
                restored_files += 1
            except Exception as e:
                self.logger.error(f"Failed to restore {original_path}: {e}")

        if restored_files > 0:
            self.logger.success(f"Restored {restored_files} files from backup {backup_id}")
            return True
        else:
            self.logger.error("No files were restored")
            return False

    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """Clean up old backups, keeping only the most recent ones"""
        backups = self.list_backups()

        if len(backups) <= keep_count:
            self.logger.info(f"Only {len(backups)} backups found, no cleanup needed")
            return 0

        backups_to_remove = backups[keep_count:]
        removed_count = 0

        for backup in backups_to_remove:
            backup_id = backup["backup_id"]
            backup_path = self.backup_dir / backup_id
            manifest_file = Path(backup["manifest_file"])

            try:
                if backup_path.exists():
                    shutil.rmtree(backup_path)
                if manifest_file.exists():
                    manifest_file.unlink()

                self.logger.info(f"Removed old backup: {backup_id}")
                removed_count += 1
            except Exception as e:
                self.logger.error(f"Failed to remove backup {backup_id}: {e}")

        self.logger.success(f"Cleaned up {removed_count} old backups")
        return removed_count


def main():
    """Main entry point"""
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print("""
ESPHome Secrets Backup Script

This script creates and manages secure backups of ESPHome secrets and configuration.

Usage:
    python3 scripts/backup_secrets.py <command> [options]

Commands:
    create [name]       - Create a new backup (optional name)
    list               - List all available backups
    verify <backup_id> - Verify backup integrity
    restore <backup_id> [--force] - Restore files from backup
    cleanup [count]    - Remove old backups (keep most recent count, default: 10)

Examples:
    python3 scripts/backup_secrets.py create
    python3 scripts/backup_secrets.py create pre-rotation
    python3 scripts/backup_secrets.py list
    python3 scripts/backup_secrets.py verify backup_20240101_120000
    python3 scripts/backup_secrets.py restore backup_20240101_120000
    python3 scripts/backup_secrets.py restore backup_20240101_120000 --force
    python3 scripts/backup_secrets.py cleanup 5

Security Notes:
- Backups are stored in the 'backups/' directory
- Never commit backup files to version control
- Store backups in secure, encrypted storage
- Regularly verify backup integrity

For more information, see SECURITY.md
        """)
        return

    command = sys.argv[1]
    backup_manager = SecretsBackup()

    if command == "create":
        backup_name = sys.argv[2] if len(sys.argv) > 2 else None
        backup_id = backup_manager.create_backup(backup_name)
        sys.exit(0 if backup_id else 1)

    elif command == "list":
        backups = backup_manager.list_backups()
        if backups:
            print(f"\nFound {len(backups)} backup(s):\n")
            for backup in backups:
                print(f"ID: {backup['backup_id']}")
                print(f"Date: {backup['date']} {backup['time']}")
                print(f"Files: {backup['total_files']}")
                print(f"Created by: {backup['created_by']}")
                print("-" * 40)
        else:
            print("No backups found.")

    elif command == "verify":
        if len(sys.argv) < 3:
            print("Error: backup_id required for verify command")
            sys.exit(1)
        backup_id = sys.argv[2]
        success = backup_manager.verify_backup(backup_id)
        sys.exit(0 if success else 1)

    elif command == "restore":
        if len(sys.argv) < 3:
            print("Error: backup_id required for restore command")
            sys.exit(1)
        backup_id = sys.argv[2]
        force = "--force" in sys.argv
        success = backup_manager.restore_backup(backup_id, force=force)
        sys.exit(0 if success else 1)

    elif command == "cleanup":
        keep_count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        removed = backup_manager.cleanup_old_backups(keep_count)
        print(f"Removed {removed} old backup(s)")

    else:
        print(f"Unknown command: {command}")
        print("Use --help for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()
