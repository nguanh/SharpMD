from ingester.Iingester import Iingester
from mysqlWrapper.mariadb import MariaDb
from conf.config import get_config
from ingester.helper import split_authors
from ingester.models import global_url
import re

def is_not_empty(var):
    return var is not None and len(var) > 0

class ArxivIngester(Iingester):

    def __init__(self, name, harvester_db=None):
        Iingester.__init__(self,name)
        # find global url/ add global URL
        g_url,created = global_url.objects.get_or_create(
            domain='http://arxiv.org',
            url='http://arxiv.org/abs/'
        )
        self.global_url = g_url
        if harvester_db is None:
            self.harvester_db = get_config("DATABASES")["harvester"]
        else:
            self.harvester_db = harvester_db
        self.query = "SELECT * FROM {}.arxiv_articles WHERE last_harvested = 0".format(self.harvester_db)

    def get_global_url(self):
        return self.global_url

    def update_harvested(self):
        return "UPDATE {}.arxiv_articles SET last_harvested = CURRENT_TIMESTAMP  WHERE identifier = %s"\
                .format(self.harvester_db)


    def mapping_function(self, query_tuple):
        mapping = self.generate_empty_mapping()
        # is set later
        mapping["local_url"] = query_tuple[0]
        mapping["publication"]["date_published"] = query_tuple[1].year #TODO parse date
        mapping["publication"]["date_added"] = query_tuple[13].year #TODO parse date
        authors_list = split_authors(query_tuple[3])
        for author in authors_list:
            stripped_numbers = re.sub(r'\d{4}', '', author).strip()
            mapping["authors"].append(self.generate_author_mapping(author,stripped_numbers))

        mapping["publication"]["title"] = query_tuple[4]
        mapping["publication"]["abstract"] = query_tuple[10]
        mapping["publication"]["doi"] = query_tuple[12]
        mapping["study_fields"] = query_tuple[11]
        mapping["publication"]["type_ids"] = 1

        #TODO try to extract some information from journalref
        return mapping
