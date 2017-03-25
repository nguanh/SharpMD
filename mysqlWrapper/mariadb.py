import mysql.connector
from mysql.connector import errorcode

from conf.config import get_config


class MariaDb:
    #TODO test

    def __init__(self,credentials= None,db = None):
        self.query = None
        if credentials is None:
            credentials = dict(get_config("MARIADB"))
            self.storage_engine = get_config("MISC")["storage_engine"]
        else:
            self.storage_engine = "InnoDB"

        try:
            self.connector = mysql.connector.connect(**credentials)
        except mysql.connector.Error as err:
            raise Exception("MariaDB connection error: {}".format(err))

        if self.connector is not None:
            self.cursor = self.connector.cursor()

            if db is not None:
                self.current_database = db
                self.connector.database = db


    def create_database(self, name):
        try:
            self.cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(name))
        except mysql.connector.Error as err:
            print("Failed creating ingester: {}".format(err))

    def create_db(self, name):

        # try to change to DB  DB_NAME
        try:
            self.connector.database = name
            self.current_database = name
        except mysql.connector.Error as err:
        # if there is no such db, create DB and change afterwards
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                self.create_database(name)
                self.connector.database = name
            else:
                print(err)


    #TODO remove name parameter and get name from query
    def createTable(self, name, query):

        try:
            print("Creating table {}: ".format(name), end='')
            #insert storage engine
            self.cursor.execute(query.format(self.storage_engine))
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
                return True
            else:
                print(err)
                return False
        else:
            print("successful")
            return True

    def add_foreign_key(self,query):

        try:
            print("Adding foreign key ", end='')
            self.cursor.execute(query)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_CANT_CREATE_TABLE:
                print("already exists.")
                return True
            else:
                print(err)
                return False
        print("successful")
        return True

    def set_query(self, query):
        self.query = query

    def execute_ex(self, operation, params=None,multi=False):
        """
        wrapper for execute method from mysql_connector with try catch and commit
        :param operation:
        :param params:
        :param multi:
        :return:
        """
        try:
            self.cursor.execute(operation, params, multi)
            self.connector.commit()
        except mysql.connector.Error as err:
            raise Exception("MariaDB query error: {}".format(err))
        return self.cursor.lastrowid

    def execute(self, tup):
        if self.query is None:
            raise Exception("query not set")
        try:
            self.cursor.execute(self.query, tup)
            self.connector.commit()
            return self.cursor.lastrowid
        except mysql.connector.Error as err:
            raise Exception("MariaDB query error: {} File not added".format(err))

    def fetch_one(self, tup, query=None,ret_tup = False):
        if query is None:
            query = self.query
        try:
            self.cursor.execute(query, tup)
        except mysql.connector.Error as err:
            raise Exception("MariaDB query error: {} invalid single fetch".format(err))

        result = self.cursor.fetchone()
        #TODO clear rest of results from cursor
        if result is not None:
            if ret_tup is False:
                return result[0]
            return result
        return None


    def set_storage_engine(self,engine):
        self.storage_engine= engine

    def close_connection(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.connector is not None:
            self.connector.close()
        print("Connection closed")
