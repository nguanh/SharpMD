from .dblpingester import DblpIngester
from ingester.helper import split_authors
import re

def is_not_empty(var):
    return var is not None and len(var) > 0

class DuplicateDblpIngester(DblpIngester):
    """
    USED FOR TESTING ONLY
    This ingester allows ingesting records that are already included by adding the 'XX' prefix to every local_url
    this allows simulating test cases, where publications from different sources refer to the same publication
    """
    def __init__(self, name, harvesterdb=None):
        DblpIngester.__init__(self,name,harvesterdb)
        self.query = ("SELECT * FROM {}.dblp_article WHERE last_harvested != 0").format(self.harvester_db)

    def mapping_function(self, query_tuple):
        mapping = self.generate_empty_mapping()
        # is set later
        mapping["local_url"] = "XX{}".format(query_tuple[0])
        mapping["publication"]["date_added"] = query_tuple[1].year
        authors_list = split_authors(query_tuple[2])
        for author in authors_list:
            stripped_numbers = re.sub(r'\d{4}', '', author).strip()
            mapping["authors"].append(self.generate_author_mapping(author, stripped_numbers))

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

        # find key for publication
        pub_type = mapping["publication"]["type_ids"]
        if (pub_type == "phdthesis" or pub_type == "mastersthesis") and is_not_empty(mapping["pub_release"]["school"]):
            mapping["pub_release"]["key"] = mapping["pub_release"]["school"]
        elif pub_type == "inproceedings" and is_not_empty(mapping["pub_release"]["book_title"]):
            mapping["pub_release"]["key"] = mapping["pub_release"]["book_title"]
        elif pub_type == "article" and is_not_empty(mapping["pub_release"]["journal"]):
            mapping["pub_release"]["key"] = mapping["pub_release"]["journal"]

        return mapping
