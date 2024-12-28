from kultunaut.lib import jsoncache

def fetchAndSaveNewData():
  # From Kultunaut - called from cronjob?
  jsondata = jsoncache.fetch_jsoncache()
  print(jsondata[0])
  
  
  
if __name__ == "__main__":
  fetchAndSaveNewData()