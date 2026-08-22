# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

"""Shared status-line helpers for ``nora`` CLI commands.

The init/import/export commands all surface step-by-step progress with the same prefixed
style — ``[ok]``, ``[skip]``, ``[warn]``, ``[err]``, ``[info]``. Centralizing the helpers
keeps the column alignment and Rich color scheme consistent across commands; emoji are
intentionally avoided so the output renders the same in CI logs, plain terminals, and
copy-pasted tickets.

Rich treats bare ``[xxx]`` as markup, so the leading bracket is escaped with a backslash
in each format string.
"""

from rich.console import Console


class CliStatus:
    """Shared status-line printers for ``nora`` CLI commands."""

    # Class-level Console — Rich is happy to share one across writers, and the
    # printers stay cheap to call from any command module.
    _console = Console()

    @classmethod
    def ok(cls, msg: str) -> None:
        """Successful step (file copied, action completed)."""
        cls._console.print(f"[green]\\[ok][/green]    {msg}")

    @classmethod
    def skip(cls, msg: str) -> None:
        """Step intentionally skipped (idempotent re-run, already-present target)."""
        cls._console.print(f"[yellow]\\[skip][/yellow]  {msg}")

    @classmethod
    def warn(cls, msg: str) -> None:
        """Recoverable issue worth surfacing (missing dep, unknown spec) but not fatal."""
        cls._console.print(f"[yellow]\\[warn][/yellow]  {msg}")

    @classmethod
    def err(cls, msg: str) -> None:
        """Failure that aborts the action — typically followed by ``sys.exit(1)``."""
        cls._console.print(f"[red]\\[err][/red]   {msg}")

    @classmethod
    def info(cls, msg: str) -> None:
        """Neutral progress line (analyzing, importing, summarizing)."""
        cls._console.print(f"[cyan]\\[info][/cyan]  {msg}")
