from .Iingester import Iingester
from .exception import *
from .models import *
import logging
from mysqlWrapper.mariadb import MariaDb
from django.db.models import ObjectDoesNotExist
from .matching_functions import match_type,match_pub_medium,simple_author_match,match_title2, match_keywords, advanced_author_match
from .limbo_functions import push_limbo
from .creation_functions import create_publication,create_authors,create_title,update_diff_tree
from .difference_storage import *
from .helper import *
import datetime
from silk.profiling.profiler import silk_profile


@silk_profile(name='Ingester')
def ingest_data(ingester_obj):
    if isinstance(ingester_obj, Iingester) is False:
        raise IIngester_Exception("Object is not of type IIngester")

    pub_added = 0
    pub_limbo = 0
    pub_duplicate = 0
    logger = logging.getLogger("ingester.{}".format(ingester_obj.get_name()))
    # mysql connector to read from harvester
    read_connector = MariaDb()
    write_connector= MariaDb()
    try:
        read_connector.cursor.execute(ingester_obj.get_query())
    except Exception as e:
        raise IIngester_Exception(e)

    globl_url_obj = global_url.objects.get(id=1)
    ingester_obj_global_url = ingester_obj.get_global_url()

    for query_dataset in read_connector.cursor:
        mapping = ingester_obj.mapping_function(query_dataset)
        write_connector.execute_ex(ingester_obj.update_harvested(), (mapping["local_url"],))
        try:
            # 1. get Harvester specific record and parse to common-form dict
            # ------------------------- LOCAL_URL ----------------------------------------------------------------------
            # check for duplicates by looking up the local URL
            try:
                local_url.objects.get(url=mapping["local_url"], global_url=ingester_obj_global_url)
                logger.info("%s: skip duplicate", mapping["local_url"])
                pub_duplicate += 1
                continue
            except ObjectDoesNotExist:
                pass

            # 2. create local url entry for record
            type_obj = match_type(mapping["publication"]["type_ids"])
            source_lurl_obj = local_url.objects.create(url=mapping["local_url"],
                                                       global_url=ingester_obj.get_global_url(),
                                                       type=type_obj)
            # ------------------------- MATCHINGS ----------------------------------------------------------------------
            # 3. find matching cluster for title and matching existing authors
            title_match = match_title2(mapping["publication"]["title"])
            author_matches = advanced_author_match(mapping["authors"])

            author_valid = True
            for author in author_matches:
                if author["status"] == Status.LIMBO:
                    author_valid = False
                    break

            # 4. ambiguous matching, push into limbo and delete local url record
            if title_match["status"] == Status.LIMBO or author_valid is False:
                logger.info("%s: Ambiguous title/authors", mapping["local_url"])
                source_lurl_obj.delete()
                push_limbo(mapping, author_matches, str(title_match["reason"]))
                pub_limbo += 1
                #TODO include in test
                write_connector.execute_ex(ingester_obj.update_harvested(), (mapping["local_url"],))
                continue

            # ------------------------ CREATION ------------------------------------------------------------------------
            pub_medium_obj = match_pub_medium(mapping["pub_release"], source_lurl_obj)
            cluster_name = normalize_title(mapping["publication"]["title"])
            author_ids = create_authors(author_matches, mapping["authors"], source_lurl_obj)
            keyword_obj = match_keywords(mapping["keywords"],source_lurl_obj)
            cluster_obj = create_title(title_match, cluster_name)
            # 5.create default publication / or find existing one and link with authors and cluster
            def_pub_obj, def_url_obj = create_publication(globl_url_obj,
                                                          cluster_obj,
                                                          author_ids,
                                                          type_obj,
                                                          pub_medium_obj,
                                                          keyword_obj)
            # update local url with pub_medium_obj and study field
            source_lurl_obj.medium = pub_medium_obj
            source_lurl_obj.save()
            # 6.get /create diff tree
            mapping['publication']['url_id'] = source_lurl_obj.id
            # handle if there is no pub_medium
            if pub_medium_obj is not None:
                mapping['publication']['pub_source_ids'] = pub_medium_obj.id
            if len(keyword_obj) > 0:
                key_id_list = []
                for keyword in keyword_obj:
                    key_id_list.append(keyword.id)
                mapping['publication']['keyword_ids'] = key_id_list or None
            mapping['publication']['type_ids'] = type_obj.id
            diff_tree = update_diff_tree(def_pub_obj, mapping['publication'], author_ids)
            # 7.get default values from diff tree and re-serialize tree
            publication_values = get_default_values(diff_tree)
            get_default_ids(diff_tree, def_url_obj)

            serialized_tree = serialize_diff_store(diff_tree)
            # set missing values that are not default
            publication_values["differences"] = serialized_tree
            publication_values["cluster"] = cluster_obj
            publication_values["url"] = def_url_obj
            publication_values["date_added"] = None # is set to None because this value is ambiguous
            publication_values["date_published"] = datetime.date(publication_values["date_published"],1,1)
            # 8.store publication
            for key, value in publication_values.items():
                setattr(def_pub_obj, key, value)
            def_pub_obj.save()
            logger.debug("%s: Publication added %s", mapping["local_url"], def_pub_obj)
            # 9.set publication as harvested
            #write_connector.execute_ex(ingester_obj.update_harvested(), (mapping["local_url"],))
            pub_added += 1
        except Exception as e:
            logger.error("%s: %s", mapping["local_url"], e)
            continue
    logger.debug("Terminate ingester %s", ingester_obj.get_name())
    logger.info("publications added %s / limbo %s / skipped %s", pub_added,pub_limbo,pub_duplicate)
    read_connector.close_connection()
    write_connector.close_connection()
    return pub_added
