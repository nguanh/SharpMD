from unittest import TestCase
from ingester.helper import get_search_query, get_relevant_words


class TestGet_search_query(TestCase):
    def test_get_search_query_1(self):
        title = "this is a title"
        result = get_relevant_words(title)
        self.assertEqual(result, ['title'])

    def test_get_search_query_2(self):
        title = "using deep learning and google street view to estimate the demographic makeup of the us"
        result = get_relevant_words(title)
        self.assertEqual(result, ["demographic", "estimate", "learning"])

    def test_get_search_query_3(self):
        title = "using deep learning and google street view to estimate the demographic makeup of the us"
        result = get_search_query(title)
        self.assertEqual(result, "demographic* estimate* learning*")

    def test_short_title(self):
        title= "this is a sho rt tit le"
        result = get_search_query(title)
        self.assertEqual(result, title)
