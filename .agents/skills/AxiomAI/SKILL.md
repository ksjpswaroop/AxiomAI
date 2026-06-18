```markdown
# AxiomAI Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches the core development patterns and conventions used in the AxiomAI Python repository. You'll learn how to structure files, write and organize code, follow commit message standards, and set up and run tests. These patterns ensure consistency and maintainability across the codebase.

## Coding Conventions

### File Naming
- Use **camelCase** for file names.
  - Example: `dataProcessor.py`, `modelTrainer.py`

### Import Style
- Use **relative imports** within the package.
  - Example:
    ```python
    from .utils import calculateScore
    ```

### Export Style
- Use **named exports** (i.e., explicitly define what is exported).
  - Example:
    ```python
    def processData(data):
        # processing logic
        return result

    __all__ = ['processData']
    ```

### Commit Messages
- Follow **conventional commit** style.
- Prefixes used: `fix`, `docs`
- Example:
  ```
  fix: resolve issue with data normalization
  docs: update README with setup instructions
  ```

## Workflows

### Code Contribution
**Trigger:** When adding or updating code in the repository  
**Command:** `/contribute-code`

1. Create or update files using camelCase naming.
2. Use relative imports for internal modules.
3. Explicitly define exports with `__all__`.
4. Write clear, conventional commit messages (e.g., `fix:`, `docs:`).

### Writing Tests
**Trigger:** When testing new or existing functionality  
**Command:** `/write-test`

1. Create test files matching the pattern `*.test.*` (e.g., `dataProcessor.test.py`).
2. Place test files alongside the code or in a dedicated test directory.
3. Use the preferred (unknown) testing framework.
4. Run tests to ensure correctness.

## Testing Patterns

- Test files follow the `*.test.*` naming convention.
  - Example: `modelTrainer.test.py`
- The specific testing framework is not detected; check existing test files for patterns.
- Place tests close to the code they verify or in a dedicated test folder.

## Commands
| Command           | Purpose                                            |
|-------------------|----------------------------------------------------|
| /contribute-code  | Steps for contributing code following conventions   |
| /write-test       | Steps for writing and organizing tests              |
```
