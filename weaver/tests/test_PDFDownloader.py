from django.test import TransactionTestCase,mock
from unittest.mock import patch
from weaver.PDFDownloader import download_queue,PdfDownloader
from weaver.models import PDFDownloadQueue,OpenReferences,SingleReference
from weaver.exceptions import GrobidException
import os
import logging
import sys
import datetime

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



class TestPDFDownloader(TransactionTestCase):
    def setUp(self):
        self.output_folder ="C:\\Users\\anhtu\\Desktop\\pdf"
        # delete all files in test folder
        for the_file in os.listdir(self.output_folder):
            file_path = os.path.join(self.output_folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

        PDFDownloadQueue.objects.bulk_create([
            PDFDownloadQueue(url="https://arxiv.org/pdf/1704.03738.pdf", tries=0),
            PDFDownloadQueue(url="https://arxiv.org/pdf/1704.03732.pdf", tries=0),
            PDFDownloadQueue(url="https://arxiv.org/pdf/1704.03723.pdf", tries=0),
            ]
        )

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # create the logging file handler
        fh = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        # add handler to logger object
        self.logger.addHandler(fh)

    def test_success(self):
        self.assertEqual(PDFDownloadQueue.objects.count(), 3)
        result=download_queue(self.output_folder,self.logger)
        self.assertEqual(PDFDownloadQueue.objects.count(), 0)
        self.assertTrue(os.path.isfile(os.path.join(self.output_folder,"1704.03738.pdf")))
        self.assertTrue(os.path.isfile(os.path.join(self.output_folder, "1704.03732.pdf")))
        self.assertTrue(os.path.isfile(os.path.join(self.output_folder, "1704.03723.pdf")))
        self.assertEqual(result["successful"], 3)

    def test_success_limit(self):
        self.assertEqual(PDFDownloadQueue.objects.count(), 3)
        result = download_queue(self.output_folder, self.logger, limit=1)
        self.assertEqual(PDFDownloadQueue.objects.count(), 2)
        self.assertTrue(os.path.isfile(os.path.join(self.output_folder, "1704.03738.pdf")))
        self.assertEqual(result["successful"], 1)

    def test_invalid_link(self):
        PDFDownloadQueue.objects.all().delete()
        PDFDownloadQueue.objects.create(url="https://arxiv.org/pdf/1704dasdsad738.pdf", tries=0)
        result = download_queue(self.output_folder, self.logger)
        self.assertEqual(result["invalid"],1)
        self.assertEqual(PDFDownloadQueue.objects.count(),0)

    @patch("weaver.PDFDownloader.requests.get")
    def test_403(self,req):
        req.return_value.status_code = 403
        PDFDownloadQueue.objects.all().delete()
        PDFDownloadQueue.objects.create(url="https://arxiv.org/pdf/1704dasdsad738.pdf", tries=0)
        result = download_queue(self.output_folder, self.logger)
        self.assertEqual(result["skipped"], 1)
        obj = PDFDownloadQueue.objects.first()
        self.assertEqual(obj.tries, 1)
        self.assertIsNotNone(obj.last_try)




