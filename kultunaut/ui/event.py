import re
import json
#import locale
from datetime import datetime
import requests

class Event:
    def doc(self):
        return """
        Events are Time & place of Arrangements
        ArrNr is the Unique ID of events
        """
        
    def __str__(self):
        #return f"Event: {self.event['ArrNr']} / {self.event['AinfoNr']} / {self.event['tmdbId']}: {self.event['starter']} {self.event['ArrKunstner']}"
        return f"Event: {self.event['ArrNr']} / {self.event['AinfoNr']}: {self.event['starter']} {self.event['ArrKunstner']}"

    
    def __init__(self, ejson, eventC):
        self.eventColl = eventC #REF to ArrEvents
        self.ejson = ejson
        self.event = json.loads(ejson)
        self.event['starter'] = self.event['Startdato'] + ' ' + self.getTime()
        self.event['Startformat'] = datetime.strptime(self.event['starter'], '%Y-%m-%d %H:%M').strftime("%a. d. %-d/%-m") + " " + self.event['ArrTidspunkt']
        if self.event['AinfoNr'] is None: 
          self.event['AinfoNr']=self.event['ArrNr']
        
        # Aarhus universitet
        tmpA = self.event['ArrKunstner'].split(' (via livestream fra Aarhus Universitet)')
        self.event['ArrKunstner'] = tmpA[0]
        if len(tmpA)>1:
          self.event['ArrBeskrivelse'] = f"{self.event['ArrBeskrivelse']}</br>(via livestream fra Aarhus Universitet)" 
          #print(self.event['ArrBeskrivelse'])
        
        self.event['tmdbId']=None
        self.tmdb()
        print(self.event['tmdbId'])
    
    def tmdb(self):
        if self.event['ArrNr'] != self.event['AinfoNr'] and self.event['tmdbId'] is None:
            tmp = self._AinfoNrToTmdbId()
            self.event['tmdbId']=''
            if tmp != '':
                self.event['tmdbId']
            return self.event['tmdbId']
    
    def _AinfoNrToTmdbId(self): 
        TMDBKEY = "dc2ad647c9f680ddb69ef6f15bd3e859"
        TMDBBASE = "https://api.themoviedb.org/3"
        #TMDBPATH = "tmdb"
        AINFOURL = "http://kultunaut.dk/perl/service/film.json"
        AinfoNr=self.event['AinfoNr']  #self.rec(2)
        # Kult AinfoNr => imdb_id => TmdbId
        # http://kultunaut.dk/perl/service/film.json?AinfoNr=7098903
        
        if AinfoNr is None or AinfoNr=='': 
            return ''
        url1 = f"{AINFOURL}?AinfoNr={AinfoNr}"
        response = requests.get(url1)
        retval=''
        if response.status_code == 200:
            # Parse JSON data
            data = json.loads(response.text)
            film = data['film'][str(AinfoNr)] 
            #print(film)
            if 'TmdbId' in film:
                retval = film['TmdbId']
            elif 'Imdb' in film:
                url2 = f"{TMDBBASE}/find/tt{film['Imdb']}?api_key={TMDBKEY}&language=da_DK&external_source=imdb_id"
                #print(url2)
                response2 = requests.get(url2)
            if response2.status_code == 200:
                # Parse JSON data
                data2 = json.loads(response2.text)
                retval = data2['movie_results'][0]['id']
                #print(data2)
        return retval
    
    def getTime(self):
        # clean out "Kl. "
        ArrTidspunkt=self.event['ArrTidspunkt']
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