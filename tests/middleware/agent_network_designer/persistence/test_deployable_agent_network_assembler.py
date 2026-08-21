# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

"""Tests for DeployableAgentNetworkAssembler's sly_data_schema emission."""

import asyncio
import os
from pathlib import Path

import pytest

pytest.importorskip("middleware.agent_network_designer.persistence.deployable_agent_network_assembler")

# The import must stay below importorskip so environments whose nora-fleet
# predates the assembler's imports skip cleanly.
# pylint: disable=wrong-import-position
from middleware.agent_network_designer.persistence.deployable_agent_network_assembler import (  # noqa: E402
    DeployableAgentNetworkAssembler,
)

REPO_ROOT = Path(__file__).resolve().parents[4]

OAUTH_URL = "https://oauth.example.com/mcp"
FILE_AUTH_URL = "https://file-auth.example.com/mcp"

# Client-token servers (from the conversation's sly_data http_headers), each
# mapped to the header names it supplied; FILE_AUTH_URL is a file-configured
# server and deliberately not in it.
CLIENT_TOKEN_MCP_HEADERS: dict[str, list[str]] = {OAUTH_URL: ["Authorization"]}

NETWORK_DEF: dict = {
    "front_man": {"description": "top", "instructions": "Coordinate.", "tools": ["helper", OAUTH_URL]},
    "helper": {"description": "helps", "instructions": "Help.", "tools": [FILE_AUTH_URL]},
}


def assemble(client_token_mcp_headers: dict[str, list[str]] | None) -> dict:
    """
    Assemble the test network into a deployable config dict (real templates).

    Runs from the repo root: the wrapper template's include resolves
    CWD-relatively, so without the chdir these tests error out under any
    runner whose working directory is not the repo root (IDE test runners,
    CI steps with a different workdir).
    """
    assembler = DeployableAgentNetworkAssembler(demo_mode=False)
    cwd = os.getcwd()
    os.chdir(REPO_ROOT)
    try:
        return asyncio.run(
            assembler.assemble_agent_network(
                NETWORK_DEF, "front_man", "test_net", ["query one"], client_token_mcp_headers
            )
        )
    finally:
        os.chdir(cwd)


class TestDeployableAssemblerSlyDataSchema:
    """The deployable config dict declares the network's MCP header needs."""

    def test_front_man_declares_the_schema(self):
        """The top agent's function block carries the nora_flow contract."""
        agent_network = assemble(CLIENT_TOKEN_MCP_HEADERS)

        front_man = agent_network["tools"][0]
        assert front_man["name"] == "front_man"
        http_headers = front_man["function"]["sly_data_schema"]["properties"]["http_headers"]
        assert list(http_headers["properties"]) == [OAUTH_URL]
        assert http_headers["required"] == [OAUTH_URL]
        # The description injection it sits next to still happened.
        assert front_man["function"]["description"] == "top"

    def test_non_top_agents_carry_no_schema(self):
        """Only the front man talks to clients; helpers must not declare one."""
        agent_network = assemble(CLIENT_TOKEN_MCP_HEADERS)
        for agent in agent_network["tools"][1:]:
            function = agent.get("function")
            if isinstance(function, dict):
                assert "sly_data_schema" not in function

    def test_no_client_urls_means_no_schema(self):
        """Without client-token servers the function block stays as templated."""
        for client_headers in (None, {}):
            agent_network = assemble(client_headers)
            assert "sly_data_schema" not in agent_network["tools"][0]["function"]
