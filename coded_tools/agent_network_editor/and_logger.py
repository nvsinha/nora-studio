# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from logging import Logger

from nora_common.logging.conditional_logger import ConditionalLogger


class AndLogger(ConditionalLogger):
    """
    A ConditionalLogger that is always enabled which can redirect INFO logs to DEBUG based on
    an environment variable setting. The idea is to get rid of most of the INFO chatter
    in production logs, but still allow them through for the default developer setting.
    """

    def __init__(self, logger: Logger):
        """
        Constructor

        :param logger: The wrapped logger to redirect write() calls to.
        """
        super().__init__(logger, "AGENT_NETWORK_DESIGNER_VERBOSE")

        self.use_info: bool = super().should_log()

    def should_log(self) -> bool:
        """
        :return: True if this logger should log
        """
        # We're always going to log. It's a matter of what level.
        return True

    def info(self, msg, *args, **kwargs):
        """
        By default, when the env var is unset or set to "true", log 'msg % args' with severity 'INFO'.
        When the env var is set to any other value (e.g. "false"), log 'msg % args' with severity 'DEBUG'.
        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "notable problem", exc_info=True)
        """
        if self.use_info:
            super().info(msg, *args, **kwargs)
        else:
            super().debug(msg, *args, **kwargs)

    def always_info(self, msg, *args, **kwargs):
        """
        Always log 'msg % args' with severity 'INFO'.  Bypasses the env var.

        This is meant to be for specialized use cases where we always want
        the log message to be INFO when sent to the logs, in cases where
        the people who read server logs will actually be interested in the message.
        (Most of the time this is not the case, and the intention of this class
        is to get rid of the mountain of INFO chatter in production logs,
        hence we make you think about it.)

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "notable problem", exc_info=True)
        """
        super().info(msg, *args, **kwargs)
