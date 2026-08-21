# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

import logging
import os
import subprocess
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as library_version
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)

# The distribution name as published / installed (see pyproject `[project].name`).
DISTRIBUTION_NAME = "nora-studio"

# Repo root (…/nora_studio/utils/version.py -> two parents up), for the
# source-checkout fallbacks when the package isn't installed.
_REPO_ROOT = Path(__file__).resolve().parents[2]

# Where the version was resolved from.
SOURCE_ENV = "env"
SOURCE_INSTALLED = "installed"
SOURCE_SCM = "source"
SOURCE_GIT = "git"
SOURCE_UNKNOWN = "unknown"


def studio_version() -> str:
    """Bare version string, for callers that don't care where it came from."""
    return resolve_version()[0]


def resolve_version() -> Tuple[str, str]:
    """Resolve ``(version, source)``, never raising: env var, installed metadata, then scm, then git sha,
    then unknown.
    """
    env_version = os.environ.get("NORA_STUDIO_VERSION")
    if env_version and env_version != "unknown":
        return env_version, SOURCE_ENV

    try:
        return str(library_version(DISTRIBUTION_NAME)), SOURCE_INSTALLED
    except PackageNotFoundError:
        logger.warning("%s is not installed as a distribution; trying setuptools-scm.", DISTRIBUTION_NAME)

    scm = _scm_version()
    if scm:
        return scm, SOURCE_SCM

    logger.warning("setuptools-scm unavailable; trying the git sha.")
    sha = _git_sha()
    if sha:
        return sha, SOURCE_GIT

    logger.warning("Could not determine a git sha; version is unknown.")
    return "unknown", SOURCE_UNKNOWN


def _scm_version() -> str:
    """Version from setuptools-scm reading the repo, or '' if it isn't importable."""
    try:
        from setuptools_scm import get_version  # pylint: disable=import-outside-toplevel

        return str(get_version(root=str(_REPO_ROOT)))
    except (ImportError, LookupError, OSError):
        return ""


def _git_sha() -> str:
    """Short git sha of the repo checkout, or '' if not a git checkout / git is missing."""
    try:
        result = subprocess.run(
            ["git", "-C", str(_REPO_ROOT), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""
