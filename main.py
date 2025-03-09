

import asyncio
#from kultunaut.backend.kultToCache import kultToCache
#from kultunaut.lib import jsoncache
from kultunaut.lib.events import Events
from kultunaut.lib.arrangements import Arrangements
  
if __name__ == "__main__":

  #from kultunaut.lib import jsonToDB
  #from kultunaut.lib.events import Events
  
  #def kultToCache():
  #asyncio.run(jsoncache.fetch_jsoncache())
  #asyncio.run(jsoncache.fetch_from_kult())
  #kultToCache()
  ev = Events()
  #asyncio.run(ev.fetch_from_kult())
  asyncio.run(ev.cacheToDBevents())
  ars = Arrangements()
  asyncio.run(ars.DBEventsToArrangs(forceUpdate=False))

