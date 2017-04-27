from unittest import TestCase
from ingester.helper import get_author_relevant_names,get_author_search_query, normalize_authors,calculate_author_similarity


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

    def test_search_query_3(self):
        result = get_author_search_query("kim lee  lu Meyers A. Bueno")
        self.assertEqual(result,"+meyers +bueno +lux")

    def test_similarity(self):
        result = calculate_author_similarity("Chin Jen Lin","Chin A lin")
        self.assertEqual(result, False)

    def test_similarity_2(self):
        result = calculate_author_similarity("chin jen lin","chin j lin")
        self.assertEqual(result, True)

    def test_similarity_3(self):
        result = calculate_author_similarity("chin jen lin","lin j chin")
        self.assertEqual(result, True)

    def test_similarity_4(self):
        result = calculate_author_similarity("chin a jin","anton j chin")
        self.assertEqual(result, True)

    def test_similarity_5(self):
        result = calculate_author_similarity("chin a jin","anton j b chin")
        self.assertEqual(result, True)

    def test_similarity_6(self):
        result = calculate_author_similarity("chin a bing jin","anton j lin chin")
        self.assertEqual(result, False)


