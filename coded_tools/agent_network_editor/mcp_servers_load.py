# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from typing import NamedTuple


class McpServersLoad(NamedTuple):
    """
    Result of loading mcp_info.hocon: the file-configured MCP server URLs
    plus whether the file was read successfully.

    loaded_ok separates an authoritatively empty result (a missing or empty
    file — there really are no file-configured servers) from a degraded one
    (the file exists but could not be read or parsed — the set is UNKNOWN).
    Only the former makes it safe to treat a conversation-connected server
    as client-token; see GetMcpTool.get_mcp_servers_load and
    AgentNetworkPersistenceMiddleware for the caller that acts on the
    difference.
    """

    urls: list[str]
    """The MCP server URLs read from the file; [] when missing or unreadable."""

    loaded_ok: bool
    """True when the file was read (or is genuinely absent); False when it
    exists but could not be read or parsed, making urls non-authoritative."""
