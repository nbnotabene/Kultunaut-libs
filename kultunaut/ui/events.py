from collections.abc import MutableMapping
import asyncio 
from kultunaut.lib.MariaDBInterface import MariaDBInterface
from kultunaut.lib import lib
#from datetime import datetime
from kultunaut.ui.event import Event

class Events:
    def doc(self):
        return """
        Events are Time & place of Arrangements
        ArrNr is the Unique ID of events
        
        select json_value(kjson, '$.AinfoNr'), json_value(kjson, '$.ArrNr') from kultInput;
        select kjson from kultInput;
        select JSON_KEYS(kjson) from kultInput;
        """

    async def pullFromDB(self):        
        #self._events._fields = await self._db.get_field_names('kult')
        self._db = MariaDBInterface()
        self._eventRecs = await self._db.fetchall('select ArrNr,kjson from kultInput where Starter > now() order by Starter, ArrNr')
        self._arrangements = MutableMapping()
        for e in self._eventRecs:
            (ArrNr,kjson) = e
            newE = Event(kjson, self)
            print(newE)
            
            #eObj = Event(e)
            #zipObj = dict(zip(self._events._fields,e))
            #self._events[eventID] = zipObj
      
    async def printEvents(self):
        print ("\nEvent: ArrNr /    AinfoNr  tmdbId starter             ArrKunstner")
        for e in self._events:
            print(self._events[e])

    async def printFields(self):
        print(self._events._fields)
    
    async def printArrs(self):
        print ("\n AinfoNr: arrNums")
        #print(self._events._arrs)
        for key in self._events._arrs:
            print(key, self._events._arrs[key])
            for arr in self._events._arrs[key]['arrNums']:
              print(self._events[arr].properties['starter'])
      

async def main():
    #my_dict = EventsDict()
    e=Events()
    await e.pullFromDB()

if __name__ == "__main__":
    asyncio.run(main())
