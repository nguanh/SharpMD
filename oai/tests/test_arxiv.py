from unittest import TestCase
from lxml import etree
from oai.arxiv_handler import ArXivRecord
import datetime

def get_record(path):
    tree = etree.parse(path)
    for element in tree.iter():
        if element.tag == "{http://www.openarchives.org/OAI/2.0/}record":
            return element
    return None


class Test_Arxiv(TestCase):

    def test_valid(self):
        record = get_record("arxiv_file_valid.xml")
        result = ArXivRecord(record)
        self.assertEqual(result.metadata, {'authors': 'Balázs,C.;Berger,E. L.;Nadolsky,P. M.;Yuan,C. -P.;',
                                          'doi': '10.1103/PhysRevD.76.013009',
                                          'created': datetime.datetime(2007, 4, 2, 0, 0),
                                          'abstract': '\nA fully differential calculation in perturbative quantum chromodynamics is presented for the production of massive photon pairs at hadron colliders. All next-to-leading order perturbative contributions from quark-antiquark, gluon-(anti)quark, and gluon-gluon subprocesses are included, as well as all-orders resummation of initial-state gluon radiation valid at next-to-next-to-leading logarithmic accuracy. The region of phase space is specified in which the calculation is most reliable. Good agreement is demonstrated with data from the Fermilab Tevatron, and predictions are made for more detailed tests with CDF and DO data. Predictions are shown for distributions of diphoton pairs produced at the energy of the Large Hadron Collider (LHC). Distributions of the diphoton pairs from the decay of a Higgs boson are contrasted with those produced from QCD processes at the LHC, showing that enhanced sensitivity to the signal can be obtained with judicious selection of events.\n',
                                          'updated': datetime.datetime(2007, 7, 24, 0, 0),
                                          'journal-ref': 'Phys.Rev.D76:013009,2007',
                                          'comments': '37 pages, 15 figures; published version',
                                          'title': 'Calculation of prompt diphoton production cross sections at Tevatron and LHC energies',
                                          'categories': 'hep-ph',
                                          'identifier': '0704.0001',
                                          'report-no': 'ANL-HEP-PR-07-12',
                                          'mdate': datetime.datetime(2008,11,26,0,0)

                                           }
                        )

    def test_deleted(self):
        record = get_record("arxiv_file_deleted.xml")
        result = ArXivRecord(record)
        self.assertEqual(result.deleted, True)


