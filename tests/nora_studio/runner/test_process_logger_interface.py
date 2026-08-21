# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

"""Tests for ProcessLoggerInterface ABC."""

import pytest

from nora_studio.interfaces.process_logger_interface import ProcessLoggerInterface


class TestProcessLoggerInterface:
    """Tests for the ProcessLoggerInterface abstract base class."""

    def test_cannot_instantiate_directly(self):
        """Test that ProcessLoggerInterface cannot be instantiated."""
        with pytest.raises(TypeError):
            ProcessLoggerInterface()  # pylint: disable=abstract-class-instantiated

    def test_concrete_subclass_must_implement_method(self):
        """Test that a subclass without attach_process_logger raises TypeError."""

        class IncompleteLogger(ProcessLoggerInterface):  # pylint: disable=too-few-public-methods
            """Intentionally incomplete subclass for testing."""

        with pytest.raises(TypeError):
            IncompleteLogger()  # pylint: disable=abstract-class-instantiated

    def test_concrete_subclass_can_be_instantiated(self):
        """Test that a fully implemented subclass can be instantiated."""

        class ConcreteLogger(ProcessLoggerInterface):  # pylint: disable=too-few-public-methods
            """Minimal concrete implementation for testing."""

            def attach_process_logger(self, process, process_name, log_file):
                pass

        logger = ConcreteLogger()
        assert isinstance(logger, ProcessLoggerInterface)
