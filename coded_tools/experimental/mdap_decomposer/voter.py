# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT


# pylint: disable=too-few-public-methods
class Voter:
    """
    Generic voter interface

    We plan to have more than one type of voter in the future, hence the interface.
    """

    async def vote(self, problem: str, candidates: list[str]) -> tuple[list[int], int]:
        """
        Generic voting interface

        :param problem: The problem to be solved
        :param candidates: The candidate solutions
        :return: A tuple of (list of number of votes per candidate, winner index)
        """
        raise NotImplementedError
