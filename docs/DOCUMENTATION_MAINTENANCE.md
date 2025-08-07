# Documentation Maintenance Guidelines

This guide explains how to maintain the unified documentation structure that
integrates with the Memory Bank system.

## Documentation Architecture

### Core Principle

The documentation follows a **Memory Bank Integration** pattern where:

- **Memory Bank** (`.kilocode/rules/memory-bank/`) contains authoritative
  technical information
- **Unified Documentation** (`docs/`) provides user-friendly guides that
  **link to** Memory Bank content
- **No duplication** - information exists in one authoritative location

### Documentation Hierarchy

```text
1. Memory Bank (.kilocode/rules/memory-bank/)
   ├── Authoritative technical documentation
   ├── Complete system architecture
   ├── Detailed procedures and workflows
   └── Current project context

2. Unified Documentation (docs/)
   ├── User-friendly guides and tutorials
   ├── Topic-based organization
   ├── Links to Memory Bank for details
   └── Troubleshooting and reference

3. Root README.md
   └── Entry point directing to docs/
```

## Memory Bank Files (DO NOT EDIT)

### Core Memory Bank Files

These files are maintained automatically and should **never be edited
directly**:

- **[brief.md](.kilocode/rules/memory-bank/brief.md)** - Project overview and
  requirements
- **[product.md](.kilocode/rules/memory-bank/product.md)** - Product
  description and goals
- **[context.md](.kilocode/rules/memory-bank/context.md)** - Current project state
- **[architecture.md](.kilocode/rules/memory-bank/architecture.md)** - Complete technical architecture
- **[tech.md](.kilocode/rules/memory-bank/tech.md)** - Technology stack and tools
- **[tasks.md](.kilocode/rules/memory-bank/tasks.md)** - Detailed workflow procedures

### Memory Bank Integration

When referencing Memory Bank content, use this format:

```markdown
For complete technical details, see
[System Architecture - Security](.kilocode/rules/memory-bank/architecture.md#security-architecture).
```

## Unified Documentation Maintenance

### File Organization

```text
docs/
├── README.md                    # Main documentation index
├── getting-started/            # New user guides
│   ├── quick-start.md
│   ├── development-setup.md
│   └── first-device.md
├── security/                   # Security-related documentation
│   ├── overview.md
│   ├── credential-rotation.md
│   ├── troubleshooting.md
│   └── migration-notes.md
├── device-management/          # Device operations
│   ├── device-types.md
│   ├── two-stage-deployment.md
│   ├── recovery-procedures.md
│   └── common-tasks.md
├── architecture/               # System design guides
│   ├── system-overview.md
│   ├── file-structure.md
│   └── integration-points.md
├── reference/                  # Complete reference
│   ├── task-commands.md
│   ├── troubleshooting.md
│   └── memory-bank-guide.md
└── status/                     # Status reports and historical info
```

### Content Guidelines

#### User-Friendly Guides

- **Start with practical information** users need immediately
- **Provide step-by-step procedures** for common tasks
- **Link to Memory Bank** for comprehensive technical details
- **Include troubleshooting** for common issues

#### Memory Bank References

Always link to Memory Bank content rather than duplicating:

```markdown
# ✅ Correct - Link to Memory Bank
For detailed credential rotation procedures, see [Credential Management Tasks](.kilocode/rules/memory-bank/tasks.md#credential-rotation).

# ❌ Incorrect - Duplicating Memory Bank content
## Credential Rotation Steps
1. Generate new credentials...
2. Update 1Password...
[duplicating content from Memory Bank]
```

#### Section Structure

Each guide should follow this structure:

```markdown
# Title

Brief introduction and purpose.

## Quick Reference
Essential commands or information.

## Detailed Procedures
Step-by-step guides with Memory Bank links.

## Troubleshooting
Common issues and solutions.

## Related Documentation
Links to related guides and Memory Bank sections.
```

## Adding New Documentation

### When to Add New Documentation

- **New user workflows** that need guided procedures
- **Common troubleshooting scenarios** not covered elsewhere
- **Integration guides** for new tools or systems
- **Topic-specific consolidation** of scattered information

### When NOT to Add Documentation

- **Technical details** already in Memory Bank (link instead)
- **Temporary status information** (use `docs/status/` directory)
- **Implementation details** that change frequently
- **Duplicate information** that exists elsewhere

### New Documentation Process

#### 1. Determine Appropriate Location

```bash
# Getting started guides
docs/getting-started/

# Security-related content
docs/security/

# Device management procedures
docs/device-management/

# System architecture guides
docs/architecture/

# Reference and troubleshooting
docs/reference/
```

#### 2. Create User-Friendly Content

- Focus on **practical guidance** and **step-by-step procedures**
- **Link to Memory Bank** for technical details
- Include **troubleshooting** and **common issues**
- Provide **clear navigation** to related content

#### 3. Update Navigation

- Add links in **[docs/README.md](README.md)**
- Update **related documentation** sections
- Ensure **cross-references** are accurate

#### 4. Validate Integration

- Verify **Memory Bank links** work correctly
- Check **navigation flow** makes sense
- Test **procedures** are accurate and complete

## Updating Existing Documentation

### Regular Maintenance Tasks

#### Monthly Reviews

- **Verify Memory Bank links** are still accurate
- **Update command examples** if Task commands change
- **Check troubleshooting sections** for new common issues
- **Review navigation** for clarity and completeness

#### After Major Changes

- **Update affected guides** when system architecture changes
- **Verify procedures** still work after tool updates
- **Update examples** to reflect current configurations
- **Check Memory Bank references** for new sections

### Content Updates

#### Updating Procedures

1. **Test procedures** to ensure they still work
2. **Update commands** if syntax has changed
3. **Add new troubleshooting** for discovered issues
4. **Update Memory Bank links** if sections have moved

#### Adding New Sections

1. **Identify user need** for new content
2. **Check Memory Bank** for existing technical details
3. **Create user-friendly guide** that links to Memory Bank
4. **Update navigation** and cross-references

## Legacy Documentation Handling

### Consolidation Process

When consolidating legacy documentation:

1. **Identify overlapping content** with Memory Bank
2. **Extract user-friendly procedures** for unified docs
3. **Create links** to Memory Bank for technical details
4. **Move or archive** original files
5. **Update references** throughout the project

### File Disposition

- **Move to `docs/status/`**: Status reports and historical information
- **Consolidate into topic guides**: Scattered procedural information
- **Archive**: Outdated or superseded documentation
- **Delete**: Completely duplicated content (after verification)

## Quality Assurance

### Documentation Standards

#### Content Quality

- **Clear, actionable procedures** for all guides
- **Accurate Memory Bank links** with specific sections
- **Complete troubleshooting** for common issues
- **Consistent formatting** and structure

#### Navigation Quality

- **Logical organization** by topic and user journey
- **Clear entry points** for different user types
- **Cross-references** between related topics
- **Memory Bank integration** clearly explained

#### Technical Accuracy

- **Test all procedures** before documenting
- **Verify command syntax** and examples
- **Check Memory Bank references** for accuracy
- **Validate troubleshooting solutions**

### Review Process

#### Before Publishing

1. **Test all procedures** in clean environment
2. **Verify Memory Bank links** work correctly
3. **Check navigation flow** makes sense
4. **Review for clarity** and completeness

#### Regular Audits

1. **Monthly link validation** for Memory Bank references
2. **Quarterly procedure testing** for accuracy
3. **Annual structure review** for organization
4. **Continuous user feedback** incorporation

## Tools and Automation

### Link Validation

```bash
# Check for broken Memory Bank links
grep -r "\.kilocode/rules/memory-bank/" docs/ | while read line; do
    file=$(echo "$line" | cut -d: -f1)
    link=$(echo "$line" | grep -o '\.kilocode/rules/memory-bank/[^)]*')
    if [ ! -f "$link" ]; then
        echo "Broken link in $file: $link"
    fi
done
```

### Content Validation

```bash
# Check for duplicated content (manual review needed)
find docs/ -name "*.md" -exec grep -l "specific-technical-term" {} \;
```

### Navigation Validation

```bash
# Verify all docs are linked from main index
find docs/ -name "*.md" -not -name "README.md" | while read file; do
    basename=$(basename "$file")
    if ! grep -q "$basename" docs/README.md; then
        echo "Potentially unlinked file: $file"
    fi
done
```

## Best Practices

### Writing Guidelines

- **Start with user goals** - what does the user want to accomplish?
- **Provide context** - why is this procedure necessary?
- **Use clear headings** - make content scannable
- **Include examples** - show actual commands and outputs
- **Link to Memory Bank** - don't duplicate technical details

### Memory Bank Integration

- **Always link** to Memory Bank for technical details
- **Use specific section links** when possible
- **Explain the relationship** between guide and Memory Bank content
- **Keep guides focused** on user procedures, not technical implementation

### User Experience

- **Progressive disclosure** - basic info first, details via links
- **Multiple entry points** - users may start anywhere
- **Clear next steps** - guide users to related information
- **Troubleshooting focus** - anticipate common problems

## Related Documentation

- **[Memory Bank Guide](reference/memory-bank-guide.md)** - How to use the Memory Bank system
- **[Documentation Index](README.md)** - Main documentation navigation
- **[System Architecture](.kilocode/rules/memory-bank/architecture.md)** - Complete technical architecture

---

*This maintenance guide ensures the documentation remains comprehensive, accurate, and well-integrated with the
Memory Bank system.*
