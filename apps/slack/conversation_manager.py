# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from typing import Any

from apps.slack.dataclass.thread_context import ThreadContext


class ConversationManager:
    """Manage conversation contexts and thread data."""

    def __init__(self):
        self.contexts: dict[str, Any] = {}
        self.networks: dict[str, str] = {}
        self.sly_data: dict[str, dict[str, Any]] = {}

    def get_network(self, thread_key: str) -> str | None:
        """Get network for a thread."""
        return self.networks.get(thread_key)

    def set_network(self, thread_key: str, network_name: str) -> None:
        """Set network for a thread."""
        self.networks[thread_key] = network_name

    def get_sly_data(self, thread_key: str) -> dict[str, Any] | None:
        """Get sly_data for a thread."""
        return self.sly_data.get(thread_key)

    def set_sly_data(self, thread_key: str, data: dict[str, Any]) -> None:
        """Set sly_data for a thread."""
        self.sly_data[thread_key] = data

    def get_context(self, conversation_key: str) -> dict[str, Any]:
        """Get conversation context."""
        return self.contexts.get(conversation_key, {})

    def set_context(self, conversation_key: str, context: dict[str, Any]) -> None:
        """Set conversation context."""
        self.contexts[conversation_key] = context

    def clear_old_contexts(self, thread_ctx: ThreadContext, network_name: str, logger: Any) -> None:
        """Clear contexts from different networks in the same thread."""
        prefix = f"{thread_ctx.channel_id}:{thread_ctx.conversation_thread}"
        keys_to_delete = [k for k in self.contexts if k.startswith(prefix) and not k.endswith(f":{network_name}")]

        for key in keys_to_delete:
            del self.contexts[key]
            logger.info(f"Cleared context for different network: {key}")
