# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from nora_studio.coded_tools.file_management.read_file import MAX_FILE_BYTES
from nora_studio.coded_tools.file_management.read_file import ReadFile


class TestCheckFileSize(TestCase):
    """Unit tests for ReadFile._check_file_size."""

    def setUp(self):
        self.tool = ReadFile()
        self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.tmp_root = Path(self.tmpdir.name).resolve()

    def tearDown(self):
        self.tmpdir.cleanup()

    def _call(self, path: Path) -> None:
        """Invoke _check_file_size; returns None or raises."""
        self.tool._check_file_size(path)  # pylint: disable=protected-access

    def test_small_file_passes(self):
        """Tests that a small file passes the size check."""
        path = self.tmp_root / "small.txt"
        path.write_text("x" * 100, encoding="utf-8")
        self._call(path)  # should not raise

    def test_file_at_limit_passes(self):
        """Tests that a file exactly at the limit is allowed (boundary)."""
        path = self.tmp_root / "at_limit.txt"
        # Don't actually create a 10MB file — mock stat() instead.
        path.write_text("x", encoding="utf-8")
        with patch.object(Path, "stat") as mock_stat:
            mock_stat.return_value.st_size = MAX_FILE_BYTES
            self._call(path)  # should not raise

    def test_file_over_limit_raises(self):
        """Tests that a file one byte over the limit raises file_too_large."""
        path = self.tmp_root / "over.txt"
        path.write_text("x", encoding="utf-8")
        with patch.object(Path, "stat") as mock_stat:
            mock_stat.return_value.st_size = MAX_FILE_BYTES + 1
            with self.assertRaises(ValueError) as ctx:
                self._call(path)
        self.assertIn("file_too_large", str(ctx.exception))

    def test_stat_error_surfaces_as_read_error(self):
        """Tests that an OSError from stat() is wrapped as read_error."""
        path = self.tmp_root / "nope.txt"
        with patch.object(Path, "stat", side_effect=OSError("permission denied")):
            with self.assertRaises(ValueError) as ctx:
                self._call(path)
        self.assertIn("read_error", str(ctx.exception))
