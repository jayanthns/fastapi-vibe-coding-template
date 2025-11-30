# Package Manager Guide (uv)

This project uses **[uv](https://github.com/astral-sh/uv)** for fast and reliable Python package management.

## Why uv?
- **Speed**: Extremely fast dependency resolution and installation.
- **Reliability**: Deterministic builds with `uv.lock`.
- **Compatibility**: Drop-in replacement for `pip` and `pip-tools`.

## Common Commands

### 1. Adding Packages

Add a package to `pyproject.toml` and lock it:

```bash
# Add a production dependency
make add-package PACKAGE=httpx
# With version constraint
make add-package PACKAGE=httpx VERSION=0.27.0

# Add a development dependency
make add-dev-package PACKAGE=pytest
```

### 2. Removing Packages

Remove a package:

```bash
make remove-package PACKAGE=httpx
make remove-dev-package PACKAGE=pytest
```

### 3. Syncing Dependencies

Install/Sync dependencies from the lock file:

```bash
make install
```

### 4. Updating Dependencies

Upgrade all packages to their latest allowed versions:

```bash
make update-deps
```

### 5. Exporting Requirements

Generate `requirements.txt` (e.g., for CI/CD or legacy tools):

```bash
make export-requirements
```

## Workflow

1. **Add/Remove** packages using `make add-package` / `make remove-package`.
2. This automatically updates `pyproject.toml` and `uv.lock`.
3. Commit both files to version control.
4. Other developers run `make install` to sync their environments.

## Troubleshooting

**Q: My environment seems broken.**
A: Run `make install` to force a sync with the lock file.

**Q: How do I install a specific version?**
A: Use `make add-package PACKAGE=name VERSION=x.y.z`.
