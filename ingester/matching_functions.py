from django.db.models import ObjectDoesNotExist
from silk.profiling.profiler import silk_profile

from .helper import *
from .models import *
from Levenshtein import distance

@silk_profile(name='match author')
def match_author(authors):
    results = []
    # iterate through all authors
    for author_index, author_dict in enumerate(authors):
        name_block = normalize_authors(author_dict["parsed_name"])
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


@silk_profile(name='match author2')
def match_author2(authors):
    results = []
    # iterate through all authors
    for author_index, author_dict in enumerate(authors):
        # Strategy 1: try to find all matching aliases and get author_model as well
        alias_match = author_aliases.objects.select_related('author').filter(alias=author_dict["original_name"]).all()
        alias_match_count = len(alias_match)
        if alias_match_count == 1:
            # one match, get author from matching alias
            results.append({
                "status": Status.SAFE,
                "match": Match.SINGLE_MATCH,
                "id": alias_match[0].author,
                "reason": None,
            })
        elif alias_match_count > 1:
            # multiple exact matches: ambiguous
            results.append({
                "status": Status.LIMBO,
                "match": Match.MULTI_MATCH,
                "id": None,
                "reason": Reason.AMB_ALIAS
            })
        else:
            # no match--> Strategy 2: match with similar authors
            name_block = normalize_authors(author_dict["parsed_name"])
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
    return results


@silk_profile(name='match title')
def match_title(title):
    cluster_name = normalize_title(title)
    # check for matching cluster (so far ONLY COMPLETE MATCH)
    cluster_matches = [element for element in cluster.objects.filter(name=cluster_name).all()]
    cluster_count = len(cluster_matches)

    if cluster_count == 0:
        result={
            "status": Status.SAFE,
            "match": Match.NO_MATCH,
            "id": None,
            "reason": None,
        }
    elif cluster_count == 1:
        cluster_id = cluster_matches[0]
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


def search_title(title, threshold = 0.5):
    """
    search for a given title in the db.
    Use levenshtein algorithm on results and calculate similarity percentage.
    :param title:  title to be searched
    :param threshold: results with similarity percentage above threshold are returned
    :return: list of matching cluster model objects
    """
    threshold *= 100
    normal_title = normalize_title(title)
    search_query = get_search_query(normal_title)
    results = [element for element in cluster.objects.search(search_query)]
    similarity = [int((1-distance(normal_title,tit.name)/max(len(normal_title),len(tit.name)))*100) for tit in results]
    ret_val = [val if sim >= threshold else None for sim, val in zip(similarity,results)]
    return ret_val

def search_author(author_name):
    normal_name = normalize_authors(author_name)
    search_query = get_author_search_query(author_name)
    results = [element for element in authors_model.objects.search(search_query)]


@silk_profile(name='match title2')
def match_title2(title):
    cluster_matches = search_title(title)
    cluster_count = len(cluster_matches)

    if cluster_count == 0:
        result={
            "status": Status.SAFE,
            "match": Match.NO_MATCH,
            "id": None,
            "reason": None,
        }
    elif cluster_count == 1:
        cluster_obj = cluster_matches[0]
        count_pub = publication.objects.filter(cluster=cluster_obj).count()
        if count_pub == 1:
            result = {
                "status": Status.SAFE,
                "match": Match.SINGLE_MATCH,
                "id": cluster_obj,
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

@silk_profile(name='match medium')
def match_pub_medium(mapping, url_obj):
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
    pub_alias_source.objects.get_or_create(alias=alias, url=url_obj)
    return pub_source_id


def match_type(pub_type):
    try:
        type_obj = publication_type.objects.get(name=pub_type)
    except ObjectDoesNotExist:
        type_obj = publication_type.objects.get(name='misc')
    return type_obj


def match_keywords(keywords, url_obj):
    key_id_list = []
    if keywords is None:
        return key_id_list
    for key in keywords:
        normalized_keyword = normalize_title(key)
        key_match = keywordsModel.objects.filter(block_name=normalized_keyword)
        key_match_count = key_match.count()

        if key_match_count == 0:
            key_record = keywordsModel.objects.create(main_name=key)
        elif key_match_count == 1:
            key_record = keywordsModel.objects.get(block_name=normalized_keyword)
        else:
            # find matching alias
            alias_match = keyword_aliases.objects.filter(alias=key, keyword__block_name=normalized_keyword)
            alias_match_count = alias_match.count()
            if alias_match_count == 1:
                key_record = alias_match.first().keyword
            else:
                key_record = keywordsModel.objects.create(main_name=key)
        #create alias and source
        alias, create = keyword_aliases.objects.get_or_create(alias=key, keyword=key_record)
        keyword_alias_source.objects.create(alias=alias, url=url_obj)
        # add publication keyword
        publication_keyword.objects.get_or_create(url=url_obj, keyword=key_record)
        key_id_list.append(key_record)

    return key_id_list






