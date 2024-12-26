import mariadb, asyncio
from kultunaut.lib import lib

#from config import settings, Singleton
# from functools import wraps

#class Singleton(type):
#    _instances = {}
#    def __call__(cls, *args, **kwargs):
#        if cls not in cls._instances:
#            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#        return cls._instances[cls]

class MariaDBInterface(metaclass=lib.Singleton):
    def doc(self):
        return """
        SINGLETON DB Client
        """
    connVars = lib.sqlconn()
    branch = lib.conf['BRANCH']
    
    db_config = connVars[branch]['mysqlcon']
    
    def __init__(self):  #self, host, user, password, database
        self.conn = mariadb.connect(**self.db_config)
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    async def execute(self, query, args=None):
        try:
            if args:
                self.cursor.execute(query, args)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return self.cursor.rowcount
        except mariadb.Error as e:
            print(f"Error executing query: {e}")
            return 0

    async def fetchall(self, query, args=None):
        try:
            if args:
                self.cursor.execute(query, args)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except mariadb.Error as e:
            print(f"Error fetching data: {e}")
            return []
          
    async def get_field_names(self, table_name):
        try:
            self.cursor.execute(f"DESCRIBE {table_name}") 
            field_names = [field[0] for field in self.cursor.fetchall()]
            return field_names
        except mariadb.Error as e:
            print(f"Error fetching METAdata: {e}")
            return []

if __name__ == '__main__':
    db=MariaDBInterface()
    fields = asyncio.run(db.get_field_names('kult'))
    print("\nFIELDS")
    print(fields)
    recs= asyncio.run(db.fetchall('select * from kult'))
    print("\nRECS")
    print(recs)

