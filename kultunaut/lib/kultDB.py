import asyncio  #mariadb
from kultunaut.lib.MariaDBInterface import MariaDBInterface
from kultunaut.lib.event import Event
from kultunaut.lib import lib

"""
fields = '"ArrNr", "starter", "Startformat", "startdato", "ArrTidspunkt", "ArrKunstner", "ArrGenre", "ArrUGenre", "AinfoNr", "ArrLangBeskriv", '
fields += '"ArrBeskrivelse", "BilledeUrl", "Filmvurdering", "Nautanb", "Nautanmeld", "Playdk", "Slutdato", "StedNavn"'

extraFields = '"kulthash", "tmdbId", "created", "updated_at", "binint"'
Arr =   {
    "AinfoNr": "7091081",
    "ArrBeskrivelse": "Russisk animeret eventyrfilm om Snedronningen, der ønsker en kold verden drænet for menneskelige følelser og søger at indhylle alt i is. Men troldmanden Vegards magiske spejle er en trussel mod disse planer",
    "ArrGenre": "Film",
    "ArrKunstner": "Snedronningen!",
    "ArrLangBeskriv": "",
    "ArrNr": 18208353,
    "ArrTidspunkt": "kl. 16",
    "ArrUGenre": "Tegnefilm/Animation",
    "BilledeUrl": "http://www.kultunaut.dk/images/film/7091081/plakat.jpg",
    "Filmvurdering": "f.u.7",
    "Nautanb": null,
    "Nautanmeld": null,
    "Playdk": null,
    "Slutdato": "2024-12-28",
    "Startdato": "2024-12-28",
    "StedNavn": "Svaneke Bio"
  }

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
    fields = '"ArrNr", "starter", "Startformat", "startdato", "ArrTidspunkt", "ArrKunstner", "ArrGenre", "ArrUGenre", "AinfoNr", "ArrLangBeskriv", "ArrBeskrivelse", "BilledeUrl", "Filmvurdering", "Nautanb", "Nautanmeld", "Playdk", "Slutdato", "StedNavn", "kulthash", "tmdbId", "created", "updated_at", "binint"'
    arrObject = {'AinfoNr': '7091081', 'ArrBeskrivelse': 'Russisk animeret eventyrfilm om Snedronningen, der ønsker en kold verden drænet for menneskelige følelser og søger at indhylle alt i is. Men troldmanden Vegards magiske spejle er en trussel mod disse planer', 'ArrGenre': 'Film', 'ArrKunstner': 'Snedronningen!', 'ArrLangBeskriv': '', 'ArrNr': 18208353, 'ArrTidspunkt': 'kl. 16', 'ArrUGenre': 'Tegnefilm/Animation', 'BilledeUrl': 'http://www.kultunaut.dk/images/film/7091081/plakat.jpg', 'Filmvurdering': 'f.u.7', 'Nautanb': None, 'Nautanmeld': None, 'Playdk': None, 'Slutdato': '2024-12-28', 'Startdato': '2024-12-28', 'StedNavn': 'Svaneke Bio'}
    db=MariaDBInterface()
    for jevent in data:        
        ev = Event(**jevent)
        rec= asyncio.run(db.fetchOneDict(f"select * from kult where ArrNr={jevent['ArrNr']}"))
        if rec==None:
            # INSERT
            print(f"INSERT: {str(ev)}")
            myStatement = ev.insertStatement()
            asyncio.run(db.execute(myStatement))
        elif rec['kulthash']!=ev.properties['kulthash']:
            #UPDATE
            print(f"UPDATE: {str(ev)}")
            myStatement = ev.updateStatement(rec)
            #print(f"{myStatement}")
            asyncio.run(db.execute(myStatement))
        else:
            print(f"NO-ACTION: {str(ev)}")
           

        
        #eventID=jevent['ArrNr']
        #self._events[eventID] = jevent

def fetchAndSaveNewData():
  # From Kultunaut - called from cronjob?
  from kultunaut.lib import jsoncache
  jsondata = jsoncache.fetch_jsoncache()
  print(jsondata[0])
  jsonToDB(jsondata)
  
  
  
if __name__ == "__main__":
  fetchAndSaveNewData()