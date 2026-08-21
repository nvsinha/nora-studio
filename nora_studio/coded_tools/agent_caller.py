# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from typing import Any


class AgentCaller:
    """
    Generic interface for calling an agent
    """

    def get_name(self) -> str:
        """
        Get the name of the agent

        :return: The name of the agent
        """
        raise NotImplementedError

    async def call_agent(self, tool_args: dict[str, Any], sly_data: dict[str, Any] = None) -> str:
        """
        Call an agent with text

        :param tool_args: A dictionary of arguments to pass to the agent
        :param sly_data: A dictionary of private data to pass to the agent
        :return: The text of the response
        """
        raise NotImplementedError
