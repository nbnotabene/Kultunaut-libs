import asyncio  #mariadb
#from kultunaut.lib.MariaDBInterface import MariaDBInterface
from kultunaut.lib import jsoncache
from kultunaut.lib.jsoncache import jsonToDB

#import hashlib
#import json

"""
kultToDB  => __jsonToDB()
cacheToDB => __jsonToDB()

fields = '"ArrNr", "starter", "Startformat", "startdato", "ArrTidspunkt", "ArrKunstner", "ArrGenre", "ArrUGenre", "AinfoNr", "ArrLangBeskriv", '
fields += '"ArrBeskrivelse", "BilledeUrl", "Filmvurdering", "Nautanb", "Nautanmeld", "Playdk", "Slutdato", "StedNavn"'

  fields = asyncio.run(db.get_field_names('kult'))
  assert fields[0] == 'ArrNr'

  for each event:
    select dbevent
    if no dbevent 
    - insert event
    else if changed kulthash
    - update event      
"""

def kultToDB():
  # From Kultunaut - called from cronjob?
  #from kultunaut.lib import jsoncache
  #jsondata = jsoncache.fetch_jsoncache()
  
  jsondata = jsoncache.fetch_from_kult()
  if jsondata is not None:
    #print(jsondata[0])
    jsonToDB(jsondata)
  
def cacheToDB():
  jsondata = jsoncache.fetch_jsoncache()
  if jsondata is not None:
    #print(jsondata[0])
    jsonToDB(jsondata)

if __name__ == "__main__":
  cacheToDB()