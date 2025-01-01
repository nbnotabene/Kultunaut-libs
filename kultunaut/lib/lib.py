import json
#https://pypi.org/project/python-dotenv/
from dotenv import dotenv_values
conf = {**dotenv_values(".env"),**dotenv_values(".env.secret")}
 #  **dotenv_values(".env.secret"),  # load sensitive variables

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

def add_one(number):
  return number + 1

def sqlconn():
  conn1 = json.loads(conf['SQLCONN'])  
  conn2 = conn1[conf['WS']]
  conn2['mysqlcon']["password"]=conf['PW']
  return conn2['mysqlcon']

if __name__ == '__main__':
  #conf = dotenv_values(".env")
  #XX = AppSetup()
  print(sqlconn())