from kultunaut.lib import lib
from kultunaut.lib.MariaDBInterface import MariaDBInterface
from collections.abc import MutableMapping #Interface
#from dataclasses import dataclass, field
from kultunaut.lib.arrangment import Arrangement
import asyncio
import json, datetime

# metaclass=lib.Singleton
class Arrangements(MutableMapping):
    def doc(self):
        return """
        Implement: __len__, __iter__, __getitem__, __setitem__, and __delitem__
        MutableMapping: https://realpython.com/python-mappings/
        """
    def __init__(self):
        self._db=MariaDBInterface()
        self._arrangs = {}   
        
    async def DBEventsToArrangs(self):
        start = datetime.datetime.now()
        start = '2024-12-12'
        sql = f"select ArrNr, AinfoNr, kjson from kultevents where vStarter > '{start}' order by vStarter" #  where starter > '{datetime.datetime.now()}'")
        Dbevents= await self._db.fetchall(sql)
        #for dbev in Dbevents:
        for (arrnr, ainfonr, jev) in Dbevents:  
            #arrnr = dbev[0]
            #ainfonr = dbev[1]
            jevent = json.loads(jev)
            #print(f"{arrnr} - {jevent['ArrKunstner']} {ainfonr}")
            if ainfonr not in self._arrangs.keys():
                self.__setitem__(ainfonr,jevent)
                
                ArrDbDict= await self._db.fetchOneDict(f"select * from kultarrs where AinfoNr={ainfonr}")
                #forceUpdate = False
                #await self._events[arrnr].dbUpsert(eventDbDict,forceUpdate = False)
                #self._arrangs[ainfonr].AinfoNrToTmdbId()
                await self._arrangs[ainfonr].dbUpsert(ArrDbDict, forceUpdate = False)
                #tmdbInfo = self._arrangs[ainfonr].tmdbInfo()
                #print(tmdbInfo)
        
        #print(f"self._arrangs: ")
        #for arr in self._arrangs:  print(arr)
    
    def __len__(self):
        len(self._arrangs)

    def __iter__(self):
        return iter(self._arrangs)

    def __delitem__(self, key: int ):
        if key not in self._arrangs and key < 1:
            raise KeyError(key)
        del self._arrangs[key]

    def __getitem__(self, key:int):
        return self._arrangs[key]

    def __setitem__(self, key:int , value:dict):
        #if len(self._arrangs)==0 or key not in self._arrangs.keys():
        A = Arrangement(value, parent=self)
        self._arrangs.__setitem__(key, A)

        #def __init__(self):  #self, host, user, password, database
        #    self.__arrs = []
        #
        #def __setitem__(self, key, value):
        #    super().__setitem__(key, value * 10)

#async def main():
#    #my_dict = EventsDict()
#    #{"AinfoNr": "7104969", "ArrBeskrivelse": "Ridley Scott er nu klar med fortsættelsen til Gladiator om den tidligere kejser Marcus Aurelius barnebarn Lucius som tvinges til at kæmpe i Colosseum", "ArrGenre": "Film", "ArrKunstner": "Gladiator II", "ArrLangBeskriv": "", "ArrNr": 18208349, "ArrTidspunkt": "kl. 19:45", "ArrUGenre": "Action/Drama", "BilledeUrl": "http://www.kultunaut.dk/images/film/7104969/plakat.jpg", "Filmvurdering": "t.o.15", "Nautanb": null, "Nautanmeld": null, "Playdk": null, "Slutdato": "2024-12-27", "Startdato": "2024-12-27", "StedNavn": "Svaneke Bio"}
#    arrs=Arrangements()
#    ArrNr=18208349
#    aObj = {'ArrNr': 18208349, 'AinfoNr': 7104969, 'tmdbid': '', 'start': '2024-12-27'}
#    #arrs.__setitem__(ArrNr, aObj)
#    arrs[ArrNr]=aObj
#    #print(arrs.__getitem__(ArrNr))
#    print(arrs[ArrNr])
#    #Arrangements.__setitem__(18208349, 7104969, "", "2024-12-27")
#    
#if __name__ == "__main__":
#    asyncio.run(main())
