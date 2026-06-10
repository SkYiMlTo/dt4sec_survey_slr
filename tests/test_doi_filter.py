"""
tests/test_doi_filter.py
=========================
Unit tests for ``slr.processors.doi_filter``.
"""
import pytest

from slr.models import Article
from slr.processors.doi_filter import filter_no_doi


def _make(doi: str) -> Article:
    return Article(
        title=f"Test article doi={doi!r}",
        authors=[],
        publication_year="2022",
        doi=doi,
        source="http://test.com",
    )


class TestFilterNoDoi:
    def test_valid_doi_passes(self):
        articles = [_make("10.1109/access.2022.001")]
        filtered, report = filter_no_doi(articles)
        assert len(filtered) == 1
        assert report.output_count == 1

    def test_empty_doi_rejected(self):
        articles = [_make("")]
        filtered, report = filter_no_doi(articles)
        assert len(filtered) == 0
        assert report.rejected_count == 1

    def test_na_sentinel_rejected(self):
        for sentinel in ["N/A", "n/a", "N.A.", "null", "none", "NA"]:
            articles = [_make(sentinel)]
            filtered, report = filter_no_doi(articles)
            assert len(filtered) == 0, f"Expected {sentinel!r} to be rejected"

    def test_doi_url_prefix_only_rejected(self):
        articles = [_make("https://doi.org/")]
        filtered, report = filter_no_doi(articles)
        assert len(filtered) == 0

    def test_invalid_format_rejected(self):
        articles = [_make("not-a-doi-at-all")]
        filtered, report = filter_no_doi(articles)
        assert len(filtered) == 0

    def test_mixed_corpus(self):
        articles = [
            _make("10.1234/valid"),
            _make(""),
            _make("N/A"),
            _make("10.9999/another.valid"),
            _make("https://doi.org/"),
        ]
        filtered, report = filter_no_doi(articles)
        assert len(filtered) == 2
        assert report.input_count == 5
        assert report.rejected_count == 3

    def test_empty_input(self):
        filtered, report = filter_no_doi([])
        assert filtered == []
        assert report.input_count == 0
        assert report.output_count == 0

    def test_report_summary_contains_count(self):
        articles = [_make(""), _make("10.1234/x")]
        _, report = filter_no_doi(articles)
        summary = report.summary()
        assert "2 in" in summary
        assert "1 out" in summary
