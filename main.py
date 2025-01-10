

import asyncio
from kultunaut.backend.kultToCache import kultToCache
from kultunaut.backend.CacheToDBEvents import cacheToEventsColl
from kultunaut.lib.events import Events
  
if __name__ == "__main__":
  #kultToCache()
  ev = Events()
  #asyncio.run(cacheToEventsColl())'
  asyncio.run(ev.cacheToDBevents())

