"""
tests/test_deduplicator.py
===========================
Unit tests for ``slr.processors.deduplicator``.
"""
import pytest

from slr.models import Article
from slr.processors.deduplicator import deduplicate, DEFAULT_FUZZY_THRESHOLD


def _make(title: str, doi: str = "", source: str = "http://test.com") -> Article:
    return Article(title=title, authors=[], publication_year="2022", doi=doi, source=source)


class TestDeduplicateDoiExact:
    def test_identical_dois_kept_once(self):
        articles = [
            _make("Paper One", doi="10.1234/one"),
            _make("Paper One (duplicate)", doi="10.1234/one"),
        ]
        unique, report = deduplicate(articles)
        assert len(unique) == 1
        assert report.doi_duplicates == 1

    def test_doi_case_insensitive(self):
        articles = [
            _make("Paper A", doi="10.1234/UPPER"),
            _make("Paper B", doi="10.1234/upper"),  # same after normalise
        ]
        unique, report = deduplicate(articles)
        assert len(unique) == 1
        assert report.doi_duplicates == 1

    def test_different_dois_both_kept(self):
        articles = [
            _make("Paper A", doi="10.1234/aaa"),
            _make("Paper B", doi="10.1234/bbb"),
        ]
        unique, report = deduplicate(articles)
        assert len(unique) == 2
        assert report.doi_duplicates == 0


class TestDeduplicateTitleExact:
    def test_same_title_different_case(self):
        articles = [
            _make("Digital Twin Security Survey", doi="10.1234/one"),
            _make("digital twin security survey", doi="10.1234/two"),  # different DOI
        ]
        unique, report = deduplicate(articles)
        assert len(unique) == 1
        assert report.title_exact_duplicates == 1

    def test_title_with_punctuation(self):
        articles = [
            _make("A Survey: Digital Twins!", doi="10.1234/one"),
            _make("A Survey Digital Twins", doi="10.1234/two"),
        ]
        unique, report = deduplicate(articles)
        assert len(unique) == 1

    def test_distinct_titles_kept(self):
        articles = [
            _make("Digital Twin Security", doi="10.1234/aaa"),
            _make("IoT Cybersecurity Framework", doi="10.1234/bbb"),
        ]
        unique, report = deduplicate(articles)
        assert len(unique) == 2


class TestDeduplicateFuzzy:
    def test_near_identical_titles(self):
        # 'Digital Twin for Cybersecurity' vs 'Digital Twins for Cybersecurity'
        articles = [
            _make("Digital Twin for Cybersecurity Applications", doi="10.1234/aaa"),
            _make("Digital Twins for Cybersecurity Applications", doi="10.1234/bbb"),
        ]
        unique, report = deduplicate(articles, fuzzy_threshold=90)
        assert len(unique) == 1
        assert report.title_fuzzy_duplicates == 1

    def test_very_different_titles_not_merged(self):
        articles = [
            _make("Machine Learning in Healthcare", doi="10.1234/aaa"),
            _make("Digital Twin Cybersecurity Survey", doi="10.1234/bbb"),
        ]
        unique, report = deduplicate(articles, fuzzy_threshold=DEFAULT_FUZZY_THRESHOLD)
        assert len(unique) == 2
        assert report.title_fuzzy_duplicates == 0


class TestDeduplicationReport:
    def test_report_counts_correct(self):
        articles = [
            _make("Paper One", doi="10.1234/one"),
            _make("Paper One", doi="10.1234/two"),    # title-exact dup
            _make("Paper Two", doi="10.1234/three"),
        ]
        unique, report = deduplicate(articles)
        assert report.input_count == 3
        assert report.output_count == 2
        assert report.total_dropped == 1

    def test_empty_input(self):
        unique, report = deduplicate([])
        assert unique == []
        assert report.input_count == 0
        assert report.output_count == 0
