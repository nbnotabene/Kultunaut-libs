import asyncio  #mariadb
from kultunaut.lib import jsoncache

async def kultToCache():
  # From Kultunaut - called from cronjob?  
  jsondata = await jsoncache.fetch_from_kult()
  return jsondata

if __name__ == "__main__":
  #cacheToDB()
  asyncio.run(kultToCache())