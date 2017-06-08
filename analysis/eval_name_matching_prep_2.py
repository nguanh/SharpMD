import os
import pymysql
from sshtunnel import SSHTunnelForwarder
from conf.config import get_config
import pandas
from ingester.helper import normalize_authors
from metaphone import doublemetaphone
from mysqlWrapper.mariadb import MariaDb
local_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(local_path,'data')

DB_NAME= "names"

def metaphone(normal_name):
    name_list = []
    base_list = normal_name.split(" ")
    for subname in base_list:
        metaphone, tmp =doublemetaphone(subname)
        name_list.append(metaphone)

    return " ".join(name_list)

def setup():
    NORMAL_TITLES =("CREATE TABLE `authorspapers` ("
        " `Id` INT NOT NULL,"
        " `main_name` TEXT,"
        " `normal_name` TEXT,"
        " `metaphone_name` TEXT,"
        "  PRIMARY KEY (`Id`)"
        ") ENGINE= {} CHARSET=utf8mb4")
    connector = MariaDb()
    storage_engine = get_config("MISC")["storage_engine"]
    connector.create_database(DB_NAME)
    connector.createTable("dvfds", NORMAL_TITLES.format(storage_engine))
    try:
        connector.execute_ex("CREATE FULLTEXT INDEX main_name_idx  ON authorspapers (main_name)", ())
        connector.execute_ex("CREATE FULLTEXT INDEX normal_name_idx  ON authorspapers (normal_name)", ())
        connector.execute_ex("CREATE FULLTEXT INDEX metaphone_name_idx  ON authorspapers (metaphone_name)", ())
    except:
        print("Index already exists")

    connector.close_connection()





authors = pandas.read_csv(os.path.join(file_path,"PaperAuthor.csv"), index_col="AuthorId")
read_connector = pymysql.connect(user="root",
                                 password="master",
                                 host="localhost",
                                 charset="utf8mb4")
counter = 0
setup()
with read_connector.cursor() as cursor:
    for key, value in authors.iterrows():
        name = str(value['Name'])
        main_name = name

        if name == '' or pandas.isnull(name):
            print(key, "empty name")
            continue

        normal_name = normalize_authors(name)
        metaphone_name = metaphone(normal_name)

        cursor.execute("INSERT IGNORE INTO names.authorspapers(Id,main_name,normal_name,metaphone_name) VALUES (%s,%s,%s,%s)",
                    (int(key),main_name,normal_name,metaphone_name))

        if counter % 100 == 0:
            read_connector.commit()
        counter += 1
        if counter % 10000 == 0:
            print(counter)
    read_connector.commit()
read_connector.close()

