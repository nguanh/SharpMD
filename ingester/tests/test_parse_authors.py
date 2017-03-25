from unittest import TestCase
from ingester.helper import get_name_block


class TestParse_authors(TestCase):
    def test_parse_authors1(self):
        name = get_name_block("Walter Vogler")
        self.assertEqual(name, "vogler,w")

    def test_parse_authors2(self):
        name = get_name_block("Richard Müller")
        self.assertEqual(name, "muller,r")

    def test_parse_authors3(self):
        name = get_name_block("Alexander S. szalay")

        self.assertEqual(name, "szalay,a")

    def test_parse_authors4(self):
        name = get_name_block("luqi")

        self.assertEqual(name, "luqi,")

    def test_parse_authors5(self):
        name = get_name_block("Peter van der Stok")

        self.assertEqual(name, "van der stok,p")

    def test_parse_authors6(self):
        name = get_name_block("Yi-Ping Phoebe Chen")

        self.assertEqual(name, "chen,y")

    def test_parse_authors7(self):
        name = get_name_block("Jóhanna V. Gísladóttir")
        self.assertEqual(name, "gisladottir,j")

    def test_parse_authors8(self):
        name = get_name_block("Andreas Giskeødegård")
        self.assertEqual(name, "giskeodegard,a")

    def test_parse_authors9(self):
        name = get_name_block("Ola R. Snøve Jr")
        self.assertEqual(name, "snove,o")
