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


class TestCheckPathExists(TestCase):
    """Unit tests for ReadFile._check_path_exists."""

    def setUp(self):
        self.tool = ReadFile()
        self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.tmp_root = Path(self.tmpdir.name).resolve()

    def tearDown(self):
        self.tmpdir.cleanup()

    def _call(self, path: Path) -> None:
        """Invoke _check_path_exists; returns None or raises."""
        self.tool._check_path_exists(path)  # pylint: disable=protected-access

    def test_existing_file_passes(self):
        """Tests that an existing regular file passes the check."""
        path = self.tmp_root / "a.txt"
        path.write_text("x", encoding="utf-8")
        self._call(path)  # should not raise

    def test_nonexistent_path_raises(self):
        """Tests that a missing path raises path_not_found."""
        with self.assertRaises(ValueError) as ctx:
            self._call(self.tmp_root / "missing.txt")
        self.assertIn("path_not_found", str(ctx.exception))

    def test_directory_raises(self):
        """Tests that a directory raises is_a_directory."""
        with self.assertRaises(ValueError) as ctx:
            self._call(self.tmp_root)
        self.assertIn("is_a_directory", str(ctx.exception))
