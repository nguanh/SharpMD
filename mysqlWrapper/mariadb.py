from conf.config import get_config
import pymysql
from pymysql.err import *


class MariaDb:

    def __init__(self, credentials=None, db=None):
        self.query = None
        if credentials is None:
            credentials = dict(get_config("MARIADBX"))
            self.storage_engine = get_config("MISC")["storage_engine"]
        else:
            self.storage_engine = "InnoDB"

        try:
            self.connector = pymysql.connect(**credentials)
        except Error as err:
            raise Exception("MariaDB connection error: {}".format(err))
        self.current_database = None
        if self.connector is not None:
            self.cursor = self.connector.cursor()

            if db is not None:
                self.current_database = db
                self.connector.select_db(db)




    def create_database(self, name):
        try:
            self.cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(name))
            self.current_database = name
        except ProgrammingError:
            self.current_database = name
            print("Database {} already exists".format(name))
        except Error as err:
            raise Exception("Failed creating Database: {}".format(err))

    def create_db(self, name):

        # try to change to DB  DB_NAME
        try:
            self.connector.database = name

            self.current_database = name

        except Error as err:
                self.create_database(name)
                self.connector.database = name


    #TODO remove name parameter and get name from query
    def createTable(self, name, query):
        try:
            print("Creating table {}: ".format(name), end='')
            #insert storage engine
            self.connector.select_db(self.current_database)
            self.cursor.execute(query.format(self.storage_engine))
        except InternalError:
            print("already exists.")
        except Error as err:
            print(err)
            return False

        print("successful")
        return True

    def set_query(self, query):
        self.query = query

    def execute_ex(self, query, args=None):
        """
        wrapper for execute method from mysql_connector with try catch and commit
        :param query:
        :param args: tuple with args passes to query
        :return: id  of last inserted element, if query was insert and autoincrement was used
        """
        try:
            # begin transaction
            self.connector.begin()
            self.cursor.execute(query, args)
            self.connector.commit()
        except Error as err:
            raise Exception("MariaDB query error: {}".format(err))
        return self.cursor.lastrowid

    def execute(self, tup):
        if self.query is None:
            raise Exception("query not set")
        try:
            self.connector.begin()
            #self.connector.start_transaction(isolation_level="READ COMMITTED")
            self.cursor.execute(self.query, tup)
            self.connector.commit()
            return self.cursor.lastrowid
        except Error as err:
            raise Exception("MariaDB query error: {} File not added".format(err))

    def set_storage_engine(self,engine):
        self.storage_engine= engine

    def close_connection(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.connector is not None:
            self.connector.close()
        print("Connection closed")
