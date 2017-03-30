from .helper import *
from .models import *


def match_author(authors):
    results = []
    # iterate through all authors
    for author_index, author_dict in enumerate(authors):
        name_block = get_name_block(author_dict["parsed_name"])
        # find matching existing author with name block
        author_block_match = authors_model.objects.filter(block_name=name_block)
        author_match_count = author_block_match.count()
        # case 0 matching name blocks: create new  publication author
        if author_match_count == 0:
            results.append({
                "status": Status.SAFE,
                "match": Match.NO_MATCH,
                "id": None,
                "reason": None,
            })
        # case 1 matching name blocks: include author names as possible alias
        elif author_match_count == 1:
            # get authors id
            author_id = author_block_match.first().id
            results.append({
                "status": Status.SAFE,
                "match": Match.SINGLE_MATCH,
                "id": author_id,
                "reason": None,
            })
        # case more than 1 matching name blocks:  match by alias
        else:
            # count possible matching name blocks by matching alias
            alias_count_match = author_aliases.objects.filter(alias=author_dict["original_name"],
                                                              author__block_name= name_block)
            if alias_count_match.count() == 1:
                author_id = alias_count_match.first().author.id
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


def match_title(title):
    cluster_name = normalize_title(title)
    # check for matching cluster (so far ONLY COMPLETE MATCH) TODO levenshtein distance
    cluster_matches = cluster.objects.filter(name=cluster_name)
    cluster_count = cluster_matches.count()

    if cluster_count == 0:
        result={
            "status": Status.SAFE,
            "match": Match.NO_MATCH,
            "id": None,
            "reason": None,
        }
    elif cluster_count == 1:
        cluster_id = cluster_matches.first()
        count_pub = publication.objects.filter(cluster=cluster_id).count()
        if count_pub == 1:
            result = {
                "status": Status.SAFE,
                "match": Match.SINGLE_MATCH,
                "id": cluster_id.id,
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
        result = {
            "status": Status.LIMBO,
            "match": Match.MULTI_MATCH,
            "id": None,
            "reason": Reason.AMB_CLUSTER
        }
    return result


def match_pub_medium(mapping, url):
    if mapping["key"] is None:
        return None
    normalized_key = normalize_title(mapping["key"])
    mapping["block_name"] = normalized_key
    mapping["main_name"] = mapping["key"]
    del mapping["key"]
    medium_match = pub_medium.objects.filter(block_name=normalized_key)
    count_match = medium_match.count()
    if count_match == 0:
        pub_source_id = pub_medium.objects.create(**mapping)
    elif count_match == 1:
        pub_source_id = pub_medium.objects.get(block_name=normalized_key)
    else:
        # count possible matching name blocks by matching alias
        alias_match=pub_medium_alias.objects.filter(alias=mapping["main_name"],
                                                    medium__block_name=mapping["block_name"])
        alias_count_match = alias_match.count()
        if alias_count_match == 1:
            pub_source_id = alias_match.first().medium
        else:
            # create pub source
            pub_source_id = pub_medium.objects.create(**mapping)
    # create alias and alias source
    alias, created = pub_medium_alias.objects.get_or_create(alias=mapping["main_name"], medium=pub_source_id)
    pub_alias_source.objects.get_or_create(alias=alias, url=url)
    return pub_source_id


#TODO
"""
def match_type(type):
    type_id = connector.fetch_one((type,), CHECK_TYPE)
    if type_id is None:
        # if type is not available, set type is miscellaneous,
        return connector.fetch_one(('misc',), CHECK_TYPE)
    return type_id
"""

