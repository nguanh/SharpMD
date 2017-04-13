from django.test import TransactionTestCase,mock
from weaver.PDFDownloader import download_queue
from weaver.models import PDFDownloadQueue
import os
import logging
import sys

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


