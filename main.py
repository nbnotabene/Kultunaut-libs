

import asyncio
from kultunaut.backend.kultToCache import kultToCache
from kultunaut.lib.events import Events
from kultunaut.lib.arrangments import Arrangements
  
if __name__ == "__main__":
  #kultToCache()
  #ev = Events()
  #asyncio.run(ev.cacheToDBevents())
  ars = Arrangements()
  asyncio.run(ars.DBEventsToArrangs(forceUpdate=True))

