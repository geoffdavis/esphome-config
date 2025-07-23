#!/bin/bash
# Mise Python Wrapper for Pre-commit Hooks
# This script ensures pre-commit hooks use the Mise-managed Python environment

set -e

# Change to the repository root directory
cd "$(git rev-parse --show-toplevel)"

# Source mise environment if available
if command -v mise >/dev/null 2>&1; then
    # Use mise exec to run the command in the proper environment
    exec mise exec -- python3 "$@"
else
    # Fallback to system python3 if mise is not available
    exec python3 "$@"
fi
