# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

"""Plugin wrapper for ProcessLogBridge."""

import os

from nora_studio.interfaces.base_plugin import BasePlugin
from nora_studio.interfaces.process_logger_interface import ProcessLoggerInterface
from nora_studio.plugins.log_bridge.process_log_bridge import ProcessLogBridge


class ProcessLogBridgePlugin(BasePlugin, ProcessLoggerInterface):
    """
    Plugin wrapper for ProcessLogBridge.

    Implements ProcessLoggerInterface so that nora_studio/commands/run.py can detect pipe draining
    via isinstance check and fall back to a simple logger if this plugin is disabled.
    """

    def __init__(self, args=None):
        """
        Initialize the plugin and its internal ProcessLogBridge instance.

        :param args (dict | None): Optional configuration for the logging bridge.
        """
        super().__init__("ProcessLogBridgePlugin", args)
        self.log_file = os.path.join(self.args.get("logs_dir", "logs"), "runner.log")
        self.log_bridge = ProcessLogBridge(
            level=self.args.get("log_level", "info"),
            runner_log_file=self.log_file,
        )

    def attach_process_logger(self, process, process_name: str, log_file: str) -> None:
        """Delegate to the internal ProcessLogBridge instance.

        Args:
            process: A running subprocess with .stdout and .stderr pipes.
            process_name: Human-readable label for the process.
            log_file: Path to the file where raw output should be mirrored.
        """
        self.log_bridge.attach_process_logger(process, process_name, log_file)

    def post_server_start_action(self):
        """Attach process logger after the server starts."""
        process = self.args.get("process")
        process_name = self.args.get("process_name", "UnnamedProcess")
        log_file = self.args.get("log_file", self.log_file)
        self.attach_process_logger(process, process_name, log_file)
