# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

import logging
from typing import Any

from nora_fleet.interfaces.coded_tool import CodedTool

from coded_tools.agent_network_editor.and_logger import AndLogger

AGENT_NETWORK_QUERIES: str = "agent_network_queries"


class SetSampleQueries(CodedTool):
    """
    CodedTool implementation which sets the sample queries of the agent network in sly data.
    """

    async def async_invoke(self, args: dict[str, Any], sly_data: dict[str, Any]) -> str:
        """
        :param args: An argument dictionary whose keys are the parameters
                to the coded tool and whose values are the values passed for them
                by the calling agent.  This dictionary is to be treated as read-only.

                The argument dictionary expects the following keys:
                    "sample_queries": sample queries for the agent network.

        :param sly_data: A dictionary whose keys are defined by the agent hierarchy,
                but whose values are meant to be kept out of the chat stream.

                This dictionary is largely to be treated as read-only.
                It is possible to add key/value pairs to this dict that do not
                yet exist as a bulletin board, as long as the responsibility
                for which coded_tool publishes new entries is well understood
                by the agent chain implementation and the coded_tool implementation
                adding the data is not invoke()-ed more than once.

                Keys expected for this implementation are:
                    "agent_network_queries": a list of sample queries

        :return:
            In case of successful execution:
                a text string indicating the sample queries were successfully set in the sly data.
            otherwise:
                a text string an error message in the format:
                "Error: <error message>"
        """
        sample_queries: list[str] = args.get("sample_queries")
        if not sample_queries:
            raise ValueError("Error: No sample_queries provided.")
        if not isinstance(sample_queries, list):
            raise ValueError("Error: sample_queries must be a list of strings.")
        if not all(isinstance(sample_query, str) for sample_query in sample_queries):
            raise ValueError("Error: sample_queries must be a list of strings.")

        logger = AndLogger(logging.getLogger(self.__class__.__name__))
        logger.info(">>>>>>>>>>>>>>>>>>>Set Sample Queries>>>>>>>>>>>>>>>>>>")
        sly_data[AGENT_NETWORK_QUERIES] = sample_queries
        logger.info("The Sample queries: %s", str(sample_queries))

        logger.debug(">>>>>>>>>>>>>>>>>>> DONE %s !!!>>>>>>>>>>>>>>>>>>", self.__class__.__name__)
        return "Sample queries have been set successfully."
