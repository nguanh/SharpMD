from conf.config import get_config
from mysqlWrapper.mariadb import MariaDb
from ingester.helper import normalize_title
import datetime
DB_NAME = "analysis"
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

N_POPULAR = ("CREATE TABLE `n_popular_words` ("
    "  `word` varchar(100) NOT NULL,"
    "  `counter` INT NOT NULL,"
    "  PRIMARY KEY (`word`)"
    ") ENGINE={} CHARSET=utf8mb4")


DBLP_QUERY = ("SELECT mdate,title,pub_year FROM {}.dblp_article").format("harvester")


def setup():
    """
    create database and table structure
    :return:
    """
    connector = MariaDb()

    storage_engine = get_config("MISC")["storage_engine"]

    # create database
    connector.create_db("analysis")
    connector.createTable("dates", DATE_TABLE.format(storage_engine))
    connector.createTable("publication year", PUB_YEAR_TABLE.format(storage_engine))
    connector.createTable("popular_words", POPULAR.format(storage_engine))
    connector.createTable("title_length", TITLE_LENGTH.format(storage_engine))
    connector.createTable("popular words normalized", N_POPULAR.format(storage_engine))
    connector.close_connection()


def dblp_mapping(query_tuple):
    return {
        "pub": query_tuple[2],
        "mdate": query_tuple[0],
        "title": query_tuple[1].split(" "),
        "normal": normalize_title(query_tuple[1]).split(" "),
    }
def set_mdate(connector,mdate):
    connector.execute_ex(("INSERT INTO `mdates`(mdate,counter) VALUES(%s,1)"
                         "ON DUPLICATE KEY UPDATE counter= counter+1"),(mdate,))


def set_pubyear(connector,pubyear):
    connector.execute_ex(("INSERT INTO `pub_year`(pubyear,counter) VALUES(%s,1)"
                          "ON DUPLICATE KEY UPDATE counter= counter+1"), (pubyear,))

def set_title_length(connector,length):
    connector.execute_ex(("INSERT INTO `title_length`(length,counter) VALUES(%s,1)"
                         "ON DUPLICATE KEY UPDATE counter= counter+1"),(length,))

def set_popular(connector,word_list):
    for word in word_list:
        connector.execute_ex(("INSERT INTO `popular_words`(word,counter) VALUES(%s,1)"
                              "ON DUPLICATE KEY UPDATE counter= counter+1"), (word,))

def n_set_popular(connector,word_list):
    for word in word_list:
        connector.execute_ex(("INSERT INTO `n_popular_words`(word,counter) VALUES(%s,1)"
                              "ON DUPLICATE KEY UPDATE counter= counter+1"), (word,))


def run():
    setup()
    read_connector = MariaDb()
    write_connector = MariaDb(db=DB_NAME)
    count = 0
    read_connector.cursor.execute(DBLP_QUERY)
    for query_dataset in read_connector.cursor:
        mapping = dblp_mapping(query_dataset)
        count += 1
        if count % 10000== 0:
            print(count)
        #set_mdate(write_connector, mapping["mdate"])
        #set_pubyear(write_connector, mapping["pub"])
        #set_title_length(write_connector, len(mapping["title"]))
        #set_popular(write_connector, mapping["title"])
        #n_set_popular(write_connector,mapping["normal"])


    read_connector.close_connection()
    write_connector.close_connection()
if __name__ =="__main__":
    run()
