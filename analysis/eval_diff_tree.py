from ingester.models import *
from ingester.difference_storage import *
from ingester.tests.ingester_tools import get_pub_dict
from ingester.helper import *
from time import time
import os
import logging
from pympler import asizeof

idx = 666999666
id_counter = 0
local_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(local_path,'data')


#TODO vote
def get_template(number):
    global id_counter
    id_counter += 1
    return {
        "url_id": id_counter,
        "title":"evaluation title {}".format(number),
        "pages": "{}--{}".format(number,number+1),
        "note": "This is note number {}".format(number),
        "doi": "http://google.de/{}".format(number),
        "abstract": "Lorem ipsum dolor kolaris {}".format(number),
        "copyright": "copyright {}".format(number),
        "date_published": "Not a valid date{}".format(number),
        "volume": "{}".format(number),
        "number": "{}".format(number),
    }


def get_input_list(range_func):
    result = []
    for element in range_func:
        result.append(get_template(element))
    return result




def setup():
    gurl = global_url.objects.get(id=1)

    clus, tmp = cluster.objects.get_or_create(id=idx, name="Any title")
    publ, tmp = publication.objects.get_or_create(id=idx, cluster=clus)
    diff_tree = generate_diff_store(get_pub_dict(url_id=idx))
    lurl = local_url.objects.get_or_create(id=idx, global_url=gurl, publication= publ,defaults={
        "url": "dummy"
    })
    seri = serialize_diff_store(diff_tree) # generate empty diff tree
    publ.differences = seri
    publ.save()
    print("Diff tree created")


def insert_value(pub_dict_list):
    """
    Insert and update diff tree
    :param pub_dict_list:
    :return:
    """
    pub= publication.objects.get(id=idx)
    diff_tree = deserialize_diff_store(pub.differences)
    for element in pub_dict_list:
        insert_diff_store(element,diff_tree)
    serial = serialize_diff_store(diff_tree)
    pub.differences = serial
    pub.save()
    return asizeof.asizeof(serial)


def source_view():
    pub = publication.objects.get(id=idx)
    diff_tree = deserialize_diff_store(pub.differences)
    return get_sources(diff_tree)



def benchmark(a,b,c):

    logger = logging.getLogger("eval_diff_tree")
    logger.setLevel(logging.INFO)
    # create the logging file handler
    fh = logging.FileHandler(os.path.join(file_path,"eval_diff_tree.log"))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # add handler to logger object
    logger.addHandler(fh)
    setup()
    for counter in range(1,4):
        first =(counter-1)*10+1
        last = counter*10+1
        it_insert = get_input_list(range(first,last))
        it_update = get_input_list(range(1, 11))
        logger.info("Iteration Number %s",counter)
        start = time()
        insert_size = insert_value(it_insert)
        end = time() - start
        logger.info("Insertion size: %s", insert_size)
        logger.info("Insertion step: %s", end)
        start = time()
        update_size = insert_value(it_update)
        end = time() - start
        logger.info("Update size: %s", update_size)
        logger.info("Update step: %s", end)
        start = time()
        source_view()
        end = time() - start
        logger.info("Source view step: %s", end)