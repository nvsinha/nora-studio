# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

"""Tests for SimpleProcessLogger."""

import io
import os
import tempfile
import time

from nora_studio.interfaces.process_logger_interface import ProcessLoggerInterface
from nora_studio.runner.simple_process_logger import SimpleProcessLogger


class _FakeProcess:  # pylint: disable=too-few-public-methods
    """Fake subprocess with readable stdout/stderr pipes."""

    def __init__(self, stdout_lines, stderr_lines):
        self.stdout = io.StringIO("".join(f"{line}\n" for line in stdout_lines))
        self.stderr = io.StringIO("".join(f"{line}\n" for line in stderr_lines))


class TestSimpleProcessLogger:
    """Tests for the SimpleProcessLogger fallback."""

    def test_implements_interface(self):
        """Test that SimpleProcessLogger implements ProcessLoggerInterface."""
        assert issubclass(SimpleProcessLogger, ProcessLoggerInterface)
        logger = SimpleProcessLogger()
        assert isinstance(logger, ProcessLoggerInterface)

    def test_drains_pipes_to_log_file(self):
        """Test that attach_process_logger writes output to the log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            process = _FakeProcess(["hello", "world"], ["error line"])

            logger = SimpleProcessLogger()
            logger.attach_process_logger(process, "TestProc", log_file)

            # Give daemon threads time to drain
            time.sleep(0.5)

            with open(log_file, encoding="utf-8") as f:
                content = f.read()

            assert "[TestProc:stdout] hello" in content
            assert "[TestProc:stdout] world" in content
            assert "[TestProc:stderr] error line" in content

    def test_handles_none_pipes(self):
        """Test that None pipes are skipped without error."""

        class _NullPipeProcess:  # pylint: disable=too-few-public-methods
            """Fake process with None pipes."""

            stdout = None
            stderr = None

        logger = SimpleProcessLogger()
        # Should not raise
        logger.attach_process_logger(_NullPipeProcess(), "NullProc", "/tmp/null.log")

    def test_creates_log_directory(self):
        """Test that missing parent directories are created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "nested", "deep", "test.log")
            process = _FakeProcess(["line"], [])

            logger = SimpleProcessLogger()
            logger.attach_process_logger(process, "TestProc", log_file)

            time.sleep(0.5)
            assert os.path.exists(log_file)
