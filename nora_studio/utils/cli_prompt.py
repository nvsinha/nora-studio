# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

"""Shared key-binding helpers for questionary prompts.

Esc is bound ``eager=True`` so the binding fires on a bare Escape press without
waiting out the prompt_toolkit Esc-as-meta-prefix timeout. Composite keys (arrow
keys, etc.) arrive at prompt_toolkit pre-assembled by the terminal, so they
aren't affected by the eager binding.
"""

from typing import Any

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding import merge_key_bindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.keys import Keys


class CliPrompt:
    """Bind extra keys onto a ``questionary`` prompt before ``.ask()`` is called.

    Two flavours:

    - :py:meth:`bind_back_keys` — ← / Esc resolve a sub-menu prompt to a caller-supplied
      back sentinel. The two keys play the same role ("go back one screen") so they
      share a binding entry-point.
    - :py:meth:`bind_exit_on_esc` — Esc resolves a top-level prompt to :data:`EXIT`,
      meaning "abort the entire flow". Use on screens where there's nothing to back up
      to (top menu, final confirm).
    """

    EXIT = "__exit__"

    @classmethod
    def bind_back_keys(cls, question: Any, back_sentinel: str) -> Any:
        """Bind ← and Esc → ``back_sentinel`` on a sub-menu prompt. Returns ``question``."""
        cls._bind(question, Keys.Left, back_sentinel)
        cls._bind(question, Keys.Escape, back_sentinel, eager=True)
        return question

    @classmethod
    def bind_exit_on_esc(cls, question: Any) -> Any:
        """Bind Esc → :data:`EXIT` on a prompt with no back target. Returns ``question``."""
        cls._bind(question, Keys.Escape, cls.EXIT, eager=True)
        return question

    @staticmethod
    def _bind(question: Any, key: Keys, sentinel: str, *, eager: bool = False) -> None:
        """Register ``key`` to resolve the prompt to ``sentinel`` via ``event.app.exit``.

        Some questionary prompts (e.g. ``confirm``) expose a read-only ``_MergedKeyBindings``
        on their application — we can't ``.add`` to that directly. Build a fresh writable
        registry, merge it on top of whatever's there, and reassign. This works uniformly
        for both writable and read-only registries.
        """
        extra = KeyBindings()
        registrar = extra.add(key, eager=eager)
        registrar(lambda event: CliPrompt._resolve(event, sentinel))
        # Order matters: put our extra first so it wins over any existing handler for
        # the same key. (questionary.confirm already binds Esc to "no answer / None"; we
        # want our EXIT sentinel to take precedence so the caller can distinguish.)
        existing = question.application.key_bindings
        question.application.key_bindings = merge_key_bindings([extra, existing]) if existing else extra

    @staticmethod
    def _resolve(event: KeyPressEvent, sentinel: str) -> None:
        """Resolve the prompt to ``sentinel`` (questionary returns this from ``ask()``)."""
        event.app.exit(result=sentinel)
