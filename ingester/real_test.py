from dblp.dblpingester import DblpIngester
from .ingesting_function import ingest_data



def full_execution():
    ingester = DblpIngester("dblp.ingester")
    ingester.set_limit(1000)
    result = ingest_data(ingester)
