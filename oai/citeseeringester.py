from ingester.Iingester import Iingester
from mysqlWrapper.mariadb import MariaDb
from conf.config import get_config
from ingester.helper import split_authors
import datetime

def is_not_empty(var):
    return var is not None and len(var) > 0

class CiteseerIngester(Iingester):

    def __init__(self, ingester_db, harvester_db):
        Iingester.__init__(self)
        credentials = dict(get_config("MARIADB"))
        connector = MariaDb(credentials)
        connector.connector.database = ingester_db
        # find global url/ add global URL
        global_url_query = "SELECT id FROM global_url WHERE domain = 'http://citeseerx.ist.psu.edu/'"
        result = connector.fetch_one((), global_url_query)
        if result is None:
            insert_global_url = ("INSERT INTO global_url(domain,url) "
                                 "VALUES ('http://citeseerx.ist.psu.edu/',"
                                 "'http://citeseerx.ist.psu.edu/viewdoc/summary?doi=')")
            connector.execute_ex(insert_global_url)
            result = connector.fetch_one((), global_url_query)
        connector.close_connection()
        self.global_url = result
        self.harvester_db = harvester_db
        self.query = "SELECT * FROM {}.oaipmh_articles WHERE last_harvested = 0".format(self.harvester_db)

    def get_global_url(self):
        return self.global_url

    def update_harvested(self):
        return "UPDATE {}.oaipmh_articles SET last_harvested = CURRENT_TIMESTAMP  WHERE identifier = %s"\
                .format(self.harvester_db)

    def get_name(self):
        return "ingester.citeseer"

    def mapping_function(self, query_tuple):
        mapping = self.generate_empty_mapping()
        # is set later
        mapping["local_url"] = query_tuple[0].replace(";","")
        authors_list = split_authors(query_tuple[1])
        for author in authors_list:
            mapping["authors"].append(self.generate_author_mapping(author, author))
        mapping["publication"]["title"] = query_tuple[2].replace(";","")
        mapping["publication"]["abstract"] = query_tuple[3].replace(";","")
        mapping["publication"]["type_ids"] = 2 # misc
        if query_tuple[13] is not None:
            mapping["keywords"] = query_tuple[13].split(";")
            del mapping["keywords"][-1]
        if query_tuple[6] is not None:
            dates = query_tuple[6].split(";")
            del dates[-1]
            try:
                # publication date ist the last date
                mapping["publication"]["date_published"] = datetime.datetime.strptime(dates[-1],"%Y-%m-%d").year
            except ValueError:
                try:
                    mapping["publication"]["date_published"] = datetime.datetime.strptime(dates[-1], "%Y").year
                except:
                    print("No Date")
                    mapping["publication"]["date_published"] = None
            return mapping
