# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT
"""
Tests for the ProcessGlobals registry of process-wide caches.

Deliberately stdlib-only (no nora-fleet imports), so the registry mechanics
are testable in any environment that can collect the suite; the real owner
modules are only validated when a test run happens to have imported them.
"""

import sys
import types
from unittest import TestCase
from unittest.mock import patch

from coded_tools.agent_network_editor.globals import ProcessGlobals


class TestProcessGlobals(TestCase):
    """Tests for the registry triples and the clear-all helper."""

    def test_clear_all_clears_imported_owners_and_skips_unimported(self):
        """The registry clears imported owners and skips unimported ones."""
        cleared: list[str] = []

        class FakeOwner:  # pylint: disable=too-few-public-methods
            """Stand-in owner class exposing a clear method like the real caches."""

            @classmethod
            def clear_fake_for_testing(cls):
                """Record that the registry reached this clear method."""
                cleared.append("cleared")

        fake_module = types.ModuleType("fake_process_globals_owner_module")
        fake_module.FakeOwner = FakeOwner
        registry = [
            ("fake_process_globals_owner_module", "FakeOwner", "clear_fake_for_testing"),
            # Never imported: must be skipped silently (an unimported module
            # cannot have a populated cache), not raise.
            ("module_that_was_never_imported_for_test", "Nope", "clear_nope_for_testing"),
        ]
        with patch.dict(sys.modules, {"fake_process_globals_owner_module": fake_module}):
            with patch.object(ProcessGlobals, "REGISTRY", registry):
                ProcessGlobals.clear_all_for_testing()
        self.assertEqual(cleared, ["cleared"])

    def test_registry_entries_resolve_when_imported(self):
        """Registry triples must resolve against any imported owner module."""
        for module_name, class_name, clear_method_name in ProcessGlobals.REGISTRY:
            self.assertTrue(module_name.startswith("coded_tools."))
            # Owner modules need nora-fleet, so only validate the ones this test
            # run happens to have imported; a typo'd class or method name in an
            # imported module must fail here rather than being skipped silently.
            module = sys.modules.get(module_name)
            if module is not None:
                self.assertTrue(callable(getattr(getattr(module, class_name), clear_method_name)))
