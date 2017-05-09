from django.test import  TransactionTestCase

from ingester.matching_functions import match_pub_medium
from ingester.models import local_url, pub_alias_source, pub_medium, pub_medium_alias, global_url
from .ingester_tools import get_pub_source


class TestMatchMedium(TransactionTestCase):
    def setUp(self):
        self.gurl=global_url.objects.create(id= 5, domain="http://dummy.de", url="http://dummy.de")
        self.lurl=local_url.objects.create(id=1, url="blabla", global_url=self.gurl)

    def test_none(self):
        data = get_pub_source()
        identifier = match_pub_medium(data, self.lurl)
        self.assertEqual(identifier, None)

    def test_multi_match_multi_alias(self):
        med1 = pub_medium.objects.create(id=1, main_name="myJournal", block_name="myjournal", journal="myJournal")
        med2 = pub_medium.objects.create(id=2, main_name="myJournal", block_name="myjournal", journal="myJournal")
        pub_medium_alias.objects.create(id=1, medium=med1, alias="myJournal" )
        pub_medium_alias.objects.create(id=2, medium=med2, alias="myJournal")
        # sanity check
        self.assertEqual(pub_medium.objects.count(),2)
        data = get_pub_source(key="myJournal", journal="myJournal")
        identifier = match_pub_medium(data, self.lurl)

        self.assertEqual(identifier.id, 3)
        self.assertEqual(pub_alias_source.objects.get(id=1).alias.id, 3)


    def test_multi_match_single_alias(self):
        med1 = pub_medium.objects.create(main_name="myJournal", block_name="myjournal", journal="myJournal")
        med2 = pub_medium.objects.create(main_name="myJournal", block_name="myjournal", journal="myJournal")
        pub_medium_alias.objects.create(medium=med1, alias="myJournal?" )
        pub_medium_alias.objects.create( medium=med2, alias="myJournal")

        data = get_pub_source(key="myJournal", journal="myJournal")
        identifier = match_pub_medium(data, self.lurl)

        self.assertEqual(identifier.id, 2)
        self.assertEqual(pub_alias_source.objects.get(id=1).alias.id,2)


    def test_no_match(self):
        data = get_pub_source(key="myJournal", journal="myJournal")
        identifier = match_pub_medium(data, self.lurl)
        self.assertEqual(identifier.id, 1)
        self.assertEqual(pub_medium_alias.objects.get(id=1).alias,"myJournal")
        self.assertEqual(pub_alias_source.objects.get(id=1).alias.alias,"myJournal")
        self.assertEqual(pub_alias_source.objects.get(id=1).url.id,1)
        pub_source = pub_medium.objects.get(id=1)
        self.assertEqual(pub_source.main_name,"myJournal")
        self.assertEqual(pub_source.block_name,"myjournal")
        self.assertEqual(pub_source.journal,"myJournal")

    def test_single_match(self):
        pub_medium.objects.create(id=1,main_name="myJournal",block_name="myjournal",journal="myJournal")
        data = get_pub_source(key="myJournal", journal="myJournal")
        identifier = match_pub_medium(data,self.lurl)

        self.assertEqual(identifier.id, 1)
        alias = pub_medium_alias.objects.get(id=1).alias
        self.assertEqual(alias, "myJournal")
        self.assertEqual(pub_alias_source.objects.get(id=1).alias.alias, "myJournal")
        self.assertEqual(pub_alias_source.objects.get(id=1).url.id, 1)






