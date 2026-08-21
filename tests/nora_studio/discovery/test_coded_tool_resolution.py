# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

"""Tests for DependencyAnalyzer.resolve_coded_tool_path short-form hierarchy resolution."""

from pathlib import Path

from nora_studio.discovery.dependency_analyzer import DependencyAnalyzer


def _analyzer(tmp_path: Path) -> DependencyAnalyzer:
    """A DependencyAnalyzer pointed at empty registries/coded_tools/middleware under tmp_path."""
    return DependencyAnalyzer(
        str(tmp_path / "registries"),
        str(tmp_path / "coded_tools"),
        str(tmp_path / "middleware"),
    )


class TestShortFormResolution:
    """A short-form ``module.Class`` ref resolves up the group hierarchy, like nora-fleet."""

    def test_resolves_tool_in_per_network_dir(self, tmp_path: Path) -> None:
        """A tool under coded_tools/<group>/<network>/ is found via context_dir."""
        tool = tmp_path / "coded_tools" / "basic" / "music_nerd" / "lookup.py"
        tool.parent.mkdir(parents=True)
        tool.write_text("class Lookup: pass\n")

        result = _analyzer(tmp_path).resolve_coded_tool_path("lookup.Lookup", context_dir="basic/music_nerd")
        assert result == "coded_tools/basic/music_nerd/lookup.py"

    def test_resolves_group_level_tool(self, tmp_path: Path) -> None:
        """A tool at the group level coded_tools/<group>/ is found when not in the network dir.

        Regression for issue #1147: music_nerd_pro's ``accountant.Accountant`` lives at
        coded_tools/basic/accountant.py, not coded_tools/basic/music_nerd_pro/accountant.py.
        """
        tool = tmp_path / "coded_tools" / "basic" / "accountant.py"
        tool.parent.mkdir(parents=True)
        tool.write_text("class Accountant: pass\n")

        result = _analyzer(tmp_path).resolve_coded_tool_path(
            "accountant.Accountant", context_dir="basic/music_nerd_pro"
        )
        assert result == "coded_tools/basic/accountant.py"
