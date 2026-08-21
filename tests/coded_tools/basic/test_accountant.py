# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

import asyncio
from typing import Any
from typing import Dict
from typing import cast
from unittest import TestCase

import pytest

from coded_tools.basic.accountant import Accountant


class TestAccountant(TestCase):
    """
    Unit tests for Accountant class.
    """

    @pytest.mark.asyncio
    async def test_async_invoke(self):
        """
        Tests the invoke method of the Accountant CodedTool.
        The Accountant CodedTool should increment the passed running cost by 3.0 each time it is invoked,
        and should return a dictionary with the updated running cost.
        """
        accountant = Accountant()
        # Initial running cost
        a_running_cost = 0.0
        response_1 = cast(
            Dict[str, Any], asyncio.run(accountant.async_invoke(args={"running_cost": a_running_cost}, sly_data={}))
        )
        expected_dict_1 = {"running_cost": 3.0}
        self.assertDictEqual(response_1, expected_dict_1)
        updated_running_cost = response_1["running_cost"]
        response_2 = cast(
            Dict[str, Any],
            asyncio.run(accountant.async_invoke(args={"running_cost": updated_running_cost}, sly_data={})),
        )
        expected_dict_2 = {"running_cost": 6.0}
        self.assertDictEqual(response_2, expected_dict_2)
