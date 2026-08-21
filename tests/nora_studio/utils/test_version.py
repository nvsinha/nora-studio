# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

from importlib.metadata import PackageNotFoundError

import pytest

from nora_studio.utils import version as version_module
from nora_studio.utils.version import resolve_version
from nora_studio.utils.version import studio_version


class TestResolveVersion:
    """Resolving (version, source) for nora-studio."""

    @staticmethod
    def _uninstalled(monkeypatch: pytest.MonkeyPatch) -> None:
        """Make the distribution-metadata lookup behave as not-installed."""

        def boom(_name: str) -> str:
            raise PackageNotFoundError("nora-studio")

        monkeypatch.setattr(version_module, "library_version", boom)

    def test_env_var_override_takes_precedence(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """If NORA_STUDIO_VERSION is set in environment and not 'unknown', it takes precedence."""
        monkeypatch.setenv("NORA_STUDIO_VERSION", "2.3.4")
        monkeypatch.setattr(version_module, "library_version", lambda _name: "1.2.3")
        assert resolve_version() == ("2.3.4", version_module.SOURCE_ENV)

    def test_installed_distribution_reports_installed_source(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Distribution metadata gives the version tagged as 'installed'."""
        monkeypatch.setattr(version_module, "library_version", lambda _name: "1.2.3")
        assert resolve_version() == ("1.2.3", "installed")

    def test_resolves_the_studio_distribution_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """The resolver looks up the published distribution name, not the import package."""
        seen: dict = {}

        def fake_version(name: str) -> str:
            seen["name"] = name
            return "9.9.9"

        monkeypatch.setattr(version_module, "library_version", fake_version)
        resolve_version()
        assert seen["name"] == "nora-studio"

    def test_scm_fallback_reports_source(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """An uninstalled checkout resolves via setuptools-scm, tagged 'source'."""
        self._uninstalled(monkeypatch)
        monkeypatch.setattr(version_module, "_scm_version", lambda: "0.0.0.dev1+gabc1234")
        assert resolve_version() == ("0.0.0.dev1+gabc1234", "source")

    def test_git_fallback_reports_git_source(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """With no distribution and no scm, the short git sha is used, tagged 'git'."""
        self._uninstalled(monkeypatch)
        monkeypatch.setattr(version_module, "_scm_version", lambda: "")
        monkeypatch.setattr(version_module, "_git_sha", lambda: "abc1234")
        assert resolve_version() == ("abc1234", "git")

    def test_unknown_when_nothing_resolves(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """No distribution, no scm, and no git sha surfaces ('unknown', 'unknown')."""
        self._uninstalled(monkeypatch)
        monkeypatch.setattr(version_module, "_scm_version", lambda: "")
        monkeypatch.setattr(version_module, "_git_sha", lambda: "")
        assert resolve_version() == ("unknown", "unknown")

    def test_warns_through_each_fallback(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Each degradation step logs a warning rather than failing silently."""
        self._uninstalled(monkeypatch)
        monkeypatch.setattr(version_module, "_scm_version", lambda: "")
        monkeypatch.setattr(version_module, "_git_sha", lambda: "")
        with caplog.at_level("WARNING"):
            resolve_version()
        assert "not installed" in caplog.text
        assert "setuptools-scm unavailable" in caplog.text
        assert "git sha" in caplog.text

    def test_studio_version_returns_bare_string(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """studio_version() drops the source tag, returning just the version string."""
        monkeypatch.setattr(version_module, "library_version", lambda _name: "1.2.3")
        assert studio_version() == "1.2.3"
