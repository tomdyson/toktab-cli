# TokTab CLI - Project Guide for Claude

This document provides context for AI assistants working on this project.

## Project Overview

TokTab CLI is a command-line tool for querying LLM pricing data from the TokTab API ([toktab.com](https://toktab.com/)). The API provides pricing and capability information for 2000+ LLM models, sourced from LiteLLM and updated nightly.

## Architecture

```
toktab-cli/
├── src/toktab/
│   ├── __init__.py       # Version info
│   ├── cli.py            # Click CLI commands and TokTabGroup
│   ├── api.py            # httpx API client for TokTab
│   └── display.py        # Rich formatting for terminal output
├── tests/
│   ├── test_api.py       # API client tests (httpx mocking)
│   ├── test_cli.py       # CLI tests (CliRunner)
│   └── test_display.py   # Display formatting tests
├── pyproject.toml        # Package config, dependencies
└── README.md             # User documentation
```

## Tech Stack

- **Python 3.10+** - Modern type hints
- **Click 8.0+** - CLI framework
- **httpx 0.24+** - HTTP client
- **Rich 13.0+** - Terminal formatting
- **pytest** - Testing framework
- **pytest-httpx** - httpx mocking for tests

## Key Implementation Details

### CLI Design Pattern

The CLI uses a custom `TokTabGroup` that extends `click.Group` to support both:
1. **Subcommands**: `toktab search <query>`
2. **Direct model lookup**: `toktab <model-slug>` (treated as a dynamic command)

The `get_command()` method checks if the argument matches a registered subcommand. If not, it creates a dynamic command that performs a model lookup.

### API Client

- Base URL: `https://toktab.com/api`
- Endpoints:
  - `GET /api/{slug}/` - Get model details
  - `GET /api/search?q=<query>&limit=<N>` - Search models
- Error handling: Custom exceptions (`ModelNotFoundError`, `APIError`)
- Timeout: 10 seconds

### Display Formatting

- **Costs**: Displayed per million tokens (e.g., `$2.50 / 1M`) instead of per token
- **Color coding**:
  - Green: < $1 per million tokens
  - Yellow: $1-10 per million tokens
  - Red: > $10 per million tokens
- **Token counts**: Formatted with K/M suffixes (e.g., `128K`, `1M`)
- **JSON output**: Available via `--json` flag on all commands

## Publishing a New Release

**Important**: The package is published to PyPI as `toktab` via GitHub Actions.

### Release Process

1. **Update version** in `pyproject.toml`:
   ```toml
   version = "0.2.0"  # Increment version
   ```

2. **Commit and push**:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.2.0"
   git push
   ```

3. **Create and push git tag**:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

4. **Create GitHub release**:
   ```bash
   gh release create v0.2.0 --title "v0.2.0 - Release Title" --notes "Release notes"
   ```

5. **Automated publishing**: GitHub Actions (`.github/workflows/publish.yml`) will:
   - Build the package with `python -m build`
   - Publish to PyPI using trusted publishing
   - Package appears at [pypi.org/project/toktab](https://pypi.org/project/toktab/)

### PyPI Setup

The project uses **PyPI Trusted Publishing** (no API tokens needed):
- Publisher: `tomdyson/toktab-cli`
- Workflow: `publish.yml`
- Configured at: [pypi.org/manage/project/toktab/settings/publishing/](https://pypi.org/manage/project/toktab/settings/publishing/)

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=toktab

# Run specific test file
pytest tests/test_cli.py

# Run specific test
pytest tests/test_cli.py::TestModelCommand::test_model_lookup
```

All tests use `pytest-httpx` for mocking HTTP requests. Tests achieve 100% coverage of core functionality.

## Development Workflow

```bash
# Setup
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Make changes
# ... edit code ...

# Run tests
pytest

# Test locally
toktab gpt-4o
toktab search claude

# Test from PyPI (after publishing)
uvx toktab@latest gpt-4o
```

## Code Style

- **Type hints**: Required for all function signatures
- **Docstrings**: Google style for all public functions
- **Error handling**: Use custom exceptions, provide user-friendly messages
- **Formatting**: Rich output by default, JSON via `--json` flag

## API Response Examples

### Model Details (`/api/{slug}/`)
```json
{
  "litellm_model_name": "gpt-4o",
  "litellm_provider": "openai",
  "input_cost_per_token": 0.0000025,
  "output_cost_per_token": 0.00001,
  "max_tokens": 128000,
  "max_input_tokens": 128000,
  "max_output_tokens": 16384,
  "supports_vision": true,
  "supports_function_calling": true
}
```

### Search Results (`/api/search?q=...`)
```json
{
  "results": [
    {
      "slug": "claude-3-opus",
      "provider": "anthropic",
      "input_cost_per_token": 0.000015,
      "output_cost_per_token": 0.000075
    }
  ],
  "query": "claude",
  "count": 20
}
```

## Common Tasks

### Adding a new command
1. Add command function with `@cli.command()` decorator in `cli.py`
2. Add corresponding display function in `display.py`
3. Add tests in `tests/test_cli.py`

### Updating dependencies
1. Modify `dependencies` in `pyproject.toml`
2. Run `uv pip install -e ".[dev]"` to update lock
3. Test thoroughly before releasing

### Debugging
- Use `click.testing.CliRunner` for CLI testing
- Use `pytest-httpx` fixtures for API mocking
- Check GitHub Actions logs for CI/CD issues

## Important Notes

- **No API key required** - The TokTab API is free and public
- **Model slugs** - Derived from LiteLLM names with special chars → hyphens
- **Search query** - Minimum 1 character (API rejects empty queries)
- **Provider filtering** - Use `provider:anthropic` syntax in search

## Resources

- **TokTab API**: [toktab.com](https://toktab.com/)
- **OpenAPI Spec**: [toktab.com/openapi.json](https://toktab.com/openapi.json)
- **PyPI Package**: [pypi.org/project/toktab](https://pypi.org/project/toktab/)
- **GitHub Repo**: [github.com/tomdyson/toktab-cli](https://github.com/tomdyson/toktab-cli)
- **LiteLLM**: [github.com/BerriAI/litellm](https://github.com/BerriAI/litellm)
