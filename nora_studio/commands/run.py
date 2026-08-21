# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

import logging
import os
import signal
import socket
import subprocess
import sys
import time
from importlib.util import find_spec
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from timedinput import timedinput

from nora_studio.commands.project_environment import ProjectEnvironment
from nora_studio.interfaces.process_logger_interface import ProcessLoggerInterface
from nora_studio.plugins.plugin_loader import PluginLoader
from nora_studio.runner.simple_process_logger import SimpleProcessLogger

# Long enough to never bite a real user; finite so timedinput is happy and so a
# detached terminal can't hang the process forever.
INPUT_TIMEOUT_SECONDS = 300


class NoraFleetRunner:
    """Command-line tool to run the Nora Fleet server and web client."""

    # pylint: disable=too-many-instance-attributes
    def __init__(self, cli_overrides: Optional[Dict[str, Any]] = None, extra_args: Optional[List[str]] = None):
        """Initialize configuration.

        Args:
            cli_overrides: Values parsed by the Typer `run` command, keyed by the same names
                as ``self.args`` (e.g. ``server_host``). Only user-supplied flags are present;
                they take precedence over env-var defaults and plugin-provided defaults.
            extra_args: Unrecognized CLI tokens forwarded verbatim (plugin-injected flags).
                Retained for the upcoming Typer-native plugin-option contract; unused today.
        """
        self.extra_args: List[str] = extra_args or []
        self._logger = logging.getLogger(self.__class__.__name__)
        self.is_windows = os.name == "nt"
        self.root_dir = Path.cwd()
        self.logs_dir = self.root_dir / "logs"
        self.thinking_file = self.logs_dir / "agent_thinking.txt"
        self.thinking_dir = self.logs_dir / "thinking_dir"
        print(f"Root directory: {self.root_dir}")
        # Shared project-resource resolution (manifest, tool path, mcp, toolbox),
        # also used by `nora chat` so the two commands resolve a project identically.
        # The project .env file is loaded once, globally, by the CLI's top-level
        # callback before any subcommand runs.
        self.project_env = ProjectEnvironment(self.root_dir)

        # Fail fast on a misconfiguration that otherwise surfaces as per-request
        # server errors and an nora_flow client that hangs forever: nora-fleet's
        # built-in Langfuse tracing requires the optional langfuse package.
        if os.getenv("LANGFUSE_ENABLED", "false").strip().lower() == "true" and find_spec("langfuse") is None:
            sys.exit(
                "LANGFUSE_ENABLED=true but the 'langfuse' package is not installed.\n"
                "Install it with: pip install -r nora_studio/plugins/langfuse/requirements.txt\n"
                '(or: pip install "nora-studio[langfuse]"), or set LANGFUSE_ENABLED=false.'
            )

        plugins_file = PluginLoader.resolve_plugins_file(self.root_dir)
        self.plugin_classes = PluginLoader.load_plugin_classes(plugins_file)

        # Default Configuration
        self.args: Dict[str, Any] = {
            "server_host": os.getenv("NORA_SERVER_HOST", "localhost"),
            "server_http_port": int(os.getenv("NORA_SERVER_HTTP_PORT", "8080")),
            "server_connection": str(os.getenv("NORA_SERVER_CONNECTION", "http")),
            "manifest_update_period_seconds": int(os.getenv("AGENT_MANIFEST_UPDATE_PERIOD_SECONDS", "5")),
            # "spawn" is not the fastest, but the safest and most available on all OSes.
            # See comment on the env var in the Dockerfile for more info.
            "manifest_concurrency_context": os.getenv("AGENT_MANIFEST_CONCURRENCY_CONTEXT", "spawn"),
            "default_sly_data": str(os.getenv("DEFAULT_SLY_DATA", "")),
            "nora_flow_host": os.getenv("NORA_FLOW_HOST", "localhost"),
            "nora_flow_port": int(os.getenv("NORA_FLOW_PORT", "4173")),
            "nora_flow_plugin_cruse": os.getenv("NORA_FLOW_PLUGIN_CRUSE", "true").lower() in ("true", "1", "yes"),
            "log_level": os.getenv("LOG_LEVEL", "info"),
            "vite_api_protocol": os.getenv("VITE_API_PROTOCOL", "http"),
            "vite_ws_protocol": os.getenv("VITE_WS_PROTOCOL", "ws"),
            "thinking_file": os.getenv("THINKING_FILE", str(self.thinking_file)),
            "thinking_dir": os.getenv("THINKING_DIR", str(self.thinking_dir)),
            # Ensure all paths are resolved relative to `self.root_dir`
            "agent_manifest_file": self.project_env.resolve_manifest_file(),
            "agent_tool_path": self.project_env.resolve_tool_path(),
            "agent_toolbox_info_file": self.project_env.resolve_toolbox_info_file(),
            "mcp_servers_info_file": self.project_env.resolve_mcp_info_file(),
            "logs_dir": str(self.logs_dir),
            # Run-mode flags default off; a CLI override flips them on. Kept in the base dict
            # so the runner can read them unconditionally regardless of what was passed.
            "client_only": False,
            "server_only": False,
        }

        # Ensure logs directory exists
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.thinking_dir.mkdir(parents=True, exist_ok=True)

        # Instantiate plugins now that args are fully built
        self.plugins = [cls(self.args) for cls in self.plugin_classes]
        for plugin in self.plugins:
            self._logger.info("Loaded plugin: %s", plugin)

        for plugin in self.plugins:
            self._logger.info("Updating args dict with plugin: %s", plugin)
            plugin.update_args_dict(self.args)

        # Apply CLI overrides last so user-supplied flags win over env-var and plugin defaults.
        # Only keys actually passed on the command line are present, so unset flags keep their
        # resolved defaults.
        for key, value in (cli_overrides or {}).items():
            self.args[key] = value

        # Process references
        self.server_process = None
        self.nora_flow_process = None

    def _apply_toolbox_env(self) -> None:
        """Export AGENT_TOOLBOX_INFO_FILE only if a user-provided toolbox path is configured.

        When unset, the nora-fleet framework falls back to its built-in default toolbox,
        so a user-provided file is a pure override and is optional.
        """
        toolbox_file = self.args["agent_toolbox_info_file"]
        if toolbox_file:
            os.environ["AGENT_TOOLBOX_INFO_FILE"] = toolbox_file
            print(f"AGENT_TOOLBOX_INFO_FILE set to: {toolbox_file}")
        else:
            print("AGENT_TOOLBOX_INFO_FILE: (not set — using built-in default toolbox)")

    def set_environment_variables(self):
        """Set required environment variables, optionally using nora-fleet defaults."""
        print("\n" + "=" * 50 + "\n")
        print("Setting environment variables...\n")
        # Common env variables
        self.project_env.set_pythonpath()
        os.environ["AGENT_MANIFEST_FILE"] = self.args["agent_manifest_file"]
        os.environ["AGENT_TOOL_PATH"] = self.args["agent_tool_path"]
        self._apply_toolbox_env()
        os.environ["MCP_SERVERS_INFO_FILE"] = self.args["mcp_servers_info_file"]
        os.environ["NORA_SERVER_CONNECTION"] = self.args["server_connection"]
        os.environ["AGENT_MANIFEST_UPDATE_PERIOD_SECONDS"] = str(self.args["manifest_update_period_seconds"])
        os.environ["AGENT_MANIFEST_CONCURRENCY_CONTEXT"] = str(self.args["manifest_concurrency_context"])
        os.environ["LOG_LEVEL"] = self.args["log_level"]
        print(f"PYTHONPATH set to: {os.environ['PYTHONPATH']}")
        print(f"AGENT_MANIFEST_FILE set to: {os.environ['AGENT_MANIFEST_FILE']}")
        print(f"AGENT_TOOL_PATH set to: {os.environ['AGENT_TOOL_PATH']}")
        print(f"MCP_SERVERS_INFO_FILE set to: {os.environ['MCP_SERVERS_INFO_FILE']}")
        print(f"NORA_SERVER_CONNECTION set to: {os.environ['NORA_SERVER_CONNECTION']}")
        print(f"AGENT_MANIFEST_UPDATE_PERIOD_SECONDS set to: {os.environ['AGENT_MANIFEST_UPDATE_PERIOD_SECONDS']}")
        print(f"AGENT_MANIFEST_CONCURRENCY_CONTEXT set to: {os.environ['AGENT_MANIFEST_CONCURRENCY_CONTEXT']}")
        print(f"LOG_LEVEL set to: {os.environ['LOG_LEVEL']}\n")

        # Client-only env variables
        if not self.args["server_only"]:
            os.environ["THINKING_FILE"] = self.args["thinking_file"]
            os.environ["THINKING_DIR"] = self.args["thinking_dir"]
            print(f"THINKING_FILE set to: {os.environ['THINKING_FILE']}")
            print(f"THINKING_DIR set to: {os.environ['THINKING_DIR']}")
            os.environ["NORA_FLOW_HOST"] = str(self.args["nora_flow_host"])
            os.environ["NORA_FLOW_PORT"] = str(self.args["nora_flow_port"])
            os.environ["NORA_FLOW_PLUGIN_CRUSE"] = str(self.args["nora_flow_plugin_cruse"])
            os.environ["VITE_API_PROTOCOL"] = str(self.args["vite_api_protocol"])
            os.environ["VITE_WS_PROTOCOL"] = str(self.args["vite_ws_protocol"])
            print(f"NORA_FLOW_HOST set to: {os.environ['NORA_FLOW_HOST']}")
            print(f"NORA_FLOW_PORT set to: {os.environ['NORA_FLOW_PORT']}")
            print(f"NORA_FLOW_PLUGIN_CRUSE set to: {os.environ['NORA_FLOW_PLUGIN_CRUSE']}")
            print(f"VITE_API_PROTOCOL set to: {os.environ['VITE_API_PROTOCOL']}")
            print(f"VITE_WS_PROTOCOL set to: {os.environ['VITE_WS_PROTOCOL']}")
            # Set env variable for using nora_flow in client-only mode
            if self.args["client_only"]:
                os.environ["NORA_FLOW_CLIENT_ONLY"] = "True"
                print(f"NORA_FLOW_CLIENT_ONLY set to: {os.environ['NORA_FLOW_CLIENT_ONLY']}")

        # Server-only env variables
        if not self.args["client_only"]:
            os.environ["NORA_SERVER_HOST"] = self.args["server_host"]
            os.environ["NORA_SERVER_HTTP_PORT"] = str(self.args["server_http_port"])

            print(f"NORA_SERVER_HOST set to: {os.environ['NORA_SERVER_HOST']}")
            print(f"NORA_SERVER_HTTP_PORT set to: {os.environ['NORA_SERVER_HTTP_PORT']}\n")

        print("\n" + "=" * 50 + "\n")

    def start_process(self, command, process_name, log_file):
        """Start a subprocess and capture logs."""
        # pylint: disable=consider-using-with
        if self.is_windows:
            # On Windows, don't use CREATE_NEW_PROCESS_GROUP to allow Ctrl+C propagation
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
        else:
            # On Unix, use start_new_session for proper process group management
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                start_new_session=True,
            )

        print(f"Started {process_name} with PID {process.pid}")

        for plugin in self.plugins:
            plugin.args["process_name"] = process_name
            plugin.args["process"] = process
            plugin.args["log_file"] = log_file
            plugin.post_server_start_action()

        return process

    def start_nora_fleet(self):
        """Start the Nora Fleet server."""
        print("Starting Nora Fleet server...")
        command = [
            sys.executable,
            "-u",
            "-m",
            "nora_studio.runner.nora_fleet_server_wrapper",
            "--http_port",
            str(self.args["server_http_port"]),
        ]
        self.server_process = self.start_process(command, "NoraFleet", "logs/server.log")
        print("NoraFleet server http started on port: ", self.args["server_http_port"])

    def start_nora_flow(self):
        """Start nora_flow client."""
        print("Starting nora_flow client...")
        command = [
            sys.executable,
            "-u",
            "-m",
            "uvicorn",
            "nora_flow.backend.main:app",
            "--host",
            str(self.args["nora_flow_host"]),
            "--port",
            str(self.args["nora_flow_port"]),
            "--reload",
        ]

        self.nora_flow_process = self.start_process(command, "nora_flow", "logs/nora_flow.log")
        print(f"nora_flow client started on {self.args['nora_flow_host']}:{self.args['nora_flow_port']}")

    # pylint: disable=unused-argument
    def signal_handler(self, signum, frame):
        """Handle termination signals to cleanly exit."""
        print("\nTermination signal received. Stopping all processes...")

        if self.server_process:
            print(f"\nStopping SERVER (PID {self.server_process.pid})...")
            if self.is_windows:
                self.server_process.terminate()
            else:
                os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
            # Wait for the server to finish cleanup (e.g. flushing observability traces)
            self.server_process.wait(timeout=10)

        if self.nora_flow_process:
            print(f"Stopping NORA_FLOW (PID {self.nora_flow_process.pid})...")
            if self.is_windows:
                self.nora_flow_process.terminate()
            else:
                os.killpg(os.getpgid(self.nora_flow_process.pid), signal.SIGKILL)

        for plugin in self.plugins:
            self._logger.info("Running cleanup for plugin: %s", plugin)
            plugin.cleanup()

        sys.exit(0)

    def is_port_open(self, host: str, port: int, timeout=1.0) -> bool:
        """
        Check if a port is open on a given host.
        :return: True if the port is open, False otherwise.
        """
        # Create a socket and set a timeout
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            try:
                sock.connect((host, port))
                return True
            except (ConnectionRefusedError, TimeoutError, OSError):
                return False

    def _check_port_conflicts(self) -> Tuple[list[str], list[int]]:
        """Check if any of the ports are in use."""
        port_conflicts = []
        conflicting_ports: list[int] = []

        if not self.args["server_only"] and self.args["nora_flow_host"] == "localhost":
            if self.is_port_open(self.args["nora_flow_host"], self.args["nora_flow_port"]):
                port_conflicts.append(f"NoraFlow client port {self.args['nora_flow_port']} is already in use.")
                conflicting_ports.append(self.args["nora_flow_port"])

        if not self.args["client_only"] and self.args["server_host"] == "localhost":
            if self.is_port_open(self.args["server_host"], self.args["server_http_port"]):
                port_conflicts.append(
                    f"Nora Fleet server http port {self.args['server_http_port']} is already in use."
                )
                conflicting_ports.append(self.args["server_http_port"])

        return port_conflicts, conflicting_ports

    def _kill_processes_on_ports(self, ports: list[int]):
        """Kill processes using the specified ports."""
        for port in ports:
            print(f"Attempting to kill process on port {port}...")
            try:
                if self.is_windows:
                    # Windows: Find and kill process using netstat and taskkill
                    result = subprocess.run(
                        ["netstat", "-ano", "-p", "TCP"], capture_output=True, text=True, check=True
                    )
                    for line in result.stdout.splitlines():
                        if f":{port}" in line and "LISTENING" in line:
                            pid = line.strip().split()[-1]
                            subprocess.run(["taskkill", "/F", "/PID", pid], check=True)
                            print(f"  Killed process {pid} on port {port}")
                            break
                else:
                    # Unix/Mac: Use lsof to find and kill process
                    result = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True, check=False)
                    if result.stdout.strip():
                        pids = result.stdout.strip().split("\n")
                        for pid in pids:
                            subprocess.run(["kill", "-9", pid], check=True)
                            print(f"  Killed process {pid} on port {port}")
                    else:
                        print(f"  No process found on port {port}")
            except subprocess.CalledProcessError as e:
                print(f"  Failed to kill process on port {port}: {e}")
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"  Error handling port {port}: {e}")

    def _validate_yes_no_input(self, prompt: str, max_attempts: int = 3) -> bool:
        """Prompt the user for a yes/no answer, validating against a whitelist.

        Returns True for yes/y, False for no/n or after max_attempts invalid
        responses. Input is stripped and lower-cased before comparison.
        """
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        valid_yes = {"yes", "y"}
        valid_no = {"no", "n"}
        for attempt in range(max_attempts):
            try:
                # Default to "" (empty), which is an invalid input that triggers the prompt again
                # if there are remaining attempts or gives up otherwise with a 'no'.
                raw = timedinput(prompt, timeout=INPUT_TIMEOUT_SECONDS, default="").strip().lower()
            except EOFError:
                print("No input available. Considering the answer is 'no'.")
                return False
            except KeyboardInterrupt:
                print("\nInput interrupted. Considering the answer is 'no'.")
                return False
            if raw in valid_yes:
                return True
            if raw in valid_no:
                return False
            remaining = max_attempts - attempt - 1
            if remaining > 0:
                print(f"Invalid input. Please enter 'yes' or 'no'. ({remaining} attempt(s) left)")
        print("Too many invalid responses. Considering the answer is 'no'.")
        return False

    def conditional_start_servers(self):
        """
        Start nora-fleet server and nora_flow client based on --client-only and --server-only flags.
        Exit if any port is in use.
        """
        client_only = self.args["client_only"]
        server_only = self.args["server_only"]

        if client_only and server_only:
            print("Cannot use --client-only and --server-only together.")
            sys.exit(1)

        port_conflicts, conflicting_ports = self._check_port_conflicts()

        # Exit early if any conflict is found
        if port_conflicts:
            print("\n" + "=" * 50)
            for msg in port_conflicts:
                print(msg)
            print("=" * 50)

            if self._validate_yes_no_input("\nDo you want to kill the processes using these ports? (yes/no): "):
                self._kill_processes_on_ports(conflicting_ports)
                print("\nProcesses killed. Continuing with startup...\n")
            else:
                print("\nExiting due to port conflicts.\n")
                sys.exit(1)

        if not server_only:
            self.start_nora_flow()
            print("nora_flow client is now running.")

        if not client_only:
            self.start_nora_fleet()
            time.sleep(3)
            print("Nora Fleet server is now running.")

    def run(self):
        """Run the Nora Fleet server and a client."""
        print("\nInitial Run Config:\n" + "\n".join(f"{key}: {value}" for key, value in self.args.items()) + "\n")

        # Set environment variables
        self.set_environment_variables()

        for plugin in self.plugins:
            self._logger.info("Running pre server start action for plugin: %s", plugin)
            plugin.pre_server_start_action()

        # Ensure logs directory exists
        Path("logs").mkdir(parents=True, exist_ok=True)

        # Set up signal handling for termination
        signal.signal(signal.SIGINT, self.signal_handler)  # Handle Ctrl+C
        if self.is_windows:
            signal.signal(
                signal.SIGBREAK,  # pylint: disable=no-member
                self.signal_handler,
            )  # Handle Ctrl+Break on Windows
        else:
            signal.signal(signal.SIGTERM, self.signal_handler)  # Handle kill command (not available on Windows)

        # Start all relevant processes
        self.conditional_start_servers()

        # Fallback: if no plugin implements ProcessLoggerInterface, use a simple
        # logger to drain subprocess pipes and prevent pipe buffer deadlocks.
        has_process_logger = any(isinstance(p, ProcessLoggerInterface) for p in self.plugins)
        if not has_process_logger:
            simple_logger = SimpleProcessLogger()
            for name, proc in [
                ("NoraFleet", self.server_process),
                ("nora_flow", self.nora_flow_process),
            ]:
                if proc is not None:
                    log_file = str(self.logs_dir / f"{name.lower()}.log")
                    simple_logger.attach_process_logger(proc, name, log_file)

        print("\n" + "=" * 50 + "\n")
        print("All processes now running.")
        print("Press Ctrl+C to stop any running processes.")
        print("\n" + "=" * 50 + "\n")

        # Wait on active processes to finish
        if self.nora_flow_process:
            self.nora_flow_process.wait()
        if self.server_process:
            self.server_process.wait()
