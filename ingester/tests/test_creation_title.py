
from django.test import TestCase

from ingester.helper import *
from ingester.creation_functions import create_title
from ingester.models import *


class TestCreateTitle(TestCase):

    def test_single_match(self):
        cluster.objects.create(id=1, name= "matching title")
        title = "matching title"
        matching = {
            "status": Status.SAFE,
            "match": Match.SINGLE_MATCH,
            "id": 1,
            "reason": None,
        }

        result = create_title(matching,title,)
        self.assertEqual(result,1)

    def test_no_match(self):
        title = "matching title"
        matching = {
            "status": Status.SAFE,
            "match": Match.NO_MATCH,
            "id": None,
            "reason": None,
        }

        result = create_title(matching, title)
        self.assertEqual(result, 1)
        self.assertEqual(cluster.objects.first().name, "matching title")

