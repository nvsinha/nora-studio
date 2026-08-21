# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

"""Tests for the ProcessLogBridgePlugin wrapper."""

from unittest.mock import MagicMock
from unittest.mock import patch

from nora_studio.interfaces.base_plugin import BasePlugin
from nora_studio.interfaces.process_logger_interface import ProcessLoggerInterface
from nora_studio.plugins.log_bridge.process_log_bridge_plugin import ProcessLogBridgePlugin


class TestProcessLogBridgePlugin:
    """Tests for ProcessLogBridgePlugin."""

    def test_extends_base_plugin(self):
        """Test that ProcessLogBridgePlugin is a BasePlugin subclass."""
        assert issubclass(ProcessLogBridgePlugin, BasePlugin)

    def test_implements_process_logger_interface(self):
        """Test that ProcessLogBridgePlugin implements ProcessLoggerInterface."""
        assert issubclass(ProcessLogBridgePlugin, ProcessLoggerInterface)

    @patch("nora_studio.plugins.log_bridge.process_log_bridge_plugin.ProcessLogBridge")
    def test_constructor_sets_plugin_name(self, _mock_bridge):
        """Test that the constructor sets the plugin name."""
        plugin = ProcessLogBridgePlugin(args={"logs_dir": "/tmp"})
        assert plugin.plugin_name == "ProcessLogBridgePlugin"

    @patch("nora_studio.plugins.log_bridge.process_log_bridge_plugin.ProcessLogBridge")
    def test_constructor_creates_bridge(self, mock_bridge_cls):
        """Test that the log bridge is always created."""
        plugin = ProcessLogBridgePlugin(args={"logs_dir": "/tmp", "log_level": "info"})
        mock_bridge_cls.assert_called_once()
        assert plugin.log_bridge is not None

    @patch("nora_studio.plugins.log_bridge.process_log_bridge_plugin.ProcessLogBridge")
    def test_post_server_start_action_attaches_logger(self, mock_bridge_cls):
        """Test that post_server_start_action attaches process logger."""
        mock_bridge = MagicMock()
        mock_bridge_cls.return_value = mock_bridge
        mock_process = MagicMock()

        plugin = ProcessLogBridgePlugin(args={"logs_dir": "/tmp", "log_level": "info"})
        plugin.args["process"] = mock_process
        plugin.args["process_name"] = "TestProcess"
        plugin.post_server_start_action()

        mock_bridge.attach_process_logger.assert_called_once_with(mock_process, "TestProcess", plugin.log_file)

    @patch("nora_studio.plugins.log_bridge.process_log_bridge_plugin.ProcessLogBridge")
    def test_attach_process_logger_delegates_to_bridge(self, mock_bridge_cls):
        """Test that attach_process_logger delegates to the internal bridge."""
        mock_bridge = MagicMock()
        mock_bridge_cls.return_value = mock_bridge
        mock_process = MagicMock()

        plugin = ProcessLogBridgePlugin(args={"logs_dir": "/tmp", "log_level": "info"})
        plugin.attach_process_logger(mock_process, "TestProcess", "/tmp/test.log")

        mock_bridge.attach_process_logger.assert_called_once_with(mock_process, "TestProcess", "/tmp/test.log")
