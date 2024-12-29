#from kultunaut.lib.MariaDBInterface import MariaDBInterface
#from kultunaut.lib import lib
from datetime import datetime
import hashlib
import re
      
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

if __name__ == '__main__':
    print("")
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
