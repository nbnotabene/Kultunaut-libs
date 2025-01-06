import asyncio  #mariadb
#from kultunaut.lib.MariaDBInterface import MariaDBInterface
from kultunaut.lib import jsoncache
from kultunaut.lib import jsonToDB
from kultunaut.lib.events import Events


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

def cacheToEventsColl():
  jsondata = jsoncache.fetch_jsoncache()
  if jsondata is not None:
    evs=Events()
    #print(jsondata[0])
    for jevent in jsondata:
      #ArrNr=18208349
      #aObj = {'ArrNr': 18208349, 'AinfoNr': 7104969, 'tmdbid': '', 'start': '2024-12-27'}
      #arrs.__setitem__(ArrNr, aObj)
      evs.__setitem__(jevent['ArrNr'],jevent)
      
    evs.print()
    evs.dbUpsert()
    

if __name__ == "__main__":
  #cacheToDB()
  cacheToEventsColl()