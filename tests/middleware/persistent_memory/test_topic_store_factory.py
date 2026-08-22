# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

"""Tests for ``TopicStoreFactory`` backend selection."""

from __future__ import annotations

from middleware.persistent_memory.json_file_store import JsonFileStore
from middleware.persistent_memory.markdown_file_store import MarkdownFileStore
from middleware.persistent_memory.topic_store_factory import TopicStoreFactory
from tests.middleware.persistent_memory.base import MemoryTestBase


class TopicStoreFactoryTests(MemoryTestBase):
    """Factory dispatch tests."""

    def test_default_backend_is_json_file(self) -> None:
        """With no config supplied the factory builds a JSON-backed store."""
        store = TopicStoreFactory.create(None)
        self.assertIsInstance(store, JsonFileStore)

    def test_markdown_file_backend(self) -> None:
        """``markdown_file`` yields a markdown-backed store."""
        store = TopicStoreFactory.create({"backend": "markdown_file", "folder_name": self._tmp})
        self.assertIsInstance(store, MarkdownFileStore)

    def test_unknown_backend_raises(self) -> None:
        """An unrecognized backend name raises ``ValueError``."""
        with self.assertRaises(ValueError):
            TopicStoreFactory.create({"backend": "no_such_backend"})

    def test_file_name_propagates_to_json_backend(self) -> None:
        """The ``file_name`` HOCON field is forwarded to ``JsonFileStore``."""
        store = TopicStoreFactory.create({"backend": "json_file", "folder_name": self._tmp, "file_name": "notes"})
        self.assertIsInstance(store, JsonFileStore)
        # Internal check: the resolved file path uses the custom stem.
        path = store._path_for("net.agent")  # pylint: disable=protected-access
        self.assertTrue(str(path).endswith("notes.json"))

    def test_backend_name_normalized(self) -> None:
        """Backend names are lower-cased and stripped before dispatch."""
        store = TopicStoreFactory.create({"backend": "  MARKDOWN_FILE  ", "folder_name": self._tmp})
        self.assertIsInstance(store, MarkdownFileStore)
