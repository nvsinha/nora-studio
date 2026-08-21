# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

import datetime
import logging
from typing import Any
from typing import Dict
from typing import Union

from nora_fleet.interfaces.coded_tool import CodedTool

logger = logging.getLogger(__name__)


class TimeTool(CodedTool):
    """
    Returns either the time from sly_data or the current time.
    """

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        :param args: an empty dictionary (not used).

        :param sly_data: a dictionary with the following keys:
            - time: optional - the time to return to calling agents.

        :return: the current time
        """
        logger.debug(">>>>>>>>>>>>>>>>>>> TimeTool >>>>>>>>>>>>>>>>>>")
        sly_time = sly_data.get("time")
        if sly_time:
            response = sly_time
        else:
            # No time was provided in sly_data. Return the current time.
            response = datetime.datetime.now().strftime("%I:%M %p").lstrip("0")
        logger.debug("Response: %s", response)
        logger.debug(">>>>>>>>>>>>>>>>>>> DONE !!! >>>>>>>>>>>>>>>>>>")
        return response

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Delegates to the synchronous invoke method because it's quick, non-blocking.
        """
        return self.invoke(args, sly_data)
