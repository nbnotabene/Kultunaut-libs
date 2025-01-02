import asyncio  #mariadb
from kultunaut.lib.MariaDBInterface import MariaDBInterface
#from kultunaut.lib.event import Event
from kultunaut.lib import jsoncache
#from kultunaut.lib import lib

import hashlib
import json

"""
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

def jsonToDB(data):
    # SELECT group_concat(column_name) FROM information_schema.COLUMNS WHERE table_schema=DATABASE() AND TABLE_NAME='kult';
    #fields = '"ArrNr", "starter", "Startformat", "startdato", "ArrTidspunkt", "ArrKunstner", "ArrGenre", "ArrUGenre", "AinfoNr", "ArrLangBeskriv", "ArrBeskrivelse", "BilledeUrl", "Filmvurdering", "Nautanb", "Nautanmeld", "Playdk", "Slutdato", "StedNavn", "kulthash", "tmdbId", "created", "updated_at", "binint"'
    #arrObject = {'AinfoNr': '7091081', 'ArrBeskrivelse': 'Russisk animeret eventyrfilm om Snedronningen, der ønsker en kold verden drænet for menneskelige følelser og søger at indhylle alt i is. Men troldmanden Vegards magiske spejle er en trussel mod disse planer', 'ArrGenre': 'Film', 'ArrKunstner': 'Snedronningen!', 'ArrLangBeskriv': '', 'ArrNr': 18208353, 'ArrTidspunkt': 'kl. 16', 'ArrUGenre': 'Tegnefilm/Animation', 'BilledeUrl': 'http://www.kultunaut.dk/images/film/7091081/plakat.jpg', 'Filmvurdering': 'f.u.7', 'Nautanb': None, 'Nautanmeld': None, 'Playdk': None, 'Slutdato': '2024-12-28', 'Startdato': '2024-12-28', 'StedNavn': 'Svaneke Bio'}
    db=MariaDBInterface()
    for jevent in data:        
        #ev = Event(**jevent)
        rec= asyncio.run(db.fetchOneDict(f"select * from kultInput where ArrNr={jevent['ArrNr']}"))
        
        eventStr = ''.join(str(v) for v in jevent.values())
        kulthash = hashlib.md5(eventStr.encode()).hexdigest()
        ev = f"Event: {jevent['ArrNr']} / {jevent['AinfoNr']}: {jevent['Startdato']} {jevent['ArrKunstner']}"
        if rec!=None and kulthash == rec['kulthash']:
          continue
        else:
          for largeVar in ['ArrBeskrivelse', 'ArrLangBeskriv', 'ArrKunstner']:
            jevent[largeVar] = jevent[largeVar].replace("'", "´")
            jevent[largeVar] = jevent[largeVar].replace('"', '\\"')
          cjevent=json.dumps(jevent,ensure_ascii=False)
          if rec==None:
            # INSERT
            print(f"INSERT: {str(ev)}")
            myStatement =f"insert into kultInput (ArrNr, Starter, kulthash, kjson) values ({jevent['ArrNr']}, '{jevent['Startdato']}', '{kulthash}', '{cjevent}')"
            asyncio.run(db.execute(myStatement))
            #print(myStatement)
            print("")
          else:   #rec['kulthash']!=kulthash:
            #UPDATE
            print(f"UPDATE: {str(ev)}")
            myStatement =f"update kultInput set kulthash = '{kulthash}', Starter = '{jevent['Startdato']}', kjson= '{cjevent}' where ArrNr = {jevent['ArrNr']}"
            asyncio.run(db.execute(myStatement))

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