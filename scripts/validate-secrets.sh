#!/bin/bash

# ESPHome Secrets Validation Script
# Validates secrets.yaml format and 1Password integration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if secrets.yaml exists
check_secrets_file() {
    if [[ ! -f "secrets.yaml" ]]; then
        log_error "secrets.yaml not found"
        log_info "Generate it with: ./scripts/generate_secrets.sh"
        return 1
    fi
    log_success "secrets.yaml found"
    return 0
}

# Validate API key format
validate_api_key() {
    local api_key
    api_key=$(grep "^api_key:" secrets.yaml | cut -d'"' -f2 2>/dev/null || echo "")

    if [[ -z "$api_key" ]]; then
        log_error "API key not found in secrets.yaml"
        return 1
    fi

    # Check if it's exactly 44 characters and ends with =
    if [[ ${#api_key} -eq 44 && "$api_key" =~ ^[A-Za-z0-9+/]{43}=$ ]]; then
        log_success "API key format is valid (44 chars, base64)"

        # Check if it's the known exposed key
        if [[ "$api_key" == "rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk=" ]]; then  # pragma: allowlist secret
            log_error "API key is the known exposed credential - must be rotated!"
            return 1
        fi

        return 0
    else
        log_error "API key format is invalid"
        log_info "Expected: 44 characters, base64 encoded, ending with ="
        log_info "Generate new: openssl rand -base64 32"
        return 1
    fi
}

# Validate OTA password format
validate_ota_password() {
    local ota_password
    ota_password=$(grep "^ota_password:" secrets.yaml | cut -d'"' -f2 2>/dev/null || echo "")

    if [[ -z "$ota_password" ]]; then
        log_error "OTA password not found in secrets.yaml"
        return 1
    fi

    # Check if it's exactly 32 characters and hexadecimal
    if [[ ${#ota_password} -eq 32 && "$ota_password" =~ ^[a-fA-F0-9]{32}$ ]]; then
        log_success "OTA password format is valid (32 chars, hex)"

        # Check if it's the known exposed password
        if [[ "$ota_password" == "5929ccc1f08289c79aca50ebe0a9b7eb" ]]; then  # pragma: allowlist secret
            log_error "OTA password is the known exposed credential - must be rotated!"
            return 1
        fi

        return 0
    else
        log_error "OTA password format is invalid"
        log_info "Expected: 32 characters, hexadecimal only"
        log_info "Generate new: openssl rand -hex 16"
        return 1
    fi
}

# Validate fallback password format
validate_fallback_password() {
    local fallback_password
    fallback_password=$(grep "^fallback_password:" secrets.yaml | cut -d'"' -f2 2>/dev/null || echo "")

    if [[ -z "$fallback_password" ]]; then
        log_error "Fallback password not found in secrets.yaml"
        return 1
    fi

    # Check if it's at least 12 characters and alphanumeric
    if [[ ${#fallback_password} -ge 12 && "$fallback_password" =~ ^[A-Za-z0-9]+$ ]]; then
        log_success "Fallback password format is valid (${#fallback_password} chars, alphanumeric)"

        # Check if it's the known exposed password
        if [[ "$fallback_password" == "1SXRpeXi7AdU" ]]; then  # pragma: allowlist secret
            log_error "Fallback password is the known exposed credential - must be rotated!"
            return 1
        fi

        return 0
    else
        log_error "Fallback password format is invalid"
        log_info "Expected: At least 12 characters, alphanumeric only"
        log_info "Generate new: openssl rand -base64 12 | tr -d '=+/' | cut -c1-12"
        return 1
    fi
}

# Validate WiFi credentials
validate_wifi_credentials() {
    local wifi_ssid wifi_password wifi_domain
    wifi_ssid=$(grep "^wifi_ssid:" secrets.yaml | cut -d'"' -f2 2>/dev/null || echo "")
    wifi_password=$(grep "^wifi_password:" secrets.yaml | cut -d'"' -f2 2>/dev/null || echo "")
    wifi_domain=$(grep "^wifi_domain:" secrets.yaml | cut -d'"' -f2 2>/dev/null || echo "")

    local errors=0

    if [[ -z "$wifi_ssid" ]]; then
        log_error "WiFi SSID not found in secrets.yaml"
        errors=$((errors + 1))
    elif [[ ${#wifi_ssid} -gt 32 ]]; then
        log_error "WiFi SSID too long (max 32 characters)"
        errors=$((errors + 1))
    else
        log_success "WiFi SSID is valid"
    fi

    if [[ -z "$wifi_password" ]]; then
        log_error "WiFi password not found in secrets.yaml"
        errors=$((errors + 1))
    elif [[ ${#wifi_password} -lt 8 || ${#wifi_password} -gt 63 ]]; then
        log_error "WiFi password length invalid (must be 8-63 characters)"
        errors=$((errors + 1))
    else
        log_success "WiFi password is valid"
    fi

    if [[ -n "$wifi_domain" ]]; then
        if [[ "$wifi_domain" =~ ^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
            log_success "WiFi domain is valid"
        else
            log_warning "WiFi domain format may be invalid"
        fi
    else
        log_warning "WiFi domain not set (optional)"
    fi

    return $errors
}

# Check for 1Password integration
validate_1password_integration() {
    if ! command -v op >/dev/null 2>&1; then
        log_warning "1Password CLI not found - cannot validate integration"
        return 0
    fi

    if [[ -z "$OP_ACCOUNT" ]]; then
        log_error "OP_ACCOUNT environment variable not set"
        log_info "Set with: export OP_ACCOUNT=your-account-name"
        log_info "Or sign in with: op signin"
        return 1
    fi

    log_info "Validating 1Password integration..."

    # Check if we can access the account
    if ! op account list --account="$OP_ACCOUNT" >/dev/null 2>&1; then
        log_error "Cannot access 1Password account '$OP_ACCOUNT'"
        log_info "Sign in with: op signin"
        return 1
    fi

    # Check if we can access the ESPHome item
    if ! op item get "ESPHome" --vault="Automation" --account="$OP_ACCOUNT" >/dev/null 2>&1; then
        log_error "Cannot access ESPHome item in Automation vault"
        return 1
    fi

    # Check if we can access the Home IoT item
    if ! op item get "Home IoT" --vault="Shared" --account="$OP_ACCOUNT" >/dev/null 2>&1; then
        log_error "Cannot access Home IoT item in Shared vault"
        return 1
    fi

    log_success "1Password integration is working"
    return 0
}

# Check for exposed credentials in files
scan_for_exposed_credentials() {
    log_info "Scanning for exposed credentials in YAML files..."

    local found_issues=0

    # Known exposed credentials
    local exposed_api_key="rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk="  # pragma: allowlist secret
    local exposed_ota_password="5929ccc1f08289c79aca50ebe0a9b7eb"  # pragma: allowlist secret
    local exposed_fallback_password="1SXRpeXi7AdU"  # pragma: allowlist secret

    # Scan all YAML files except secrets.yaml (which we validate separately)
    while IFS= read -r -d '' file; do
        if [[ "$file" != "./secrets.yaml" ]]; then
            if grep -qF "$exposed_api_key" "$file"; then
                log_error "Exposed API key found in $file"
                found_issues=$((found_issues + 1))
            fi

            if grep -qF "$exposed_ota_password" "$file"; then
                log_error "Exposed OTA password found in $file"
                found_issues=$((found_issues + 1))
            fi

            if grep -qF "$exposed_fallback_password" "$file"; then
                log_error "Exposed fallback password found in $file"
                found_issues=$((found_issues + 1))
            fi
        fi
    done < <(find . -name "*.yaml" -o -name "*.yml" -print0 2>/dev/null)

    if [[ $found_issues -eq 0 ]]; then
        log_success "No exposed credentials found in YAML files"
    else
        log_error "Found $found_issues exposed credential(s) in YAML files"
    fi

    return $found_issues
}

# Main validation function
main() {
    echo "=================================================="
    echo "ESPHome Secrets Validation"
    echo "=================================================="
    echo

    local total_errors=0

    # Check if secrets file exists
    if ! check_secrets_file; then
        exit 1
    fi

    # Validate credential formats
    if ! validate_api_key; then
        total_errors=$((total_errors + 1))
    fi

    if ! validate_ota_password; then
        total_errors=$((total_errors + 1))
    fi

    if ! validate_fallback_password; then
        total_errors=$((total_errors + 1))
    fi

    if ! validate_wifi_credentials; then
        total_errors=$((total_errors + 1))
    fi

    # Validate 1Password integration
    if ! validate_1password_integration; then
        total_errors=$((total_errors + 1))
    fi

    # Scan for exposed credentials
    if ! scan_for_exposed_credentials; then
        total_errors=$((total_errors + 1))
    fi

    echo
    echo "=================================================="
    if [[ $total_errors -eq 0 ]]; then
        log_success "All validations passed!"
        echo "=================================================="
        exit 0
    else
        log_error "Validation failed with $total_errors error(s)"
        echo "=================================================="
        echo
        echo "To fix issues:"
        echo "1. Rotate exposed credentials: Follow CREDENTIAL_ROTATION_GUIDE.md"
        echo "2. Fix format issues: Use the generation commands shown above"
        echo "3. Update 1Password: Ensure credentials are stored correctly"
        echo "4. Re-run validation: ./scripts/validate-secrets.sh"
        exit 1
    fi
}

# Run main function
main "$@"
