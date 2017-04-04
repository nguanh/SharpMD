from django.test import TestCase

from ingester.matching_functions import match_type
import os

ingester_path = os.path.dirname(os.path.dirname(__file__))


class TestMatchType(TestCase):
    fixtures = [os.path.join(ingester_path, "fixtures", "initial_data.json")]

    def test_success(self):
        identifier = match_type('article')
        self.assertEqual(identifier.id, 1)

    def test_no_matching_type(self):
        identifier = match_type('blubb')
        self.assertEqual(identifier.id, 2)

    def test_no_matching_type2(self):
        identifier = match_type(None)
        self.assertEqual(identifier.id, 2)

