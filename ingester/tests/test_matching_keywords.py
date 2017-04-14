from django.test import  TransactionTestCase

from ingester.matching_functions import match_keywords
from ingester.models import local_url, global_url,keyword_aliases,keyword_alias_source,keywordsModel,publication_keyword


class TestMatchKeyword(TransactionTestCase):
    def setUp(self):
        self.gurl=global_url.objects.create(id= 5, domain="http://dummy.de", url="http://dummy.de")
        self.lurl=local_url.objects.create(id=1, url="blabla", global_url=self.gurl)

    def test_none(self):
        data = None
        identifier = match_keywords(data, self.lurl)
        self.assertEqual(identifier, [])

    def test_empty(self):
        data=[]
        identifier = match_keywords(data, self.lurl)
        self.assertEqual(identifier, [])

    def test_no_match(self):
        identifier = match_keywords(["He?llo", "World"], self.lurl)
        self.assertEqual(identifier, [1, 2])
        self.assertEqual(keyword_aliases.objects.get(id=1).alias, "He?llo")
        self.assertEqual(keyword_aliases.objects.get(id=2).alias, "World")
        self.assertEqual(keyword_alias_source.objects.get(id=1).test(), [1, 1])
        self.assertEqual(keyword_alias_source.objects.get(id=2).test(), [2, 1])
        self.assertEqual(publication_keyword.objects.get(id=1).test(), [1, 1])
        self.assertEqual(publication_keyword.objects.get(id=2).test(), [1, 2])

    def test_single_match(self):
        x= keywordsModel.objects.create(id=3,main_name="Key?Wor!d..", block_name="keyword")
        publication_keyword.objects.create(url=self.lurl,keyword=x)

        data = ["Keyword", "Nonsense"]
        identifier = match_keywords(data, self.lurl)

        self.assertEqual(identifier, [3,4])
        self.assertEqual(keyword_aliases.objects.get(id=1).alias, "Keyword")
        self.assertEqual(keyword_aliases.objects.get(id=2).alias, "Nonsense")
        self.assertEqual(keyword_alias_source.objects.get(id=1).test(), [1, 1])
        self.assertEqual(keyword_alias_source.objects.get(id=2).test(), [2, 1])
        self.assertEqual(publication_keyword.objects.get(id=1).test(), [1, 3])
        self.assertEqual(publication_keyword.objects.get(id=2).test(), [1, 4])

    def test_multi_match_single_alias(self):
        med1 = keywordsModel.objects.create(main_name="myJournal", block_name="myjournal")
        med2 = keywordsModel.objects.create(main_name="myJournal", block_name="myjournal")
        keyword_aliases.objects.create(keyword=med1, alias="myJournal?")
        keyword_aliases.objects.create(keyword=med2, alias="myJournal")

        identifier = match_keywords(["myJournal"], self.lurl)

        self.assertEqual(identifier, [2])
        self.assertEqual(keyword_alias_source.objects.get(id=1).test(),[2,1])
        self.assertEqual(publication_keyword.objects.get(id=1).test(),[1,2])

    def test_multi_match_multi_alias(self):
        med1 = keywordsModel.objects.create(main_name="myJournal", block_name="myjournal")
        med2 = keywordsModel.objects.create(main_name="myJournal", block_name="myjournal")
        keyword_aliases.objects.create(keyword=med1, alias="myJournal")
        keyword_aliases.objects.create(keyword=med2, alias="myJournal")
        # sanity check
        self.assertEqual(keywordsModel.objects.count(),2)
        identifier = match_keywords(["myJOurnal"], self.lurl)

        self.assertEqual(identifier, [3])
        self.assertEqual(keyword_alias_source.objects.get(id=1).test(), [3,1])
        self.assertEqual(publication_keyword.objects.get(id=1).test(), [1, 3])






