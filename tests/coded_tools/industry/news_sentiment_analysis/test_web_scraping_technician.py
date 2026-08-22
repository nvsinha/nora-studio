# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

"""
Tests that the news scraper does not log the API keys it puts in its URLs.

CodeQL flagged this as py/clear-text-logging-sensitive-data. The tool already
called sanitize_url() when logging a URL, but logged the exception text beside
it -- and a requests exception carries the URL that failed, query string and
all. scrape_nyt builds its URL as ...home.json?api-key=<key>, so any failed
NYT call wrote the key to the log in clear text.
"""

import sys
import types
from unittest import TestCase
from unittest.mock import MagicMock


def _install_stubs() -> None:
    """
    Stub the scraper's optional third-party imports.

    backoff, feedparser and newspaper3k are not in requirements.txt -- this
    tool is optional -- so the module cannot be imported in a standard install
    or in CI. The redaction under test is pure string handling and does not
    touch any of them, so stubbing keeps this security check running
    everywhere rather than silently skipping exactly where it matters.
    """
    if "backoff" not in sys.modules:
        backoff = types.ModuleType("backoff")
        # Used as @backoff.on_exception(backoff.expo, ..., max_tries=10): the
        # call must return a decorator, and that decorator must return the
        # function unchanged.
        backoff.on_exception = lambda *args, **kwargs: (lambda func: func)
        backoff.expo = object()
        sys.modules["backoff"] = backoff

    if "feedparser" not in sys.modules:
        feedparser = types.ModuleType("feedparser")
        feedparser.parse = MagicMock()
        sys.modules["feedparser"] = feedparser

    if "newspaper" not in sys.modules:
        newspaper = types.ModuleType("newspaper")
        newspaper.Article = MagicMock()

        # Caught in an except clause, so it has to be a real exception type.
        class ArticleException(Exception):
            """Stand-in for newspaper.ArticleException."""

        newspaper.ArticleException = ArticleException
        sys.modules["newspaper"] = newspaper


_install_stubs()

# pylint: disable=wrong-import-position
from coded_tools.industry.news_sentiment_analysis.web_scraping_technician import SENSITIVE_QUERY_KEYS  # noqa: E402
from coded_tools.industry.news_sentiment_analysis.web_scraping_technician import sanitize_text  # noqa: E402

# pylint: enable=wrong-import-position

# What requests actually raises when the NYT call fails. The key is in the
# path, not a header, so it travels inside the exception message.
NYT_FAILURE = (
    "HTTPSConnectionPool(host='api.nytimes.com', port=443): Max retries exceeded "
    "with url: /svc/topstories/v2/home.json?api-key=SEKRET_NYT_KEY "
    "(Caused by ConnectTimeoutError)"
)

GUARDIAN_FAILURE = (
    "404 Client Error: Not Found for url: "
    "https://content.guardianapis.com/search?q=climate&api-key=SEKRET_GUARDIAN&page-size=50"
)


class TestSanitizeText(TestCase):
    """Unit tests for sanitize_text."""

    def test_nyt_key_is_redacted(self):
        """The NYT key, which sits in the URL path, does not survive into the log line."""
        out = sanitize_text(NYT_FAILURE)
        self.assertNotIn("SEKRET_NYT_KEY", out)
        self.assertIn("api-key=[redacted]", out)

    def test_guardian_key_is_redacted(self):
        """The Guardian key is redacted without disturbing the parameters around it."""
        out = sanitize_text(GUARDIAN_FAILURE)
        self.assertNotIn("SEKRET_GUARDIAN", out)
        self.assertIn("api-key=[redacted]", out)
        # Non-sensitive parameters are diagnostic and should survive.
        self.assertIn("q=climate", out)
        self.assertIn("page-size=50", out)

    def test_every_sensitive_key_is_covered(self):
        """Each key the module declares sensitive is redacted, in any casing."""
        for key in SENSITIVE_QUERY_KEYS:
            for rendered in (key, key.upper()):
                with self.subTest(key=rendered):
                    out = sanitize_text(f"failed for https://x.test/a?{rendered}=LEAKED&next=1")
                    self.assertNotIn("LEAKED", out)
                    self.assertIn("next=1", out)

    def test_longest_key_wins(self):
        """access_token is redacted as itself rather than as a trailing 'token' match."""
        out = sanitize_text("url: https://x.test/a?access_token=LEAKED")
        self.assertNotIn("LEAKED", out)
        self.assertIn("access_token=[redacted]", out)

    def test_value_stops_at_the_parameter_boundary(self):
        """Redaction consumes the value only, not the rest of the message."""
        out = sanitize_text("url: https://x.test/a?token=LEAKED&keep=yes (Caused by X)")
        self.assertNotIn("LEAKED", out)
        self.assertIn("keep=yes", out)
        self.assertIn("(Caused by X)", out)

    def test_text_without_secrets_is_unchanged(self):
        """A message with nothing sensitive passes through untouched."""
        msg = "Connection reset by peer for https://x.test/a?q=climate"
        self.assertEqual(sanitize_text(msg), msg)
