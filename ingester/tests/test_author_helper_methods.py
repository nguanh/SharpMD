from unittest import TestCase
from ingester.helper import get_author_relevant_names,get_author_search_query, normalize_authors,calculate_author_similarity, similarity_helper


class TestAuthorHelper(TestCase):
    def test_normalize_authors(self):
        result = normalize_authors("! Kim lu Yee ")
        self.assertEqual(result, "kim lux yee")

    def test_normalize_authors3(self):
        result = normalize_authors("C.B. Lee")
        self.assertEqual(result, "c b lee")

    def test_normalize_authors_2(self):
        result = normalize_authors("Martin S. Müller ")
        self.assertEqual(result, "martin s muller")

    def test_relevant_names(self):
        result = get_author_relevant_names(normalize_authors("Martin S. Müller"))
        self.assertEqual(result,["martin", "muller"])

    def test_relevant_names_2(self):
        result = get_author_relevant_names(normalize_authors("Kim Li Suu"))
        self.assertEqual(result,["kim", "lix", 'suu'])

    def test_search_query(self):
        result = get_author_search_query(normalize_authors("Fang a Yang Su"))
        self.assertEqual(result,"+yang +fang +sux")

    def test_search_query_2(self):
        result = get_author_search_query(normalize_authors("Richard Dawson A. St. Louis"))
        self.assertEqual(result,"+richard +dawson +louis +stx")

    def test_search_query_3(self):
        result = get_author_search_query(normalize_authors("kim lee  lu Meyers A. Bueno"))
        self.assertEqual(result,"+meyers +bueno +lux")

    def test_similarity(self):
        result = calculate_author_similarity("Chin Jen Lin","Chin A lin")
        self.assertEqual(result, False)

    def test_similarity_2(self):
        result = calculate_author_similarity("chin jen lin","chin j lin")
        self.assertEqual(result, True)

    def test_similarity_3(self):
        result = calculate_author_similarity("chin jen lin","lin j chin")
        self.assertEqual(result, False)

    def test_similarity_4(self):
        result = calculate_author_similarity("chin anton jin","anton j chin")
        self.assertEqual(result, True)

    def test_similarity_5(self):
        result = calculate_author_similarity("chin a j","anton j b chin")
        self.assertEqual(result, False)

    def test_similarity_6(self):
        result = calculate_author_similarity("chin a bing jin","anton j lin chin")
        self.assertEqual(result, False)

    def test_similarity_regression_1(self):
        result = calculate_author_similarity("yufeng xin", "xinzhi xing")
        self.assertEqual(result,False)

    def test_similarity_regression_2(self):
        result = calculate_author_similarity("x", "xin xin")
        self.assertEqual(result,False)

    def test_similarity_regression_3(self):
        result = calculate_author_similarity("ernest j", "john e")
        self.assertEqual(result, False)

    def test_similarity_regression_4(self):
        result = calculate_author_similarity("p d h hill", "hillary d protas")
        self.assertEqual(result, False)

    def test_similarity_regression_6(self):
        result = calculate_author_similarity("pedro bernaola galva n", "pedro neto")
        self.assertEqual(result, False)
        result = calculate_author_similarity("ahmed metwally", "ahmed hassan m h ali")
        self.assertEqual(result, False)

    def test_similarity_regression_5(self):
        result = calculate_author_similarity("dah ming chiu", "dah ming w chiu")
        self.assertEqual(result, True)
        result2 = calculate_author_similarity("dah ming chiu", "chiu dah ming")
        self.assertEqual(result2, True)

    def test_similarity_regression_8(self):
        self.assertEqual(calculate_author_similarity("howard ottensen", "howard o meyer"), False)
        self.assertEqual(calculate_author_similarity("howard ottensen", "h ottensen"), True)

    def test_sim_helper_1(self):
        self.assertEqual(similarity_helper("chim sum cha".split(" "), "chim sum cha".split(" ")),True)
        self.assertEqual(similarity_helper("chim sum cha".split(" "), "chim s cha".split(" ")), True)
        self.assertEqual(similarity_helper("chim sum".split(" "), "chim sum cha".split(" ")), True)
        self.assertEqual(similarity_helper("chim s c".split(" "), "chim sum cha".split(" ")), True)
        self.assertEqual(similarity_helper("chim sum c".split(" "), "chim s cha".split(" ")), False)
        self.assertEqual(similarity_helper("chim sum c ban tu".split(" "), "chim sum cha".split(" ")), False)
        self.assertEqual(similarity_helper("chim cha sum".split(" "), "chim sum cha".split(" ")), False)
        self.assertEqual(similarity_helper("la lu mu".split(" "),"la le lu mu".split(" ")),True)
        self.assertEqual(similarity_helper("la le lu mu".split(" "), "la lu mu".split(" ")), False)

    def test_similarity_regression_7(self):
        result = calculate_author_similarity("j p olivier dex sardan", "olivier peulen")
        self.assertEqual(result, False)

    def test_similarity_regression_9(self):
        self.assertEqual(calculate_author_similarity("zhang xiu", "zhang xiu"), True)
        self.assertEqual(calculate_author_similarity("zhang xiu", "xiu zhang"), True)

        self.assertEqual(calculate_author_similarity("zhang xiu", "zhang x"), True)
        self.assertEqual(calculate_author_similarity("zhang xiu", "x zhang"), True)

    def test_regression_10(self):
        self.assertEqual(calculate_author_similarity("John Michael", "John Meyer Michael"), True)
        self.assertEqual(calculate_author_similarity("Mohn Michael", "John Michael"), False)
        self.assertEqual(calculate_author_similarity("rhys hill", "donna r hill"), False)
        self.assertEqual(calculate_author_similarity("jose pereira", "jose m g torres pereira"), False)




