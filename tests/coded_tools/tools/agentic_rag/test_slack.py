# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

"""Unit tests for the agentic RAG Slack tool."""

import json
from unittest.mock import AsyncMock
from unittest.mock import call
from unittest.mock import patch

import pytest

from coded_tools.tools.agentic_rag.slack import Slack


@pytest.mark.asyncio
async def test_async_invoke_returns_messages_from_configured_slack():
    """The tool paginates private channels and filters fields and incomplete messages."""
    client = AsyncMock()
    client.conversations_list.side_effect = [
        {
            "channels": [{"id": "C100", "name": "public"}],
            "response_metadata": {"next_cursor": "next-page"},
        },
        {
            "channels": [{"id": "C123", "name": "general"}],
            "response_metadata": {"next_cursor": ""},
        },
    ]
    client.conversations_history.return_value = {
        "messages": [
            {"user": "U123", "text": "Hello", "ts": "123.456", "blocks": ["unused"]},
            {"bot_id": "B123", "text": "Automated update", "ts": "123.457"},
        ]
    }

    with (
        patch.dict("os.environ", {"SLACK_BOT_TOKEN": "xoxb-token"}),
        patch("coded_tools.tools.agentic_rag.slack.AsyncWebClient", return_value=client) as client_class,
    ):
        result = await Slack().async_invoke({"channel_name": "general"}, {})

    assert json.loads(result) == [{"user": "U123", "text": "Hello", "ts": "123.456"}]
    client_class.assert_called_once_with(token="xoxb-token")
    assert client.conversations_list.await_args_list == [
        call(types="public_channel,private_channel", limit=200, cursor=None),
        call(types="public_channel,private_channel", limit=200, cursor="next-page"),
    ]
    client.conversations_history.assert_awaited_once_with(channel="C123")


@pytest.mark.asyncio
async def test_async_invoke_accepts_user_token():
    """A user token is used when no bot token is configured."""
    client = AsyncMock()
    client.conversations_list.return_value = {"channels": []}

    with (
        patch.dict("os.environ", {"SLACK_USER_TOKEN": "xoxp-token"}, clear=True),
        patch("coded_tools.tools.agentic_rag.slack.AsyncWebClient", return_value=client) as client_class,
    ):
        await Slack().async_invoke({"channel_name": "missing"}, {})

    client_class.assert_called_once_with(token="xoxp-token")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("client_class", "environment"),
    [(None, {"SLACK_BOT_TOKEN": "xoxb-token"}), (AsyncMock(), {})],
)
async def test_async_invoke_returns_mock_data_when_slack_is_unavailable(client_class, environment):
    """An absent SDK or token keeps the demo fallback behavior."""
    with (
        patch.dict("os.environ", environment, clear=True),
        patch("coded_tools.tools.agentic_rag.slack.AsyncWebClient", client_class),
    ):
        result = await Slack().async_invoke({"channel_name": "retail"}, {})

    assert "AI-driven demand forecasting" in result


@pytest.mark.asyncio
async def test_async_invoke_returns_channel_not_found():
    """A configured client reports an unknown channel without fetching history."""
    client = AsyncMock()
    client.conversations_list.return_value = {"channels": []}

    with (
        patch.dict("os.environ", {"SLACK_BOT_TOKEN": "xoxb-token"}),
        patch("coded_tools.tools.agentic_rag.slack.AsyncWebClient", return_value=client),
    ):
        result = await Slack().async_invoke({"channel_name": "missing"}, {})

    assert result == "The missing channel not found."
    client.conversations_history.assert_not_awaited()


@pytest.mark.asyncio
async def test_async_invoke_does_not_mask_slack_api_errors():
    """Errors from a configured Slack client propagate to the caller."""
    client = AsyncMock()
    client.conversations_list.side_effect = RuntimeError("Slack API failed")

    with (
        patch.dict("os.environ", {"SLACK_BOT_TOKEN": "xoxb-token"}),
        patch("coded_tools.tools.agentic_rag.slack.AsyncWebClient", return_value=client),
        pytest.raises(RuntimeError, match="Slack API failed"),
    ):
        await Slack().async_invoke({"channel_name": "general"}, {})


@pytest.mark.asyncio
async def test_async_invoke_requires_channel_name():
    """The required argument is validated before Slack configuration."""
    assert await Slack().async_invoke({}, {}) == "Error: No slack channel name provided."
