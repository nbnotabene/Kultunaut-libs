from kultunaut.lib import lib
from kultunaut.lib.MariaDBInterface import MariaDBInterface
#from kultunaut.lib.arrangments import Arrangements
from collections.abc import MutableMapping #Interface
import re, hashlib, json
from datetime import datetime
            
class Event():
    """Class for keeping track of one event."""
    def __init__(self, jevent:dict, parent):
        self._event=jevent
        self.parent=parent         
                
    def __str__(self):
        return f"Event: {self._event['ArrNr']} / {self._event['AinfoNr']}, {self._event['Starter']} {self._event['ArrKunstner']}"

    def updateJSONvalues(self):
        #kulthash - before values are changed
        eventStr = ''.join(str(v) for v in self._event.values())
        self._event['kulthash'] = hashlib.md5(eventStr.encode()).hexdigest()
        
        #if 'starter' not in self._event.keys():
        self._event['Starter'] = self._event['Startdato'] + ' ' + self.getTime()
        self._event['Startformat'] = datetime.strptime(self._event['Starter'], '%Y-%m-%d %H:%M').strftime("%a. d. %-d/%-m") + " " + self._event['ArrTidspunkt']
        
        #AinfoNr
        if self._event['AinfoNr'] is None: 
            self._event['AinfoNr'] = self._event['ArrNr']

        # Aarhus universitet
        tmpA = self._event['ArrKunstner'].split(' (via livestream fra Aarhus Universitet)')
        self._event['ArrKunstner'] = tmpA[0]
        if len(tmpA)>1:
          self._event['ArrBeskrivelse'] = f"{self._event['ArrBeskrivelse']}</br>(via livestream fra Aarhus Universitet)" 

        for largeVal in ['ArrBeskrivelse', 'ArrLangBeskriv', 'ArrKunstner']:
            self._event[largeVal] = self._event[largeVal].replace("'", "´")
            self._event[largeVal] = self._event[largeVal].replace('"', '\\"')

    async def dbUpsert(self, eventDbDict, forceUpdate=False):
        self.updateJSONvalues()
        #eventDbDict from DB - eventually None
        if eventDbDict is None or len(eventDbDict)==0:
            # INSERT
            print(f"INSERT: {str(self)}")
            _eventStr = json.dumps(self._event,ensure_ascii=False)
            myStatement =f"insert into kultevents (ArrNr, kulthash, kjson, AinfoNr) values ({self._event['ArrNr']}, '{self._event['kulthash']}', '{_eventStr}', {self._event['AinfoNr']})"
            await self.parent._db.execute(myStatement)
        elif forceUpdate or (self._event['kulthash'] != eventDbDict['kulthash']):
            #UPDATE
            print(f"UPDATE: {str(self)}")
            _eventStr = json.dumps(self._event,ensure_ascii=False)
            myStatement =f"update kultevents set kulthash = '{self._event['kulthash']}', kjson= '{_eventStr}', AinfoNr={self._event['AinfoNr']} where ArrNr = {self._event['ArrNr']}"
            await self.parent._db.execute(myStatement)
        else:
            print(f"PASS: {str(self)}")
            #print(f"self._event['kulthash'] == kultInput['kulthash'], {self._event['kulthash']} {kultInput['kulthash']} ")


            

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
    ##arrs.__setitem__(ArrNr, aObj)
    #evs.__setitem__(18208349,aObj)
    ##print(arrs.__getitem__(ArrNr))
    #print(evs[ArrNr])
    ##Arrangements.__setitem__(18208349, 7104969, "", "2024-12-27")
    
#if __name__ == "__main__":
#    asyncio.run(main())

