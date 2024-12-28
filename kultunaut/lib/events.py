from collections.abc import MutableMapping
import asyncio 
from kultunaut.lib.MariaDBInterface import MariaDBInterface
from kultunaut.lib import lib
from kultunaut.lib.jsoncache import fetch_jsoncache
from datetime import datetime
import hashlib
import re
import locale

class Kontrol(metaclass=lib.Singleton):
    def doc(self):
        return """
        Control ArrCollection
        """
    def __init__(self, **kwargs):
        #self.properties = kwargs
        self._db = MariaDBInterface()
        self._events = EventsDict()
        #####self._arrs = ArrsDict()

    async def pullFromJSON(self):
        data = fetch_jsoncache()
        #print(data)
        for jevent in data:
            eventID=jevent['ArrNr']
            self._events[eventID] = jevent

    async def pullFromDB(self):
        self._events._fields = await self._db.get_field_names('kult')
        _eventRecs = await self._db.fetchall('select * from kult where starter > now() order by starter')
        for e in _eventRecs:
            eventID=e[0]
            #eObj = Event(e)
            zipObj = dict(zip(self._events._fields,e))
            self._events[eventID] = zipObj
      
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
      
class Event:
    def doc(self):
        return """
        Events are Time & place of Arrangements
        ArrNr is the Unique ID of events
        """
    #def __init__(self, ArrNr: int, **kwargs):
    def __init__(self, **kwargs):
        self.properties = kwargs
        self.properties['kulthash'] = self.hashValue()
        self.properties['starter'] = self.properties['Startdato'] + ' ' + self.getTime()
        self.properties['startformat'] = datetime.strptime(self.properties['starter'], '%Y-%m-%d %H:%M').strftime("%a. d. %-d/%-m") + " " + self.properties['ArrTidspunkt']

    def getTime(self):
        # clean out "Kl. "
        ArrTidspunkt=self.properties['ArrTidspunkt']
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
        
    def hashValue(self):
        str2hash=''.join(str(self.properties[k]) for k in sorted(self.properties.keys()) if k != 'kulthash')        
        # encode to bytes and format to hexadecimal
        return hashlib.md5(str2hash.encode()).hexdigest()

    def __str__(self):
        #return f"Event: {self.properties['ArrNr']} / {self.properties['AinfoNr']} / {self.properties['tmdbId']}: {self.properties['starter']} {self.properties['ArrKunstner']}"
        return f"Event: {self.properties['ArrNr']} / {self.properties['AinfoNr']}: {self.properties['starter']} {self.properties['ArrKunstner']}"
        
    def binint(self, index):
        # handling 3D, Baby-bio .....
        #insert b'1101'+0 (=13) in DB: int(binint)
        #bin(12) or list(f'{13:07b}') == ['0', '0', '0', '1', '1', '0', '1']
        localBin = list(format(self.properties['binint'], f'0{8}b'))
        localBin.reverse()
        return localBin[index] == '1'        
        sql = "update kult set binint = b'0001100'+0 where ArrNr= 18153597";
        print(sql)

#class Arr:
#    def doc(self):
#        return """
#        Events are Time & place of Arrangements
#        AinfoNr is the Unique ID of Arrangments
#        """
#    def __init__(self, **kwargs):
#        #self.AinfoNr = AinfoNr
#        self.properties = kwargs
#        self.arrEvents = []
#
#    def __str__(self):
#        return f"Arr: {self.properties['AinfoNr']} Properties: {self.properties}"

class EventsDict(MutableMapping):
    def __init__(self):
        self._data = {}
        self._fields = []
        self._arrs = {}
        #self._arrs = {7104940:[18153597, 18153599, 18153599], .......}
        #self._db = MariaDBInterface()
        #self._fields = self._db.get_field_names('kult')

    def setFieldNames(self, names):
        self._fields=names

    def __getitem__(self, key):
        return self._data[key]

    #def arrsFilter(self):
    #    for ev in self._data:
    #      if ev.properties['AinfoNr']  not in self._arrs:
    #        self._arrs.append(ev.properties['AinfoNr'])

    def __setitem__(self, key, value):
        if key != int(key):
            raise ValueError(
                f"'{key}' is invalid."
                " All event ids are integers")
        
        newEvent = Event(**value)
        self._data[key] = newEvent
        
        aId = newEvent.properties['AinfoNr']
        if not aId: aId = newEvent.properties['ArrNr']
        if aId not in self._arrs:
            #self._arrs = {7104940:{arrNums:[18153597, 18153599, 18153599]}, .......}
            self._arrs[aId] = {'arrNums':[newEvent.properties['ArrNr']]}
        else:
          self._arrs[aId]['arrNums'].append(key)
        
    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

#class ArrsDict(MutableMapping):
#    def __init__(self):
#        self._data = {}
#
#    def __getitem__(self, key):
#        return self._data[key]
#
#    def __setitem__(self, key, value):
#        if key != int(key):
#            raise ValueError(
#                f"'{key}' is invalid."
#                " All event ids are integers")
#        zipObj = dict(zip(self._fields,value))
#        #zipObj = {'ArrNr': 18153597, 'starter': datetime.datetime(2024, 11, 11, 15, 58, 23)}
#        #newEvent = Event(key,**kwargs)
#        newEvent = Event(**zipObj)
#        self._data[key] = newEvent
#        self._data[value.AinfoNr] = value

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

async def main():
    #my_dict = EventsDict()
    ctl = Kontrol()
    await ctl.pullFromJSON()
    await ctl.printFields()
    await ctl.printEvents()
    await ctl.printArrs()
    #print(result)

if __name__ == "__main__":
    asyncio.run(main())

#if __name__ == '__main__':      
#    my_dict = EventsDict()
#    event1 = Event(899, brand="Dell", model="Inspiron", storage="512GB")
#    event2 = Event(999, brand="Dell", model="Inspiron", storage="512GB")
#    
#    my_dict[event1] = event1
#    my_dict[event2] = event2
#    
#    print(my_dict[899])  # Output: <__main__.Person object at ...>
#    print(my_dict[999])   # Output: <__main__.Person object at ...>
#    for o in my_dict:
#      print(o) 
