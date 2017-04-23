from conf.config import get_config
from mysqlWrapper.mariadb import MariaDb
from ingester.helper import normalize_title,split_authors, normalize_authors
import pandas
import pymysql
from conf.config import get_config
import datetime
import os
local_path = os.path.dirname(os.path.abspath(__file__))
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

N_POPULAR = ("CREATE TABLE `popular_names` ("
    "  `name` varchar(100) NOT NULL,"
    "  `counter` INT NOT NULL,"
    "  PRIMARY KEY (`name`)"
    ") ENGINE= {} CHARSET=utf8mb4")


DBLP_QUERY = ("SELECT mdate,title,pub_year,author FROM {}.dblp_article").format("harvester")


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
    connector.createTable("popular names", N_POPULAR.format(storage_engine))
    connector.close_connection()


def dblp_mapping(query_tuple):
    return {
        "pub": query_tuple[2],
        "mdate": query_tuple[0],
        "normal": normalize_title(query_tuple[1]).split(" "),
        "author": split_authors(query_tuple[3]),
    }

def set_mdate(connector,mdate):
    connector.execute(("INSERT INTO `mdates`(mdate,counter) VALUES(%s,1)"
                       "ON DUPLICATE KEY UPDATE counter= counter+1"), (mdate,))

def set_pubyear(connector,year):
    connector.execute(("INSERT INTO `pub_year`(pubyear,counter) VALUES(%s,1)"
                       "ON DUPLICATE KEY UPDATE counter= counter+1"), (year,))

def set_title_length(connector,length):
    connector.execute(("INSERT INTO `title_length`(length,counter) VALUES(%s,1)"
                       "ON DUPLICATE KEY UPDATE counter= counter+1"), (length,))

def set_popular(connector,word_list):
    for word in word_list:
        connector.execute(("INSERT INTO `popular_words`(word,counter) VALUES(%s,1)"
                              "ON DUPLICATE KEY UPDATE counter= counter+1"), (word,))

def set_popular_names(connector,name_list):
    for name in name_list:
        normal_name_list = normalize_authors(name).split(" ")
        for normal_name in normal_name_list:
            connector.execute(("INSERT INTO `popular_names`(name,counter) VALUES(%s,1)"
                              "ON DUPLICATE KEY UPDATE counter= counter+1"), (normal_name,))



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
                                     database="analysis",
                                     charset="utf8mb4")
    count = 0
    with read_connector.cursor() as cursor:
        with write_connector.cursor() as wcursor:
            cursor.execute(DBLP_QUERY, ())
            for query_dataset in cursor:
                mapping = dblp_mapping(query_dataset)
                set_pubyear(wcursor, mapping["pub"])
                set_mdate(wcursor, mapping["mdate"])
                set_popular(wcursor, mapping["normal"])
                set_title_length(wcursor, len(mapping["normal"]))
                set_popular_names(wcursor,mapping["author"])
                write_connector.commit()
                count += 1
                if count % 10000 == 0:
                    print(count)

        write_connector.close()
    read_connector.close()
def run():
    #setup()
    mdates = pandas.DataFrame(index=["count"])
    pubyear = pandas.DataFrame(index=["count"])
    title_length = pandas.DataFrame(index=["count"])
    title_popular = pandas.DataFrame(index=["count"])
    name_popular = pandas.DataFrame(index=["count"])
    read_connector = pymysql.connect(user="root",
                                     password="master",
                                     host="localhost",
                                     database="harvester",
                                     charset="utf8mb4")
    with read_connector.cursor() as cursor:
        cursor.execute(DBLP_QUERY,())
        for query_dataset in cursor:
            mapping = dblp_mapping(query_dataset)
            # Modify Date
            if mapping["mdate"] not in mdates:
                mdates.insert(0,mapping["mdate"],1)
            else:
                mdates.ix["count",mapping["mdate"]] += 1
            # publication year
            if mapping["pub"] not in pubyear:
                pubyear.insert(0,mapping["pub"],1)
            else:
                pubyear.ix["count",mapping["pub"]] += 1
            # title length
            if len(mapping["normal"]) not in title_length:
                title_length.insert(0, len(mapping["normal"]), 1)
            else:
                title_length.ix["count", len(mapping["normal"])] += 1
            # popular words
            for word in mapping["normal"]:
                if word not in title_popular:
                    title_popular.insert(0, word, 1)
                else:
                    title_popular.ix["count", word] += 1
            # popular names
            for author in mapping["author"]:
                name_list = normalize_authors(author).split(" ")
                for word in name_list:
                    if word not in name_popular:
                        name_popular.insert(0, word, 1)
                    else:
                        name_popular.ix["count", word] += 1

    mdates.to_csv(os.path.join(local_path,"mdates.csv"))
    pubyear.to_csv(os.path.join(local_path,"pubyear.csv"))
    title_length.to_csv(os.path.join(local_path, "titlelength.csv"))
    title_popular.to_csv(os.path.join(local_path, "titlepop.csv"))
    name_popular.to_csv(os.path.join(local_path, "namepop.csv"))
    read_connector.close()
if __name__ =="__main__":
    run_db()
