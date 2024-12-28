"""
fields = '"ArrNr", "starter", "Startformat", "startdato", "ArrTidspunkt", "ArrKunstner", "ArrGenre", "ArrUGenre", "AinfoNr", "ArrLangBeskriv", '
fields += '"ArrBeskrivelse", "BilledeUrl", "Filmvurdering", "Nautanb", "Nautanmeld", "Playdk", "Slutdato", "StedNavn"'

extraFields = '"kulthash", "tmdbId", "created", "updated_at", "binint"'
Arr =   {
    "AinfoNr": "7091081",
    "ArrBeskrivelse": "Russisk animeret eventyrfilm om Snedronningen, der ønsker en kold verden drænet for menneskelige følelser og søger at indhylle alt i is. Men troldmanden Vegards magiske spejle er en trussel mod disse planer",
    "ArrGenre": "Film",
    "ArrKunstner": "Snedronningen!",
    "ArrLangBeskriv": "",
    "ArrNr": 18208353,
    "ArrTidspunkt": "kl. 16",
    "ArrUGenre": "Tegnefilm/Animation",
    "BilledeUrl": "http://www.kultunaut.dk/images/film/7091081/plakat.jpg",
    "Filmvurdering": "f.u.7",
    "Nautanb": null,
    "Nautanmeld": null,
    "Playdk": null,
    "Slutdato": "2024-12-28",
    "Startdato": "2024-12-28",
    "StedNavn": "Svaneke Bio"
  }
"""
def jsonToDB():
    # SELECT group_concat(column_name) FROM information_schema.COLUMNS WHERE table_schema=DATABASE() AND TABLE_NAME='kult';
    fields = '"ArrNr", "starter", "Startformat", "startdato", "ArrTidspunkt", "ArrKunstner", "ArrGenre", "ArrUGenre", "AinfoNr", "ArrLangBeskriv", "ArrBeskrivelse", "BilledeUrl", "Filmvurdering", "Nautanb", "Nautanmeld", "Playdk", "Slutdato", "StedNavn", "kulthash", "tmdbId", "created", "updated_at", "binint"'
    arrObject = {'AinfoNr': '7091081', 'ArrBeskrivelse': 'Russisk animeret eventyrfilm om Snedronningen, der ønsker en kold verden drænet for menneskelige følelser og søger at indhylle alt i is. Men troldmanden Vegards magiske spejle er en trussel mod disse planer', 'ArrGenre': 'Film', 'ArrKunstner': 'Snedronningen!', 'ArrLangBeskriv': '', 'ArrNr': 18208353, 'ArrTidspunkt': 'kl. 16', 'ArrUGenre': 'Tegnefilm/Animation', 'BilledeUrl': 'http://www.kultunaut.dk/images/film/7091081/plakat.jpg', 'Filmvurdering': 'f.u.7', 'Nautanb': None, 'Nautanmeld': None, 'Playdk': None, 'Slutdato': '2024-12-28', 'Startdato': '2024-12-28', 'StedNavn': 'Svaneke Bio'}