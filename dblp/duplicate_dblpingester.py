from .dblpingester import DblpIngester


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
        mapping = DblpIngester.mapping_function(self,query_tuple)
        print(mapping['local_url'])
        mapping['local_url'] = "XX{}".format(mapping['local_url'])
        return mapping
