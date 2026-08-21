# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from unittest import TestCase

from nora_studio.coded_tools.file_management.read_file import ReadFile


class TestValidateExtensionList(TestCase):
    """Unit tests for ReadFile._validate_extension_list."""

    def setUp(self):
        self.tool = ReadFile()

    def _call(self, value, param_name="test_param"):
        """Invoke _validate_extension_list with the given value and return the result."""
        return self.tool._validate_extension_list(value, param_name)  # pylint: disable=protected-access

    def test_none_returned_as_none_sentinel(self):
        """Tests that None is preserved (sentinel: omitted = skip filtering)."""
        self.assertIsNone(self._call(None))

    def test_empty_list_returned_as_empty(self):
        """Tests that an empty list is preserved (means deny all extensions)."""
        self.assertEqual(self._call([]), [])

    def test_single_string_coerced_to_list(self):
        """Tests that a single string extension is coerced into a one-element list."""
        self.assertEqual(self._call(".py"), [".py"])

    def test_valid_list_returned_unchanged(self):
        """Tests that a valid list of extension strings is returned unchanged."""
        exts = [".py", ".md"]
        self.assertEqual(self._call(exts), exts)

    def test_non_list_non_string_raises(self):
        """Tests that a non-list, non-string value raises ValueError with invalid_input."""
        with self.assertRaises(ValueError) as ctx:
            self._call(42)
        self.assertIn("invalid_input", str(ctx.exception))

    def test_list_with_non_string_element_raises(self):
        """Tests that a list containing a non-string element raises ValueError with invalid_input."""
        with self.assertRaises(ValueError) as ctx:
            self._call([".py", 1])
        self.assertIn("invalid_input", str(ctx.exception))
