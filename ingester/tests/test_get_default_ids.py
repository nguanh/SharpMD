
from django.test import TransactionTestCase
from ingester.difference_storage import get_default_ids,generate_diff_store
from .ingester_tools import get_pub_dict
from ingester.models import *
import os

ingester_path = os.path.dirname(os.path.dirname(__file__))

class TestGet_defbault_ids(TransactionTestCase):
    fixtures = [os.path.join(ingester_path, "fixtures", "initial_data.json")]
    def setUp(self):
        self.gurl=global_url.objects.create(id= 5, domain="http://dummy.de", url="http://dummy.de")
        self.lurl=local_url.objects.create(id=1, url="blabla", global_url=self.gurl)

    def test_success_empty(self):
        # article
        t = publication_type.objects.get(id=1)
        medium = pub_medium.objects.create(main_name="Testest", book_title="Testest")

        pre_store = get_pub_dict(url_id=5,type_ids=t.id, pub_source_ids=medium.id)
        store = generate_diff_store(pre_store)
        get_default_ids(store,self.lurl)
        self.assertEqual(self.lurl.medium, medium)
        self.assertEqual(self.lurl.type,t)

    def test_success_filled(self):
        t = publication_type.objects.get(id=1)
        medium = pub_medium.objects.create(main_name="Testest", book_title="Testest")
        self.lurl.medium = medium
        self.lurl.type = t
        self.lurl.save()
        pre_store = get_pub_dict(url_id=5, type_ids=None, pub_source_ids=None)

        store = generate_diff_store(pre_store)
        get_default_ids(store,self.lurl)
        self.assertEqual(self.lurl.medium, medium)
        self.assertEqual(self.lurl.type,t)

    def test_success_filled_2(self):
        t = publication_type.objects.get(id=1)
        t2 = publication_type.objects.get(id=2)
        medium = pub_medium.objects.create(main_name="Testest", book_title="Testest")
        medium2 = pub_medium.objects.create(main_name="Testest2", book_title="Testest2")
        self.lurl.medium = medium
        self.lurl.type = t
        self.lurl.save()
        pre_store = get_pub_dict(url_id=5,type_ids=t2.id, pub_source_ids=medium2.id)

        store = generate_diff_store(pre_store)
        get_default_ids(store,self.lurl)
        self.assertEqual(self.lurl.medium, medium2)
        self.assertEqual(self.lurl.type, t2)


