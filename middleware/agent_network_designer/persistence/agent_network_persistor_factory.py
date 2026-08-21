# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from typing import Any

from nora_fleet.interfaces.reservationist import Reservationist

from middleware.agent_network_designer.persistence.agent_network_persistor import AgentNetworkPersistor
from middleware.agent_network_designer.persistence.file_system_agent_network_persistor import (
    FileSystemAgentNetworkPersistor,
)
from middleware.agent_network_designer.persistence.reservations_agent_network_persistor import (
    ReservationsAgentNetworkPersistor,
)


# pylint: disable=too-few-public-methods
class AgentNetworkPersistorFactory:
    """
    Factory class for AgentNetworkPersistors.
    """

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    @staticmethod
    def create_persistor(
        args: dict[str, Any],
        write_to_file: bool,
        demo_mode: bool,
        subdirectory: str,
        subnetworks: list[str],
        mcp_servers: list[str],
    ) -> AgentNetworkPersistor:
        """
        Creates a new persistor of the specified type.

        :param args: The args from the calling CodedTool.
        :param write_to_file: True if the agent network should be written to a file.
        :param demo_mode: Whether to include demo mode instructions for agents
        :param subdirectory: The subdirectory under the output path where networks are saved
        :param subnetworks: The subnetworks for the agent network
        :param mcp_servers: The MCP servers for the agent network
        :return: A new AgentNetworkPersistor of the specified type.
        """
        persistor: AgentNetworkPersistor = None
        reservationist: Reservationist = None

        if args:
            reservationist = args.get("reservationist")

        if write_to_file:
            # If the write_to_file flag is True, then that's what we're doing.
            persistor = FileSystemAgentNetworkPersistor(demo_mode, subdirectory)
        elif reservationist:
            # If we have a reservationist as part of the args, use the ReservationsAgentNetworkPersistor
            persistor = ReservationsAgentNetworkPersistor(args, demo_mode, subnetworks, mcp_servers)
        else:
            # Fallback null implementation
            persistor = AgentNetworkPersistor()

        return persistor
