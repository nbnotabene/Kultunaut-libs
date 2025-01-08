#import asyncio  
#from kultunaut.lib.MariaDBInterface import MariaDBInterface
from kultunaut.lib import jsoncache
#from kultunaut.lib import jsonToDB
#from kultunaut.lib.events import Events

def kultToCache():
    jsoncache.fetch_from_kult()
