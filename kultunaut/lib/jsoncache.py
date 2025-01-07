import requests
import json
import os
import datetime
import asyncio
from kultunaut.lib import lib

#from dotenv import load_dotenv
#load_dotenv()


def doc():
  return """
    fetch_jsoncache
    fetch_from_kult
  """

#url = 'http://www.kultunaut.dk/perl/export/cassiopeia.json'
filename = "sb.json"
pathToCache='filecache/'

async def fetch_jsoncache():
    try:
        filePath = os.path.join(pathToCache, filename)
        if os.path.exists(filePath):
            with open(filePath, 'r') as f:
                data = json.load(f)
                return data
        else:
          print(f"Error fetching data from json-file")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from json-file: {e}")

async def fetch_from_kult():
    """Fetch and save a JSON file from Kultunaut.
    """
    try:
        KULTURL = lib.conf["KULTURL"]
        response =  requests.get(KULTURL)
        response.raise_for_status()  # Raise an exception for error HTTP statuses
        dontdump=True
        new_data = response.json()
        newfilePath = os.path.join(pathToCache, filename)
        # Check if file exists and if the content has changed
        
        if not os.path.exists(newfilePath):
            dontdump=False
            old_data=""
            if not os.path.exists(pathToCache): os.makedirs(pathToCache) 
        else:
            with open(newfilePath, 'r') as f:
                old_data = json.load(f)
            dontdump = (new_data == old_data)
                        
        if not dontdump:
            if os.path.exists(newfilePath):
                #BACKUP:move newfilePath to  oldfilePath 
                yearPath = os.path.join(pathToCache, datetime.date.today().strftime("%Y"))
                if not os.path.exists(yearPath): os.makedirs(yearPath)
                old_filename = f'{yearPath}/{datetime.date.today().strftime("%V")}.json'
                
                if not os.path.exists(old_filename):
                    os.rename(newfilePath, old_filename)
                else: #OVERWRITE?
                    with open(old_filename, 'r') as f: very_old_data = json.load(f)
                    if (very_old_data != old_data):
                        with open(old_filename, 'w') as f: json.dump(old_data, f, indent=2, ensure_ascii=False)

            with open(newfilePath, 'w') as f:
                json.dump(new_data, f, indent=2, ensure_ascii=False)
            print(f"Kultunaut data fetched and stored in {newfilePath}")
            return new_data

        # Manage old files
        #today = datetime.date.today()
        #week_start = today - datetime.timedelta(days=today.weekday())
        #week_dir = f"week_{week_start.strftime('%Y_%W')}"
        #if not os.path.exists(week_dir):
        #    os.makedirs(week_dir)
        #old_filename = os.path.join(week_dir, filename)
        #os.rename(filename, old_filename)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

# Example usage:

# Set up a cron job to run this script twice a day
# For example, using crontab:
# 0 0,12 * * * python /path/to/your/script.py

if __name__ == "__main__":
  #fetch_from_kult()
  print(lib.conf["KULTURL"])
  print(f"ArrNr: {fetch_jsoncache()[0]['ArrNr']}")    