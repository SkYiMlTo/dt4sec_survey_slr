"""
tests/test_models.py
====================
Unit tests for ``slr.models`` — Article normalisation and helpers.
"""
import pytest

from slr.models import Article, normalise_doi, normalise_title, is_valid_doi


class TestNormaliseDoi:
    def test_bare_doi(self):
        assert normalise_doi("10.1109/ACCESS.2022.001") == "10.1109/access.2022.001"

    def test_doi_with_url_prefix(self):
        assert normalise_doi("https://doi.org/10.1007/s12345") == "10.1007/s12345"

    def test_doi_with_http_prefix(self):
        assert normalise_doi("http://doi.org/10.1007/s12345") == "10.1007/s12345"

    def test_doi_with_doi_colon(self):
        assert normalise_doi("DOI: 10.1234/example") == "10.1234/example"

    def test_na_sentinel(self):
        assert normalise_doi("N/A") == ""

    def test_empty(self):
        assert normalise_doi("") == ""

    def test_none(self):
        assert normalise_doi(None) == ""

    def test_href_form(self):
        result = normalise_doi('href="/10.1145/3456789"')
        assert result == "10.1145/3456789"

    def test_doi_url_prefix_only(self):
        assert normalise_doi("https://doi.org/") == ""

    def test_trailing_dot_stripped(self):
        assert normalise_doi("10.1234/test.") == "10.1234/test"


class TestNormaliseTitle:
    def test_lowercase(self):
        assert normalise_title("Digital Twin Security") == "digital twin security"

    def test_strip_punctuation(self):
        assert normalise_title("A Survey: Digital Twins!") == "survey digital twins"

    def test_strip_leading_article(self):
        assert normalise_title("The Study") == "study"
        assert normalise_title("A Review") == "review"
        assert normalise_title("An Analysis") == "analysis"

    def test_collapse_whitespace(self):
        assert normalise_title("  Too   Many   Spaces  ") == "too many spaces"

    def test_empty(self):
        assert normalise_title("") == ""


class TestIsValidDoi:
    def test_valid(self):
        assert is_valid_doi("10.1109/access.2022.001") is True
        assert is_valid_doi("10.1007/s12345-678") is True

    def test_invalid_empty(self):
        assert is_valid_doi("") is False

    def test_invalid_na(self):
        assert is_valid_doi("N/A") is False

    def test_invalid_url_only(self):
        assert is_valid_doi("https://doi.org/") is False


class TestArticleNormalisation:
    def test_doi_normalised_on_init(self):
        article = Article(
            title="Test",
            authors=[],
            publication_year="2022",
            doi="https://doi.org/10.1234/test",
            source="http://example.com",
        )
        assert article.doi == "10.1234/test"

    def test_title_stripped(self):
        article = Article(
            title="  Spaces  ",
            authors=[],
            publication_year="2022",
            doi="10.1234/x",
            source="http://example.com",
        )
        assert article.title == "Spaces"

    def test_normalised_title_computed(self):
        article = Article(
            title="The Digital Twin Survey",
            authors=[],
            publication_year="2022",
            doi="10.1234/x",
            source="http://example.com",
        )
        assert article._normalised_title == "digital twin survey"

    def test_has_valid_doi_true(self):
        article = Article("T", [], "2022", "10.1234/x", "http://e.com")
        assert article.has_valid_doi is True

    def test_has_valid_doi_false(self):
        article = Article("T", [], "2022", "", "http://e.com")
        assert article.has_valid_doi is False

    def test_authors_str_no_authors(self):
        article = Article("T", [], "2022", "10.1234/x", "http://e.com")
        assert article.authors_str == "No authors"

    def test_authors_str_with_authors(self):
        article = Article(
            "T",
            [{"fullName": "Alice Smith"}, {"fullName": "Bob Jones"}],
            "2022",
            "10.1234/x",
            "http://e.com",
        )
        assert "Alice Smith" in article.authors_str
        assert "Bob Jones" in article.authors_str

    def test_to_dict_keys(self):
        article = Article("T", [], "2022", "10.1234/x", "http://e.com")
        d = article.to_dict()
        assert set(d.keys()) == {"title", "authors", "publication_year", "doi", "source", "abstract"}
