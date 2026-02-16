# Contributing to Power BI Visual Regression Testing

Thank you for your interest in contributing! This guide will help you get started.

## Prerequisites

- Python 3.10+
- Git

> **Note:** You do **not** need Azure credentials or a Power BI workspace to contribute. The project includes mock unit tests that run without any external services.

## Development Setup

1. **Fork and clone the repository:**

   ```bash
   git clone https://github.com/<your-username>/power-bi-visual-testing-python.git
   cd power-bi-visual-testing-python
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/Mac
   .venv\Scripts\activate      # Windows
   ```

3. **Install with dev dependencies:**

   ```bash
   pip install -e ".[dev]"
   ```

4. **Install Playwright browsers** (only needed for integration tests):

   ```bash
   playwright install --with-deps chromium
   ```

## Running Tests

### Unit tests (no credentials needed)

```bash
pytest tests/unit/ -v
```

These tests use mocks and can be run by any contributor without Azure or Power BI access.

### Integration tests (requires credentials)

```bash
pytest tests/ -v -m integration
```

These require a `.env` file with valid Service Principal credentials and a Power BI workspace. See [README.md](README.md) for setup instructions.

### All tests

```bash
pytest -v
```

## Code Quality

We use automated tooling to maintain code quality. Run these before submitting a PR:

```bash
# Linting
ruff check .

# Formatting
ruff format --check .

# Type checking
mypy helper_functions/ fabric_ci_test/
```

To auto-fix formatting:

```bash
ruff format .
ruff check . --fix
```

## Submitting Changes

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and ensure all checks pass:
   ```bash
   ruff check .
   ruff format --check .
   mypy helper_functions/ fabric_ci_test/
   pytest tests/unit/ -v
   ```

3. Commit with a clear message describing the change.

4. Push and open a Pull Request against `main`.

## PR Guidelines

- Keep PRs focused on a single change.
- Include tests for new functionality.
- Update documentation if behavior changes.
- Ensure CI checks pass before requesting review.

## Reporting Issues

- Use the [bug report template](https://github.com/FilippDor/power-bi-visual-testing-python/issues/new?template=bug_report.yml) for bugs.
- Use the [feature request template](https://github.com/FilippDor/power-bi-visual-testing-python/issues/new?template=feature_request.yml) for suggestions.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this standard.
