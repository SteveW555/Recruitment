# Scripts Directory

Build automation and utility scripts for the project.

## Contents

### Makefile
Build automation and common development tasks.

**Usage:**
```bash
# Initialize environment
make -f scripts/Makefile setup

# Start all services
make -f scripts/Makefile start

# Run test suite
make -f scripts/Makefile test

# Code quality checks
make -f scripts/Makefile lint

# Deploy to staging
make -f scripts/Makefile deploy-staging
```

**Available Targets:**
Run `make -f scripts/Makefile help` to see all available commands.

## Future Scripts

This directory may contain additional utility scripts:
- Database migration scripts
- Data seeding scripts
- Deployment automation
- Testing utilities
- Code generation tools

## See Also

- [infrastructure/](../infrastructure/) - Deployment configurations
- [CLAUDE.md](../CLAUDE.md) - Development standards
