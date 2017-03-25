from conf.config import get_config
from mysqlWrapper.mariadb import MariaDb
from .foreign_keys import *
from .tables import *


def setup_database(db_name):

    credentials = dict(get_config("MARIADB"))
    connector = MariaDb(credentials)

    storage_engine = get_config("MISC")["storage_engine"]

    # create database
    connector.create_db(db_name)

    # create tables
    connector.createTable("global_url", GLOBAL_URL.format(storage_engine))
    connector.createTable("local_url", LOCAL_URL.format(storage_engine))

    connector.createTable("publication_authors", PUBLICATION_AUTHORS.format(storage_engine))
    connector.createTable("authors", AUTHORS.format(storage_engine))
    connector.createTable("name_alias", NAMEALIAS.format(storage_engine))
    connector.createTable("alias_source", ALIASSOURCE.format(storage_engine))

    connector.createTable("pub_source", PUB_SOURCE.format(storage_engine))
    connector.createTable("pub_source_alias", PUB_SOURCE_ALIAS.format(storage_engine))
    connector.createTable("pub_source_source", PUB_SOURCE_SOURCE.format(storage_engine))

    connector.createTable("cluster", CLUSTER.format(storage_engine))
    connector.createTable("publication", PUBLICATION.format(storage_engine))
    connector.createTable("types", TYPES.format(storage_engine))

    #limbo tables
    connector.createTable("limbo publication", LIMBO_PUBLICATION)
    connector.createTable("limbo authors", LIMBO_AUTHORS)

    # create foreign keys
    connector.add_foreign_key(LOCAL_URL_FK)
    connector.add_foreign_key(PUBLICATIONS_AUTHORS_FK)
    connector.add_foreign_key(NAME_ALIAS_FK)
    connector.add_foreign_key(ALIAS_SOURCE_FK)
    connector.add_foreign_key(PUBLICATION_FK)
    connector.add_foreign_key(LIMBO_AUTHORS_FK)
    connector.add_foreign_key(PS_ALIAS_FK)
    connector.add_foreign_key(PS_SOURCE_FK)

    # insert default
    global_url =("INSERT INTO global_url(id,domain,url) "
                 "VALUES (1,'http://localhost/publications','http://localhost/publications'),"
                 "       (2,'http://localhost/users','http://localhost/users')"
                 "ON DUPLICATE KEY UPDATE domain= VALUES(domain),"
                 "                        url   = VALUES(url)")

    # insert values for types table
    types = ("INSERT INTO types(id,name) VALUES(1,'article'),(2,'misc'), (3,'inproceedings'),(4,'mastersthesis'),(5,'phdthesis')"
             "ON DUPLICATE KEY UPDATE  name = VALUES(name)")
    connector.execute_ex(global_url)
    connector.execute_ex(types)
    connector.close_connection()








