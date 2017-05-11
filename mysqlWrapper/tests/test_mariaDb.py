from unittest import TestCase
from mysqlWrapper.mariadb import MariaDb

DB_NAME = "blubb"
TABLE_NAME = "muhz"


class TestMariaDb(TestCase):


    def tearDown(self):
        x = MariaDb(db=DB_NAME)
        try:
            x.execute_ex("DROP TABLE IF EXISTS `muhz`")
        except Exception as e:
            print(e)
            pass


    def test_init_success(self):
        MariaDb()


    def test_init_exeception(self):
        credentials={
            "user": "fake",
        "password" : "master",
        "host" : "127.0.0.1",
        "charset":"utf8mb4"
        }
        self.assertRaises(Exception,MariaDb,credentials)

    def test_create_db(self):
        x= MariaDb()
        x.create_database(DB_NAME)
        x.create_database(DB_NAME)
        x.close_connection()

    def test_create_table(self):
        x = MariaDb()
        x.create_database(DB_NAME)
        x.createTable("test", ( "CREATE TABLE `muhz` ("
                                "  `dblp_key` varchar(100) NOT NULL,"
                                "  PRIMARY KEY (`dblp_key`)"
                                ") ENGINE={} CHARSET=utf8mb4"))
        x.close_connection()

    def test_execute_ex(self):
        x = MariaDb()
        x.create_database(DB_NAME)
        x.createTable("test", ( "CREATE TABLE `muhz` ("
                                "  `ID` int NOT NULL AUTO_INCREMENT,"
                                "  `dblp_key` varchar(100) NOT NULL,"
                                "  PRIMARY KEY (`ID`)"
                                ") ENGINE={} CHARSET=utf8mb4"))
        idx= x.execute_ex("INSERT INTO muhz (dblp_key) VALUES (%s)",('mi'))
        self.assertEqual(idx,1)
        x.close_connection()

    def test_execute(self):
        x = MariaDb()
        x.create_database(DB_NAME)
        x.createTable("test", ( "CREATE TABLE `muhz` ("
                                "  `ID` int NOT NULL AUTO_INCREMENT,"
                                "  `dblp_key` varchar(100) NOT NULL,"
                                "  PRIMARY KEY (`ID`)"
                                ") ENGINE={} CHARSET=utf8mb4"))
        x.set_query("INSERT INTO muhz (dblp_key) VALUES (%s)")
        idx= x.execute(('do',))
        idx = x.execute(('re',))
        idx = x.execute(('mi',))
        self.assertEqual(idx,3)
        x.close_connection()



