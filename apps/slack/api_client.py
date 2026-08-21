# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from typing import Any

from requests import get
from requests import post
from requests.exceptions import HTTPError


class APIClient:
    """Handle API communication with nora-fleet server."""

    def __init__(self, port: str):
        self.port = port
        self.base_url = f"http://localhost:{port}/api/v1"

    def call(self, endpoint: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Make API call to endpoint.

        :param endpoint: Server endpoint
        :param payload: Request payload for HTTP POST

        :return: Response in JSON format
        """
        url = f"{self.base_url}/{endpoint}"

        if endpoint == "list":
            response = get(url, timeout=30)
        else:
            response = post(url, json=payload, timeout=300)

        response.raise_for_status()
        return response.json()

    def test_connection(self, network_name: str) -> bool:
        """
        Test if network exists.

        :param network_name: Name of the agent network to check connection

        :return: True if the connection is valid, False otherwise
        """
        try:
            self.call(f"{network_name}/streaming_chat", {})
            return True
        except HTTPError:
            return False
