# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from dataclasses import dataclass
from typing import Any


@dataclass
class NetworkCommand:
    """Parsed network command data."""

    network_name: str
    input_prompt: str | None = None
    sly_data: dict[str, Any] | None = None
