from .models import *
from .helper import *
from .difference_storage import *
from django.db.models import ObjectDoesNotExist
from django.db import transaction
from silk.profiling.profiler import silk_profile

@silk_profile(name='create author')
def create_authors(matching_list, author_list, local_url_obj):
    """
    uses transactions! Potentially less stable due to bugs
    :param matching_list:
    :param author_list:
    :param local_url_obj:
    :return:
    """
    result = []
    priority = 0
    creation_list = []
    creation_name_list = []
    selection_list = []
    selection_name_list = []
    authors_pub_list =[]
    # split authors into already existing authors and new authors

    try:
        # create all authors_model instances in a single transaction
        with transaction.atomic():
            for match, author in zip(matching_list, author_list):
                # create author record first depending on matching status
                if match["match"] == Match.NO_MATCH:
                    # NOMATCH: create new  publication author
                    author_obj = authors_model.objects.create(main_name=author["parsed_name"])
                    creation_list.append(author_obj)
                    creation_name_list.append([author["original_name"],author["parsed_name"], priority])
                    authors_pub_list.append(publication_author(url=local_url_obj, author=author_obj, priority=priority))
                else:
                    # else add id
                    selection_name_list.append([author["original_name"], author["parsed_name"], priority])
                    selection_list.append(match["id"])
                priority += 1
    except Exception:
        print("Error HH")

    # combine lists
    merged_objs = creation_list + selection_list
    merged_names = creation_name_list + selection_name_list
    try:
        # create aliases in a single transaction
        source_list = []
        with transaction.atomic():
            for author_obj, name_data in zip(merged_objs, merged_names):
                # add ALIASES
                result.append(author_obj)
                orig = author_aliases.objects.get_or_create(alias=name_data[0], author=author_obj)[0]
                source_list.append(author_alias_source(alias=orig, url=local_url_obj))
                if name_data[0] != name_data[1]:
                    parsed = author_aliases.objects.get_or_create(alias=name_data[1], author=author_obj)[0]
                    source_list.append(author_alias_source(alias=parsed, url=local_url_obj))
    except Exception:
        print("Error JJ")

    # add alias sources
    author_alias_source.objects.bulk_create(source_list)
    # add bulk publication authors
    publication_author.objects.bulk_create(authors_pub_list)

    for author_obj, name_data in zip(selection_list, selection_name_list):
        publication_author.objects.get_or_create(url=local_url_obj, author=author_obj, defaults={'priority': name_data[2]})
    return result



@silk_profile(name='create title2')
def create_title(matching, cluster_name):
    if matching["match"] == Match.NO_MATCH:
        cluster_obj = cluster.objects.create(name=cluster_name)
    else:
        cluster_obj = matching["id"]
    return cluster_obj


@silk_profile(name='create publication2')
def create_publication(g_url, cluster_obj, author_objs, type_obj=None, pub_medium_obj=None, keyword_objs=[]):
    pub_aut_list = []
    keyword_list = []
    # find publication associated with cluster_id
    try:
        publication_data = publication.objects.get(cluster=cluster_obj)
        url_id = publication_data.local_url
        for priority, author_obj in enumerate(author_objs):
            publication_author.objects.get_or_create(url=url_id, author=author_obj, defaults={'priority': priority})
        for keyword in keyword_objs:
            publication_keyword.objects.get_or_create(url=url_id, keyword=keyword)

    except ObjectDoesNotExist:
        # create local url and default publication
        publication_data = publication.objects.create(cluster=cluster_obj)
        url_id = local_url.objects.create(url="TODO PLATZHALTER", global_url=g_url,
                                          medium=pub_medium_obj, type=type_obj, publication=publication_data)
        for priority, author_obj in enumerate(author_objs):
            pub_aut_list.append(publication_author(url=url_id, author=author_obj, priority=priority))
        for keyword in keyword_objs:
            keyword_list.append(publication_keyword(url=url_id, keyword=keyword))
        publication_author.objects.bulk_create(pub_aut_list)
        publication_keyword.objects.bulk_create(keyword_list)
    # get return publication_id as tuple with (id,url_id)
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
