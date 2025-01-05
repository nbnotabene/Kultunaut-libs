import asyncio  #mariadb
from kultunaut.lib.MariaDBInterface import MariaDBInterface
from kultunaut.lib.events import Events, Event
import hashlib
import json


def update_arrangement(jevent):
  AinfoNr = jevent['AinfoNr']
  print(AinfoNr)
  #if jevent['AinfoNr'] in arrs 


def jsonToDB(data):
    # SELECT group_concat(column_name) FROM information_schema.COLUMNS WHERE table_schema=DATABASE() AND TABLE_NAME='kult';
    #fields = '"ArrNr", "starter", "Startformat", "startdato", "ArrTidspunkt", "ArrKunstner", "ArrGenre", "ArrUGenre", "AinfoNr", "ArrLangBeskriv", "ArrBeskrivelse", "BilledeUrl", "Filmvurdering", "Nautanb", "Nautanmeld", "Playdk", "Slutdato", "StedNavn", "kulthash", "tmdbId", "created", "updated_at", "binint"'
    #arrObject = {'AinfoNr': '7091081', 'ArrBeskrivelse': 'Russisk animeret eventyrfilm om Snedronningen, der ønsker en kold verden drænet for menneskelige følelser og søger at indhylle alt i is. Men troldmanden Vegards magiske spejle er en trussel mod disse planer', 'ArrGenre': 'Film', 'ArrKunstner': 'Snedronningen!', 'ArrLangBeskriv': '', 'ArrNr': 18208353, 'ArrTidspunkt': 'kl. 16', 'ArrUGenre': 'Tegnefilm/Animation', 'BilledeUrl': 'http://www.kultunaut.dk/images/film/7091081/plakat.jpg', 'Filmvurdering': 'f.u.7', 'Nautanb': None, 'Nautanmeld': None, 'Playdk': None, 'Slutdato': '2024-12-28', 'Startdato': '2024-12-28', 'StedNavn': 'Svaneke Bio'}
    db=MariaDBInterface()
    for jevent in data:        
        #ev = Event(**jevent)
        rec= asyncio.run(db.fetchOneDict(f"select * from kultInput where ArrNr={jevent['ArrNr']}"))
        
        ev = Events[jevent['ArrNr'],jevent]
            
        if rec['AinfoNr'] is None:
          if jevent['AinfoNr']=='' or jevent['AinfoNr']==None:
            AinfoNr = rec['ArrNr']
          
        
        eventStr = ''.join(str(v) for v in jevent.values())
        kulthash = hashlib.md5(eventStr.encode()).hexdigest()
        
        # AinfoNr (empty? = ArrNr)
        if jevent['AinfoNr']==None: 
          jevent['AinfoNr'] = jevent['ArrNr']
        else:
          update_arrangement(jevent)
        
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
            myStatement =f"insert into kultInput (ArrNr, Starter, kulthash, kjson, AinfoNr) values ({jevent['ArrNr']}, '{jevent['Startdato']}', '{kulthash}', '{cjevent}', jevent['AinfoNr'])"
            asyncio.run(db.execute(myStatement))
            #print(myStatement)
            print("")
          else:   #rec['kulthash']!=kulthash:
            #UPDATE
            print(f"UPDATE: {str(ev)}")
            myStatement =f"update kultInput set kulthash = '{kulthash}', Starter = '{jevent['Startdato']}', kjson= '{cjevent}', AinfoNr={jevent['AinfoNr']} where ArrNr = {jevent['ArrNr']}"
            asyncio.run(db.execute(myStatement))