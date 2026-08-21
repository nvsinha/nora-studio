# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

import logging

# pylint: disable=import-error
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from apps.slack.api_client import APIClient
from apps.slack.command_handler import CommandHandler
from apps.slack.config import NORA_SERVER_HTTP_PORT
from apps.slack.config import SLACK_APP_TOKEN
from apps.slack.config import SLACK_BOT_TOKEN
from apps.slack.conversation_manager import ConversationManager
from apps.slack.event_handler import EventHandler
from apps.slack.network_handler import NetworkHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Initialize app
app = App(token=SLACK_BOT_TOKEN)

# Initialize dependencies
conversation_manager = ConversationManager()
api_client = APIClient(NORA_SERVER_HTTP_PORT)
network_handler = NetworkHandler(conversation_manager, api_client)

# Initialize and register handlers
event_handlers = EventHandler(conversation_manager, network_handler)
command_handlers = CommandHandler(api_client)

event_handlers.register(app)
command_handlers.register(app)


def main():
    """Start the Slack bot."""
    if not NORA_SERVER_HTTP_PORT:
        raise ValueError("NORA_SERVER_HTTP_PORT required")

    print(f"Starting Slack bot on port {NORA_SERVER_HTTP_PORT}")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()


if __name__ == "__main__":
    main()
