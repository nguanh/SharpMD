import msgpack
import datetime
from .models import *
URL_LIST_MAX = 62


def generate_node(value, index =0):
    """
    generate node from value
    set votes 0
    set bitvector by offset index
    parse dates
    :param value: any value to be stored
    :param index: index of url_id for bitvector
    :return: dict
    """
    if value is None:
        return None
    elif isinstance(value,datetime.datetime):
        value = value.strftime("%Y-%m-%d %H:%M:%S")
    return {
        "value": value,
        "votes": 0,
        "bitvector": 1 << index,
    }


def append_node(value,index, store):
    has_changed = False
    for i in range(len(store)):
        if store[i]["value"] == value:
            has_changed = True
            # value already exists in tree --> set bitvector
            store[i]["bitvector"] |= 1 << index
    if has_changed is False:
        store.append(generate_node(value, index))


excluded_keys =["url_id","author_ids","keyword_ids","type_ids","pub_source_ids","study_field_ids"]
def get_default_values(store):
    """
    get default values from diff tree by returning the values of the first node in every list
    :param store: diff tree
    :return: pub_dict without url_id
    """
    result = {}
    for key,value in store.items():
        # skip url_id since its only relevant for bitvectors
        if key in excluded_keys:
            continue
        if len(value) > 0:
            # try parse to datetime, if possible
            try:
                result[key] = datetime.datetime.strptime(value[0]["value"],"%Y-%m-%d %H:%M:%S")
            except:
                result[key] = value[0]["value"]
        else:
            result[key] = None
    return result


def get_default_ids(store, url_obj):
    # get popular IDs
    if len(store["type_ids"]) > 0:
        type_id = store["type_ids"][0]["value"]
    else:
        type_id = None
    if len(store["pub_source_ids"]) > 0:
        pub_source_id = store["pub_source_ids"][0]["value"]
    else:
        pub_source_id = None

    # set type, study field and pub medium id for urls
    types = None if url_obj.type is None else url_obj.type.id
    medium = None if url_obj.medium is None else url_obj.medium.id

    if types != type_id and type_id is not None:
        url_obj.type = publication_type.objects.get(id=type_id)
    if medium != pub_source_id and pub_source_id is not None:
        url_obj.medium = pub_medium.objects.get(id=pub_source_id)
    url_obj.save()



def vote(store,attribute,value,vote_count = 1):
    pass


def un_vote(store,attribute,value,vote_count = 1):
    pass


def generate_diff_store(pub_dict):
    """
    create diff tree
    for every field in pub_dict create an array containing nodes
    first element of array is always default/best value
    exception for url_id this is just an array containing all url_id
    :param pub_dict: publication_dict
    :return: diff tree
    """
    obj = {
        "url_id": [],  # url list for bitvector
        "title": [],
        "pages": [],  # pages from-to are always stored together
        "note": [],
        "doi": [],
        "abstract": [],
        "copyright": [],
        "date_published": [],
        "volume": [],
        "number": [],
        "keyword_ids": [],
        "author_ids": [],
        "pub_source_ids": [],
        "type_ids": [],
        "study_field_ids": [],
    }
    for key in obj.keys():
            if key == "url_id":
                obj["url_id"].append((pub_dict["url_id"]))
            else:
                node = generate_node(pub_dict[key])
                if node is not None:
                    obj[key].append(node)

    return obj
    # TODO testfall wenn pub_dict bestimmte schlüssel einfach noch nicht enthält


def insert_diff_store(pub_dict, diff_store):
    """
    include publication_dict to an existing difff_tree
    :param pub_dict:
    :param diff_store: already existing diff tree
    :return: diff_tree
    """
    # get bitvector index first
    try:
        idx = diff_store["url_id"].index(pub_dict["url_id"])
    except ValueError:
        diff_store["url_id"].append(pub_dict["url_id"])
        # TODO check if limit is reached
        idx = len(diff_store["url_id"]) - 1

    for key in pub_dict.keys():
        if key == "url_id":
            continue
        else:
            # insert value into tree
            # skip empty values
            if pub_dict[key] is None:
                continue
            append_node(pub_dict[key], idx ,diff_store[key])


def serialize_diff_store(store):
    """
    wrapper for serialising
    serialise diff tree using messagepack
    :param store: diff tree
    :return: serialised diff tree
    """
    return msgpack.packb(store)


def deserialize_diff_store(store):
    """
    wrapper for de-serialising

    :param store: serialised diff tree
    :return: diff tree
    """
    return msgpack.unpackb(store, encoding="utf-8")


def get_url_indexes(bitvector):
    """
    return a list of indexes from the given bitvector
    :param bitvector: int
    :return: list of int
    """
    return_list = []
    index = 1
    counter = 0
    while index <= bitvector:
        if index & bitvector:
            return_list.append(counter)
        counter += 1
        index <<= 1
    return return_list


id_list = ["keyword_ids", "author_ids", "pub_source_ids", "type_ids", "study_field_ids"]


def get_sources(store):
    """
    generate a list of values containing the original sources and their values from a
    diff tree
    :param store: deserialized diff tree
    :return: list of dicts
    """
    url_list = store["url_id"]
    obj_list = []
    sources = []

    # generate list of dicts first containing only the source url
    for element in url_list:
        # get local url object
        url_obj = local_url.objects.select_related('global_url').get(id=element)
        source_dict = dict()
        source_dict["source"] = {
            "url":"{}{}".format(url_obj.global_url.url,url_obj.url),
            "domain": url_obj.global_url.domain
        }
        sources.append(source_dict)
        obj_list.append(url_obj)

    # split values and votes up by source
    for key, value in store.items():
        if key == "url_id":
            continue
        else:
            # iterate through values per key
            for entry in value:
                node_value = entry["value"]
                nodes_vote = entry["votes"]
                index_list = get_url_indexes(entry["bitvector"])
                for index in index_list:
                    sources[index][key] = {
                        'votes': nodes_vote,
                        'value': node_value
                    }
    #TODO  resolve ids

    return sources
