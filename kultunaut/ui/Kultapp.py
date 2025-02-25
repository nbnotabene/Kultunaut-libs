# -*- coding: utf-8 -*-
# from cls.env import *
from cls.Database import Database
from cls.ArrEvents import ArrEvents
# from cls.Arrcoll import Arrcoll
# from cls.Arr import Arr
from cls.Sted import Sted


class Kultapp():
    def __init__(self, sysconf):
        # storage_service = DBHandler(SQFile)
        self.sysconf = sysconf
        # self.__db = storage_service
        self.__db = Database()
        # self.__db.connect()
        # self.__arrColl = Arrcoll()
        self.__arrEvents = ArrEvents(self.__db, self.sysconf)
        # includes reference to kultapp for sysconf
        self.__Sted = Sted(self.__db, self)

    # def eventsFromDB(self):
    #    dbevents = self.__db.select("select * from kult where start>'2024-01-15' order by start")
    #    #print("SELECT Result:", dbevents)
    #    for dbe in dbevents:
    #        self.__arrEvents.add_event(Event(dbe))
    #    #print("")
    #    pass

    def pagesFromDB(self):
        # dbPages = self.__db.select("select * from pages")
        dbPages = self.__db.fetch_dicts("select * from pages")
        for data in dbPages:
            data['relativeUrl'] = '../'
            output_file_path = f"{self.sysconf['webroot']}/pages/{data['fname']}"
            self.__arrEvents.jinja.render_templates(
                'page.html', data, output_file_path)

    # def generatePages(self):
    #    pagehtml="""
    #    <div class="omtext">
    #        <p> Svaneke Bio har for nylig fået et nyt, stort og avanceret højtalersystem (et "surround-anlæg med Dolby 7.1").
    #        Lydanlæget er en stor forbedring af film-oplevelsen. </p>
    #        <p></p>
    #        <p> Samtidig har biografen fået et teleslynge.<br><a target="_new" title="Høreforeningen: Om teleslynge"
    #            href="https://hoereforeningen.dk/viden-om/hjaelpemidler/teleslynge/">Læs mere om teleslynge</a>. </p>
    #        <p><b>Kender DU nogen med høreproblemer?</b> - så kan du jo sikre dig at de også kender mulighederne i Svaneke Bio!</p>
    #    </div>
    #    """
    #    #"relativeUrl":"../",
    #    data= {
    #        "fname": "lyd.html",
    #        "img":"megafon.png",
    #        "title":"Lyt til filmen - i Svaneke Bio",
    #        "pagehtml":pagehtml
    #    }
    #    output_file_path = f"{self.sysconf['webroot']}/pages/{data['fname']}"
    #    self.__arrEvents.jinja.render_templates('page.html',data,output_file_path)

    def hentKultunaut(self, fromCache=True):
        # BACKEND
        # Hent fra cache / eller kultunaut
        json = self.__Sted._hentKultunaut(fromCache)
        # og opdater DB
        self.__Sted.updateDB(json)
        return json

    # def updateDB(self,fromCache=True):
    #    json = self.__Sted._hentKultunaut(fromCache)
    #    self.__Sted.updateDB(json)
    #    #return json

    def loadFromDB(self):
        # CREATE UI Frontend
        # storage_service = DBHandler("/home/nb/proj/bio_sqlite/backend/db/kult.db")
        # application = Bioapp(storage_service)
        # self.eventsFromDB()
        # self.__arrEvents.loadFromDB('2024-03-15', '2024-04-15')
        self.__arrEvents.loadFromDB()
        self.__arrEvents.toHTML()

        # self.__arrEvents.loadFromDB() #Defaults
        # print("Get events:")
        # print(self.__arrEvents.get_all_events())
        # print("Get arrangementer:")
        # arrs = self.__arrEvents.get_arrColl()
        # print(self.__arrEvents.toJSON())
        # self.__arrEvents.toHTML()
        #
        # print(self.__arrEvents.to_json())
#
        # for key in arrs:
        #    print(key)
        #    myarr = arrs[key]
        #    #print(myarr._tmdb())
        #    print(f"AinfoNr: {myarr.AinfoNr}")
        #    #print(f"proplist: {myarr.proplist}")
        #    #myarr.createHTML()
        #    print(f"Title: {arrs[key]}")
        #    for start in arrs[key].startarr:
        #        print(f"    {start}")

        # print("\nGet Arr 7104068:")
        # arr = self.__arrEvents.get_Arrang(7104068)
        # print(arr)

        # events = [event.start for event in self.__arrEvents]
        # print(events)

        # b1 = Arr(1, "The Life of Python")
        # b2 = Arr(2,"The Old Man and the C")
        # b3 = Arr(3,"A Good Cup of Java")
        # arrColl = Arrcoll()
        # self.__arrColl.add_arr(b1)
        # self.__arrColl.add_arr(b2)
        # self.__arrColl.add_arr(b3)
        # self.__arrColl.add_arr(Arr(4,"NBNB"))
        # Create a list containing the names of all arrs
        # arr_names = [arr.name for arr in self.__arrColl]
        # print(arr_names)

    def test(self):
        # json = self.__Sted._hentKult()
        # print(json)
        self.__arrEvents.loadFromDB()  # Defaults
        events = [event.start for event in self.__arrEvents]
        print(events)
