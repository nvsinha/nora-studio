# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

import logging
from typing import Any
from typing import Dict

from nora_fleet.interfaces.coded_tool import CodedTool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GetArxivPaper(CodedTool):
    """
    CodedTool implementation which get arXiv papers content from sly data.
    """

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """
        Load arXiv papers based on entry ID.

        :param args: Dictionary containing:
            "entry_id": ID of the arxiv paper

        :param sly_data: A dictionary whose keys are defined by the agent
            hierarchy, but whose values are meant to be kept out of the
            chat stream.

            This dictionary is largely to be treated as read-only.
            It is possible to add key/value pairs to this dict that do not
            yet exist as a bulletin board, as long as the responsibility
            for which coded_tool publishes new entries is well understood
            by the agent chain implementation and the coded_tool implementation
            adding the data is not invoke()-ed more than once.

            Keys expected for this implementation are:
                "arxiv_contents": content of the paper of the entry id

        :return: Result of the query against the vector store.
        """
        # Extract arguments from the input dictionary
        entry_id: str = args.get("entry_id")

        # Validate presence of required inputs
        if not entry_id:
            logger.error("Missing required input: 'entry_id'.")
            raise ValueError("❌ Missing required input: 'entry_id'.")

        # Ensure the ID always start with "http://arxiv.org/abs/"
        if not entry_id.startswith("http://arxiv.org/abs/"):
            entry_id = "http://arxiv.org/abs/" + entry_id

        return sly_data.get("arxiv_contents", {}).get(entry_id)
