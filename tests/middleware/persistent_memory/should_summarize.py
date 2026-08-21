# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

"""Test helper: a callable that mirrors ``TopicSummarizer.should_summarize``."""

from __future__ import annotations


class ShouldSummarize:  # pylint: disable=too-few-public-methods
    """Callable wrapping the ``max_topic_size`` threshold used in tests.

    Mirrors :py:meth:`TopicSummarizer.should_summarize` so mocks can be
    swapped in without recreating the threshold logic in every test.
    """

    def __init__(self, threshold: int) -> None:
        self._threshold: int = threshold

    def __call__(self, content: str) -> bool:
        """Return ``True`` when ``content`` exceeds the configured threshold."""
        return self._threshold > 0 and len(content) > self._threshold
