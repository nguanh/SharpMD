
from ingester.ingest_task import ingest_task
from ingester.exception import IIngester_Disabled,IIngester_Exception

mode = 2
if mode == 0:
    package = "dblp.dblpingester"
    class_name = "DblpIngester"
elif mode == 1:
    package = "oai.arxivingester"
    class_name = "ArxivIngester"
else:
    package = "oai.citeseeringester"
    class_name = "CiteseerIngester"
try:
    ingest_task(package, class_name)
except ImportError as e:
    print(e)
except IIngester_Exception as e:
    print(e)
except IIngester_Disabled as e:
    print(e)

