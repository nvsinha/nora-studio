# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

import json
import logging
from typing import Any

from nora_fleet.internals.graph.activations.branch_activation import BranchActivation

from nora_studio.coded_tools.agent_caller import AgentCaller
from nora_studio.coded_tools.solver_parsing import SolverParsing


class CodedToolAgentCaller(AgentCaller):
    """
    AgentCaller implementation that uses a BranchActivation from a CodedTool for calling an agent
    """

    def __init__(self, branch_activation: BranchActivation, parsing: SolverParsing = None, name: str = None):
        """
        Constructor

        :param branch_activation: The BranchActivation (CodedTool) used to call the agents.
                                  This ends up being the reference back to the CodedTool
                                  that is also derived from BranchActivation that wants to do
                                  the calling out to an agent internal to the network.
        :param parsing: The SolverParsing instance to use (if any) to extract the final answer
        :param name: The name of the agent
        """
        self.branch_activation: BranchActivation = branch_activation
        self.solver_parsing: SolverParsing = parsing
        self.name: str = name

    def get_name(self) -> str:
        """
        Get the name of the agent

        :return: The name of the agent
        """
        return self.name

    async def call_agent(self, tool_args: dict[str, Any], sly_data: dict[str, Any] = None) -> str:
        """
        Call a single agent with given text, return its response.
        :param tool_args: A dictionary of arguments to pass to the agent
        :param sly_data: A dictionary of private data to pass to the agent
        :return: The text of the response
        """

        use_name: str = self.get_name()
        logging.debug("call_agent(%s) sending args: %s", use_name, json.dumps(tool_args, indent=4))

        if sly_data is None:
            # No sly_data to pass on.
            sly_data = {}

        # Call my agent.
        # This is the magic hook back into the nora-fleet framework that allows us to
        # invoke another agent (within the same network or not) from within a CodedTool.
        resp: str = await self.branch_activation.use_tool(use_name, tool_args, sly_data=sly_data)

        logging.debug("call_agent(%s): received %s chars", use_name, len(resp))
        if self.solver_parsing is not None:
            resp = self.solver_parsing.extract_final(resp)

        return resp
