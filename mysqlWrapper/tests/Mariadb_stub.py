from mysqlWrapper.mariadb import MariaDb


class Mariadb_test(MariaDb):

    def __init__(self):
        self.list = []
        pass

    def execute(self,a):
        # append key to list
        self.list.append(a[0])
        return True

    def getList(self):
        return self.list

    def close_connection(self):
        pass