# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

"""Interface for process loggers that drain subprocess pipes."""

import subprocess
from abc import ABC
from abc import abstractmethod


class ProcessLoggerInterface(ABC):  # pylint: disable=too-few-public-methods
    """Interface for consuming subprocess stdout/stderr pipes.

    Any class that drains subprocess pipes should implement this interface.
    This allows nora_studio/commands/run.py to detect whether a plugin is handling pipe consumption
    and fall back to a simple logger if not.
    """

    @abstractmethod
    def attach_process_logger(self, process: subprocess.Popen[str], process_name: str, log_file: str) -> None:
        """Attach to a subprocess and drain its stdout/stderr pipes.

        Args:
            process: A running subprocess with .stdout and .stderr pipes.
            process_name: Human-readable label for the process.
            log_file: Path to the file where raw output should be mirrored.
        """
