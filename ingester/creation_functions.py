from .models import *
from .helper import *
from django.db.models import ObjectDoesNotExist

def create_authors(matching_list, author_list, local_url):
    result = []
    priority = 0
    for match, author in zip(matching_list,author_list):
        #name_block = get_name_block(author["parsed_name"])
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
            author_id = authors_model.objects.create(**author_entry)
        else:
            # SINGLE MATCH:
            # MULTIMATCH:  author id is already included
            author_id = authors_model.objects.get(id=match["id"])

        # add ALIASES and alias SOURCES
        # add original name as alias

        orig,created = author_aliases.objects.get_or_create(alias=author["original_name"], author=author_id)
        # add parsed name as alias, if it's = original name, skip
        parsed,created = author_aliases.objects.get_or_create(alias=author["parsed_name"], author=author_id)
        author_alias_source.objects.get_or_create(alias=orig, url=local_url)
        author_alias_source.objects.get_or_create(alias=parsed, url=local_url)
        publication_author.objects.create(url=local_url, author=author_id, priority=priority)
        # store author
        result.append(author_id)
        priority += 1
    return result


def create_title(matching, cluster_name):
    if matching["match"] == Match.NO_MATCH:
        cluster_id = cluster.objects.create(name= cluster_name)
        cluster_id = cluster_id.id
    else:
        cluster_id = matching["id"]
    return cluster_id

#TODO handle none for type and pubmediu
def create_publication(cluster_id, author_ids, type_id=None, pub_medium_id=None):
    # find publication associated with cluster_id
    try:
        publication_data = publication.objects.get(cluster=cluster_id)
        url_id = publication_data.url
    except ObjectDoesNotExist:
        # create local url and default publication
        gurl_id = global_url.objects.get(id=1)
        url_id = local_url.objects.create(url="TODO PLATZHALTER", global_url= gurl_id, medium=pub_medium_id)
        publication_data = publication.objects.create(url=url_id, cluster=cluster_id)
    # publication_data is tuple with (id,url_id)


    # add authors to default pub
    for priority, idx in enumerate(author_ids):
        author = authors_model.objects.get(id=idx)
        publication_author.objects.create(url=url_id,author=author,priority=priority)
    # get return publication_id
    return [publication_data,url_id]