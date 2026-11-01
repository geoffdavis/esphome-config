#!/bin/bash
# Python Wrapper for Pre-commit Hooks
# This script ensures pre-commit hooks use the project's uv-managed virtualenv,
# so hook scripts can import project dependencies (e.g. PyYAML).

set -e

# Change to the repository root directory
cd "$(git rev-parse --show-toplevel)"

export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$(pwd)/scripts"

# Prefer the project venv (created by `uv sync`, which .envrc runs); fall back
# to whatever python3 is on PATH.
if [ -x .venv/bin/python3 ]; then
    exec .venv/bin/python3 "$@"
fi
exec python3 "$@"
