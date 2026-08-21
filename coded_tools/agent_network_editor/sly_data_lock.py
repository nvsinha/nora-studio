# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from asyncio import Lock
from typing import Any


# pylint: disable=too-few-public-methods
class SlyDataLock:
    """
    Class for getting a lock on the sly_data for modification.
    """

    @staticmethod
    async def get_lock(sly_data: dict[str, Any], lock_name: str = "lock") -> Lock:
        """
        Get a lock stored on the sly_data for atomic modification of certain fields.
        If no lock is on the sly_data, then create one.

        :param sly_data: The sly_data to get a lock on.
        :return: A common lock for modifying the sly_data.
        """

        # Under normal circumstances we might be tempted to hold a synchronous lock
        # while looking for the existing async lock, but we know that async methods
        # should all be running in their own thread, so that's not necessary.
        lock: Lock = sly_data.get(lock_name)
        if lock is None:
            lock = sly_data[lock_name] = Lock()
        return lock
