from harvester.harvest_task import harvest_task
from harvester.exception import *
mode = 2
if mode == 0:
    package = "dblp.dblpharvester"
    class_name = "DblpHarvester"
    name = "DBLP_HARVESTER"
elif mode == 1:
    package = "oai.oaiharvester"
    class_name = "OaiHarvester"
    name = "OAI_HARVESTER"
else:
    package = "oai.arxivharvester"
    class_name = "ArXivHarvester"
    name = "ARXIV_HARVESTER"

try:
    harvest_task(package, class_name, name, path="configs/harvester_local.ini")
except ImportError as e:
    print(e)
except IHarvest_Exception as e:
    print(e)
except IHarvest_Disabled:
    print("Task disabled")

