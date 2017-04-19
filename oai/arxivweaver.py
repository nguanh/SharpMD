from weaver.IWeaver import IWeaver
from mysqlWrapper.mariadb import MariaDb
from weaver.exceptions import IWeaver_Exception
from weaver.models import OpenReferences,PDFDownloadQueue


class ArxivWeaver(IWeaver):
    def __init__(self, limit, database):
        IWeaver.__init__(self,limit)
        self.database = database
        self.table_nr = 0

    def run(self):
        """
        fetch unreferenced entries from harvester table and aggregate the pdf url from the recor key.
        Add url to PDF Downloader queue database
        :return:
        """
        query = "SELECT identifier FROM {}.arxiv_articles WHERE last_referenced = 0 LIMIT {}".format(self.database, self.limit)
        connector = MariaDb()
        write_connector = MariaDb()
        try:
            connector.cursor.execute(query)
        except Exception as e:
            raise IWeaver_Exception(e)

        for query_dataset in connector.cursor:
            key = query_dataset[0]
            url = "https://arxiv.org/pdf/{}.pdf".format(key)

            ref,created = OpenReferences.objects.get_or_create(source_table=self.table_nr, source_key=key)
            # add url to download queue
            PDFDownloadQueue.objects.get_or_create(tries=0, url=url, source=ref)
            # set entry as referenced
            write_connector.execute_ex(("UPDATE {}.arxiv_articles "
                                        "SET last_referenced = CURRENT_TIMESTAMP  "
                                        "WHERE identifier = %s").format(self.database), (key,))

        connector.close_connection()
        write_connector.close_connection()








