# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from dataclasses import dataclass
from typing import Any

# pylint: disable=import-error
from slack_bolt import Say

from apps.slack.dataclass.thread_context import ThreadContext


@dataclass
class MessageContext:
    """Complete message context including thread and Slack functions."""

    thread_ctx: ThreadContext
    say: Say
    logger: Any
