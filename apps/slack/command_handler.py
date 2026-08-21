# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from typing import Any

from requests.exceptions import RequestException

# pylint: disable=import-error
from slack_bolt import Ack
from slack_bolt import App

from apps.slack.api_client import APIClient


class CommandHandler:
    """Handle Slack slash commands."""

    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    def list_networks(self, ack: Ack, respond: Any, logger: Any) -> None:
        """
        List available networks.

        :param ack: Slack acknowledgement function
        :param respond: Slack respond function to send response
        :param logger: Logger instance for logging information
        """
        ack()

        try:
            logger.info("Fetching networks")
            data = self.api_client.call("list")
            agents = data.get("agents", [])

            if not agents:
                respond("No networks available.")
                return

            # Format and send
            agents.sort(key=lambda x: x.get("agent_name", ""))
            lines = ["*Available Networks:*\n"]

            for agent in agents:
                name = agent.get("agent_name", "Unknown")
                desc = " ".join(agent.get("description", "No description").split())
                tags = agent.get("tags", [])
                tags_str = f" `{', '.join(tags)}`" if tags else ""

                lines.extend([f"• *{name}*{tags_str}", f"  {desc}", ""])

            respond("\n".join(lines))

        except RequestException as e:
            logger.error(f"Error fetching networks: {e}", exc_info=True)
            respond(f"Error: {e}")

    def nora_fleet_help(self, ack: Ack, respond: Any) -> None:
        """
        Provide usage instructions.
        :param ack: Slack acknowledgement function
        :param respond: Slack respond function to send response
        """
        ack()

        respond(
            """*How to use Nora Fleet slack app:*

*Format:*
- `<network_name>`
- `<network_name> <prompt>`
- `<network_name> --sly_data <json>`
- `<network_name> <prompt> --sly_data <json>`

*Examples:*
- `music_nerd_pro`
- `music_nerd_pro Tell me about jazz`
- `math_guy --sly_data {"x": 7, "y": 6}`

*Note:*
- DMs: Just type the command
- Channels: Mention bot `@BotName <command>`
- Each thread keeps independent context
"""
        )

    def register(self, app: App) -> None:
        """
        Register all command handlers with the app.

        :param app: Slack app function
        """
        app.command("/list_networks")(self.list_networks)
        app.command("/nora_fleet_help")(self.nora_fleet_help)
