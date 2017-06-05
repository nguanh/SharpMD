from conf.config import get_config
from mysqlWrapper.mariadb import MariaDb
from ingester.helper import normalize_title,split_authors, normalize_authors
import pandas
import pymysql
from conf.config import get_config
import datetime
import os
local_path = os.path.dirname(os.path.abspath(__file__))
#=========================================== TABLE NAME ===============================================================
DB_NAME = "dblp_analyse"
#DB_NAME = "citeseerx_analyse"
#=========================================== ANALYSE TABLES ===========================================================
DATE_TABLE = ("CREATE TABLE `mdates` ("
    "  `mdate` date NOT NULL,"
    "  `counter` INT NOT NULL,"
    "  PRIMARY KEY (`mdate`)"
    ") ENGINE={} CHARSET=utf8mb4")

PUB_YEAR_TABLE = ("CREATE TABLE `pub_year` ("
    "  `pubyear` date NOT NULL,"
    "  `counter` INT NOT NULL,"
    "  PRIMARY KEY (`pubyear`)"
    ") ENGINE={} CHARSET=utf8mb4")

TITLE_LENGTH = ("CREATE TABLE `title_length` ("
    "  `length` INT NOT NULL,"
    "  `counter` INT NOT NULL,"
    "  PRIMARY KEY (`length`)"
    ") ENGINE={} CHARSET=utf8mb4")

POPULAR = ("CREATE TABLE `popular_words` ("
    "  `word` varchar(100) NOT NULL,"
    "  `counter` INT NOT NULL,"
    "  PRIMARY KEY (`word`)"
    ") ENGINE= {} CHARSET=utf8mb4")

N_POPULAR = ("CREATE TABLE `popular_names` ("
    "  `name` varchar(100) NOT NULL,"
    "  `counter` INT NOT NULL,"
    "  PRIMARY KEY (`name`)"
    ") ENGINE= {} CHARSET=utf8mb4")

NUM_AUTHOR =("CREATE TABLE `number_author` ("
    "  `number` varchar(100) NOT NULL,"
    "  `counter` INT NOT NULL,"
    "  PRIMARY KEY (`number`)"
    ") ENGINE= {} CHARSET=utf8mb4")

AUTHORS =("CREATE TABLE `authors` ("
    "  `name` varchar(150) NOT NULL,"
    "  `counter` INT NOT NULL,"
    "  PRIMARY KEY (`name`)"
    ") ENGINE= {} CHARSET=utf8mb4")

NORMAL_TITLES =("CREATE TABLE `normal_title` ("
    " `ID` INT NOT NULL AUTO_INCREMENT ,"
    " `titles` TEXT,"
    "  PRIMARY KEY (`ID`)"
    ") ENGINE= {} CHARSET=utf8mb4")


CAREER =("CREATE TABLE `career` ("
    " `author` VARCHAR(100) NOT NULL ,"
    " `pub_year` DATE NOT NULL ,"
    " `counter` INT DEFAULT 1,"
    "  UNIQUE KEY (`author`,`pub_year`),"
    "  INDEX (`pub_year`)"
    ") ENGINE= {} CHARSET=utf8mb4")


# ================================================= HARVESTER SELECTION QUERIES ========================================
DBLP_QUERY = ("SELECT mdate,title,pub_year,author FROM harvester.dblp_article")
ARXIV_QUERY = ("SELECT mdate,title,created,author FROM harvester.arxiv_articles")
OAI_QUERY = ("SELECT title,author,dates FROM harvester.oaipmh_articles")


def setup():
    """
    create database and table structure
    :return:
    """
    connector = MariaDb()

    storage_engine = get_config("MISC")["storage_engine"]

    # create database
    connector.create_database(DB_NAME)
    connector.createTable("dates", DATE_TABLE.format(storage_engine))
    connector.createTable("publication year", PUB_YEAR_TABLE.format(storage_engine))
    connector.createTable("popular_words", POPULAR.format(storage_engine))
    connector.createTable("title_length", TITLE_LENGTH.format(storage_engine))
    connector.createTable("popular names", N_POPULAR.format(storage_engine))
    connector.createTable("number authors", NUM_AUTHOR.format(storage_engine))
    connector.createTable("Authors", AUTHORS.format(storage_engine))
    connector.createTable("Normal Titles", NORMAL_TITLES.format(storage_engine))
    connector.createTable("Career",CAREER.format(storage_engine))
    # create index
    try:
        connector.execute_ex("CREATE FULLTEXT INDEX title_idx  ON normal_title (titles)", ())
    except:
        print("Index already exists")

    connector.close_connection()


def dblp_mapping(query_tuple):
    return {
        "pub": query_tuple[2],
        "mdate": query_tuple[0],
        "normal": normalize_title(query_tuple[1]),
        "author": split_authors(query_tuple[3]),
    }


def oai_mapping(query_tuple):
    dates = query_tuple[2].split(";")
    del dates [-1]

    try:
        publication_date = datetime.datetime.strptime(dates[-1],"%Y")
    except ValueError:
        try:
            publication_date = datetime.datetime.strptime(dates[-1], "%Y-%m-%d")
        except ValueError:
            print(dates)
            raise Exception()

    return {
        "pub":  publication_date,
        "mdate": datetime.datetime.strptime(dates[0],"%Y-%m-%d"),
        "normal": normalize_title(query_tuple[0]),
        "author": split_authors(query_tuple[1]),
    }


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
    print(len(authors))
    print(str(len(authors)))
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


def set_career(connector, authors, pub_year):

    for guy in authors:
        connector.execute(("INSERT INTO `career`(author,pub_year) VALUES(%s,%s)"
                           "ON DUPLICATE KEY UPDATE counter= counter+1"), (guy,pub_year))



def run_db():
    setup()
    read_connector = pymysql.connect(user="root",
                                     password="master",
                                     host="localhost",
                                     database="harvester",
                                     charset="utf8mb4")
    write_connector = pymysql.connect(user="root",
                                     password="master",
                                     host="localhost",
                                     database=DB_NAME,
                                     charset="utf8mb4")
    count = 0
    with read_connector.cursor() as cursor:
        with write_connector.cursor() as wcursor:
            cursor.execute(DBLP_QUERY, ())
            #cursor.execute(OAI_QUERY, ())
            for query_dataset in cursor:
                mapping = dblp_mapping(query_dataset)
                """
                try:
                    mapping = oai_mapping(query_dataset)
                except Exception:
                    continue
                """
                #set_pubyear(wcursor, mapping["pub"])
                #set_mdate(wcursor, mapping["mdate"])
                #set_title(wcursor, mapping["normal"])
                #set_authors(wcursor, mapping["author"])
                set_career(wcursor,mapping["author"], mapping["pub"])
                write_connector.commit()

                count += 1
                if count % 10000 == 0:
                    print(count)
        write_connector.close()
    read_connector.close()

if __name__ =="__main__":
    run_db()
