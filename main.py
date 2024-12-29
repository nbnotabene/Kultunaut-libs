from kultunaut.lib import jsoncache
from kultunaut.lib import kultDB

def fetchAndSaveNewData():
  # From Kultunaut - called from cronjob?
  jsondata = jsoncache.fetch_jsoncache()
  print(jsondata[0])
  kultDB.jsonToDB(jsondata)
  
  
  
if __name__ == "__main__":
  fetchAndSaveNewData()