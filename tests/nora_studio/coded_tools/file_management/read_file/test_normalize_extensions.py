# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from unittest import TestCase

from nora_studio.coded_tools.file_management.read_file import ReadFile


class TestNormalizeExtensions(TestCase):
    """Unit tests for ReadFile._normalize_extensions."""

    def setUp(self):
        self.tool = ReadFile()

    def _call(self, extensions):
        """Invoke _normalize_extensions and return the result list."""
        return self.tool._normalize_extensions(extensions)  # pylint: disable=protected-access

    def test_already_normalized(self):
        """Tests that lowercase dot-prefixed extensions are returned unchanged."""
        self.assertEqual(self._call([".py", ".md"]), [".py", ".md"])

    def test_adds_leading_dot(self):
        """Tests that extensions without a leading dot get one added."""
        self.assertEqual(self._call(["py", "md"]), [".py", ".md"])

    def test_lowercases_extensions(self):
        """Tests that uppercase extensions are lowercased."""
        self.assertEqual(self._call([".PY", ".Md"]), [".py", ".md"])

    def test_mixed_input(self):
        """Tests that a mix of dotted/undotted and case variants is normalized."""
        self.assertEqual(self._call(["PY", ".Md", "txt"]), [".py", ".md", ".txt"])

    def test_empty_list(self):
        """Tests that an empty list returns an empty list."""
        self.assertEqual(self._call([]), [])
