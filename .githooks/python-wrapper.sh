#!/bin/bash
# Python Wrapper for Pre-commit Hooks
# This script ensures pre-commit hooks use the correct Python environment

set -e

# Change to the repository root directory
cd "$(git rev-parse --show-toplevel)"

# Check if we're in a mise environment and use it if available
if command -v mise >/dev/null 2>&1 && mise current python >/dev/null 2>&1; then
    # Use mise exec to run the command in the proper environment
    exec mise exec -- python3 "$@"
else
    # Fallback to system python3 with PYTHONPATH set to include scripts
    export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$(pwd)/scripts"
    exec python3 "$@"
fi
