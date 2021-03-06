import csv
import datetime

from conf.config import get_config
from mysqlWrapper.mariadb import MariaDb

TESTDB = "test_storage"


def get_table_data(table, null_dates = True):
    credentials = dict(get_config("MARIADBX"))
    # connect to database
    connector = MariaDb(credentials)
    connector.connector.database = TESTDB
    # fetch everything
    query = "SELECT * FROM test_storage.{}".format(table)
    connector.cursor.execute(query)
    print(query)
    result = set()
    for dataset in connector.cursor:
        print(dataset)
        tmp = ()
        for element in dataset:
            # overwrite timestamps with generic date for easier testing
            if null_dates and isinstance(element,datetime.datetime):
                tmp+=((datetime.datetime(1990,1,1,1,1,1),))
            else:
                tmp+=(element,)
        result.add(tmp)
    connector.close_connection()
    return result

def setup_tables(filename, table_query, insert_query):
    # load testconfig
    credentials = dict(get_config("MARIADBX"))
    # setup database
    connector = MariaDb(credentials)
    connector.create_db(TESTDB)
    connector.connector.database = TESTDB
    connector.createTable("test dblp table", table_query)

    # setup test ingester database
   # setup_database(TESTDB)
    # import records from csv
    with open(filename, newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='"')
        do_once = False
        for row in spamreader:
            # remove last updated and harvest date
            del row[-2:]
            # skip first line
            if do_once is True:
                tup = tuple(map(lambda x: x if x != "" else None, row))
                connector.execute_ex(insert_query, tup)
            else:
                do_once = True
    connector.close_connection()


def get_pub_dict(url_id=None, title=None, pages=None, note=None, doi=None, abstract= None, copyright = None,
                 date_published=None, volume=None, number=None, date_added = None,
                 author_ids=None, keyword_ids=None,type_ids = None, study_field_ids = None, pub_source_ids = None):
    return{
        "url_id": url_id,
        "title":title,
        "pages": pages,
        "note": note,
        "doi": doi,
        "abstract": abstract,
        "copyright": copyright,
        "date_published": date_published,
        "volume": volume,
        "number": number,
        "author_ids": author_ids,
        "keyword_ids": keyword_ids,
        "type_ids": type_ids,
        "study_field_ids": study_field_ids,
        "pub_source_ids": pub_source_ids,
    }


def get_pub_source(key=None, series=None, edition=None, location=None, publisher=None, institution=None, school=None,
                   address=None, isbn=None, howpublished=None, book_title=None, journal=None):
    return{
        "key": key,
        "series": series,
        "edition": edition,
        "location": location,
        "publisher": publisher,
        "institution": institution,
        "school": school,
        "address": address,
        "isbn": isbn,
        "howpublished": howpublished,
        "book_title": book_title,
        "journal": journal,
    }