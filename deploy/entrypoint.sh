#!/bin/bash
# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

# Entry point script which manages the transition from
# Docker bash to Python

cat /etc/os-release

PYTHON=python3
echo "Using python ${PYTHON}"

PIP=pip3
echo "Using pip ${PIP}"

# The Log Bridge plugin aggregates logs from server and client subprocesses, and pretty-prints them.
# But we only deploy the nora-fleet server here, and it has its own logging configuration.
# So we forcibly disable the log bridge plugin to avoid conflicts.
export LOGBRIDGE_ENABLED=false

echo "Preparing app..."
if [ -z "${PYTHONPATH}" ]
then
    PYTHONPATH=$(pwd)
fi
export PYTHONPATH

echo "Configuration information:"
grep MemTotal < /proc/meminfo
if [ -f /sys/fs/cgroup/memory/memory.limit_in_bytes ]
then
    cat /sys/fs/cgroup/memory/memory.limit_in_bytes
fi
if [ -f /sys/fs/cgroup/memory.max ]
then
    cat /sys/fs/cgroup/memory.max
fi

if command -v lscpu >/dev/null 2>&1
then
    lscpu | grep "^CPU(s):"
fi
if [ -f /sys/fs/cgroup/cpu/cpu.cfs_quota_us ]
then
    cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us
fi
if [ -f /sys/fs/cgroup/cpu.max ]
then
    cat /sys/fs/cgroup/cpu.max
fi

ulimit -a

echo "Toolchain:"
${PYTHON} --version
${PIP} --version
${PIP} freeze

PACKAGE_INSTALL=${PACKAGE_INSTALL:-.}
echo "PACKAGE_INSTALL is ${PACKAGE_INSTALL}"

echo "AGENT_SESSION_REQUIRE_HTTPS = ${AGENT_SESSION_REQUIRE_HTTPS}"

echo "DIAGNOSTIC: Dumping sys.path and PYTHONPATH before server start..."
${PYTHON} -c "import sys, os; print('DIAGNOSTIC sys.path:', sys.path); print('DIAGNOSTIC PYTHONPATH:', os.environ.get('PYTHONPATH'))"

echo "Starting service with args '$1'..."
${PYTHON} "${APP_SOURCE}"/nora_studio/runner/nora_fleet_server_wrapper.py "$@"

echo "Done."
