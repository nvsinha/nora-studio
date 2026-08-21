# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from typing import Any

from nora_fleet.internals.validation.network.keyword_network_validator import KeywordNetworkValidator

from middleware.agent_network_designer.validation.agent_network_validation_middleware import (
    AgentNetworkValidationMiddleware,
)


class AgentNetworkInstructionsValidationMiddleware(AgentNetworkValidationMiddleware):
    """
    Middleware that validates agent instructions and descriptions after each agent turn.

    Runs keyword validation against the current network definition stored
    in sly_data to detect missing or incomplete agent instructions and descriptions.
    If validation errors are found, a `HumanMessage` containing the errors
    is injected into the conversation and control returns to the model so it can self-correct.
    """

    def no_network_error_message(self) -> str:
        """Return the error message when no agent network definition is found."""

        return "Error: No agent network found. Cannot edit or create instructions or description."

    def validation_label(self) -> str:
        """Return a label for log messages (e.g. 'Structure', 'Instructions/Description')."""
        return "Instructions/Description"

    async def validate(self, network_def: dict[str, Any]) -> list[str]:
        """
        Run validators against the network definition to check for missing "instructions" and "description" fields.

        :param network_def: The agent network definition to validate
        :return: A list of error strings (empty if valid)
        """
        # Copy network_def and modify the copy so that the "description" is under "function".
        # This allows the keyword validator to check for missing "description" fields.
        use_network_def: dict[str, Any] = {}
        for agent_name, agent_def in network_def.items():
            agent_copy: dict[str, Any] = agent_def.copy()
            if "description" in agent_copy:
                description: str = agent_copy.pop("description")
                agent_copy["function"] = {"description": description}
            use_network_def[agent_name] = agent_copy
        # The keyword validator only checks that "instructions" and "description" fields are present and non-empty.
        # We do not check if "tools" field is a list of str here since that is related to structure validation and
        # this agent network has no tools to fix this issue.
        return KeywordNetworkValidator().validate(use_network_def)

    def format_error(self, error_list: list[str]) -> str:
        """
        Format the list of validation errors into a message string.

        :param error_list: Non-empty list of error strings
        :return: Formatted error message
        """
        return "Error(s):\n" + "\n".join(error_list)
