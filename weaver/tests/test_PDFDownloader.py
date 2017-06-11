from django.test import TransactionTestCase,mock
from unittest.mock import MagicMock
from unittest.mock import patch
from weaver.PDFDownloader import PdfDownloader
from weaver.models import PDFDownloadQueue,OpenReferences,SingleReference
from weaver.exceptions import GrobidException
import os
import logging
import sys
import datetime
from requests.exceptions import ConnectionError

path = os.path.dirname(os.path.abspath(__file__))


class TestGrobid(TransactionTestCase):
    def setUp(self):
        self.file_path = os.path.join(path, "grobid1.pdf")
        self.grobid_url = "http://localhost:8080/processReferences"
        self.source = OpenReferences.objects.create(source_table="0",source_key="AAAAA")

    def test_success(self):
        x = PdfDownloader(path,self.grobid_url)
        x.parse_references(self.file_path,self.source)
        self.assertEqual(SingleReference.objects.count(),5)
        ref1 = SingleReference.objects.get(id=1).test()
        ref2 = SingleReference.objects.get(id=2).test()
        ref3 = SingleReference.objects.get(id=3).test()
        ref4 = SingleReference.objects.get(id=4).test()
        ref5 = SingleReference.objects.get(id=5).test()
        self.assertEqual(ref1, [1, 'Retrieving metadata for your local scholarly papers',
                                datetime.date(2009, 1, 1), 'D. Aumueller', 'OP'])

        self.assertEqual(ref2, [1, 'Introducing Mr. DLib, a Machine-readable Digital Library',
                                datetime.date(2011, 1, 1),
                                'J. Beel;B. Gipp;S. Langer;M. Genzmehr;E. Wilde;A. NĂźrnberger;J. Pitman', 'OP'])
        self.assertEqual(ref3, [1, 'SciPlore Xtract: Extracting Titles from Scientific PDF Documents by Analyzing Style Information (Font Size)',
                                datetime.date(2010, 1, 1), 'J. Beel;B. Gipp;A. Shaker;N. Friedrich', 'OP'])

    def test_invalid_path(self):
        x = PdfDownloader(path,self.grobid_url)
        self.assertRaises(GrobidException,x.parse_references,"nkjk",self.source)

    def test_invalid_file(self):
        x = PdfDownloader(path, self.grobid_url)
        file = os.path.join(path, "invalid.txt")
        self.assertRaises(GrobidException, x.parse_references, file, self.source)

    def test_get_reference_no_analytics(self):
        tei_doc = {
            "monogr":{
                "title": "title",
                "authors":["A. And; B. And"],
                "pubyear": "2001"
            }
        }
        x = PdfDownloader.get_reference(tei_doc)
        self.assertEqual(x, {"title": "title",
                             "authors": ["A. And; B. And"],
                             "pubyear": datetime.date(2001, 1, 1)})

    def test_get_reference_no_analytics_no_date(self):
        tei_doc = {
            "monogr":{
                "title": "title",
                "authors":["A. And; B. And"],
                "pubyear": None
            }
        }
        x = PdfDownloader.get_reference(tei_doc)
        self.assertEqual(x, {"title": "title",
                             "authors": ["A. And; B. And"],
                             "pubyear": None})

    def test_analytics(self):
        tei_doc = {
            "monogr": {
                "title": "title",
                "authors": None,
                "pubyear": None
            },
            "analytic": {
                "title": "better title",
                "authors": ["A. And; B. And"],
                "pubyear": "1999"
            }
        }
        x = PdfDownloader.get_reference(tei_doc)
        self.assertEqual(x, {"title": "better title",
                             "authors": ["A. And; B. And"],
                             "pubyear": datetime.date(1999, 1, 1)})

    def test_analytics_2(self):
        tei_doc = {
            "monogr": {
                "title": "title",
                "authors": None,
                "pubyear": "1998"
            },
            "analytic": {
                "title": "better title",
                "authors": ["A. And; B. And"],
                "pubyear": None
            }
        }
        x = PdfDownloader.get_reference(tei_doc)
        self.assertEqual(x, {"title": "better title",
                             "authors": ["A. And; B. And"],
                             "pubyear": datetime.date(1998, 1, 1)})

    def test_no_title(self):
        tei_doc = {
            "monogr": {
                "title": None,
                "authors": None,
                "pubyear": None
            },
            "analytic": {
                "title": None,
                "authors": ["A. And; B. And"],
                "pubyear": "1999"
            }
        }
        x = PdfDownloader.get_reference(tei_doc)
        self.assertEqual(x, None)

    def test_no_authors(self):
        tei_doc = {
            "monogr": {
                "title": "title",
                "authors": None,
                "pubyear": None
            },
            "analytic": {
                "title": "better title",
                "authors": [],
                "pubyear": "1999"
            }
        }
        x = PdfDownloader.get_reference(tei_doc)
        self.assertEqual(x, None)


class TestPDFDownloader(TransactionTestCase):
    def setUp(self):
        self.grobid_url = "http://localhost:8080/processReferences"
        self.source = OpenReferences.objects.create(source_table="0",source_key="AAAAA")
        self.output_folder = "C:\\Users\\anhtu\\Desktop\\pdf"

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # create the logging file handler
        fh = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        # add handler to logger object
        self.logger.addHandler(fh)

        self.obj = PdfDownloader(self.output_folder, self.grobid_url ,logger=self.logger)
        self.obj.parse_references= MagicMock(return_value=None)
        # delete all files in test folder
        for the_file in os.listdir(self.output_folder):
            file_path = os.path.join(self.output_folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

        self.source = OpenReferences.objects.create(source_table=0, source_key="AAAAA")

        PDFDownloadQueue.objects.bulk_create([
            PDFDownloadQueue(url="https://arxiv.org/pdf/1704.03738.pdf", tries=0, source=self.source),
            PDFDownloadQueue(url="https://arxiv.org/pdf/1704.03732.pdf", tries=0, source=self.source),
            PDFDownloadQueue(url="https://arxiv.org/pdf/1704.03723.pdf", tries=0, source=self.source),
            ]
        )

    def test_success(self):
        self.assertEqual(PDFDownloadQueue.objects.count(), 3)
        result= self.obj.process_pdf()
        self.assertEqual(PDFDownloadQueue.objects.count(), 0)
        self.assertEqual(result["successful"], 3)
        self.obj.parse_references.assert_called_with(os.path.join(self.output_folder,"1704.03723.pdf"),self.source)

    def test_success_limit(self):
        self.assertEqual(PDFDownloadQueue.objects.count(), 3)
        self.obj.limit=1
        result = self.obj.process_pdf()
        self.assertEqual(PDFDownloadQueue.objects.count(), 2)
        self.assertEqual(result["successful"], 1)
        self.obj.parse_references.assert_called_with(os.path.join(self.output_folder, "1704.03738.pdf"), self.source)


    @patch("weaver.PDFDownloader.requests.get")
    def test_403(self, req):
        req.return_value.status_code = 403
        PDFDownloadQueue.objects.all().delete()
        PDFDownloadQueue.objects.create(url="https://arxiv.org/pdf/1704dasdsad738.pdf", tries=0)
        result = self.obj.process_pdf()
        self.assertEqual(result["skipped"], 1)
        obj = PDFDownloadQueue.objects.first()
        self.assertEqual(obj.tries, 1)
        self.assertIsNotNone(obj.last_try)

    @patch("weaver.PDFDownloader.requests.get")
    def test_404(self, req):
        req.return_value.status_code = 404
        PDFDownloadQueue.objects.all().delete()
        PDFDownloadQueue.objects.create(url="https://arxiv.org/pdf/1704dasdsad738.pdf", tries=0)
        result = self.obj.process_pdf()
        self.assertEqual(result["invalid"], 1)
        self.assertEqual(PDFDownloadQueue.objects.count(), 0)



    @patch("weaver.PDFDownloader.requests.get")
    def test_false(self, req):
        req.return_value.ok = False
        PDFDownloadQueue.objects.all().delete()
        PDFDownloadQueue.objects.create(url="https://arxiv.org/pdf/1704dasdsad738.pdf", tries=0)
        result = self.obj.process_pdf()
        self.assertEqual(result["skipped"], 1)
        obj = PDFDownloadQueue.objects.first()
        self.assertEqual(obj.tries, 1)
        self.assertIsNotNone(obj.last_try)

    def test_connection_error(self):
        self.assertEqual(PDFDownloadQueue.objects.count(), 3)
        self.obj.parse_references.side_effect = ConnectionError()
        result = self.obj.process_pdf()
        self.assertEqual(PDFDownloadQueue.objects.count(), 3)
        self.assertEqual(result["skipped"], 1)

    def test_error(self):
        self.obj.limit=1
        self.obj.parse_references.side_effect = Exception()
        result = self.obj.process_pdf()
        self.assertEqual(PDFDownloadQueue.objects.count(), 3)
        self.assertEqual(result["skipped"], 1)

    def test_regression(self):
        file_path = os.path.join(path, "0704.0251.pdf")
        x = PdfDownloader(path, self.grobid_url)
        x.parse_references(file_path, self.source)

    def test_regression1(self):
        file_path = os.path.join(path, "reg1.pdf")
        x = PdfDownloader(path, self.grobid_url)
        x.parse_references(file_path, self.source)

    def test_regression2(self):
        file_path = os.path.join(path, "reg2.pdf")
        x = PdfDownloader(path, self.grobid_url)
        x.parse_references(file_path, self.source)

    def test_regression3(self):
        file_path = os.path.join(path, "reg3.pdf")
        x = PdfDownloader(path, self.grobid_url)
        x.parse_references(file_path, self.source)

    def test_regression4(self):
        file_path = os.path.join(path, "reg4.pdf")
        x = PdfDownloader(path, self.grobid_url)
        x.parse_references(file_path, self.source)

    def test_regression5(self):
        file_path = os.path.join(path, "reg5.pdf")
        x = PdfDownloader(path, self.grobid_url)
        x.parse_references(file_path, self.source)

    def test_regression6(self):
        file_path = os.path.join(path, "reg6.pdf")
        x = PdfDownloader(path, self.grobid_url)
        x.parse_references(file_path, self.source)

    def test_regression7(self):
        file_path = os.path.join(path, "reg7.pdf")
        x = PdfDownloader(path, self.grobid_url)
        x.parse_references(file_path, self.source)

    def test_regression8(self):
        file_path = os.path.join(path, "reg8.pdf")
        x = PdfDownloader(path, self.grobid_url)
        x.parse_references(file_path, self.source)

    def test_regression9(self):
        file_path = os.path.join(path, "reg9.pdf")
        x = PdfDownloader(path, self.grobid_url)
        x.parse_references(file_path, self.source)

    def test_regression10(self):
        file_path = os.path.join(path, "reg10.pdf")
        x = PdfDownloader(path, self.grobid_url)
        x.parse_references(file_path, self.source)

    @patch("weaver.PDFDownloader.requests.get")
    def test_pdf_downloader_regression1(self, req):
        req.return_value.status_code = 403
        PDFDownloadQueue.objects.all().delete()
        PDFDownloadQueue.objects.create(url="http://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC4656104&blobtype=pdf", tries=0)
        result = self.obj.process_pdf(user_agent='Mozilla/5.0')
        self.assertEqual(result["skipped"], 0)



