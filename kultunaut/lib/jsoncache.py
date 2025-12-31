import requests
import json
import os
import datetime

# import asyncio
from kultunaut.lib import lib

# from dotenv import load_dotenv
# load_dotenv()


def doc():
    return """
    fetch_jsoncache
    fetch_from_kult
  """


# url = 'http://www.kultunaut.dk/perl/export/cassiopeia.json'
filename = "sb.json"
pathToCache = "filecache/"


async def fetch_jsoncache():
    try:
        xtra = [
            {
                "AinfoNr": "1000",
                "ArrBeskrivelse": "",
                "ArrGenre": "Film",
                "ArrKunstner": "Svaneke Friskole",
                "ArrLangBeskriv": "<h3>Mord på Alpehotellet!</h3><p>Fra d. 12. - 30. januar er der liv og glade dage i FREM!</p><p>Svaneke Friskoles 5. + 6. klasse flytter al undervisning fra skolen og indtager kulturhuset FREM, for at sætte årets musical op.</p><p>Et hotel i bjergene, en lavine lukker bjergpasset, der sker et mord, ingen kan slippe væk - alle er mistænkt! En krimi i bedste Agatha Christie stil.</p><p>Musicalen skrives hvert år særligt til den gruppe børn, der skal være med, og fra august er alle musik og billedkunsttimer omlagt til performancetimer. Der skabes scenografi, plakater, kostumer og rekvisitter. Der øves drama, musik og sang, så alle er klar til at indtage FREM efter nytår. Forældre, børn og lærere har syet, designet, limet, malet og bygget i en hel weekend inden d. 12., for at skabe det, der i år danner rammen om krimien “Mord på Alpehotellet”.</p><p>Link til bestilling af billetter lægges på SVANEKE siden på Facebook 14 dage før forestillingerne.</p><ul>Forestillinger:<li>Tirsdag d. 27. januar kl. 17.00</li><li>Onsdag d. 28. januar kl. 17.00</li><li>Torsdag d. 29 januar kl. 17.00 </li></ul>",
                "ArrNr": 1000,
                "ArrTidspunkt": "kl. 9:00",
                "ArrUGenre": "Andet",
                "BilledeUrl": "https://local.svanekebio.dk/div/svanekefriskole2.jpg",
                "Filmvurdering": "",
                "Slutdato": "2026-01-12",
                "Startdato": "2026-01-12",
                "StedNavn": "Svaneke Bio",
            },
            {
                "AinfoNr": "1001",
                "ArrBeskrivelse": "",
                "ArrGenre": "Film",
                "ArrKunstner": "Svaneke Friskole",
                "ArrLangBeskriv": "<h3>Mord på Alpehotellet!</h3><p>Fra d. 12. - 30. januar er der liv og glade dage i FREM!</p><p>Svaneke Friskoles 5. + 6. klasse flytter al undervisning fra skolen og indtager kulturhuset FREM, for at sætte årets musical op.</p><p>Et hotel i bjergene, en lavine lukker bjergpasset, der sker et mord, ingen kan slippe væk - alle er mistænkt! En krimi i bedste Agatha Christie stil.</p><p>Musicalen skrives hvert år særligt til den gruppe børn, der skal være med, og fra august er alle musik og billedkunsttimer omlagt til performancetimer. Der skabes scenografi, plakater, kostumer og rekvisitter. Der øves drama, musik og sang, så alle er klar til at indtage FREM efter nytår. Forældre, børn og lærere har syet, designet, limet, malet og bygget i en hel weekend inden d. 12., for at skabe det, der i år danner rammen om krimien “Mord på Alpehotellet”.</p><p>Link til bestilling af billetter lægges på SVANEKE siden på Facebook 14 dage før forestillingerne.</p><ul>Forestillinger:<li>Tirsdag d. 27. januar kl. 17.00</li><li>Onsdag d. 28. januar kl. 17.00</li><li>Torsdag d. 29 januar kl. 17.00 </li></ul>",
                "ArrNr": 1001,
                "ArrTidspunkt": "kl. 9:00",
                "ArrUGenre": "Andet",
                "BilledeUrl": "https://local.svanekebio.dk/div/svanekefriskole2.jpg",
                "Filmvurdering": "",
                "Slutdato": "2026-01-19",
                "Startdato": "2026-01-19",
                "StedNavn": "Svaneke Bio",
            },
            {
                "AinfoNr": "1003",
                "ArrBeskrivelse": "",
                "ArrGenre": "Film",
                "ArrKunstner": "Svaneke Friskole",
                "ArrLangBeskriv": "<h3>Mord på Alpehotellet!</h3><p>Fra d. 12. - 30. januar er der liv og glade dage i FREM!</p><p>Svaneke Friskoles 5. + 6. klasse flytter al undervisning fra skolen og indtager kulturhuset FREM, for at sætte årets musical op.</p><p>Et hotel i bjergene, en lavine lukker bjergpasset, der sker et mord, ingen kan slippe væk - alle er mistænkt! En krimi i bedste Agatha Christie stil.</p><p>Musicalen skrives hvert år særligt til den gruppe børn, der skal være med, og fra august er alle musik og billedkunsttimer omlagt til performancetimer. Der skabes scenografi, plakater, kostumer og rekvisitter. Der øves drama, musik og sang, så alle er klar til at indtage FREM efter nytår. Forældre, børn og lærere har syet, designet, limet, malet og bygget i en hel weekend inden d. 12., for at skabe det, der i år danner rammen om krimien “Mord på Alpehotellet”.</p><p>Link til bestilling af billetter lægges på SVANEKE siden på Facebook 14 dage før forestillingerne.</p><ul>Forestillinger:<li>Tirsdag d. 27. januar kl. 17.00</li><li>Onsdag d. 28. januar kl. 17.00</li><li>Torsdag d. 29 januar kl. 17.00 </li></ul>",
                "ArrNr": 1003,
                "ArrTidspunkt": "kl. 9:00",
                "ArrUGenre": "Andet",
                "BilledeUrl": "https://local.svanekebio.dk/div/svanekefriskole2.jpg",
                "Filmvurdering": "",
                "Slutdato": "2026-01-26",
                "Startdato": "2026-01-26",
                "StedNavn": "Svaneke Bio",
            },
        ]
        filePath = os.path.join(pathToCache, filename)
        if os.path.exists(filePath):
            with open(filePath, "r") as f:
                data = json.load(f)
                ## XTRA ###
                data.extend(xtra)
                return data
        else:
            print(f"{filePath} not found")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from json-file: {e}")


async def fetch_from_kult():
    """Fetch and save a JSON file from Kultunaut."""
    try:
        KULTURL = lib.conf["KULTURL"]
        response = requests.get(KULTURL)
        response.raise_for_status()  # Raise an exception for error HTTP statuses
        dontdump = True
        new_data = response.json()
        newfilePath = os.path.join(pathToCache, filename)
        # Check if file exists and if the content has changed

        if not os.path.exists(newfilePath):
            dontdump = False
            old_data = ""
            if not os.path.exists(pathToCache):
                os.makedirs(pathToCache)
        else:
            with open(newfilePath, "r") as f:
                old_data = json.load(f)
            dontdump = new_data == old_data

        if not dontdump:
            if os.path.exists(newfilePath):
                # BACKUP:move newfilePath to  oldfilePath
                yearPath = os.path.join(
                    pathToCache, datetime.date.today().strftime("%Y")
                )
                if not os.path.exists(yearPath):
                    os.makedirs(yearPath)
                old_filename = f"{yearPath}/{datetime.date.today().strftime('%V')}.json"

                if not os.path.exists(old_filename):
                    os.rename(newfilePath, old_filename)
                else:  # OVERWRITE?
                    with open(old_filename, "r") as f:
                        very_old_data = json.load(f)
                    if very_old_data != old_data:
                        with open(old_filename, "w") as f:
                            json.dump(old_data, f, indent=2, ensure_ascii=False)

            with open(newfilePath, "w") as f:
                json.dump(new_data, f, indent=2, ensure_ascii=False)
            print(f"Kultunaut data fetched and stored in {newfilePath}")
            return new_data
        else:
            print(f"{newfilePath}: No changes in fileCache")

        # Manage old files
        # today = datetime.date.today()
        # week_start = today - datetime.timedelta(days=today.weekday())
        # week_dir = f"week_{week_start.strftime('%Y_%W')}"
        # if not os.path.exists(week_dir):
        #    os.makedirs(week_dir)
        # old_filename = os.path.join(week_dir, filename)
        # os.rename(filename, old_filename)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")


# Example usage:

# Set up a cron job to run this script twice a day
# For example, using crontab:
# 0 0,12 * * * python /path/to/your/script.py

if __name__ == "__main__":
    # fetch_from_kult()
    print(lib.conf["KULTURL"])
    print(f"ArrNr: {fetch_jsoncache()[0]['ArrNr']}")
