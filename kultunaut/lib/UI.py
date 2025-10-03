from kultunaut.lib.MariaDBInterface import MariaDBInterface
from kultunaut.lib.JinjaRenderer import JinjaRenderer
from kultunaut.lib.PosterImage import PosterImage
import asyncio
import json
import os
from dotenv import dotenv_values
conf = {**dotenv_values(".env"),**dotenv_values(".env.secret")}
#from kultunaut.lib import lib

ROOTDIR = f"{conf['ROOTDIR']}"    #/home/nb/repos/kultunaut/kultunaut-libs"
WEBROOT = f"{ROOTDIR}/{conf['WEBROOT']}"
TEMPLATES = f"{ROOTDIR}/{conf['TEMPLATES']}"


# metaclass=lib.Singleton
class UI():
    """
    """

    def __init__(self):
        self._db = MariaDBInterface()
        # self._type=type
        self.jinja = JinjaRenderer(TEMPLATES)
        self.output_dir = WEBROOT
        #self.getEvents()
        
    async def getEvents(self):    
        self.dbEvents= await self._db.fetchDict("select * from curArrs where mstart > now()")
        
    async def pagesFromDB(self):
        # dbPages = self.__db.select("select * from pages")
        dbPages = await self._db.fetchDict("select * from pages")
        for data in dbPages:
            data['relativeUrl'] = '../'
            output_file_path = f"{WEBROOT}/pages/{data['fname']}"
            #self.__arrEvents.jinja.render_templates(
            self.jinja.render_templates('page.html', data, output_file_path)

    #async def eventsToHTML(self):
    #    eventsdb = await self._db.fetchDict("select * from pages")e

    async def createArrFolders(self):
        for arr in self.dbEvents:
            if arr['AinfoNr'] == 7092924:
                print (7092924)
            newFolder = f"{WEBROOT}/arr/{arr['AinfoNr']}"
            os.makedirs(newFolder,exist_ok=True)
            kjson = json.loads(arr['ekjson'])   #json.loads(arr['Kjson'])
            PosterImage(newFolder,kjson['BilledeUrl'])
            
            data = kjson        
            data['relativeUrl'] = "../../"
            
            startArr=[]
            starterA=arr['arrstarter'].split(',')
            startformatA=arr['startformat'].split(',')
            #arrNrA = arr['arrnums'].split(',')
            for i,eventnr in enumerate(arr['arrnums'].split(',')):
                #startArr.append([int(eventnr), starterA[i], startformatA[i],'00000000'])
                startArr.append([int(eventnr), starterA[i], startformatA[i]])
            data['startdatoer'] = startArr
            if arr['tmdb'] is None:
                data['tmdb'] =''                
            else:
                try:
                    jsonObj = json.loads(arr['tmdb'])
                except(json.decoder.JSONDecodeError):
                    jsonObj = '{error: "JSONDecodeError", errormsg: "Could not decode JSON"}'               
                data['tmdb'] = jsonObj
                
            
            f = open(f"{newFolder}/arrdata.json", "w", encoding="utf_8")
            f.write(json.dumps(data, ensure_ascii=False))
            f.close()
            
            
            f = open(f"{newFolder}/tmdb.json", "w", encoding="utf_8")
            f.write(json.dumps(arr['tmdb'], ensure_ascii=False))
            f.close()
            
            #output_file_path = f"{newFolder}/index.html"
            self.jinja.render_templates('arr.html', data, f"{newFolder}/index.html")
            print(f"Oprettet: {kjson['AinfoNr']}")
            
            
            


    async def createIndex(self):
        #data = self.get_all_events()
        #data = self.dbEvents
        #self.dbEvents['relativeUrl']="./"
        #data['list'] = list(self._arrColl)
        #data['events'] = self.get_all_events()
        #data = jsonpickle.encode(self._events, unpicklable=False)
        #data = self._events.values()
        #[17386703: 2024-03-16 19:45 Den grænseløse, .....

        info_message = (
           "Har du lyst til at være støtte-medlem? "
           "Eller vælge din favoritfilm til visning i biografen? Check <a href='/pages/medlem.html'>dette link</a>"
           )
        data={ 
            'info_message': info_message,
            'relativeUrl': './',
            'events': list(self.dbEvents)
        }
        
        output_file_path = f"{self.output_dir}/index.html"
        self.jinja.render_templates('index.html',data,output_file_path)




async def main():
    myUI = UI()
    await myUI.getEvents()
    await myUI.pagesFromDB()
    await myUI.createArrFolders()
    await myUI.createIndex()

if __name__ == "__main__":
    asyncio.run(main())
