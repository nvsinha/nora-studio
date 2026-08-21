# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

"""Locate the installed nora-studio library on disk."""

import os

import nora_studio


class PackagePaths:  # pylint: disable=too-few-public-methods
    """Resolve filesystem paths owned by the installed nora-studio package."""

    @staticmethod
    def installed_library_root() -> str:
        """Return the directory that contains the library's bundled ``registries/``.

        Anchors on the ``nora_studio`` package — a regular package whose
        ``__file__`` unambiguously points at the install location — rather than the
        ``registries`` namespace package, which gets shadowed by any ``registries/``
        directory on ``sys.path``, including the one ``nora init`` creates in the
        user's project.
        """
        pkg_dir = os.path.dirname(os.path.abspath(nora_studio.__file__))
        install_root = os.path.dirname(pkg_dir)
        if os.path.exists(os.path.join(install_root, "registries", "manifest.hocon")):
            return install_root
        raise FileNotFoundError("Cannot find nora-studio installation. Make sure nora-studio is installed via pip.")
