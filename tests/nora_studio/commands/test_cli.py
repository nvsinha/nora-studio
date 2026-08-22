# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

"""Tests for the Typer CLI dispatcher and `main()` entry point."""

import os
import sys
from pathlib import Path

import pytest
from pytest import MonkeyPatch

from nora_studio.commands import cli as cli_module
from nora_studio.commands import import_networks as import_networks_module
from nora_studio.commands import init as init_module
from nora_studio.commands import internalize_agents as internalize_agents_module
from nora_studio.commands.cli import main


@pytest.fixture(autouse=True)
def _isolate_cwd(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """Run every test in this module from an empty directory.

    The CLI's top-level callback loads `<cwd>/.env`. Without this, a test invoking main() from a
    repo checkout picks up the developer's real .env and injects those variables into os.environ
    for the rest of the session, making results depend on an untracked file.
    """
    monkeypatch.chdir(tmp_path)


class TestMainEntryPoint:
    """Tests for the `main()` console script entry point."""

    @staticmethod
    def _install_fake_runner(monkeypatch: MonkeyPatch) -> list[str]:
        """Replace NoraFleetRunner with a recording stand-in and return the call log."""
        call_order: list[str] = []

        class FakeRunner:  # pylint: disable=too-few-public-methods
            """Stand-in for NoraFleetRunner that records method calls."""

            # pylint: disable-next=unused-argument
            def __init__(self, cli_overrides: dict | None = None, extra_args: list | None = None) -> None:
                call_order.append("init")

            def run(self) -> None:
                """Record that run() was invoked."""
                call_order.append("run")

        monkeypatch.setattr(cli_module, "NoraFleetRunner", FakeRunner)
        return call_order

    def test_main_with_no_args_shows_help(self, monkeypatch: MonkeyPatch) -> None:
        """Bare `nora-studio` should show help and exit cleanly without starting the server."""
        call_order = self._install_fake_runner(monkeypatch)
        monkeypatch.setattr(sys, "argv", ["nora-studio"])
        # typer <0.26 exits 0 after printing help (swallowed by main()); typer >=0.26
        # raises NoArgsIsHelpError -> SystemExit(2). Both are clean help-display outcomes.
        try:
            main()
        except SystemExit as exc:
            assert exc.code in (0, 2)
        assert not call_order

    def test_main_with_run_subcommand_runs_server(self, monkeypatch: MonkeyPatch) -> None:
        """Explicit `nora-studio run` should start the server."""
        call_order = self._install_fake_runner(monkeypatch)
        monkeypatch.setattr(sys, "argv", ["nora-studio", "run"])
        main()
        assert call_order == ["init", "run"]

    def test_main_with_init_subcommand_invokes_init(self, monkeypatch: MonkeyPatch) -> None:
        """`nora-studio init` should invoke InitCommand and NOT NoraFleetRunner."""
        runner_call_order = self._install_fake_runner(monkeypatch)
        init_calls: list[tuple[str | None]] = []

        class FakeInit:  # pylint: disable=too-few-public-methods
            """Stand-in for InitCommand that records the providers_arg it received."""

            def __init__(self, providers_arg: str | None = None) -> None:
                init_calls.append((providers_arg,))

            def run(self) -> None:
                """Record that init.run() was invoked."""
                init_calls.append(("run",))

        monkeypatch.setattr(init_module, "InitCommand", FakeInit)
        monkeypatch.setattr(sys, "argv", ["nora-studio", "init", "--providers", "openai,anthropic"])
        main()
        assert not runner_call_order
        assert init_calls == [("openai,anthropic",), ("run",)]

    def test_main_with_import_positional_passes_tokens_and_force(self, monkeypatch: MonkeyPatch) -> None:
        """`nora-studio import a.hocon b.zip --force` forwards space-separated tokens + force."""
        captured: list = []

        class FakeImport:  # pylint: disable=too-few-public-methods
            """Stand-in for ImportCommand that records constructor kwargs."""

            def __init__(
                self,
                networks_arg: list | None = None,
                force: bool = False,
            ) -> None:
                captured.append({"networks_arg": networks_arg, "force": force})

            def run(self) -> None:
                """No-op."""

        monkeypatch.setattr(import_networks_module, "ImportCommand", FakeImport)
        monkeypatch.setattr(sys, "argv", ["nora-studio", "import", "a.hocon", "b.zip", "--force"])
        main()
        assert captured == [{"networks_arg": ["a.hocon", "b.zip"], "force": True}]

    def test_main_with_internalize_agents_passes_args_through(self, monkeypatch: MonkeyPatch) -> None:
        """`internalize-agents <in> -o <out> --search-paths <p>` forwards all three kwargs."""
        captured: list[dict] = []

        class FakeInternalize:  # pylint: disable=too-few-public-methods
            """Stand-in for InternalizeAgentsCommand that records constructor kwargs."""

            def __init__(
                self,
                input_path: str,
                output_path: str,
                search_paths: str | None = None,
            ) -> None:
                captured.append(
                    {
                        "input_path": input_path,
                        "output_path": output_path,
                        "search_paths": search_paths,
                    }
                )

            def run(self) -> int:
                """Return success so main() does not raise."""
                return 0

        monkeypatch.setattr(internalize_agents_module, "InternalizeAgentsCommand", FakeInternalize)
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "nora-studio",
                "internalize-agents",
                "in.hocon",
                "--output",
                "out.hocon",
                "--search-paths",
                "registries:other",
            ],
        )
        main()
        assert captured == [
            {
                "input_path": "in.hocon",
                "output_path": "out.hocon",
                "search_paths": "registries:other",
            }
        ]

    def test_main_with_internalize_agents_propagates_exit_code(self, monkeypatch: MonkeyPatch) -> None:
        """A non-zero return from InternalizeAgentsCommand.run() should reach SystemExit."""

        class FakeInternalize:  # pylint: disable=too-few-public-methods
            """Stand-in whose run() returns a failure exit code."""

            def __init__(self, **_kwargs) -> None:
                """Accept any kwargs; we only care about the exit code."""

            def run(self) -> int:
                """Return a non-zero exit code to verify it propagates through main()."""
                return 1

        monkeypatch.setattr(internalize_agents_module, "InternalizeAgentsCommand", FakeInternalize)
        monkeypatch.setattr(
            sys,
            "argv",
            ["nora-studio", "internalize-agents", "in.hocon", "-o", "out.hocon"],
        )
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    def test_main_propagates_runner_exceptions(self, monkeypatch: MonkeyPatch) -> None:
        """Exceptions from NoraFleetRunner().run() should bubble up to the caller."""

        class ExplodingRunner:  # pylint: disable=too-few-public-methods
            """Runner whose run() raises, to verify main() does not swallow errors."""

            def __init__(self, cli_overrides: dict | None = None, extra_args: list | None = None) -> None:
                """Accept the runner's constructor kwargs; we only care about run() raising."""

            def run(self) -> None:
                """Raise to simulate a runtime failure."""
                raise RuntimeError("boom")

        monkeypatch.setattr(cli_module, "NoraFleetRunner", ExplodingRunner)
        monkeypatch.setattr(sys, "argv", ["nora-studio", "run"])
        with pytest.raises(RuntimeError, match="boom"):
            main()

    _BUILTIN_RUN_FLAGS = (
        "--server-host",
        "--server-http-port",
        "--nora_flow-port",
        "--log-level",
        "--thinking-file",
        "--client-only",
        "--server-only",
    )

    def test_run_help_lists_all_builtin_flags(self) -> None:
        """Every built-in run flag is a declared Typer option (so it shows in `nora run --help`).

        Inspects the compiled Click command's registered option strings rather than the
        rendered help text, which wraps/ANSI-styles at the terminal width and is flaky in CI.
        """
        # pylint: disable-next=import-outside-toplevel
        from typer.main import get_command

        run_cmd = get_command(cli_module.NoraStudioCli.app).commands["run"]
        declared = {opt for param in run_cmd.params for opt in getattr(param, "opts", [])}
        for flag in self._BUILTIN_RUN_FLAGS:
            assert flag in declared, f"{flag} not declared as a Typer option on `run`"

    def test_run_forwards_flag_values_as_cli_overrides(self, monkeypatch: MonkeyPatch) -> None:
        """A user-supplied flag reaches NoraFleetRunner as a cli_overrides entry."""
        captured: list[dict] = []

        class CapturingRunner:  # pylint: disable=too-few-public-methods
            """Stand-in that records the cli_overrides it was constructed with."""

            # pylint: disable-next=unused-argument
            def __init__(self, cli_overrides: dict | None = None, extra_args: list | None = None) -> None:
                captured.append(cli_overrides or {})

            def run(self) -> None:
                """No-op."""

        monkeypatch.setattr(cli_module, "NoraFleetRunner", CapturingRunner)
        monkeypatch.setattr(sys, "argv", ["nora-studio", "run", "--server-host", "myhost"])
        main()
        assert captured[0]["server_host"] == "myhost"

    @pytest.mark.parametrize("flag", ["--version", "-V"])
    def test_version_flag_prints_version_and_exits(
        self, flag: str, monkeypatch: MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """`nora --version` / `-V` prints the resolved version and exits without starting the server."""
        call_order = self._install_fake_runner(monkeypatch)
        monkeypatch.setattr(
            "nora_studio.utils.version.resolve_version",
            lambda: ("1.2.3", "installed"),
        )
        monkeypatch.setattr(sys, "argv", ["nora-studio", flag])
        # The eager callback raises typer.Exit(0); main() swallows clean exits.
        main()
        assert "nora-studio 1.2.3 (installed)" in capsys.readouterr().out
        assert not call_order


class TestLoadsProjectEnvFile:
    """The top-level callback loads the project .env before a subcommand runs, but not for --help."""

    def test_check_llm_keys_picks_up_dotenv(
        self, tmp_path: Path, monkeypatch: MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """A key defined only in <cwd>/.env is visible to `check-llm-keys` via os.getenv."""
        # tmp_path is already the cwd, via the module's _isolate_cwd fixture.
        (tmp_path / ".env").write_text("OPENAI_API_KEY=sk-from-dotenv-1234567890abcdef\n")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.setattr(sys, "argv", ["nora-studio", "check-llm-keys", "--tier", "1"])
        try:
            main()
        except SystemExit as exc:
            assert exc.code == 0
        assert "sk-f...cdef" in capsys.readouterr().out

    def test_subcommand_help_does_not_load_dotenv(
        self, tmp_path: Path, monkeypatch: MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """`nora run --help` renders help without loading <cwd>/.env.

        Asserts on the side effect rather than the rendered help text, which wraps/ANSI-styles
        at the terminal width and is flaky in CI.
        """
        # tmp_path is already the cwd, via the module's _isolate_cwd fixture.
        (tmp_path / ".env").write_text("NS_STUDIO_HELP_PROBE=loaded\n")
        monkeypatch.delenv("NS_STUDIO_HELP_PROBE", raising=False)
        monkeypatch.setattr(sys, "argv", ["nora-studio", "run", "--help"])
        # --help exits 0 after printing help; main() swallows clean exits.
        main()
        assert "Loaded environment variables from" not in capsys.readouterr().out
        assert os.environ.get("NS_STUDIO_HELP_PROBE") is None
