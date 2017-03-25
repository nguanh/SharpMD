from mysqlWrapper.mariadb import MariaDb
from .queries import DBLP_ARTICLE

DB_NAME = 'harvester'
credentials = {
    'user': 'root',
    'password': 'master',
    'host': '127.0.0.1',
}

try:
    database = MariaDb(credentials)
except Exception as err:
    print(err)
else:
    database.create_db(DB_NAME)
    database.createTable("dblp_article", DBLP_ARTICLE)
    database.close_connection()






