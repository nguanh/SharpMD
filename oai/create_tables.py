from oai.queries import OAI_DATASET
from mysqlWrapper.mariadb import MariaDb

DB_NAME = 'oaimph'
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
    database.createTable("oaimph", OAI_DATASET)
    database.close_connection()



