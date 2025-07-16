#!/bin/bash
# Git-secrets scan wrapper

if command -v git-secrets >/dev/null 2>&1; then
    git secrets --scan "$@"
else
    echo "WARNING: git-secrets not found, skipping scan"
    exit 0
fi
