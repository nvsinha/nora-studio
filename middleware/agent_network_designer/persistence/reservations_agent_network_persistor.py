# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from os import environ
from typing import Any

from nora_fleet.interfaces.reservation import Reservation
from nora_fleet.internals.reservations.reservation_util import ReservationUtil

from middleware.agent_network_designer.persistence.agent_network_assembler import AgentNetworkAssembler
from middleware.agent_network_designer.persistence.agent_network_persistor import AgentNetworkPersistor
from middleware.agent_network_designer.persistence.deployable_agent_network_assembler import (
    DeployableAgentNetworkAssembler,
)


class ReservationsAgentNetworkPersistor(AgentNetworkPersistor):
    """
    AgentNetworkPersistor implementation that saves a temporary network
    using the nora-fleet Reservations API
    """

    # 1 hour
    DEFAULT_LIFETIME_IN_SECONDS: float = 60.0 * 60.0

    def __init__(self, args: dict[str, Any], demo_mode: bool, external_networks: list[str], mcp_servers: list[str]):
        """
        Creates a new persistor of the specified type.

        :param args: The arguments from the calling CodedTool.
                    It should contain a Reservationist instance.
        :param demo_mode: Whether to include demo mode instructions for agents
        :param external_networks: The external networks for the agent network
        :param mcp_servers: The MCP servers for the agent network
        """
        self.args: dict[str, Any] = args
        self.demo_mode: bool = demo_mode
        self.external_networks: list[str] = external_networks
        self.mcp_servers: list[str] = mcp_servers

    def get_assembler(self) -> AgentNetworkAssembler:
        """
        :return: An assembler instance associated with this persistor
        """
        return DeployableAgentNetworkAssembler(self.demo_mode)

    async def async_persist(self, obj: dict[str, Any], file_reference: str = None) -> str | list[dict[str, Any]]:
        """
        Persists the object passed in.

        :param obj: an object to persist.
                In this case this is the agent network dictionary spec.
        :param file_reference: The file reference to use when persisting.
                Default is None, implying the file reference is up to the
                implementation.
        :return an object describing the location to which the object was persisted
                If the return value is a string, an error has occurred.
                Otherwise, it is a list of agent reservation dictionaries.
        """
        agent_spec: dict[str, Any] = obj

        lifetime_in_seconds: float = self.DEFAULT_LIFETIME_IN_SECONDS
        lifetime_in_seconds_str: str = environ.get("AGENT_NETWORK_DESIGNER_RESERVATIONS_LIFETIME_IN_SECONDS", "")
        lifetime_in_seconds_str = lifetime_in_seconds_str.strip()
        if len(lifetime_in_seconds_str) > 0:
            try:
                lifetime_in_seconds = float(lifetime_in_seconds_str)
            except ValueError as exception:
                raise ValueError(
                    "Value for AGENT_NETWORK_DESIGNER_RESERVATIONS_LIFETIME_IN_SECONDS needs to be a number"
                ) from exception
        if lifetime_in_seconds <= 0:
            raise ValueError("Value for AGENT_NETWORK_DESIGNER_RESERVATIONS_LIFETIME_IN_SECONDS needs to be > 0")

        reservation: Reservation = None
        error: str = None
        reservation, error = await ReservationUtil.wait_for_one(
            self.args,
            agent_spec,
            lifetime_in_seconds,
            file_reference,
            external_networks=self.external_networks,
            mcp_servers=self.mcp_servers,
        )

        if error is not None:
            return error

        agent_reservations: list[dict[str, Any]] = [
            {
                "reservation_id": reservation.get_reservation_id(),
                "lifetime_in_seconds": reservation.get_lifetime_in_seconds(),
                "expiration_time_in_seconds": reservation.get_expiration_time_in_seconds(),
            }
        ]

        return agent_reservations
