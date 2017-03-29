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
