# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT
"""
Verifies that every class path referenced from a HOCON registry actually
resolves to a class that exists on disk.

Why this test exists
--------------------
Agent networks name their coded tools as *runtime strings*::

    "class": "nora_studio.coded_tools.web_fetch.WebFetch"

Nothing statically checks those. No import is executed at lint time, no type
checker follows them, and the test suite does not exercise most registries.
A typo -- or a package rename that updates the string but not the file, or the
file but not the string -- fails only when that specific network is run, which
may be never in CI.

That makes these strings the single most fragile surface in the repo, so they
get their own gate.

How it resolves
---------------
Two shapes appear in the registries:

* Fully qualified, rooted at a first-party package
  (``nora_studio.coded_tools.web_fetch.WebFetch``).
* Relative to ``AGENT_TOOL_PATH``. These are NOT a flat lookup: the framework
  searches ``<AGENT_TOOL_PATH>/<agent-network-name>/<module>.py`` first and
  then walks *up* the network-name path to the shared root. So
  ``call_agent.CallAgent`` in ``registries/experimental/cruse_agent.hocon``
  resolves against ``coded_tools/experimental/cruse_agent/`` before
  ``coded_tools/experimental/`` and finally ``coded_tools/``. This mirrors
  ``AbstractClassActivation.resolve_class`` in nora-fleet; if that changes,
  change this with it.

A reference may also name a third-party class outright
(``langchain.agents.middleware.PIIMiddleware``). Those are resolved through
``importlib.util.find_spec``, and skipped when the package is not installed --
an uninstalled optional extra is not a broken class path.

Resolution is done by locating the module file and parsing it with ``ast``,
never by importing. Importing would drag in every optional dependency the
tools use (docling, jira, arxiv, ...), so a missing extra would masquerade as
a broken class path -- exactly the false signal this gate must not produce.
"""

import ast
import importlib.util
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRIES = REPO_ROOT / "registries"

# Directories a bare, AGENT_TOOL_PATH-relative reference may resolve against.
TOOL_ROOTS = [REPO_ROOT / "coded_tools"]

# First-party top-level packages that may appear in a fully qualified path.
FIRST_PARTY = ("nora_studio", "coded_tools", "middleware", "apps", "skills")

# Third-party top-level packages a reference may legitimately name. This is an
# explicit allowlist, not a heuristic, and the gate FAILS CLOSED: anything that
# resolves neither to a first-party file, nor under AGENT_TOOL_PATH, nor to a
# package listed here, is treated as broken.
#
# The allowlist matters. An earlier version skipped any unresolvable path whose
# root was not first-party, which meant a rename bug -- nora_studio mangled to
# nora_fleet_studio, exactly the collision this migration risked -- was reported
# as a SKIP rather than a failure. A gate that cannot fail is not a gate.
THIRD_PARTY_OK = {"langchain"}

# Keys whose values name a Python class.
CLASS_KEY = re.compile(r'"(?:class|factory)"\s*:\s*"([^"]+)"')


def _hocon_files():
    return sorted(REGISTRIES.rglob("*.hocon"))


def _class_refs():
    """Yield (hocon_path, reference) for every class-valued key."""
    for path in _hocon_files():
        text = path.read_text(encoding="utf-8")
        for ref in CLASS_KEY.findall(text):
            yield path, ref


def _candidates(dotted, hocon_path):
    """Every path the framework would try, in the order it tries them."""
    parts = dotted.split(".")
    if parts[0] in FIRST_PARTY:
        return [REPO_ROOT.joinpath(*parts).with_suffix(".py")]

    # Agent network name is the registry path minus the .hocon suffix.
    network = hocon_path.relative_to(REGISTRIES).with_suffix("")
    out = []
    for root in TOOL_ROOTS:
        segments = list(network.parts)
        # Search the network's own directory first, then walk up to the root.
        while True:
            out.append(root.joinpath(*segments, *parts).with_suffix(".py"))
            if not segments:
                break
            segments.pop()
    return out


def _module_file(dotted, hocon_path):
    """Map a dotted module path to a file, or None if nothing matches."""
    for candidate in _candidates(dotted, hocon_path):
        if candidate.is_file():
            return candidate
    return None


def _defines(path, name):
    """True if the module at `path` defines a class or function `name`."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name == name:
            return True
        # Re-exported via `from x import Name` also counts as resolvable.
        if isinstance(node, ast.ImportFrom):
            if any(name in (alias.asname, alias.name) for alias in node.names):
                return True
    return False


def test_registries_directory_exists():
    """Guards against the test silently passing on an empty glob."""
    assert REGISTRIES.is_dir(), f"missing registries dir: {REGISTRIES}"
    assert _hocon_files(), "no .hocon files found -- glob is wrong"


def test_class_references_found():
    """There should be a meaningful number of references to check."""
    refs = list(_class_refs())
    assert len(refs) > 20, f"only found {len(refs)} class refs -- regex may be wrong"


@pytest.mark.parametrize(
    "hocon_path,ref",
    [pytest.param(p, r, id=f"{p.relative_to(REGISTRIES)}::{r}") for p, r in _class_refs()],
)
def test_class_path_resolves(hocon_path, ref):
    """Every HOCON class reference must resolve to a class that exists."""
    if "." not in ref:
        pytest.skip(f"not a dotted path: {ref!r}")

    dotted, _, name = ref.rpartition(".")
    module = _module_file(dotted, hocon_path)

    top = dotted.split(".")[0]
    if module is None and top in THIRD_PARTY_OK:
        # An allowlisted third-party class. Verify the module exists; skip only
        # when the package itself is not installed (an optional extra).
        try:
            if importlib.util.find_spec(top) is None:
                pytest.skip(f"optional third-party package {top!r} not installed")
            spec = importlib.util.find_spec(dotted)
        except (ImportError, ValueError, ModuleNotFoundError):
            spec = None
        assert spec is not None, (
            f"{hocon_path.relative_to(REPO_ROOT)} references {ref!r} but the "
            f"third-party module {dotted!r} does not exist"
        )
        return

    assert module is not None, (
        f"{hocon_path.relative_to(REPO_ROOT)} references {ref!r} but no module "
        f"file was found for {dotted!r}. Searched:\n  "
        + "\n  ".join(str(c.relative_to(REPO_ROOT)) for c in _candidates(dotted, hocon_path))
    )

    assert _defines(module, name), (
        f"{hocon_path.relative_to(REPO_ROOT)} references {ref!r} but "
        f"{module.relative_to(REPO_ROOT)} does not define {name!r}"
    )
