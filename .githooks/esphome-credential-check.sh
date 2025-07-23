#!/bin/bash
# ESPHome-specific credential validation

exit_code=0

for file in "$@"; do
    if [[ -f "$file" && "$file" =~ \.(yaml|yml)$ ]]; then
        # Check for hardcoded API keys (44-char base64)
        if grep -qE '[A-Za-z0-9+/]{43}=' "$file"; then
            echo "ERROR: Potential hardcoded API key found in $file"
            echo "Use !secret api_key instead"
            exit_code=1
        fi

        # Check for hardcoded OTA passwords (32-char hex)
        if grep -qE '\b[a-fA-F0-9]{32}\b' "$file"; then
            echo "ERROR: Potential hardcoded OTA password found in $file"
            echo "Use !secret ota_password instead"
            exit_code=1
        fi

        # Check for hardcoded fallback passwords (12-char alphanumeric)
        if grep -qE '\b[A-Za-z0-9]{12}\b' "$file"; then
            echo "ERROR: Potential hardcoded fallback password found in $file"
            echo "Use !secret fallback_password instead"
            exit_code=1
        fi

        # Check for known exposed credentials
        if grep -qF 'rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk=' "$file"; then  # pragma: allowlist secret
            echo "ERROR: Known exposed API key found in $file"
            exit_code=1
        fi

        if grep -qF '5929ccc1f08289c79aca50ebe0a9b7eb' "$file"; then  # pragma: allowlist secret
            echo "ERROR: Known exposed OTA password found in $file"
            exit_code=1
        fi

        if grep -qF '1SXRpeXi7AdU' "$file"; then
            echo "ERROR: Known exposed fallback password found in $file"
            exit_code=1
        fi
    fi
done

exit $exit_code
