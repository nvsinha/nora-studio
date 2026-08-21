# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from dataclasses import dataclass


@dataclass
class ThreadContext:
    """Store thread-specific context data."""

    channel_id: str
    thread_ts: str | None
    message_ts: str

    @property
    def thread_key(self) -> str:
        """Generate unique thread key."""
        return f"{self.channel_id}:{self.thread_ts or self.message_ts}"

    @property
    def conversation_thread(self) -> str:
        """Get conversation thread timestamp."""
        return self.thread_ts or self.message_ts
