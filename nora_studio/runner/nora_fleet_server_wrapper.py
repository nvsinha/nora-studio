# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT
"""
Wrapper module that initializes plugins before starting the server.

This module ensures that plugins are initialized in the same Python process as the Nora Fleet server,
allowing, for instance, proper tracing and observability.
"""

import asyncio
import logging
import os
import signal
import sys

# Force the selector event loop on Windows. The default ProactorEventLoop on
# Python 3.8+/Windows can silently stall the in-process sub-network streaming
# used when agent_network_designer invokes /agent_network_editor via
# AsyncDirectAgentSession - the producer task hands chat messages to a
# consumer via an asyncio queue, and that handoff never connects under
# Proactor, so the editor never returns its first tool call.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# pylint: disable=wrong-import-position
from nora_fleet.service.main_loop.server_main_loop import ServerMainLoop  # noqa: E402

from nora_studio.plugins.plugin_loader import PluginLoader  # noqa: E402
from nora_studio.utils.version import studio_version  # noqa: E402


class NoraFleetServerWrapper:  # pylint: disable=too-few-public-methods
    """Wrapper that initializes plugins before starting the Nora Fleet server."""

    def __init__(self):
        """Initialize the plugins."""
        self._logger = logging.getLogger(self.__class__.__name__)
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        if self.root_dir not in sys.path:
            sys.path.insert(0, self.root_dir)

        plugins_file = PluginLoader.resolve_plugins_file(self.root_dir)
        self.plugin_classes = PluginLoader.load_plugin_classes(plugins_file)

        # Instantiate plugins now that args are fully built
        self.args = {}  # Placeholder for any args you want to pass to plugins
        self.plugins = [cls(self.args) for cls in self.plugin_classes]
        for plugin in self.plugins:
            self._logger.info("Loaded plugin: %s", plugin)

        # Expose the studio version via AGENT_VERSION_LIBS env var so the health endpoint reports it
        version = studio_version()
        existing_libs = os.environ.get("AGENT_VERSION_LIBS", "")
        libs_list = []
        for lib in existing_libs.split(" "):
            lib = lib.strip()
            if lib and not lib.startswith("nora-studio"):
                libs_list.append(lib)
        libs_list.append(f"nora-studio:{version}")
        os.environ["AGENT_VERSION_LIBS"] = " ".join(libs_list)

    def run(self):
        """Initialize plugins and run the server main loop."""
        for plugin in self.plugins:
            self._logger.info("Initializing plugin: %s", plugin)
            plugin.initialize()

        # Import and run the actual server main loop
        # Note: ServerMainLoop will parse sys.argv itself, so all command-line
        # arguments (--port, --http_port, etc.) are automatically passed through
        # Convert SIGTERM into SystemExit so Python unwinds through
        # the finally block below, allowing plugins to flush traces.
        # Tornado does not install a SIGTERM handler, so the default
        # action would terminate the process immediately.
        signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))

        try:
            ServerMainLoop().main_loop()
        finally:
            for plugin in self.plugins:
                self._logger.info("Cleaning up plugin: %s", plugin)
                plugin.cleanup()


if __name__ == "__main__":
    wrapper = NoraFleetServerWrapper()
    wrapper.run()
