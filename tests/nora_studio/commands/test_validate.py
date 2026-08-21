# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

import sys
from unittest import TestCase
from unittest.mock import patch

from nora_studio.commands.validate import ValidateCommand

_MODULE = "nora_studio.commands.validate"


class TestValidateCommandRun(TestCase):
    """Tests for ValidateCommand.run - a thin wrapper over HoconValidatorCli."""

    def test_valid_returns_zero(self):
        """When the underlying validator returns 0, run() returns 0."""
        with patch(f"{_MODULE}.HoconValidatorCli") as mock_cli:
            mock_cli.return_value.main.return_value = 0
            self.assertEqual(ValidateCommand("agent.hocon").run(), 0)

    def test_validation_errors_return_one(self):
        """When the underlying validator returns 1, run() returns 1."""
        with patch(f"{_MODULE}.HoconValidatorCli") as mock_cli:
            mock_cli.return_value.main.return_value = 1
            self.assertEqual(ValidateCommand("agent.hocon").run(), 1)

    def test_load_error_code_two_is_normalized_to_one(self):
        """The library's exit code 2 (load error) is normalized to 1 for studio's CLI."""
        with patch(f"{_MODULE}.HoconValidatorCli") as mock_cli:
            mock_cli.return_value.main.return_value = 2
            self.assertEqual(ValidateCommand("agent.hocon").run(), 1)

    def test_unexpected_validator_error_returns_one(self):
        """An exception raised by the validator is caught and reported as exit code 1."""
        with patch(f"{_MODULE}.HoconValidatorCli") as mock_cli:
            mock_cli.return_value.main.side_effect = AttributeError("boom")
            self.assertEqual(ValidateCommand("agent.hocon").run(), 1)

    def test_builds_argv_from_all_options(self):
        """All command options are marshaled into the argv passed to HoconValidatorCli."""
        captured = {}

        def fake_main():
            captured["argv"] = list(sys.argv)
            return 0

        with patch(f"{_MODULE}.HoconValidatorCli") as mock_cli:
            mock_cli.return_value.main.side_effect = fake_main
            ValidateCommand(
                "agent.hocon",
                verbose=True,
                external_agents="/a,/b",
                mcp_servers="https://mcp.example.com",
                registry_dir="/reg",
            ).run()

        argv = captured["argv"]
        self.assertEqual(argv[1], "agent.hocon")
        self.assertIn("--verbose", argv)
        self.assertIn("--external-agents", argv)
        self.assertIn("/a,/b", argv)
        self.assertIn("--mcp-servers", argv)
        self.assertIn("https://mcp.example.com", argv)
        self.assertIn("--registry-dir", argv)
        self.assertIn("/reg", argv)

    def test_optional_flags_omitted_when_not_set(self):
        """Only the file path is passed when no optional flags are provided."""
        captured = {}

        def fake_main():
            captured["argv"] = list(sys.argv)
            return 0

        with patch(f"{_MODULE}.HoconValidatorCli") as mock_cli:
            mock_cli.return_value.main.side_effect = fake_main
            ValidateCommand("agent.hocon").run()

        argv = captured["argv"]
        self.assertEqual(argv, ["hocon_validator_cli", "agent.hocon"])

    def test_sys_argv_restored_after_success(self):
        """sys.argv is restored after a normal run."""
        before = list(sys.argv)
        with patch(f"{_MODULE}.HoconValidatorCli") as mock_cli:
            mock_cli.return_value.main.return_value = 0
            ValidateCommand("agent.hocon").run()
        self.assertEqual(sys.argv, before)

    def test_sys_argv_restored_after_exception(self):
        """sys.argv is restored even when the validator raises."""
        before = list(sys.argv)
        with patch(f"{_MODULE}.HoconValidatorCli") as mock_cli:
            mock_cli.return_value.main.side_effect = RuntimeError("boom")
            ValidateCommand("agent.hocon").run()
        self.assertEqual(sys.argv, before)
