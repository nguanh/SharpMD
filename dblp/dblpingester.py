import re

from ingester.Iingester import Iingester
from ingester.helper import split_authors
from conf.config import get_config
from ingester.models import global_url


def is_not_empty(var):
    return var is not None and len(var) > 0


class DblpIngester(Iingester):
    def __init__(self, name, harvesterdb=None):
        Iingester.__init__(self,name)
        # find global url/ add global URL
        g_url,created = global_url.objects.get_or_create(
            domain='http://dblp.uni-trier.de',
            url='http://dblp.uni-trier.de/rec/xml/',
        )
        self.global_url = g_url
        if harvesterdb is None:
            self.harvester_db = get_config("DATABASES")["harvester"]
        else:
            self.harvester_db = harvesterdb
        self.query = ("SELECT * FROM {}.dblp_article WHERE last_harvested = 0").format(self.harvester_db)

    def get_global_url(self):
        return self.global_url

    def update_harvested(self):
        return "UPDATE {}.dblp_article SET last_harvested = CURRENT_TIMESTAMP  WHERE dblp_key = %s"\
                .format(self.harvester_db)

    def set_reference(self, ingester_url, harvester_id):
        pass

    def mapping_function(self, query_tuple):
        mapping = self.generate_empty_mapping()
        # is set later
        mapping["local_url"] = query_tuple[0]
        mapping["publication"]["date_added"] = query_tuple[1].year
        authors_list = split_authors(query_tuple[2])
        for author in authors_list:
            stripped_numbers = re.sub(r'\d{4}', '', author).strip()
            mapping["authors"].append(self.generate_author_mapping(author,stripped_numbers))

        mapping["publication"]["title"] = query_tuple[3]
        mapping["publication"]["pages"] = query_tuple[4]
        mapping["publication"]["date_published"] = query_tuple[5].year
        mapping["publication"]["volume"] = query_tuple[6]
        mapping["pub_release"]["journal"] = query_tuple[7]
        mapping["publication"]["number"] = query_tuple[8]
        mapping["publication"]["doi"] = query_tuple[9]
        mapping["publication"]["type_ids"] = query_tuple[19]
        mapping["pub_release"]["book_title"] = query_tuple[13]
        mapping["pub_release"]["school"] = query_tuple[14]
        mapping["pub_release"]["address"] = query_tuple[15]
        mapping["pub_release"]["publisher"] = query_tuple[16]
        mapping["pub_release"]["isbn"] = query_tuple[17]
        mapping["pub_release"]["series"] = query_tuple[18]

        #find key for publication
        pub_type = mapping["publication"]["type_ids"]
        if (pub_type == "phdthesis" or pub_type == "mastersthesis") and is_not_empty(mapping["pub_release"]["school"]):
            mapping["pub_release"]["key"] = mapping["pub_release"]["school"]
        elif pub_type == "inproceedings"and is_not_empty(mapping["pub_release"]["book_title"]):
            mapping["pub_release"]["key"] = mapping["pub_release"]["book_title"]
        elif pub_type == "article"and is_not_empty(mapping["pub_release"]["journal"]):
            mapping["pub_release"]["key"] = mapping["pub_release"]["journal"]

        return mapping