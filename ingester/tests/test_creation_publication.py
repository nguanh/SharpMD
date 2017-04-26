from django.test import TestCase,TransactionTestCase

from ingester.creation_functions import create_publication
from ingester.models import *
import os

ingester_path = os.path.dirname(os.path.dirname(__file__))


class TestCreatePublication(TransactionTestCase):
    fixtures = [os.path.join(ingester_path, "fixtures", "initial_data.json")]

    def setUp(self):
        self.gurl = global_url.objects.get(id=1)
        self.lurl = local_url.objects.create(id=1, url="a", global_url=self.gurl)
        self.cluster_id = cluster.objects.create(id=1, name="random Title")
        self.author1 = authors_model.objects.create(id=1, main_name="Nina Nonsense", block_name="nonsense,n")
        self.author2 = authors_model.objects.create(id=2, main_name="Otto Otter", block_name="otter,o")

        self.medium = pub_medium.objects.create(id=1, main_name="myJournal", block_name="myjournal",
                                                journal="myJournal")
        self.medium2 = pub_medium.objects.create(id=2, main_name="myJournal", block_name="myjournal",
                                                 journal="myJournal")
        self.type = publication_type.objects.get(name="misc")

    def test_no_publication(self):
        self.assertEqual(publication_author.objects.count(), 0)
        typ = publication_type.objects.get(id=3)
        result = create_publication(self.gurl, self.cluster_id, [self.author1,self.author2], typ, self.medium)

        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[1].id, 2)
        # check publication authors
        self.assertEqual(publication_author.objects.count(), 2)
        aut1 = publication_author.objects.get(id=1)
        aut2 = publication_author.objects.get(id=2)
        # test author publications
        self.assertEqual(aut1.test(), [2, 1, 0])
        self.assertEqual(aut2.test(), [2, 2, 1])
        # test local url
        self.assertEqual(result[1].test(), [1, "TODO PLATZHALTER", 1, 3, None])
        self.assertEqual(result[0].test(), [2, 1, ""])

    def test_existing_publication(self):
        pub = publication.objects.create(id=5,url=self.lurl,cluster= self.cluster_id, title="my title")
        result = create_publication(self.gurl, self.cluster_id, [self.author1,self.author2], 3, self.medium2)

        self.assertEqual(result[0].id, pub.id)
        self.assertEqual(result[1].id, self.lurl.id)
        aut1 = publication_author.objects.get(id=1)
        aut2 = publication_author.objects.get(id=2)
        self.assertEqual(aut1.test(), [1, 1, 0])
        self.assertEqual(aut2.test(), [1, 2, 1])

    def test_no_medium_and_type(self):
        self.assertEqual(publication_author.objects.count(), 0)
        result = create_publication(self.gurl, self.cluster_id, [self.author1,self.author2], self.type, None)

        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[1].id, 2)
        # check publication authors
        self.assertEqual(publication_author.objects.count(), 2)
        aut1 = publication_author.objects.get(id=1)
        aut2 = publication_author.objects.get(id=2)
        # test author publications
        self.assertEqual(aut1.test(), [2, 1, 0])
        self.assertEqual(aut2.test(), [2, 2, 1])
        # test local url
        self.assertEqual(result[1].test(), [1, "TODO PLATZHALTER", None, self.type.id,None])
        self.assertEqual(result[0].test(), [2, 1, ""])

    def test_keywords(self):
        key1 = keywordsModel.objects.create(id=1, main_name="Hallo")
        key2 = keywordsModel.objects.create(id=5, main_name="Welt")
        result = create_publication(self.gurl, self.cluster_id,[self.author1,self.author2],None,None, [key1,key2])
        self.assertEqual(publication_keyword.objects.get(id=1).test(), [result[1].id, key1.id])
        self.assertEqual(publication_keyword.objects.get(id=2).test(), [result[1].id, key2.id])

