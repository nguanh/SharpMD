from .helper import *
from .models import authors_model,author_aliases

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
            alias_count_match = author_aliases.objects.filter(alias=author_dict["original_name"])
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
