# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

"""Simple process logger that drains subprocess pipes to console and file."""

import subprocess
import threading
from pathlib import Path

from nora_studio.interfaces.process_logger_interface import ProcessLoggerInterface


class SimpleProcessLogger(ProcessLoggerInterface):  # pylint: disable=too-few-public-methods
    """Minimal process logger that forwards subprocess output to console and a log file.

    This is a lightweight fallback used when the full ProcessLogBridge plugin
    is not enabled. It spawns daemon threads to drain stdout/stderr, preventing
    pipe buffer deadlocks, and writes raw lines to both the console and a log file.
    """

    def attach_process_logger(self, process: subprocess.Popen[str], process_name: str, log_file: str) -> None:
        """Attach to a subprocess and drain its pipes with basic forwarding.

        Args:
            process: A running subprocess with .stdout and .stderr pipes.
            process_name: Human-readable label for the process.
            log_file: Path to the file where raw output should be mirrored.
        """
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        for pipe, label in [(process.stdout, "stdout"), (process.stderr, "stderr")]:
            if pipe is not None:
                thread = threading.Thread(
                    target=self._drain,
                    args=(pipe, process_name, label, log_file),
                    daemon=True,
                )
                thread.start()

    @staticmethod
    def _drain(pipe, process_name: str, label: str, log_file: str) -> None:
        """Read lines from a pipe, print to console, and append to a log file.

        Args:
            pipe: A file-like pipe (stdout or stderr) from a subprocess.
            process_name: Human-readable label for the process.
            label: Stream identifier ("stdout" or "stderr").
            log_file: Path to the log file for mirroring.
        """
        try:
            with open(log_file, "a", encoding="utf-8") as log:
                for line in iter(pipe.readline, ""):
                    text = line.rstrip("\n")
                    formatted = f"[{process_name}:{label}] {text}"
                    print(formatted)
                    log.write(formatted + "\n")
                    log.flush()
        finally:
            pipe.close()
