# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

"""Allow `python -m nora_studio` to dispatch to the same CLI as `nora-studio`."""

from nora_studio.commands.cli import main

if __name__ == "__main__":
    main()
