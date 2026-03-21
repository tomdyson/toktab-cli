"""Tests for the CLI commands."""

import json

import pytest
from click.testing import CliRunner

from toktab.cli import cli, _resolve_json_output


@pytest.fixture
def runner():
    return CliRunner()


class TestCLI:
    def test_help(self, runner):
        """Test --help shows usage."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "TokTab" in result.output
        assert "search" in result.output

    def test_version(self, runner):
        """Test --version shows version."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "toktab" in result.output

    def test_no_args_shows_help(self, runner):
        """Test running without args shows help."""
        result = runner.invoke(cli, [])
        assert result.exit_code == 0
        assert "Usage:" in result.output


class TestModelCommand:
    def test_model_lookup(self, runner, httpx_mock):
        """Test looking up a model."""
        httpx_mock.add_response(
            json={
                "litellm_model_name": "gpt-4o",
                "litellm_provider": "openai",
                "input_cost_per_token": 0.0000025,
                "output_cost_per_token": 0.00001,
            }
        )

        result = runner.invoke(cli, ["gpt-4o"])

        assert result.exit_code == 0
        assert "gpt-4o" in result.output

    def test_model_json_output(self, runner, httpx_mock):
        """Test --json outputs valid JSON."""
        mock_data = {
            "litellm_model_name": "gpt-4o",
            "litellm_provider": "openai",
        }
        httpx_mock.add_response(json=mock_data)

        result = runner.invoke(cli, ["--json", "gpt-4o"])

        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert parsed["litellm_model_name"] == "gpt-4o"

    def test_model_not_found(self, runner, httpx_mock):
        """Test error message for unknown model."""
        httpx_mock.add_response(status_code=404)

        result = runner.invoke(cli, ["nonexistent"])

        assert result.exit_code == 1
        assert "not found" in result.output


class TestSearchCommand:
    def test_search(self, runner, httpx_mock):
        """Test search command."""
        httpx_mock.add_response(
            json={
                "results": [{"slug": "claude-3-opus", "provider": "anthropic"}],
                "query": "claude",
                "count": 1,
            }
        )

        result = runner.invoke(cli, ["search", "claude"])

        assert result.exit_code == 0
        assert "claude-3-opus" in result.output

    def test_search_with_limit(self, runner, httpx_mock):
        """Test search with --limit."""
        httpx_mock.add_response(
            json={"results": [], "query": "test", "count": 0}
        )

        result = runner.invoke(cli, ["search", "--limit", "5", "test"])

        assert result.exit_code == 0
        request = httpx_mock.get_request()
        assert "limit=5" in str(request.url)

    def test_search_json_output(self, runner, httpx_mock):
        """Test search --json outputs valid JSON."""
        mock_data = {"results": [], "query": "test", "count": 0}
        httpx_mock.add_response(json=mock_data)

        result = runner.invoke(cli, ["search", "--json", "test"])

        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert "results" in parsed


class TestSchemaCommand:
    def test_schema_outputs_valid_json(self, runner):
        """Test schema command outputs valid JSON."""
        result = runner.invoke(cli, ["schema"])

        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert parsed["name"] == "toktab"
        assert "commands" in parsed

    def test_schema_contains_commands(self, runner):
        """Test schema describes all commands."""
        result = runner.invoke(cli, ["schema"])
        parsed = json.loads(result.output)

        assert "<model-slug>" in parsed["commands"]
        assert "search" in parsed["commands"]
        assert "schema" in parsed["commands"]

    def test_schema_contains_agent_hints(self, runner):
        """Test schema includes agent-friendly metadata."""
        result = runner.invoke(cli, ["schema"])
        parsed = json.loads(result.output)

        hints = parsed["agent_hints"]
        assert hints["output_format_env"] == "OUTPUT_FORMAT"
        assert hints["auto_json_on_pipe"] is True
        assert hints["json_flag"] == "--json"

    def test_schema_contains_version(self, runner):
        """Test schema includes version."""
        from toktab import __version__
        result = runner.invoke(cli, ["schema"])
        parsed = json.loads(result.output)

        assert parsed["version"] == __version__


class TestOutputFormatResolution:
    def test_explicit_json_flag(self, monkeypatch):
        """Test --json flag takes priority."""
        monkeypatch.setenv("OUTPUT_FORMAT", "text")
        assert _resolve_json_output(True) is True

    def test_env_json(self, monkeypatch):
        """Test OUTPUT_FORMAT=json enables JSON."""
        monkeypatch.setenv("OUTPUT_FORMAT", "json")
        assert _resolve_json_output(False) is True

    def test_env_text(self, monkeypatch):
        """Test OUTPUT_FORMAT=text forces text output."""
        monkeypatch.setenv("OUTPUT_FORMAT", "text")
        assert _resolve_json_output(False) is False

    def test_tty_detection_non_tty(self, monkeypatch):
        """Test non-TTY stdout defaults to JSON."""
        monkeypatch.delenv("OUTPUT_FORMAT")
        monkeypatch.setattr("sys.stdout.isatty", lambda: False)
        assert _resolve_json_output(False) is True

    def test_tty_detection_tty(self, monkeypatch):
        """Test TTY stdout defaults to text."""
        monkeypatch.delenv("OUTPUT_FORMAT")
        monkeypatch.setattr("sys.stdout.isatty", lambda: True)
        assert _resolve_json_output(False) is False


class TestStructuredErrors:
    def test_model_not_found_json_error(self, runner, httpx_mock):
        """Test error output is structured JSON when --json is used."""
        httpx_mock.add_response(status_code=404)

        result = runner.invoke(cli, ["--json", "nonexistent"])

        assert result.exit_code == 1
        error_data = json.loads(result.stderr)
        assert error_data["error"] is True
        assert "not found" in error_data["message"]

    def test_search_error_json(self, runner, httpx_mock):
        """Test search error with --json outputs structured error."""
        httpx_mock.add_response(status_code=400)

        result = runner.invoke(cli, ["search", "--json", ""])

        assert result.exit_code == 1
        error_data = json.loads(result.stderr)
        assert error_data["error"] is True
        assert "message" in error_data
