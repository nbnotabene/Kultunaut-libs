#from kultunaut.lib.MariaDBInterface import MariaDBInterface
#from kultunaut.lib import lib
from datetime import datetime
import locale

import hashlib
import re
      
class Event:
    def doc(self):
        return """
        Events are Time & place of Arrangements
        ArrNr is the Unique ID of events
        """
    
    def __init__(self, **kwargs):
        self.properties = kwargs
        self.properties['kulthash'] = self.hashValue()
        self.properties['starter'] = self.properties['Startdato'] + ' ' + self.getTime()
        self.properties['Startformat'] = datetime.strptime(self.properties['starter'], '%Y-%m-%d %H:%M').strftime("%a. d. %-d/%-m") + " " + self.properties['ArrTidspunkt']
        if self.properties['AinfoNr'] is None: self.properties['AinfoNr']=self.properties['ArrNr']
    
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
    
    def insertStatement(self):
        myvals = '", "'.join(str(self.properties[k]).replace('"', '\\"') for k in list(self.properties.keys()))
        myvals= f'"{myvals}"'
        mykeys = ', '.join(str(k) for k in list(self.properties.keys()))
        #print(mykeys)
        #print(f"insert into kult ({mykeys}) values ({myvals})")
        return f"insert into kult ({mykeys}) values ({myvals})"
    
    def updateStatement(self, dbrec):
        count=0
        STM = "update kult set "

        for k in list(self.properties.keys()):
            if k in dbrec: dbFname=k
            else: dbFname=k.casefold()
            
            dateCompare = self.compare_dates(self.properties[k], dbrec[dbFname])
            if dateCompare==-1: continue # equal dates
            
            if self.properties[k] != dbrec[dbFname]:                
                count+=1
                if count>1: STM += ', '
                if self.properties[k] == None:
                  fval = ''
                else:    
                    fval = str(dbrec[dbFname]).replace('"', '\\"')                    
                STM += f'{k}="{fval}"'
                #debug:
                print(f'{k}:::{self.properties[k]}-{fval}')
        if count>0:
            return f'{STM} where ArrNr={dbrec["ArrNr"]}'

    def compare_dates(self, date1, date2):
      """
      Checks if two variables can be casted as dates and compares them for equality.
    
      Args:
        date1: The first variable to check.
        date2: The second variable to check.
    
      Returns:        
        True if both variables can be casted as dates and they are equal, 
        False otherwise.
      """
      rvalue=0
      try:
        # Attempt to parse date1
        if isinstance(date1, datetime):
          date1 = date1.date()
        elif isinstance(date1, str):
          date1 = datetime.strptime(date1, "%Y-%m-%d").date()
      except (ValueError, TypeError):
        rvalue+=1
        #return False  # Failed to parse date1
    
      try:
        if isinstance(date2, datetime):
          date2 = date2.date()
        elif isinstance(date2, str):
          date2 = datetime.strptime(date2, "%Y-%m-%d").datetime()        
      except (ValueError, TypeError):
        rvalue+=2
        #return False  # Failed to parse date2
    
      if rvalue==0:      # Compare the parsed dates
        if date1 == date2: rvalue -1 
        elif date1 != date2: rvalue -2
      return rvalue
      


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
"""
UPDATE: Event: 18208354 / 18208354: 2024-12-29 16:00 Snedronningen!

AinfoNr:::18208354-7091081
ArrNr:::18208354-18208354
ArrTidspunkt:::kl. 16-kl. 16:00
Slutdato:::2024-12-29-2024-12-29
Startdato:::2024-12-29-2024-12-29
kulthash:::75040dec3adfa4b4d2713839a56c9cee-28b95a4398802d84e704be5248301551
starter:::2024-12-29 16:00-2024-12-29 16:00:00
Startformat:::Sun. d. 29/12 kl. 16-søn. d. 29/12 kl. 16:00
"""