

import asyncio
#from kultunaut.backend.kultToCache import kultToCache
#from kultunaut.lib import jsoncache

import os
import sys
from dotenv import dotenv_values
conf = {**dotenv_values(".env"),**dotenv_values(".env.secret")}

from kultunaut.lib.UI import UI

if __name__ == "__main__":
  myUI = UI()
  asyncio.run(myUI.getEvents())
  asyncio.run(myUI.pagesFromDB())
  asyncio.run(myUI.createArrFolders())
  asyncio.run(myUI.createIndex())