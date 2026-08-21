#!/bin/bash -e
# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

# Builds the free-threaded (Python 3.14t / no-GIL) nora-studio container
# using ./deploy/Dockerfile.py314t.
#
# Usage:
#   ./deploy/build_py314t.sh [--no-cache]
#
# Run it from the top-level directory of the nora-studio repo.
#
# All Python dependencies -- including nora-fleet and the in-house nora-common --
# come from requirements.txt (i.e. from PyPI), matching the venv you build from
# (which already has nora-fleet installed). No sibling source repositories are
# needed, so the whole repo directory is used as the Docker build context, just
# like ./deploy/build.sh.
#
# NOTE: There is no official `python:3.14t` Docker image (the library/python
# repo publishes no free-threaded tags), so this build provisions the
# free-threaded interpreter with uv rather than via a base image.
#
# Overridable via environment:
#   SERVICE_TAG / SERVICE_VERSION   image name/tag components
#   TARGET_PLATFORM          docker build target platform (default: linux/amd64)
#   PYTHON_VERSION           free-threaded interpreter to provision via uv
#                            (default: 3.14t -- the trailing "t" selects no-GIL)
#   BASE_IMAGE               OS base for both stages (default: debian:trixie-slim)
#   UV_IMAGE                 image to lift the uv binary from
#                            (default: ghcr.io/astral-sh/uv:latest)

# If either of these change, also change the env var in run.sh
export SERVICE_TAG=${SERVICE_TAG:-nora-studio}
export SERVICE_VERSION=${SERVICE_VERSION:-0.0.1-py314t}

PYTHON_VERSION=${PYTHON_VERSION:-3.14t}
BASE_IMAGE=${BASE_IMAGE:-debian:trixie-slim}
UV_IMAGE=${UV_IMAGE:-ghcr.io/astral-sh/uv:latest}

# This repo's Dockerfile for the free-threaded build.
DOCKERFILE="deploy/Dockerfile.py314t"

function check_directory() {
    working_dir=$(pwd)
    if [ "nora-studio" == "$(basename "${working_dir}")" ]
    then
        # We are in the nora-studio repo.
        # Change directories so that the rest of the script will work OK.
        cd . || exit 1
    fi
}


function build_main() {
    # Outline function which delegates most work to other functions

    check_directory

    # Parse for a specific arg when debugging
    CACHE_OR_NO_CACHE="--rm"
    if [ "$1" == "--no-cache" ]
    then
        CACHE_OR_NO_CACHE="--no-cache --progress=plain"
    fi

    if [ -z "${TARGET_PLATFORM}" ]
    then
        TARGET_PLATFORM="linux/amd64"
    fi
    echo "Target Platform for Docker image generation: ${TARGET_PLATFORM}"

    if [ ! -f "${DOCKERFILE}" ]
    then
        echo "ERROR: ${DOCKERFILE} not found. Run this from the top-level of the nora-studio repo." >&2
        exit 1
    fi

    # Build the docker image
    # DOCKER_BUILDKIT needed for secrets
    # shellcheck disable=SC2086
    DOCKER_BUILDKIT=1 docker build \
        -t nora-fleet/${SERVICE_TAG}:${SERVICE_VERSION} \
        --platform ${TARGET_PLATFORM} \
        --build-arg="NORA_STUDIO_VERSION=${SERVICE_VERSION}" \
        --build-arg="PYTHON_VERSION=${PYTHON_VERSION}" \
        --build-arg="BASE_IMAGE=${BASE_IMAGE}" \
        --build-arg="UV_IMAGE=${UV_IMAGE}" \
        -f "${DOCKERFILE}" \
        ${CACHE_OR_NO_CACHE} \
        .
}


# Call the build_main() outline function
build_main "$@"
