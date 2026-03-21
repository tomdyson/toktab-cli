# TokTab CLI

> LLM pricing data at your fingertips

A command-line interface for accessing [TokTab](https://toktab.com/), a free API providing pricing data for 2000+ LLM models. Powered by [LiteLLM](https://github.com/BerriAI/litellm) and updated nightly.

## Installation

```bash
# Using uvx (recommended)
uvx toktab gpt-4o

# Or install with pip
pip install toktab
```

## Usage

### Get pricing info for a specific model

```bash
toktab gpt-4o
toktab claude-3-opus
toktab gemini-1-5-flash
```

Output:
```
╭──────────────────────────────────────────────────────────────────────────────╮
│ gpt-4o (openai)                                                               │
╰──────────────────────────────────────────────────────────────────────────────╯

Pricing
 Type    Cost / 1M tokens 
 Input              $2.50 
 Output            $10.00 

Context Window
 Limit       Tokens 
 Max input      128K 
 Max output      16K 

Capabilities
✓ Vision · ✓ Functions · ✓ Tool choice · ✓ System msgs
```

### Search for models

```bash
toktab search claude
toktab search "gemini 3"
toktab search provider:anthropic
```

### JSON output

All commands support `--json` for machine-readable output:

```bash
toktab --json gpt-4o
toktab search --json claude
```

### Options

```
Options:
  --json     Output raw JSON
  --version  Show version
  --help     Show this message and exit.
```

## AI Agent Integration

TokTab CLI is designed to work well with AI agents and automated pipelines.

### Auto-detection

When stdout is not a TTY (e.g. piped to another process), output switches to JSON automatically — no flags needed.

```bash
# Human at a terminal gets rich tables
toktab gpt-4o

# Piped to another process gets JSON
toktab gpt-4o | jq .input_cost_per_token
```

### Environment variable

Set `OUTPUT_FORMAT` to force a specific format:

```bash
export OUTPUT_FORMAT=json  # Always JSON
export OUTPUT_FORMAT=text  # Always rich tables
```

### Schema introspection

Agents can discover CLI capabilities at runtime:

```bash
toktab schema
```

This outputs a machine-readable JSON description of all commands, arguments, options, and API endpoints.

### Structured errors

When JSON output is active, errors are written to stderr as structured JSON:

```json
{"error": true, "message": "Model 'nonexistent' not found"}
```

## Model Slugs

Model identifiers are derived from LiteLLM model names with special characters replaced by hyphens.  
For example:
- `gemini/gemini-pro` → `gemini-gemini-pro`
- `anthropic/claude-3-opus` → `anthropic-claude-3-opus`

Use the search command to find the exact slug for a model.

## Features

- 🚀 **Fast**: Lightweight CLI with minimal dependencies
- 📊 **Rich output**: Beautiful tables with cost color-coding (green=cheap, yellow=medium, red=expensive)
- 🔍 **Fuzzy search**: Find models by name or provider
- 💰 **Cost per million tokens**: Easy-to-read pricing format
- 🎨 **JSON output**: Perfect for scripting and automation
- 🆓 **Free**: No API key required

## Development

```bash
# Clone the repo
gh repo clone tomdyson/toktab-cli
cd toktab-cli

# Install with dev dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Run tests
pytest

# Test locally
toktab gpt-4o
```

## Publishing a New Release

1. **Update the version** in [pyproject.toml](pyproject.toml):
   ```toml
   version = "0.2.0"  # Bump version number
   ```

2. **Commit and push** your changes:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.2.0"
   git push
   ```

3. **Create and push a git tag**:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

4. **Create a GitHub release**:
   ```bash
   gh release create v0.2.0 --title "v0.2.0 - Release Title" --notes "Release notes here"
   ```

5. **Done!** GitHub Actions will automatically build and publish to PyPI.

The package will be live at [pypi.org/project/toktab](https://pypi.org/project/toktab/) within 1-2 minutes.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Credits

- Data sourced from [LiteLLM](https://github.com/BerriAI/litellm)
- API provided by [TokTab](https://toktab.com/)
