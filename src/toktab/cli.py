"""TokTab CLI - LLM pricing data at your fingertips."""

import json
import os
import sys

import click

from toktab import __version__
from toktab.api import (
    get_model,
    search as api_search,
    ModelNotFoundError,
    APIError,
)
from toktab.display import (
    display_model,
    display_search_results,
    display_error,
)


def _resolve_json_output(explicit_flag: bool) -> bool:
    """Determine whether to use JSON output.

    Priority: --json flag > OUTPUT_FORMAT env var > TTY detection.
    When stdout is not a TTY (piped to another process or an agent),
    default to JSON so AI agents get structured data automatically.
    """
    if explicit_flag:
        return True
    env_format = os.environ.get("OUTPUT_FORMAT", "").lower()
    if env_format == "json":
        return True
    if env_format == "text":
        return False
    # Auto-detect: use JSON when stdout is not a TTY (piped/agent usage)
    return not sys.stdout.isatty()


class TokTabGroup(click.Group):
    """Custom group that allows both subcommands and direct model lookup."""

    def get_command(self, ctx, cmd_name):
        """Override get_command to handle model lookups."""
        # First try to get a real subcommand
        rv = super().get_command(ctx, cmd_name)
        if rv is not None:
            return rv

        # If no subcommand found, create a dynamic command for model lookup
        @click.pass_context
        def model_lookup_command(ctx_inner):
            json_output = _resolve_json_output(
                ctx.params.get('json_output', False)
            )
            try:
                data = get_model(cmd_name)
                display_model(data, json_output=json_output)
            except ModelNotFoundError as e:
                display_error(str(e), json_output=json_output)
                ctx_inner.exit(1)
            except APIError as e:
                display_error(str(e), json_output=json_output)
                ctx_inner.exit(1)

        return click.Command(cmd_name, callback=model_lookup_command)


@click.command(cls=TokTabGroup, invoke_without_command=True)
@click.option("--json", "json_output", is_flag=True, help="Output raw JSON")
@click.option("--version", is_flag=True, help="Show version")
@click.pass_context
def cli(ctx: click.Context, json_output: bool, version: bool) -> None:
    """TokTab - LLM pricing data at your fingertips.

    Get pricing info for a model:

        toktab gpt-4o

    Search for models:

        toktab search claude

    \b
    Agent-friendly features:
        - Auto-detects non-TTY stdout and outputs JSON
        - Set OUTPUT_FORMAT=json env var to force JSON output
        - Use `toktab schema` for machine-readable CLI description
    """
    if version:
        click.echo(f"toktab {__version__}")
        ctx.exit(0)

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument("query")
@click.option("--limit", "-l", default=20, help="Number of results (max 50)")
@click.option("--json", "json_output", is_flag=True, help="Output raw JSON")
def search(query: str, limit: int, json_output: bool) -> None:
    """Search for models by name or provider.

    Examples:

        toktab search claude

        toktab search "gemini 3"

        toktab search provider:anthropic

        toktab search "provider:openai gpt-4"
    """
    json_output = _resolve_json_output(json_output)
    try:
        data = api_search(query, limit=limit)
        display_search_results(data, json_output=json_output)
    except APIError as e:
        display_error(str(e), json_output=json_output)
        raise SystemExit(1)


@cli.command()
def schema() -> None:
    """Output machine-readable CLI schema for agent introspection.

    Returns a JSON description of all commands, arguments, options,
    and API endpoints. AI agents can use this to discover capabilities
    at runtime without needing pre-loaded documentation.
    """
    schema_data = {
        "name": "toktab",
        "version": __version__,
        "description": "LLM pricing data at your fingertips",
        "api_base_url": "https://toktab.com/api",
        "agent_hints": {
            "output_format_env": "OUTPUT_FORMAT",
            "auto_json_on_pipe": True,
            "json_flag": "--json",
        },
        "commands": {
            "<model-slug>": {
                "description": "Get detailed pricing and capability info for a model",
                "arguments": {
                    "slug": {
                        "type": "string",
                        "description": "Model identifier (e.g. gpt-4o, claude-3-opus)",
                        "required": True,
                    }
                },
                "options": {
                    "--json": {
                        "type": "flag",
                        "description": "Output raw JSON",
                    }
                },
                "response_fields": {
                    "litellm_model_name": "string",
                    "litellm_provider": "string",
                    "input_cost_per_token": "number",
                    "output_cost_per_token": "number",
                    "max_tokens": "integer|null",
                    "max_input_tokens": "integer|null",
                    "max_output_tokens": "integer|null",
                    "supports_vision": "boolean",
                    "supports_function_calling": "boolean",
                    "supports_tool_choice": "boolean",
                    "supports_prompt_caching": "boolean",
                    "supports_response_schema": "boolean",
                    "supports_system_messages": "boolean",
                    "supports_audio_input": "boolean",
                    "supports_audio_output": "boolean",
                    "supports_pdf_input": "boolean",
                },
            },
            "search": {
                "description": "Search for models by name or provider",
                "arguments": {
                    "query": {
                        "type": "string",
                        "description": "Search term. Supports 'provider:NAME' prefix filtering",
                        "required": True,
                    }
                },
                "options": {
                    "--limit": {
                        "type": "integer",
                        "default": 20,
                        "max": 50,
                        "description": "Number of results",
                    },
                    "--json": {
                        "type": "flag",
                        "description": "Output raw JSON",
                    },
                },
                "response_fields": {
                    "results": "array of {slug, provider, input_cost_per_token, output_cost_per_token}",
                    "query": "string",
                    "count": "integer",
                },
            },
            "schema": {
                "description": "Output this machine-readable CLI schema",
            },
        },
    }
    click.echo(json.dumps(schema_data, indent=2))


if __name__ == "__main__":
    cli()
