from ingester.Iingester import Iingester
from ingester.models import global_url
from ingester.helper import split_authors
from conf.config import get_config
import datetime


def is_not_empty(var):
    return var is not None and len(var) > 0


class CiteseerIngester(Iingester):

    def __init__(self, name, harvester_db=None):
        Iingester.__init__(self,name)

        # find global url/ add global URL
        g_url, created = global_url.objects.get_or_create(
            domain='http://citeseerx.ist.psu.edu/',
            url='http://citeseerx.ist.psu.edu/viewdoc/summary?doi='
        )
        self.global_url = g_url
        if harvester_db is None:
            self.harvester_db = get_config("DATABASES")["harvester"]
        else:
            self.harvester_db = harvester_db

        self.query = "SELECT * FROM {}.oaipmh_articles WHERE last_harvested = 0".format(self.harvester_db)

    def get_global_url(self):
        return self.global_url

    def update_harvested(self):
        return "UPDATE {}.oaipmh_articles SET last_harvested = CURRENT_TIMESTAMP  WHERE identifier = %s"\
                .format(self.harvester_db)

    def set_reference(self, ingester_url, harvester_id):
        # TODO
        pass

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
