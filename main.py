

import asyncio
from kultunaut.backend.kultToCache import kultToCache
from kultunaut.backend.CacheToDBEvents import cacheToEventsColl
  
if __name__ == "__main__":
  #kultToCache()
  asyncio.run(cacheToEventsColl())

