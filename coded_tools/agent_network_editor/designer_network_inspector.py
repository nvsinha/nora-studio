# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT
from typing import Any

from nora_fleet.internals.run_context.interfaces.agent_network_inspector import AgentNetworkInspector
from nora_fleet.internals.validation.network.unreachable_nodes_network_validator import (
    UnreachableNodesNetworkValidator,
)
from objsize import get_deep_size


class DesignerNetworkInspector(AgentNetworkInspector):
    """
    AgentNetworkInspector implementation that wraps the internal format of the
    agent network designer and pals.
    """

    def __init__(self, network_def: dict[str, Any]):
        """
        Constructor

        :param network_def: The agent network definition as a dictionary
        """
        self.network_def = network_def
        self.size_in_bytes: int = get_deep_size(self, "bytes")

    def get_config(self) -> dict[str, Any]:
        """
        :return: The entire config dictionary given to the instance.
        """
        # 12/05/25: We are only using this for purposes of passing to the ConnectivityReporter,
        #           so just return None
        return None

    def get_agent_tool_spec(self, name: str) -> dict[str, Any]:
        """
        :param name: The name of the agent tool to get out of the registry
        :return: The dictionary representing the spec registered agent
        """
        return self.network_def.get(name)

    def get_name_from_spec(self, agent_spec: dict[str, Any]) -> str:
        """
        :param agent_spec: A single agent to register
        :return: The agent name as per the spec
        """
        return agent_spec.get("name")

    def find_front_man(self) -> str | None:
        """
        :return: A single tool name to use as the root of the chat agent.
                 This guy will be user facing.
                 Returns None when no front-man exists yet (e.g., during interactive
                 build before an entry agent has been added) — cardinality errors
                 (zero or multiple front-men) are surfaced by the validation
                 middleware rather than raised here, so the designer agent can
                 iteratively fix the network.
                 When multiple front-men exist, an arbitrary one is returned;
                 callers are expected to have already validated the network.
        """
        # The validator stuff uses the same internal network dictionary format
        validator = UnreachableNodesNetworkValidator()
        front_men: set[str] = validator.find_all_front_man_agents(self.network_def)
        if len(front_men) == 0:
            return None

        front_man: str = list(front_men)[0]
        return front_man

    def get_size_in_bytes(self) -> int:
        """
        :return: The size in bytes of this agent network definition.
        """
        return self.size_in_bytes
