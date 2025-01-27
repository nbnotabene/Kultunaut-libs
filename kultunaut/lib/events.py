from kultunaut.lib import lib
from kultunaut.lib.MariaDBInterface import MariaDBInterface
#from kultunaut.lib.arrangments import Arrangements
from kultunaut.lib.event import Event
from collections.abc import MutableMapping #Interface
import re
#import json
#import datetime

#from dataclasses import dataclass, field
import asyncio
from kultunaut.lib import jsoncache

# metaclass=lib.Singleton
class Events(MutableMapping):
    def doc(self):
        return """
        Implement: __len__, __iter__, __getitem__, __setitem__, and __delitem__
        MutableMapping: https://realpython.com/python-mappings/
        events => dbUpsert (for each event)
          upsert arrang
        """
    def __init__(self):
        self._db=MariaDBInterface()
        #self._type=type
        self._events = {}
    
    async def cacheToDBevents(self):
        jsondata = await jsoncache.fetch_jsoncache()
        if jsondata is not None:
          #evs=Events()
          #print(jsondata[0])
          for jevent in jsondata:
            arrnr = jevent['ArrNr']
            self.__setitem__(arrnr,jevent)
            #self._events[jevent['ArrNr']]=jevent
            eventDbDict= await self._db.fetchOneDict(f"select * from kultevents where ArrNr={arrnr}")
            #forceUpdate = False
            await self._events[arrnr].dbUpsert(eventDbDict,forceUpdate = False)
    
    def __len__(self):
        len(self._events)

    def __iter__(self):
        return iter(self._events)

    def __delitem__(self, key: int ):
        if key not in self._events and key < 1:
            raise KeyError(key)
        del self._events[key]

    def __getitem__(self, key:int):
        return self._events[key]

    def __setitem__(self, key, value:dict):
        if key ==  value['ArrNr'] and key not in self._events.keys():
            E = Event(value, parent=self)
            #self._events.__setitem__(key, E)
            self._events[key]=E

    def print(self):
        for value in self._events.values():
          print(value)

    #async def dbUpsert(self):
    #    for arrnr in self._events:
    #        eventDbDict= await self._db.fetchOneDict(f"select * from kultevents where ArrNr={arrnr}")
    #        await self._events[arrnr].dbUpsert(eventDbDict)
    #        #print(dbrec)
            
#class Event():
#    """Class for keeping track of one event."""
#    def __init__(self, jevent:dict, parent):
#        self._event=jevent
#        self.parent=parent
#        eventStr = ''.join(str(v) for v in jevent.values())
#        self._event['kulthash'] = hashlib.md5(eventStr.encode()).hexdigest()        
#        #if 'starter' not in self._event.keys():
#        self._event['Starter'] = self._event['Startdato'] + ' ' + self.getTime()
#        if self._event['AinfoNr'] is None:
#            self._event['AinfoNr'] = self._event['ArrNr']
#        
#                
#    def __str__(self):
#        return f"Event: {self._event['ArrNr']} / {self._event['AinfoNr']}, {self._event['Starter']} {self._event['ArrKunstner']}"
#
#    async def dbUpsert(self,eventDbDict,forceUpdate=False):
#        #eventDbDict from DB - eventually None
#        if eventDbDict is None or len(eventDbDict)==0:
#            # INSERT
#            print(f"INSERT: {str(self)}")
#            _eventStr = json.dumps(self._event,ensure_ascii=False)
#            myStatement =f"insert into kultevents (ArrNr, Starter, kulthash, kjson, AinfoNr) values ({self._event['ArrNr']}, '{self._event['Starter']}', '{self._event['kulthash']}', '{_eventStr}', self._event['AinfoNr'])"
#            await self.parent._db.execute(myStatement)
#        elif forceUpdate or (self._event['kulthash'] != eventDbDict['kulthash']):
#            #UPDATE
#            print(f"UPDATE: {str(self)}")
#            _eventStr = json.dumps(self._event,ensure_ascii=False)
#            myStatement =f"update kultevents set kulthash = '{self._event['kulthash']}', Starter = '{self._event['Starter']}', kjson= '{_eventStr}', AinfoNr={self._event['AinfoNr']} where ArrNr = {self._event['ArrNr']}"
#            #({self._event['ArrNr']}, '{self._event['Starter']}', '{self._event['kulthash']}', '{_eventStr}', self._event['AinfoNr'])"
#            await self.parent._db.execute(myStatement)
#        else:
#            print(f"PASS: {str(self)}")
#            #print(f"self._event['kulthash'] == kultInput['kulthash'], {self._event['kulthash']} {kultInput['kulthash']} ")


            

        #print(f"dbrec: {dbrec['ArrNr']}, {dbrec['AinfoNr']}")

    #@property
    #def starter(self):
    #    if 'starter' in self._event.keys():
    #        return self._event['starter']

    #@starter.setter
    #def starter(self, value):
    #    pass
        

    def getTime(self):
        # clean out "Kl. "
        ArrTidspunkt=self._event['ArrTidspunkt']
        tparts = ArrTidspunkt.split(' ')
        if (len(tparts) > 1):
            t = tparts[1] 
        elif (len(tparts) > 0):
            t = tparts[0] 
        else:
            t = "19.45" #KULTDEFTIME

        # split  "19-21"
        if (len(t.split('-')) > 1):
            t = t.split('-')[0]

        # split  "19.45 or 19:45"
        tparts = re.split("[.:]", t)

        if (len(tparts) < 2):
            tparts.append(0)
            tparts[1] = '00'
        r = "{}:{}"
        return r.format(tparts[0], tparts[1])

#async def main():
    #my_dict = EventsDict()
    #{"AinfoNr": "7104969", "ArrBeskrivelse": "Ridley Scott er nu klar med fortsættelsen til Gladiator om den tidligere kejser Marcus Aurelius barnebarn Lucius som tvinges til at kæmpe i Colosseum", "ArrGenre": "Film", "ArrKunstner": "Gladiator II", "ArrLangBeskriv": "", "ArrNr": 18208349, "ArrTidspunkt": "kl. 19:45", "ArrUGenre": "Action/Drama", "BilledeUrl": "http://www.kultunaut.dk/images/film/7104969/plakat.jpg", "Filmvurdering": "t.o.15", "Nautanb": null, "Nautanmeld": null, "Playdk": null, "Slutdato": "2024-12-27", "Startdato": "2024-12-27", "StedNavn": "Svaneke Bio"}
    #evs=Events()
    #ArrNr=18208349
    #aObj = {'ArrNr': 18208349, 'AinfoNr': 7104969, 'tmdbid': '', 'start': '2024-12-27'}
    #arrs.__setitem__(ArrNr, aObj)
    #evs.__setitem__(18208349,aObj)
    #print(arrs.__getitem__(ArrNr))
    #print(evs[ArrNr])
    #Arrangements.__setitem__(18208349, 7104969, "", "2024-12-27")
    
#if __name__ == "__main__":
#    asyncio.run(main())

