from kultunaut.lib import lib
from kultunaut.lib.MariaDBInterface import MariaDBInterface
from kultunaut.lib.arrangments import Arrangements
from collections.abc import MutableMapping #Interface

#from dataclasses import dataclass, field
import asyncio

# metaclass=lib.Singleton
class Events(MutableMapping):
    def doc(self):
        return """
        Implement: __len__, __iter__, __getitem__, __setitem__, and __delitem__
        MutableMapping: https://realpython.com/python-mappings/
        """
    def __init__(self, type='upsert'):
        self._db=MariaDBInterface()
        self._type=type
        self._events = {}
        self.ArrangDict=Arrangements()        
    
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
            E = Event(value)
            #self._events.__setitem__(key, E)
            self._events[key]=E

    def print(self):
        for value in self._events.values():
          print(value)

    def dbUpsert(self):
        for arrnr in self._events:
            dbrec= asyncio.run(self._db.fetchOneDict(f"select * from kultInput where ArrNr={arrnr}"))
            self._events[arrnr].dbUpsert(dbrec)
            #print(dbrec)
            
class Event():
    """Class for keeping track of one event."""
    def __init__(self, jevent:dict):
        self._event=jevent
        
    def __str__(self):
        return f"Event: {self._event['ArrNr']} / {self._event['AinfoNr']}"    # {self._event['Startdato']}"  {self._event['ArrKunstner']}"

    def dbUpsert(self,dbrec):
        print(f"dbrec: {dbrec['ArrNr']}, {dbrec['AinfoNr']}")

async def main():
    #my_dict = EventsDict()
    #{"AinfoNr": "7104969", "ArrBeskrivelse": "Ridley Scott er nu klar med fortsættelsen til Gladiator om den tidligere kejser Marcus Aurelius barnebarn Lucius som tvinges til at kæmpe i Colosseum", "ArrGenre": "Film", "ArrKunstner": "Gladiator II", "ArrLangBeskriv": "", "ArrNr": 18208349, "ArrTidspunkt": "kl. 19:45", "ArrUGenre": "Action/Drama", "BilledeUrl": "http://www.kultunaut.dk/images/film/7104969/plakat.jpg", "Filmvurdering": "t.o.15", "Nautanb": null, "Nautanmeld": null, "Playdk": null, "Slutdato": "2024-12-27", "Startdato": "2024-12-27", "StedNavn": "Svaneke Bio"}
    evs=Events()
    ArrNr=18208349
    aObj = {'ArrNr': 18208349, 'AinfoNr': 7104969, 'tmdbid': '', 'start': '2024-12-27'}
    #arrs.__setitem__(ArrNr, aObj)
    evs.__setitem__(18208349,aObj)
    #print(arrs.__getitem__(ArrNr))
    print(evs[ArrNr])
    #Arrangements.__setitem__(18208349, 7104969, "", "2024-12-27")
    
if __name__ == "__main__":
    asyncio.run(main())

