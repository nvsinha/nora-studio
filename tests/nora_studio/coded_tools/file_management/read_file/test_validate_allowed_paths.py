# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from unittest import TestCase

from nora_studio.coded_tools.file_management.read_file import ReadFile


class TestValidateAllowedPaths(TestCase):
    """Unit tests for ReadFile._validate_allowed_paths."""

    def setUp(self):
        self.tool = ReadFile()

    def _call(self, args):
        """Invoke _validate_allowed_paths and return the result."""
        return self.tool._validate_allowed_paths(args)  # pylint: disable=protected-access

    def test_missing_key_raises_invalid_input(self):
        """Tests that omitting allowed_paths raises invalid_input (required parameter)."""
        with self.assertRaises(ValueError) as ctx:
            self._call({})
        self.assertIn("invalid_input", str(ctx.exception))

    def test_empty_list_raises_invalid_input(self):
        """Tests that an empty allowed_paths list raises invalid_input."""
        with self.assertRaises(ValueError) as ctx:
            self._call({"allowed_paths": []})
        self.assertIn("invalid_input", str(ctx.exception))

    def test_valid_list_returned(self):
        """Tests that a non-empty list of path strings is returned."""
        self.assertEqual(self._call({"allowed_paths": ["/a", "/b"]}), ["/a", "/b"])

    def test_single_string_coerced(self):
        """Tests that a single string is coerced into a one-element list."""
        self.assertEqual(self._call({"allowed_paths": "/a"}), ["/a"])
