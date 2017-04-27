from unittest import TestCase
from ingester.helper import get_author_relevant_names,get_author_search_query, normalize_authors


class TestAuthorHelper(TestCase):
    def test_normalize_authors(self):
        result = normalize_authors("! Kim lu Yee ")
        self.assertEqual(result, "kim lux yee")

    def test_normalize_authors_2(self):
        result = normalize_authors("Martin S. Müller ")
        self.assertEqual(result, "martin s muller")

    def test_relevant_names(self):
        result = get_author_relevant_names("Martin S. Müller")
        self.assertEqual(result,["martin", "muller"])

    def test_relevant_names_2(self):
        result = get_author_relevant_names("Kim Li Suu")
        self.assertEqual(result,["kim", "lix", 'suu'])

    def test_search_query(self):
        result = get_author_search_query("Fang a Yang Su")
        self.assertEqual(result,"+yang +fang +sux")

    def test_search_query_2(self):
        result = get_author_search_query("Richard Dawson A. St. Louis")
        self.assertEqual(result,"+richard +dawson +louis")



