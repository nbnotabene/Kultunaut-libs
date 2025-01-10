import asyncio  #mariadb
#from kultunaut.lib.MariaDBInterface import MariaDBInterface
from kultunaut.lib import jsoncache
from kultunaut.lib.events import Events

async def cacheToEventsColl():
  evs = Events()
  evs.cacheToDBevents()
  #jsondata = await jsoncache.fetch_jsoncache()
  #if jsondata is not None:
  #  #evs=Events()
  #  #print(jsondata[0])
  #  for jevent in jsondata:
  #    evs[jevent['ArrNr']]=jevent
  #    
  #  #evs.print()
  #  await evs.dbUpsert()
    

if __name__ == "__main__":
  #cacheToDB()
  asyncio.run(cacheToEventsColl())