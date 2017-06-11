import os
import re
from ingester.models import cluster,local_url,global_url
from weaver.models import OpenReferences, PDFDownloadQueue
from weaver.PDFDownloader import PdfDownloader
from ingester.helper import normalize_title
import logging
from conf.config import get_config


local_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(local_path,'data')
#list of MAG ids that have a valid pdf file
match_list=[
    "0AB5DA92",
    #"003D2ABA",
    "03A0D543",
    "5DE7D587",
    "015EEC82",
    "026E4E7E",
    #"41DE1CEC",
    "46EF8055",
    "0257F156",
    "01865193",
    "03729759",
    "473B91DE"]
    #"10726450"]
# list of pdf urls in the same order
pdf_url_list =[
    "http://discovery.ucl.ac.uk/1379646/2/PhD%20thesis%20-%20CAK%20Lange%20-%2012_2012.pdf",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1760723/pdf/147-0706429a.pdf",
    "http://eknygos.lsmuni.lt/springer/520/3-30.pdf",
    "https://repub.eur.nl/pub/23546/011024_Peters,%20Jeroen%20Wilhelmus%20Bernardus.pdf",
    "https://core.ac.uk/download/pdf/338126.pdf",
    "http://www.pgedf.ufpr.br/Referencias08/Faude%20SportsMed%202009%20SG%20Fisiologia.pdf",
    "http://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC4656104&blobtype=pdf",
    "http://www.luzimarteixeira.com.br/wp-content/uploads/2011/04/exercise-and-syndrome-x.pdf",
    "https://core.ac.uk/download/pdf/9633694.pdf",
    "http://www.ingentaconnect.com/content/wef/wer/1999/00000071/00000005/art00016?crawler=true",
]
def create_clusters():
    gurl = global_url.objects.get(id=1)
    open_ref_list = {}
    with open(os.path.join(file_path,'ref.log'),encoding="utf8") as f:
        for line in f:
            re.findall(r'alpha(.*?)bravo', line)
            if 'SOURCE' in line:
                regex= r'SOURCE (.*?):'
            else:
                regex = r'REF (.*?):'
            try:
                id_match = re.findall(regex, line)[0]
                title = line[line.index(":")+1:]
            except:
                continue

            # normalize title and transform 8 byte hex number to int
            normal_title = normalize_title(title)
            normal_id  = int(id_match, 16)
            # insert into cluster
            #cluster.objects.get_or_create(id= normal_id,defaults={"name":normal_title})
            # create local urls for matching titles

            if id_match in match_list:
                index = match_list.index(id_match)
                lurl, tmp =local_url.objects.get_or_create(id=normal_id,global_url=gurl, url=id_match)
                # creat open reference
                opref,tmp =OpenReferences.objects.get_or_create(id=normal_id,ingester_key=lurl,source_table=666,source_key=id_match)
                open_ref_list[id_match] = opref

    # creates single references directly from pdf:
    logger = logging.getLogger("PDFDownloader")
    logger.setLevel(logging.INFO)
    # create the logging file handler
    log_file = os.path.join(file_path, "pdf_downloader.log")
    fh = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # add handler to logger object
    logger.addHandler(fh)
    # run actual task
    tmp = get_config("FOLDERS")["tmp"]
    grobid = get_config("WEAVER")["grobid"]
    limit = 20
    if limit is None:
        limit = int(get_config("WEAVER")["pdf_limit"])
    obj = PdfDownloader(tmp, grobid, logger=logger, limit=limit)
    for element in match_list:
        pdf_path = os.path.join("C:\\Users\\anhtu\\Google Drive\\Informatik 2016\\Related Work\\evaluation",
                                "{}.pdf".format(element))
        obj.parse_references(pdf_path, open_ref_list[element])
