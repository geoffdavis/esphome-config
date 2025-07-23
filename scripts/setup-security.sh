#!/bin/bash

# ESPHome Security Setup Script
# Simplified setup for single-user repository

set -e  # Exit on any error

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

# Check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "This script must be run from within a git repository"
        exit 1
    fi
    log_success "Git repository detected"
}

# Install git-secrets
install_git_secrets() {
    log_info "Installing git-secrets..."

    if command -v git-secrets >/dev/null 2>&1; then
        log_success "git-secrets is already installed"
        return 0
    fi

    # Detect OS and install accordingly
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew >/dev/null 2>&1; then
            log_info "Installing git-secrets via Homebrew..."
            brew install git-secrets
        else
            log_error "Homebrew not found. Please install Homebrew first or install git-secrets manually"
            log_info "Manual installation: https://github.com/awslabs/git-secrets#installing-git-secrets"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        log_info "Installing git-secrets from source..."
        if ! command -v make >/dev/null 2>&1; then
            log_error "make is required but not installed. Please install build-essential or equivalent"
            exit 1
        fi

        # Clone and install git-secrets
        TEMP_DIR=$(mktemp -d)
        cd "$TEMP_DIR"
        git clone https://github.com/awslabs/git-secrets.git
        cd git-secrets
        make install
        cd - > /dev/null
        rm -rf "$TEMP_DIR"
    else
        log_error "Unsupported operating system: $OSTYPE"
        log_info "Please install git-secrets manually: https://github.com/awslabs/git-secrets#installing-git-secrets"
        exit 1
    fi

    log_success "git-secrets installed successfully"
}

# Install pre-commit
install_pre_commit() {
    log_info "Installing pre-commit..."

    if command -v pre-commit >/dev/null 2>&1; then
        log_success "pre-commit is already installed"
        return 0
    fi

    # Try pip first, then pip3
    if command -v pip3 >/dev/null 2>&1; then
        pip3 install pre-commit
    elif command -v pip >/dev/null 2>&1; then
        pip install pre-commit
    else
        log_error "pip or pip3 not found. Please install Python and pip first"
        exit 1
    fi

    log_success "pre-commit installed successfully"
}

# Configure git-secrets
configure_git_secrets() {
    log_info "Configuring git-secrets..."

    # Install git-secrets hooks
    git secrets --install --force

    # Register AWS provider (includes common patterns)
    git secrets --register-aws

    # Add ESPHome-specific patterns from .gitsecrets file
    if [[ -f ".gitsecrets" ]]; then
        log_info "Adding ESPHome-specific patterns from .gitsecrets..."
        while IFS= read -r pattern; do
            # Skip comments and empty lines
            if [[ ! "$pattern" =~ ^[[:space:]]*# ]] && [[ -n "$pattern" ]]; then
                git secrets --add "$pattern" || log_warning "Failed to add pattern: $pattern"
            fi
        done < .gitsecrets
    else
        log_warning ".gitsecrets file not found, adding basic ESPHome patterns..."

        # Add basic ESPHome patterns manually
        git secrets --add '[A-Za-z0-9+/]{43}='  # API keys
        git secrets --add '\b[a-fA-F0-9]{32}\b'  # OTA passwords
        git secrets --add '\b[A-Za-z0-9]{12}\b'  # Fallback passwords

        # Add known exposed credentials
        git secrets --add 'rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk='
        git secrets --add '5929ccc1f08289c79aca50ebe0a9b7eb'
        git secrets --add '1SXRpeXi7AdU'
    fi

    # Add allowed patterns
    git secrets --add --allowed '!secret\s+[A-Za-z0-9_]+'  # Allow !secret references
    git secrets --add --allowed 'op\s+read\s+["\'"'"']?op://[^"'"'"'\s]+["\'"'"']?'  # Allow op read commands
    git secrets --add --allowed 'EXAMPLE_[A-Z_]+'  # Allow example placeholders
    git secrets --add --allowed 'YOUR_[A-Z_]+_HERE'  # Allow placeholder text
    git secrets --add --allowed 'test_[a-z_]+'  # Allow test values

    log_success "git-secrets configured with ESPHome patterns"
}

# Create essential git hooks
create_essential_hooks() {
    log_info "Creating essential git hooks..."

    mkdir -p .githooks

    # Create ESPHome credential checker (essential)
    cat > .githooks/esphome-credential-check.sh << 'EOF'
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
        if grep -qF 'rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk=' "$file"; then
            echo "ERROR: Known exposed API key found in $file"
            exit_code=1
        fi

        if grep -qF '5929ccc1f08289c79aca50ebe0a9b7eb' "$file"; then
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
EOF

    # Create git-secrets scan wrapper
    cat > .githooks/git-secrets-scan.sh << 'EOF'
#!/bin/bash
# Git-secrets scan wrapper

if command -v git-secrets >/dev/null 2>&1; then
    git secrets --scan "$@"
else
    echo "WARNING: git-secrets not found, skipping scan"
    exit 0
fi
EOF

    # Make hooks executable
    chmod +x .githooks/*.sh

    log_success "Essential git hooks created in .githooks/"
}

# Install pre-commit hooks
install_pre_commit_hooks() {
    log_info "Installing pre-commit hooks..."

    if [[ ! -f ".pre-commit-config.yaml" ]]; then
        log_error ".pre-commit-config.yaml not found"
        exit 1
    fi

    pre-commit install

    log_success "Pre-commit hooks installed"
}

# Create secrets baseline for detect-secrets
create_secrets_baseline() {
    log_info "Creating secrets baseline for detect-secrets..."

    if command -v detect-secrets >/dev/null 2>&1; then
        detect-secrets scan --baseline .secrets.baseline
        log_success "Secrets baseline created"
    else
        log_warning "detect-secrets not found, skipping baseline creation"
        log_info "Install with: pip install detect-secrets"
    fi
}

# Run initial security scan
run_initial_scan() {
    log_info "Running initial security scan..."

    # Run git-secrets scan
    if command -v git-secrets >/dev/null 2>&1; then
        log_info "Running git-secrets scan..."
        if git secrets --scan-history; then
            log_success "git-secrets scan completed - no issues found"
        else
            log_warning "git-secrets found potential issues - review the output above"
        fi
    fi

    # Run pre-commit on all files
    log_info "Running pre-commit on all files..."
    if pre-commit run --all-files; then
        log_success "Pre-commit checks passed"
    else
        log_warning "Pre-commit found issues - review the output above"
    fi
}

# Main execution
main() {
    echo "=================================================="
    echo "ESPHome Security Setup Script (Simplified)"
    echo "=================================================="
    echo

    # Pre-flight checks
    check_git_repo

    # Install tools
    install_git_secrets
    install_pre_commit

    # Configure security
    configure_git_secrets
    create_essential_hooks
    install_pre_commit_hooks
    create_secrets_baseline

    # Run initial scan
    run_initial_scan

    echo
    echo "=================================================="
    log_success "Security setup completed successfully!"
    echo "=================================================="
    echo
    echo "Next steps:"
    echo "1. Review any warnings or issues reported above"
    echo "2. Run 'git secrets --scan' to scan for secrets"
    echo "3. Run 'pre-commit run --all-files' to validate all files"
    echo "4. Commit your changes to activate the hooks"
    echo
    echo "The following security measures are now active:"
    echo "• git-secrets: Scans for hardcoded credentials"
    echo "• pre-commit hooks: Validates code before commits"
    echo "• ESPHome credential validator: Checks YAML files for secrets"
    echo
    echo "For more information, see the simplified security documentation"
}

# Run main function
main "$@"
