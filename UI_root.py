

import asyncio
#from kultunaut.backend.kultToCache import kultToCache
#from kultunaut.lib import jsoncache

from dotenv import dotenv_values
from kultunaut.lib.UI import UI

conf = {**dotenv_values(".env"),**dotenv_values(".env.secret")}


if __name__ == "__main__":
  myUI = UI()
  asyncio.run(myUI.getEvents())
  asyncio.run(myUI.pagesFromDB())
  asyncio.run(myUI.createArrFolders())
  asyncio.run(myUI.createIndex())