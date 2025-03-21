from kultunaut.lib import lib
#from kultunaut.lib.MariaDBInterface import MariaDBInterface
#from kultunaut.lib.arrangments import Arrangements
#from collections.abc import MutableMapping #Interface
import requests
import json
import hashlib
#from datetime import datetime

TMDBKEY = lib.conf['TMDBKEY']
#TMDBKEY = "dc2ad647c9f680ddb69ef6f15bd3e859"
TMDBBASE = lib.conf['TMDBBASE']
#TMDBBASE = "https://api.themoviedb.org/3"
#TMDBPATH = "tmdb"

class Arrangement():
    """Class for keeping track of one event."""
    def __init__(self, jevent:dict, parent):
        self._arr=jevent  # Hentet fra DB kultevents
        self.parent=parent
        self._kultfilm = None
        self._arr['tmdbId']=None
        ## {'Category': 'Komedie/Romantik', 'Censur': 't.f.a', 'Imdb': '15560314', 'OrgTitle': 'The Monk and the Gun', 'Poster': 'https://www.kultunaut.dk/images/film/7105122/plakat.jpg', 'Runtime': '107', 'Title': 'Munken og geværet', 'Year': '2023'}
                
    def __str__(self):
        return f"Arrang: {self._arr['AinfoNr']} (ev: {self._arr['ArrNr']}), {self._arr['ArrKunstner']}"
    
    # Input ArrDbDict: Hentet fra DB-table: kultarrs
    async def dbUpsert(self, ArrDbDict, forceUpdate=False):        
        self._kultfilm = await self.kultfilm()
        if self._kultfilm is not None:
              filmStr = ''.join(str(v) for v in self._kultfilm.values())
              self._arr['kulthash'] = hashlib.md5(filmStr.encode()).hexdigest()
              kultfilmdump = json.dumps(self._kultfilm, ensure_ascii=False)
              kultfilmdump=kultfilmdump.replace("\'", "\\'")
              if ArrDbDict is None:
                  print(f"INSERT: {str(self)}")
                  #kultfilmjson = json.dumps(self._kultfilm, ensure_ascii=False)
                  tmdbInfodump = await self.getTmdbInfodump()
                  if tmdbInfodump:
                      tmdbInfodump = tmdbInfodump.replace("\'", "\\'")
                      myStatement =f"insert into kultarrs (AinfoNr, kulthash, kultfilm, tmdb) values ({self._arr['AinfoNr']}, '{self._arr['kulthash']}', '{kultfilmdump}', '{tmdbInfodump}')"
                      await self.parent._db.execute(myStatement)      
              elif forceUpdate or (self._arr['kulthash'] != ArrDbDict['kulthash']):
                  print(f"UPDATE: {str(self)}")
                  tmdbInfodump = await self.getTmdbInfodump()                  
                  tmdbInfodump = tmdbInfodump.replace("\'", "\\'")
                  myStatement = f"update kultarrs set  kulthash = '{self._arr['kulthash']}', kultfilm = '{kultfilmdump}', "
                  myStatement += f"tmdb = '{tmdbInfodump}' where AinfoNr={self._arr['AinfoNr']}"
                  #myStatement =f"update kultarrs set  kulthash = '{self._arr['kulthash']}', kultfilm='{kultfilmdump.replace("\'", "\\'")}', tmdb='{tmdbInfodump.replace("\'", "\\'")}' where AinfoNr={self._arr['AinfoNr']}"
                  await self.parent._db.execute(myStatement)
              else:
                  print(f"PASS: {str(self)}")

    async def getTmdbInfodump(self):
        # property tmdbId 
        self.tmdbId = self.getTmdbId()
        if self.tmdbId is not None:
            print(f"tmdbId: {self.tmdbId}: {str(self)}")
            tmdbInfo= self.tmdbInfo()
            Infodump = json.dumps(tmdbInfo, ensure_ascii=False)
            if tmdbInfo:
                return Infodump #str(tmdbInfo)

    async def kultfilm(self):
        # json data from kultunaut about film
        AinfoNr = self._arr['AinfoNr']
        film = None
        if AinfoNr != self._arr['ArrNr']:
            url1 = f"{lib.conf['AINFOURL']}?AinfoNr={AinfoNr}"
            response = requests.get(url1)
            if response.status_code == 200:
                # Parse JSON data
                data = json.loads(response.text)
                if data['film']!={}:
                    film = data['film'][str(AinfoNr)] 
        return film    

    #@property
    """"""
    def getTmdbId(self): 
        #AinfoNr = self._arr['AinfoNr']
        if 'tmdbId' in self._arr.keys() and self._arr['tmdbId'] is not None:
            return self._arr['tmdbId']
            #elif AinfoNr is None or AinfoNr=='' or self._arr['ArrNr'] == AinfoNr:
            #    print(f"Arr is singleton: {str(self)}")
        else:
            if self._kultfilm and 'Imdb' in self._kultfilm:
                imdbId =  self._kultfilm['Imdb']
                url2 = f"{TMDBBASE}/find/tt{imdbId}?api_key={TMDBKEY}&language=da_DK&external_source=imdb_id"
                #print(url2)
                response2 = requests.get(url2)
                if response2.status_code == 200:
                    # Parse JSON data
                    data2 = json.loads(response2.text)
                    if data2['movie_results']!=[]:
                        self._arr['tmdbId'] = data2['movie_results'][0]['id']
        return self._arr['tmdbId']
              
    def _tmdbURL(self, extraURL="", language="da"):
        #tmdbId=self.__dict__['tmdbId']
        return  f"{TMDBBASE}/movie/{self.tmdbId}{extraURL}?api_key={TMDBKEY}&language={language}"
    
    
    def tmdbInfo(self):
        language="da"
        extraURL = "/videos"
        videodata = requests.get(self._tmdbURL(extraURL)).json()
        if len(videodata['results'])==0:
            videodata = requests.get(self._tmdbURL(extraURL,language="en")).json()
        videoid = None
        if len(videodata['results'])>0:
            videoid = videodata['results'][0]['key']
        
        tmdb = requests.get(self._tmdbURL("",language)).json()
        #if videoid:
        tmdb['videoid']=videoid
        
        credits = requests.get(self._tmdbURL("/credits",language)).json()
        tmdb['casted'] = [cast for cast in credits['cast'] if cast['order'] < 10]
        #tmdb['crew'] = [credit for credit in credits['crew'] if credit['order']<10 ]
        tmdb['crew'] = [credits['crew'][i] for i in range(min(10,len(credits['crew'])))]
        #tmdb['crew'] = [credits['crew'][i] for i in [0,1,2,3,4,5,6,7,8,9]]

        return tmdb
        #return json.dumps(tmdb, ensure_ascii=False)


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

