from .models import *
from .helper import *
from .difference_storage import *
from django.db.models import ObjectDoesNotExist
from silk.profiling.profiler import silk_profile
@silk_profile(name='create author')
def create_authors(matching_list, author_list, local_url_obj):
    result = []
    priority = 0
    for match, author in zip(matching_list,author_list):
        # create author record first depending on matching status
        if match["match"] == Match.NO_MATCH:
            # NOMATCH: create new  publication author
            #author["block_name"] = name_block
            # pass author dict as dict parameter
            author_entry = {
                "main_name": author["parsed_name"],
                "website": author["website"],
                "contact": author["contact"],
                "about": author["about"],
                "orcid_id": author["orcid_id"]
            }
            author_obj = authors_model.objects.create(**author_entry)
        else:
            # SINGLE MATCH:
            # MULTIMATCH:  author id is already included
            author_obj = authors_model.objects.get(id=match["id"])

        # add ALIASES and alias SOURCES
        # add original name as alias

        orig,created = author_aliases.objects.get_or_create(alias=author["original_name"], author=author_obj)
        # add parsed name as alias, if it's = original name, skip
        parsed,created = author_aliases.objects.get_or_create(alias=author["parsed_name"], author=author_obj)
        author_alias_source.objects.get_or_create(alias=orig, url=local_url_obj)
        author_alias_source.objects.get_or_create(alias=parsed, url=local_url_obj)
        publication_author.objects.get_or_create(url=local_url_obj, author=author_obj, priority=priority)
        # store author
        result.append(author_obj)
        priority += 1
    return result

@silk_profile(name='create title')
def create_title(matching, cluster_name):
    if matching["match"] == Match.NO_MATCH:
        cluster_obj = cluster.objects.create(name=cluster_name)
    else:
        cluster_obj = cluster.objects.get(id=matching["id"])
    return cluster_obj

@silk_profile(name='create publication')
def create_publication(cluster_obj, author_objs, type_obj=None, pub_medium_obj=None, keyword_objs=[]):
    # find publication associated with cluster_id
    try:
        publication_data = publication.objects.get(cluster=cluster_obj)
        url_id = publication_data.url
    except ObjectDoesNotExist:
        # create local url and default publication
        gurl_id = global_url.objects.get(id=1)
        url_id = local_url.objects.create(url="TODO PLATZHALTER", global_url=gurl_id,
                                          medium=pub_medium_obj, type=type_obj)
        publication_data = publication.objects.create(url=url_id, cluster=cluster_obj)
    # publication_data is tuple with (id,url_id)


    # add authors to default pub
    for priority, author_obj in enumerate(author_objs):
        publication_author.objects.get_or_create(url=url_id, author=author_obj, priority=priority)

    # add keyword to default pub
    for keyword in keyword_objs:
        publication_keyword.objects.get_or_create(url=url_id, keyword=keyword)
    # get return publication_id
    return [publication_data, url_id]






def update_diff_tree(pub_obj, pub_dict, author_objs):
    diff_tree = pub_obj.differences
    if diff_tree is None:
        # create diff tree
        diff_tree = generate_diff_store(pub_dict)
    else:
        # de serialize first
        diff_tree = deserialize_diff_store(diff_tree)
        insert_diff_store(pub_dict, diff_tree)
    # insert each author
    for author in author_objs:
        # create pub_dict for insertion
        author_dict = {
            "url_id": pub_dict["url_id"],
            "author_ids": author.id
        }
        insert_diff_store(author_dict, diff_tree)
    return diff_tree
