

import asyncio
from kultunaut.backend.kultToCache import kultToCache
from kultunaut.lib.events import Events
  
if __name__ == "__main__":
  #kultToCache()
  ev = Events()
  asyncio.run(ev.cacheToDBevents())

