# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from unittest import TestCase

from nora_studio.coded_tools.web_fetch import WebFetch


class TestValidateDomainList(TestCase):
    """Unit tests for WebFetch._validate_domain_list."""

    def setUp(self):
        self.tool = WebFetch()

    def _call(self, value, param_name="test_param"):
        """Invoke _validate_domain_list with the given value and return the result."""
        return self.tool._validate_domain_list(value, param_name)  # pylint: disable=protected-access

    def test_none_returns_empty_list(self):
        """Tests that passing None returns an empty list."""
        self.assertEqual(self._call(None), [])

    def test_single_string_coerced_to_list(self):
        """Tests that a single string domain is coerced into a one-element list."""
        self.assertEqual(self._call("example.com"), ["example.com"])

    def test_valid_list_returned_unchanged(self):
        """Tests that a valid list of domain strings is returned unchanged."""
        domains = ["example.com", "other.org"]
        self.assertEqual(self._call(domains), domains)

    def test_non_list_non_string_raises(self):
        """Tests that a non-list, non-string value raises ValueError with invalid_input."""
        with self.assertRaises(ValueError) as ctx:
            self._call(123)
        self.assertIn("invalid_input", str(ctx.exception))

    def test_list_with_non_string_element_raises(self):
        """Tests that a list containing a non-string element raises ValueError with invalid_input."""
        with self.assertRaises(ValueError) as ctx:
            self._call(["example.com", 42])
        self.assertIn("invalid_input", str(ctx.exception))

    def test_dict_raises(self):
        """Tests that passing a dict raises ValueError with invalid_input."""
        with self.assertRaises(ValueError) as ctx:
            self._call({"domain": "example.com"})
        self.assertIn("invalid_input", str(ctx.exception))
