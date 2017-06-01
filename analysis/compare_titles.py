from conf.config import get_config
from mysqlWrapper.mariadb import MariaDb
from ingester.helper import normalize_title,split_authors, normalize_authors
import pandas
import pymysql
from conf.config import get_config
import datetime
import os
import sys
local_path = os.path.dirname(os.path.abspath(__file__))
#=========================================== TABLE NAME ===============================================================
DB_NAME = "comparison"
#=========================================== ANALYSE TABLES ===========================================================
TITLES =("CREATE TABLE {} ("
    " `ID` INT NOT NULL AUTO_INCREMENT ,"
    " `title` TEXT,"
    " `counter` INT DEFAULT 0,"
    "  PRIMARY KEY (`ID`)"
    ") ENGINE= {} CHARSET=utf8mb4")

# ================================================= SELECTION QUERIES ========================================
# unchanged titles
DBLP_BASE_QUERY = ("SELECT title FROM harvester.dblp_article")
ARXIV_BASE_QUERY = ("SELECT title FROM harvester.arxiv_articles")
OAI_BASE_QUERY = ("SELECT title FROM harvester.oaipmh_articles")
# normal titles
DBLP_NORMAL_QUERY = ("SELECT titles FROM dblp_analyse.normal_title")
ARXIV_NORMAL_QUERY = ("SELECT titles FROM arxiv_analyse.normal_title")
OAI_NORMAL_QUERY = ("SELECT titles FROM citeseerx_analyse.normal_title")
# ================================================= SEARCH SELECTION QUERIES ========================================
DBLP_BASE_SEARCH = ("SELECT title FROM harvester.dblp_article WHERE MATCH(title) AGAINST (%s IN BOOLEAN MODE)'")
ARXIV_BASE_SEARCH = ("SELECT title FROM harvester.arxiv_articles WHERE MATCH(title) AGAINST (%s IN BOOLEAN MODE)'")
OAI_BASE_SEARCH = ("SELECT title FROM harvester.oaipmh_articles WHERE MATCH(title) AGAINST (%s IN BOOLEAN MODE)'")
DBLP_NORMAL_SEARCH = ('SELECT titles FROM dblp_analyse.normal_title WHERE MATCH(titles) AGAINST (%s IN BOOLEAN MODE)')
ARXIV_NORMAL_SEARCH = ('SELECT titles FROM arxiv_analyse.normal_title WHERE MATCH(titles) AGAINST (%s IN BOOLEAN MODE)')
OAI_NORMAL_SEARCH = ('SELECT titles FROM citeseerx_analyse.normal_title WHERE MATCH(titles) AGAINST (%s IN BOOLEAN MODE)')

def setup(TABLE_NAME):
    """
    create database and table structure
    :return:
    """
    connector = MariaDb()
    storage_engine = get_config("MISC")["storage_engine"]
    # create database
    connector.create_database(DB_NAME)
    connector.createTable(TABLE_NAME, TITLES.format(TABLE_NAME,storage_engine))
    connector.close_connection()



def set_mdate(connector,mdate):
    connector.execute(("INSERT INTO `mdates`(mdate,counter) VALUES(%s,1)"
                       "ON DUPLICATE KEY UPDATE counter= counter+1"), (mdate,))

def set_pubyear(connector,year):
    connector.execute(("INSERT INTO `pub_year`(pubyear,counter) VALUES(%s,1)"
                       "ON DUPLICATE KEY UPDATE counter= counter+1"), (year,))

def set_title(connector, title):
    # store normal title
    connector.execute(("INSERT INTO normal_title (titles) VALUES(%s)"), (title,))
    # store title length
    connector.execute(("INSERT INTO `title_length`(length,counter) VALUES(%s,1)"
                       "ON DUPLICATE KEY UPDATE counter= counter+1"), (len(title),))
    # set popular title words
    for word in title.split(" "):
        connector.execute(("INSERT INTO `popular_words`(word,counter) VALUES(%s,1)"
                              "ON DUPLICATE KEY UPDATE counter= counter+1"), (word,))



def set_authors(connector, authors):
    # set number of authors
    connector.execute(("INSERT INTO `number_author`(number,counter) VALUES(%s,1)"
                       "ON DUPLICATE KEY UPDATE counter= counter+1"), (str(len(authors)),))

    for name in authors:
        # increment author name
        connector.execute(("INSERT INTO `authors`(name,counter) VALUES(%s,1)"
                           "ON DUPLICATE KEY UPDATE counter= counter+1"), (name,))

        normal_name_list = normalize_authors(name).split(" ")
        for normal_name in normal_name_list:
            if len(normal_name)== 1:
                continue
            try:
                # do not accept numbers as names
                int(normal_name)
            except ValueError:
                connector.execute(("INSERT INTO `popular_names`(name,counter) VALUES(%s,1)"
                                   "ON DUPLICATE KEY UPDATE counter= counter+1"), (normal_name,))





def run_db(table1,table2,table_name):
    setup(table_name)
    query_list = [
        DBLP_BASE_QUERY, ARXIV_BASE_QUERY, OAI_BASE_QUERY,
        DBLP_NORMAL_QUERY, ARXIV_NORMAL_QUERY, OAI_NORMAL_QUERY
    ]
    search_list = [
        DBLP_BASE_SEARCH,ARXIV_BASE_SEARCH,OAI_BASE_SEARCH,
        DBLP_NORMAL_SEARCH, ARXIV_NORMAL_SEARCH, OAI_NORMAL_SEARCH,
    ]

    insert_query = "INSERT INTO {}.{}(title) VALUES %s ON DUPLICATE KEY UPDATE counter = counter+1".format(DB_NAME,table_name)
    read_connector = pymysql.connect(user="root",
                                     password="master",
                                     host="localhost",
                                     charset="utf8mb4")

    write_connector = pymysql.connect(user="root",
                                      password="master",
                                      host="localhost",
                                      charset="utf8mb4")
    count = 0
    with read_connector.cursor() as cursor:
        with write_connector.cursor() as wcursor:
            # read from table 1
            cursor.execute(query_list[table1], ())
            for query_dataset in cursor:
                search_title = '"{}"'.format(query_dataset[0])
                wcursor.execute(search_list[table2],(search_title,))
                match = False
                for matches in wcursor:
                    match = True
                if match:
                    wcursor.execute(insert_query,(query_dataset[0],))
                    write_connector.commit()
                count += 1
                if count % 10000 == 0:
                    print(count)
        write_connector.close()
    read_connector.close()

if __name__ =="__main__":
    run_db(sys.argv[0],sys.argv[1], sys.argv[2])
