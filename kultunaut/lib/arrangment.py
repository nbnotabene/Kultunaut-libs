from kultunaut.lib import lib
from kultunaut.lib.MariaDBInterface import MariaDBInterface
#from kultunaut.lib.arrangments import Arrangements
from collections.abc import MutableMapping #Interface
import requests
import re, hashlib, json
from datetime import datetime
            
class Arrangement():
    """Class for keeping track of one event."""
    def __init__(self, jevent:dict, parent):
        self._arr=jevent
        self.parent=parent         
                
    def __str__(self):
        return f"Arrang: {self._arr['AinfoNr']}, {self._arr['ArrKunstner']}"

    #def filmInfo(self):
    #    
    #    print(f"PASS: {str(self)}")
    #    #print(f"self._event['kulthash'] == kultInput['kulthash'], {self._event['kulthash']} {kultInput['kulthash']} ")
#
    #def tmdb(self):
    #    if self._arr['ArrNr'] != self._arr['AinfoNr'] and self._arr['tmdbId'] is None:
    #        tmp = self._AinfoNrToTmdbId()
    #        self._arr['tmdbId']=''
    #        if tmp != '':
    #            self._arr['tmdbId']
    #        return self._arr['tmdbId']

    def AinfoNrToTmdbId(self): 
        AinfoNr = self._arr['AinfoNr']
        #if self._arr['tmdbId'] is not None:
        if 'tmdbId' in self._arr.keys():
            print(f"tmdbId OK: {str(self)}")
        elif AinfoNr is None or AinfoNr=='' or self._arr['ArrNr'] == AinfoNr:
            print(f"Arr is singleton: {str(self)}")
        else:
            TMDBKEY = lib.conf['TMDBKEY']
            #TMDBKEY = "dc2ad647c9f680ddb69ef6f15bd3e859"
            TMDBBASE = lib.conf['TMDBBASE']
            TMDBBASE = "https://api.themoviedb.org/3"
            #TMDBPATH = "tmdb"
            AINFOURL = lib.conf['AINFOURL']
            #AINFOURL = "http://kultunaut.dk/perl/service/film.json"
            

            # Kult AinfoNr => imdb_id => TmdbId
            # http://kultunaut.dk/perl/service/film.json?AinfoNr=7098903
        
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
                print(retval)
                return retval
            else:
                return response


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

