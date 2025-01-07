from kultunaut.lib import lib
from collections.abc import MutableMapping #Interface
#from dataclasses import dataclass, field
import asyncio

# metaclass=lib.Singleton
class Arrangements(MutableMapping):
    def doc(self):
        return """
        Implement: __len__, __iter__, __getitem__, __setitem__, and __delitem__
        MutableMapping: https://realpython.com/python-mappings/
        """
    def __init__(self):
        self._arrangs = {}        
    
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
        if len(self._arrangs)==0 or key not in self._arrangs.keys:

            A = Arrangement(value['ArrNr'], value['AinfoNr'], value['tmdbid'], value['start'])
            self._arrangs.__setitem__(key, A)
            #super().__setitem__(key, A)

    
        #def __init__(self):  #self, host, user, password, database
        #    self.__arrs = []
        #
        #def __setitem__(self, key, value):
        #    super().__setitem__(key, value * 10)

#@dataclass
class Arrangement:
    """Class for keeping track of one arrangement."""    
    ArrNr: int = 0
    AinfoNr: int = 0
    tmdbid: str = ''
    start: str = None
    startlist: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.startlist.append(self.start)
        #print(self.tmdb())

    def tmdm(self) -> str:
        self.tmdbid = 'test1'
        return f"tmdbid: {self.tmdbid}"
    

async def main():
    #my_dict = EventsDict()
    #{"AinfoNr": "7104969", "ArrBeskrivelse": "Ridley Scott er nu klar med fortsættelsen til Gladiator om den tidligere kejser Marcus Aurelius barnebarn Lucius som tvinges til at kæmpe i Colosseum", "ArrGenre": "Film", "ArrKunstner": "Gladiator II", "ArrLangBeskriv": "", "ArrNr": 18208349, "ArrTidspunkt": "kl. 19:45", "ArrUGenre": "Action/Drama", "BilledeUrl": "http://www.kultunaut.dk/images/film/7104969/plakat.jpg", "Filmvurdering": "t.o.15", "Nautanb": null, "Nautanmeld": null, "Playdk": null, "Slutdato": "2024-12-27", "Startdato": "2024-12-27", "StedNavn": "Svaneke Bio"}
    arrs=Arrangements()
    ArrNr=18208349
    aObj = {'ArrNr': 18208349, 'AinfoNr': 7104969, 'tmdbid': '', 'start': '2024-12-27'}
    #arrs.__setitem__(ArrNr, aObj)
    arrs[ArrNr]=aObj
    #print(arrs.__getitem__(ArrNr))
    print(arrs[ArrNr])
    #Arrangements.__setitem__(18208349, 7104969, "", "2024-12-27")
    
if __name__ == "__main__":
    asyncio.run(main())
