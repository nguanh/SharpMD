import logging

from mysqlWrapper.mariadb import MariaDb
from .Iingester import Iingester
from .constants import *
from .difference_storage import *
from .exception import IIngester_Exception
from .helper import *
from .queries import *


def match_author(authors, connector):
    results = []
    # iterate through all authors
    for author_index, author_dict in enumerate(authors):
        name_block = get_name_block(author_dict["parsed_name"])
        # find matching existing author with name block
        author_block_match = connector.fetch_one((name_block,), COUNT_AUTHORS)

        # case 0 matching name blocks: create new  publication author
        if author_block_match == 0:
            results.append({
                "status": Status.SAFE,
                "match": Match.NO_MATCH,
                "id": None,
                "reason": None,
            })
        # case 1 matching name blocks: include author names as possible alias
        elif author_block_match == 1:
            # get authors id
            author_id = connector.fetch_one((name_block,), CHECK_AUTHORS)
            results.append({
                "status": Status.SAFE,
                "match": Match.SINGLE_MATCH,
                "id": author_id,
                "reason": None,
            })
        # case more than 1 matching name blocks:  match by alias
        else:
            # count possible matching name blocks by matching alias
            alias_count_match = connector.fetch_one((name_block, author_dict["original_name"]),
                                                    COUNT_MATCH_AUTHOR_BY_ALIAS)
            if alias_count_match == 1:
                author_id = connector.fetch_one((name_block, author_dict["original_name"]),
                                                MATCH_AUTHOR_BY_ALIAS)
                results.append({
                    "status": Status.SAFE,
                    "match": Match.MULTI_MATCH,
                    "id": author_id,
                    "reason": None
                })
            else:
                results.append({

                    "status": Status.LIMBO,
                    "match": Match.MULTI_MATCH,
                    "id": None,
                    "reason": Reason.AMB_ALIAS
                })
    return results


def match_title(title, connector):
    # iterate through all authors
    cluster_name = normalize_title(title)
    # check for matching cluster (so far ONLY COMPLETE MATCH) TODO levenshtein distance
    connector.cursor.execute(CHECK_CLUSTER, (cluster_name,))
    cluster_matches = []
    for match in connector.cursor:
        cluster_matches.append(match[0])

    if len(cluster_matches) == 0:
        result={
            "status": Status.SAFE,
            "match": Match.NO_MATCH,
            "id": None,
            "reason": None,
        }
    elif len(cluster_matches) == 1:
        idx = connector.fetch_one((cluster_name,),CHECK_CLUSTER)
        count_pub = connector.fetch_one((idx,),COUNT_PUBLICATION)
        if count_pub == 1:
            result = {
                "status": Status.SAFE,
                "match": Match.SINGLE_MATCH,
                "id": idx,
                "reason": None,
            }
        else:
            result = {
                "status": Status.LIMBO,
                "match": Match.MULTI_MATCH,
                "id": None,
                "reason": Reason.AMB_PUB
            }

    else:
        result ={
            "status": Status.LIMBO,
            "match": Match.MULTI_MATCH,
            "id": None,
            "reason": Reason.AMB_CLUSTER
        }
    return result


#TODO
def match_keywords():
    return None


def match_type(type, connector):
    type_id = connector.fetch_one((type,), CHECK_TYPE)
    if type_id is None:
        # if type is not available, set type is miscellaneous,
        return connector.fetch_one(('misc',), CHECK_TYPE)
    return type_id


def match_pub_source(mapping,local_url,connector):
    if mapping["key"] is None:
        return None
    normalized_key = normalize_title(mapping["key"])
    mapping["block_name"] = normalized_key
    mapping["main_name"] = mapping["key"]
    del mapping["key"]

    count_match = connector.fetch_one((normalized_key,), COUNT_PUB_SOURCE)
    if count_match == 0:
        pub_source_id = connector.execute_ex(INSERT_PUB_SOURCE, mapping)

    elif count_match == 1:
        pub_source_id = connector.fetch_one((normalized_key,), CHECK_PS)
    else:
        # count possible matching name blocks by matching alias
        alias_count_match = connector.fetch_one((mapping["block_name"], mapping["main_name"] ),
                                                COUNT_MATCH_PS_BY_ALIAS)
        if alias_count_match == 1:
            pub_source_id = connector.fetch_one((normalized_key, mapping["main_name"] ),
                                                MATCH_PS_BY_ALIAS)
        else:
            # create pub source
            pub_source_id = connector.execute_ex(INSERT_PUB_SOURCE, mapping)
    # create alias
    # create alias source
    connector.execute_ex(INSERT_PS_ALIAS, (pub_source_id, mapping["main_name"]))
    connector.execute_ex(SELECT_PS_ALIAS, (pub_source_id, mapping["main_name"]))
    connector.execute_ex(INSERT_PS_ALIAS_SOURCE, (local_url,))

    return pub_source_id


def push_limbo(mapping, author_matching, title_reason, connector):
    pub_dict = {
        "title_reason": title_reason,
        "local_url": mapping["local_url"],
        "title": mapping["publication"]["title"],
        "pages": mapping["publication"]["pages"],
        "note": mapping["publication"]["note"],
        "doi": mapping["publication"]["doi"],
        "abstract": mapping["publication"]["abstract"],
        "copyright": mapping["publication"]["copyright"],
        "date_added": mapping["publication"]["date_added"],
        "date_published": mapping["publication"]["date_published"],
        "volume": mapping["publication"]["volume"],
        "number": mapping["publication"]["number"],
        "series": mapping["pub_release"]["series"],
        "edition": mapping["pub_release"]["edition"],
        "location": mapping["pub_release"]["location"],
        "publisher": mapping["pub_release"]["publisher"],
        "institution": mapping["pub_release"]["institution"],
        "school": mapping["pub_release"]["school"],
        "address": mapping["pub_release"]["address"],
        "isbn": mapping["pub_release"]["isbn"],
        "howpublished": mapping["pub_release"]["howpublished"],
        "book_title": mapping["pub_release"]["book_title"],
        "journal": mapping["pub_release"]["journal"],
    }
    pub_id = connector.execute_ex(INSERT_LIMBO_PUB, pub_dict)
    for index, author in enumerate(mapping["authors"]):
        connector.execute_ex(INSERT_LIMBO_AUTHORS, (str(author_matching[index]["reason"]),
                                                    pub_id, author["original_name"], index))


def create_authors(matching_list, author_list, local_url,connector):
    result = []
    priority = 0
    for match, author in zip(matching_list,author_list):
        name_block = get_name_block(author["parsed_name"])
        # create author record first depending on matching status
        if match["match"] == Match.NO_MATCH:
            # NOMATCH: create new  publication author
            author["block_name"] = name_block
            author_id = connector.execute_ex(INSERT_AUTHORS, author)
        else:
            # SINGLE MATCH:
            # MULTIMATCH:  author id is already included
            author_id = match["id"]

        # add ALIASES and alias SOURCES
        # add original name as alias
        connector.execute_ex(INSERT_ALIAS, (author_id, author["original_name"]))
        connector.execute_ex(SELECT_ALIAS, (author_id, author["original_name"]))
        connector.execute_ex(INSERT_ALIAS_SOURCE, (local_url,))
        # add parsed name as alias, if it's = original name, skip
        connector.execute_ex(INSERT_ALIAS, (author_id, author["parsed_name"]))
        connector.execute_ex(SELECT_ALIAS, (author_id, author["parsed_name"]))
        connector.execute_ex(INSERT_ALIAS_SOURCE, (local_url,))
        # add to publication authors
        connector.execute_ex(INSERT_PUBLICATION_AUTHORS, (local_url, author_id, priority))
        # store author id for each author
        result.append(author_id)
        priority += 1
    return result


def create_title(matching, cluster_name, connector):
    if matching["match"] == Match.NO_MATCH:
        cluster_id = connector.execute_ex(INSERT_CLUSTER, (cluster_name,))
    else:
        cluster_id = matching["id"]
    return cluster_id


def create_publication(connector, cluster_id, author_ids, type_id=None, pub_source_id=None):
    # find publication associated with cluster_id
    publication_data = connector.fetch_one((cluster_id,),CHECK_PUBLICATION,ret_tup=True)
    # publication_data is tuple with (id,url_id)
    if publication_data is None:
        # create local url and default publication
        url_id = connector.execute_ex(INSERT_LOCAL_URL, ("TODO PLATZHALTER", 1,type_id,pub_source_id))
        pub_id = connector.execute_ex(INSERT_DEFAULT_PUBLICATION, (url_id, cluster_id))
    else:
        url_id = publication_data[1]
        pub_id = publication_data[0]

    # add authors to default pub
    for priority, idx in enumerate(author_ids):
        connector.execute_ex(INSERT_PUBLICATION_AUTHORS, (url_id, idx, priority))
    # get return publication_id
    return [pub_id,url_id]


def update_diff_tree(pub_id, pub_dict, author_ids, connector):
    diff_tree = connector.fetch_one((pub_id,), CHECK_DIFF_TREE)
    if diff_tree is None:
        # create diff tree
        diff_tree = generate_diff_store(pub_dict)
    else:
        # de serialize first
        diff_tree = deserialize_diff_store(diff_tree)
        insert_diff_store(pub_dict, diff_tree)
    # insert each author
    for author in author_ids:
        # create pub_dict for insertion
        author_dict = {
            "url_id": pub_dict["url_id"],
            "author_ids": author
        }
        insert_diff_store(author_dict, diff_tree)

    return diff_tree


def ingest_data2(ingester_obj, database=DATABASE_NAME):
    if isinstance(ingester_obj, Iingester) is False:
        raise IIngester_Exception("Object is not of type IIngester")

    pub_added = 0
    pub_limbo = 0
    pub_duplicate = 0
    logger = logging.getLogger(ingester_obj.get_name())
    # establish mariadb connections, one for reading from harvester, one for writing in ingester
    read_connector = MariaDb()
    write_connector = MariaDb(db=database)
    try:
        read_connector.cursor.execute(ingester_obj.get_query())
    except Exception as e:
        raise IIngester_Exception(e)

    for query_dataset in read_connector.cursor:
        mapping = ingester_obj.mapping_function(query_dataset)
        try:
            # 1. get Harvester specific record and parse to common-form dict
            # ------------------------- LOCAL_URL ----------------------------------------------------------------------
            # check for duplicates by looking up the local URL
            duplicate_id = write_connector.fetch_one((mapping["local_url"],
                                                     ingester_obj.get_global_url()),
                                                     CHECK_LOCAL_URL)
            if duplicate_id is not None:
                logger.info("%s: skip duplicate", mapping["local_url"])
                pub_duplicate += 1
                continue
            # 2. create local url entry for record
            type_id = match_type(mapping["publication"]["type_ids"], write_connector)
            local_url_id = write_connector.execute_ex(INSERT_LOCAL_URL, (mapping["local_url"],
                                                                         ingester_obj.get_global_url(),
                                                                         type_id,
                                                                         None))

            # ------------------------- MATCHINGS ----------------------------------------------------------------------
            # 3. find matching cluster for title and matching existing authors
            title_match = match_title(mapping["publication"]["title"], write_connector)
            author_matches = match_author(mapping["authors"], write_connector)

            author_valid = True
            for author in author_matches:
                if author["status"] == Status.LIMBO:
                    author_valid = False
                    break

            # 4. ambiguous matching, push into limbo and delete local url record
            if title_match["status"] == Status.LIMBO or author_valid is False:
                logger.info("%s: Ambiguous title/authors", mapping["local_url"])
                write_connector.execute_ex(DELETE_LOCAL_URL, (local_url_id,))
                push_limbo(mapping, author_matches, str(title_match["reason"]), write_connector)
                pub_limbo += 1
                continue

            # ------------------------ CREATION ------------------------------------------------------------------------
            pub_source_id = match_pub_source(mapping["pub_release"],local_url_id, write_connector)
            cluster_name = normalize_title(mapping["publication"]["title"])
            author_ids = create_authors(author_matches, mapping["authors"], local_url_id, write_connector)
            cluster_id = create_title(title_match, cluster_name, write_connector)
            # 5.create default publication / or find existing one and link with authors and cluster
            def_pub_id, def_url_id = create_publication(write_connector,cluster_id, author_ids, type_id,pub_source_id)
            # update local url with pub_source_id and study field
            write_connector.execute_ex(UPDATE_LOCAL_URL, (pub_source_id,None, local_url_id))
            # 6.get /create diff tree
            mapping['publication']['url_id'] = def_url_id
            mapping['publication']['pub_source_ids'] = pub_source_id
            mapping['publication']['type_ids'] = type_id
            diff_tree = update_diff_tree(def_pub_id, mapping['publication'], author_ids, write_connector)
            # 7.get default values from diff tree and re-serialize tree
            publication_values = get_default_values(diff_tree)
            serialized_tree = serialize_diff_store(diff_tree)
            # set missing values that are not default
            publication_values["differences"] = serialized_tree
            publication_values["cluster_id"] = cluster_id
            publication_values["url_id"] = def_url_id
            publication_values["date_added"] = None
            publication_values["id"] = def_pub_id
            # 8.store publication
            write_connector.execute_ex(UPDATE_PUBLICATION, publication_values)
            logger.debug("%s: Publication added %s", mapping["local_url"], def_pub_id)
            # 9.set publication as harvested
            write_connector.execute_ex(ingester_obj.update_harvested(), (mapping["local_url"],))
            pub_added += 1
        except Exception as e:
            logger.error("%s: %s", mapping["local_url"], e)
            continue
    logger.debug("Terminate ingester %s", ingester_obj.get_name())
    logger.info("publications added %s / limbo %s / skipped %s", pub_added,pub_limbo,pub_duplicate)
    write_connector.close_connection()
    read_connector.close_connection()
    return pub_added
