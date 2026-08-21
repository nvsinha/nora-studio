# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

import tempfile
from pathlib import Path
from unittest import TestCase

from nora_studio.coded_tools.file_management.read_file import ReadFile


class TestResolvePath(TestCase):
    """Unit tests for ReadFile._resolve_path."""

    def setUp(self):
        self.tool = ReadFile()
        self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.tmp_root = Path(self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def _call(self, args):
        """Invoke _resolve_path with the given args dict and return the result."""
        return self.tool._resolve_path(args)  # pylint: disable=protected-access

    def test_resolves_existing_file(self):
        """Tests that an existing file path is resolved to an absolute Path."""
        path = self.tmp_root / "a.txt"
        path.write_text("x", encoding="utf-8")
        self.assertEqual(self._call({"file_path": str(path)}), path.resolve())

    def test_resolves_nonexistent_path(self):
        """Tests that a nonexistent path still resolves without raising (no fs access)."""
        path = self.tmp_root / "nope.txt"
        result = self._call({"file_path": str(path)})
        self.assertEqual(result, path.resolve())

    def test_empty_string_raises(self):
        """Tests that an empty string path raises invalid_input."""
        with self.assertRaises(ValueError) as ctx:
            self._call({"file_path": ""})
        self.assertIn("invalid_input", str(ctx.exception))

    def test_whitespace_only_raises(self):
        """Tests that a whitespace-only path raises invalid_input after stripping."""
        with self.assertRaises(ValueError) as ctx:
            self._call({"file_path": "   "})
        self.assertIn("invalid_input", str(ctx.exception))

    def test_missing_key_raises(self):
        """Tests that an args dict missing the 'file_path' key raises invalid_input."""
        with self.assertRaises(ValueError) as ctx:
            self._call({})
        self.assertIn("invalid_input", str(ctx.exception))

    def test_non_string_raises(self):
        """Tests that a non-string path raises invalid_input."""
        with self.assertRaises(ValueError) as ctx:
            self._call({"file_path": 123})
        self.assertIn("invalid_input", str(ctx.exception))
