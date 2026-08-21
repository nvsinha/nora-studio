# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from coded_tools.basic.smart_home.lights_switch import LightsSwitch


class LivingRoomLightsSwitch(LightsSwitch):
    """
    CodedTool implementation that calls an API to turn lights on or off.
    """

    def __init__(self):
        """
        Constructs a switch for living room lights.
        """
        super().__init__("Living room")
