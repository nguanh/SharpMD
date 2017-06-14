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
        "published": "Not a valid date{}".format(number),
        "volume": "{}".format(number),
        "number": "{}".format(number),
    }


def get_input_list(range_func):
    result = []
    for element in range_func:
        result.append(get_template(element))
    return result




def update_value(base):
    global id_counter
    for key,value in base.items():
        id_counter += 1
        aliases=MultiAlias.objects.select_related('proxy').filter(alias=value).all()
        if len(aliases) == 0:
            # alias does not exist
            proxy, tmp = MultiProxy.objects.get_or_create(common=idx, attribute=key)
            alias = MultiAlias.objects.create(alias=value,proxy= proxy)
            MultiSource.objects.create(source=id_counter, alias=alias)
        else:
            # alias does exist
            MultiSource.objects.create(source=id_counter, alias=aliases[0])

def insert_value(pub_dict_list):
    """
    Insert and update diff tree
    :param pub_dict_list:
    :return:
    """
    for element in pub_dict_list:
        update_value(element)



def vote_value(base):
    for key, value in base.items():
        alias = MultiAlias.objects.get(alias=value)
        alias.vote += 1
        alias.save()

def upvote_value(pub_dict_list):
    """
    Insert and update diff tree
    :param pub_dict_list:
    :return:
    """
    for element in pub_dict_list:
        vote_value(element)


def source_view():
    attributes = MultiProxy.objects.filter(common=idx).all()
    alias_list= []
    source_list =[]

    for attr in attributes:
        aliases = MultiAlias.objects.filter(proxy=attr).all()
        alias_list.append(alias_list)
        for alias in aliases:
            sources = MultiSource.objects.filter(alias=alias).all()
            source_list.append(sources)

    return [attributes, alias_list,source_list]





def benchmark_other(a,b,c):

    logger = logging.getLogger("eval_diff_tree2")
    logger.setLevel(logging.INFO)
    # create the logging file handler
    fh = logging.FileHandler(os.path.join(file_path,"eval_diff_tree2.log"))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # add handler to logger object
    logger.addHandler(fh)
    for counter in range(1,4):
        first =(counter-1)*10+1
        last = counter*10+1
        it_insert = get_input_list(range(first,last))
        it_update = get_input_list(range(1, 11))
        logger.info("Iteration Number %s",counter)
        start = time()
        insert_value(it_insert)
        end = time() - start

        logger.info("Insertion step: %s", end)
        start = time()
        insert_value(it_update)
        end = time() - start
        logger.info("Update step: %s", end)
        start = time()
        source_view()
        end = time() - start
        logger.info("Source view step: %s", end)
        start = time()
        #upvote inserted values
        upvote_value(it_insert)
        end = time()- start
        logger.info("Vote step: %s", end)