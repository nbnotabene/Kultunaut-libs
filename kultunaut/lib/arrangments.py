class Arrangements(metaclass=lib.Singleton):
    def doc(self):
        return """
        SINGLETON DB Client
        """
    connVars = lib.sqlconn()
    #branch = lib.conf['BRANCH']    
    #db_config = connVars[branch]['mysqlcon']
    
    def __init__(self):  #self, host, user, password, database
        self.arrs = []