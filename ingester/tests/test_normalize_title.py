from unittest import TestCase
from ingester.helper import normalize_title
import string

class TestNormalize_title(TestCase):
    def test_lower_strip(self):
        title = normalize_title(" ThIs is a TITleß  ")
        self.assertEqual(title, "this is a titless")

    def test_punctuation(self):
        title = normalize_title("O`Really? What's the, iss-ue?  .")
        self.assertEqual(title,"oreally whats the iss ue")

    def test_whitespace(self):
        title = normalize_title("O`Rea\tlly?\n\n Wha\\t's t\nhe, iss\rue?  .")
        self.assertEqual(title, "oreally whats the issue")

    def test_unicode1(self):
        title = normalize_title("Enhancing Access Privacy of Range Retrievals over (𝔹+)-Trees.")#dblp
        title2 = normalize_title("Enhancing Access Privacy of Range Retrievals Over B+-trees")#citeseer
        self.assertEqual(title, title2)
#TODO fällt noch durch
    def test_unicode2(self):
        title = normalize_title("Enhancing Access Privacy of Range Retrievals over (𝔹+)-Trees.")#dblp
        title2 = normalize_title("Enhancing Access Privacy of Range Retrievals over $({\rm B}^+)$-Trees") #dl.acm
        self.assertEqual(title, title2)

    def test_unicode3(self):
        title = normalize_title("Efficient controller synthesis for a fragment of MTL0,∞")
        self.assertEqual("efficient controller synthesis for a fragment of mtl0", title)

    def test_unicode4(self):
        title = normalize_title("Sometime = Always + Recursion = Always on the Equivalence of the Intermittent and Invariant Assertions Methods for Proving Inevitability Properties of Programs.")
        self.assertEqual("sometime always recursion always on the equivalence of the intermittent and invariant assertions methods for proving inevitability properties of programs", title)



