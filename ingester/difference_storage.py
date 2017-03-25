import msgpack
import datetime
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
        "date_added":[],
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