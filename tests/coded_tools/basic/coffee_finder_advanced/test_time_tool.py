# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from datetime import datetime
from unittest import TestCase

from coded_tools.basic.coffee_finder_advanced.time_tool import TimeTool


class TestTimeTool(TestCase):
    """
    Unit tests for the TimeTool class.
    """

    def test_invoke_no_sly_data(self):
        """
        Tests the invoke method of the TimeTool CodedTool when no time is specified in the sly_data.
        """
        sly_data = {}
        time_tool = TimeTool()
        response = time_tool.invoke(args={}, sly_data=sly_data)
        self.assertTrue(TestTimeTool._is_valid_time_format(response), "Invalid time format")

    def test_invoke_sly_data(self):
        """
        Tests the invoke method of the TimeTool CodedTool when a time is specified in the sly_data.
        """
        sly_data = {"time": "8 am"}
        time_tool = TimeTool()
        response = time_tool.invoke(args={}, sly_data=sly_data)
        expected_response = "8 am"
        self.assertEqual(expected_response, response)

    @staticmethod
    def _is_valid_time_format(time_str: str) -> bool:
        try:
            datetime.strptime(time_str, "%I:%M %p")
            return True
        except ValueError:
            return False
