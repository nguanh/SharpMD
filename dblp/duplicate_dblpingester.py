from .dblpingester import DblpIngester


class DuplicateDblpIngester(DblpIngester):
    """
    USED FOR TESTING ONLY
    This ingester allows ingesting records that are already included by adding the 'XX' prefix to every local_url
    this allows simulating test cases, where publications from different sources refer to the same publication
    """

    def mapping_function(self, query_tuple):
        mapping = super(DblpIngester, self).mapping_function(query_tuple)
        mapping['local_url'] = "XX" + mapping['local_url']
        return mapping
