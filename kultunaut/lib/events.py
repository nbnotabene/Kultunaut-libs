from kultunaut.lib import lib
from kultunaut.lib.arrangments import Arrangements, Arrangement
from collections.abc import MutableMapping #Interface

from dataclasses import dataclass, field
import asyncio

# metaclass=lib.Singleton
class Events(MutableMapping):
    def doc(self):
        return """
        Implement: __len__, __iter__, __getitem__, __setitem__, and __delitem__
        MutableMapping: https://realpython.com/python-mappings/
        """
    def __init__(self):
        self._data = {}        
    
    def __len__(self):
        len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __delitem__(self, key: int ):
        if key not in self._data and key < 1:
            raise KeyError(key)
        del self._data[key]

    def __getitem__(self, key:int):
        return self._data[key]

    def __setitem__(self, key:int , value:str):
        if len(self._data)==0 or key not in self._data.keys:

            E = Event(value['ArrNr'], value['AinfoNr'], value['tmdbid'], value['start'])
            self._data.__setitem__(key, E)
            
@dataclass
class Event:
    """Class for keeping track of one event."""    
    ArrNr: int = 0
    AinfoNr: int = 0
    tmdbid: str = ''
    start: str = None

    def __post_init__(self):
        self.ArrangDict=Arrangements()

