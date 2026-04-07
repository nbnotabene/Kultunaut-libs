"""
EventsData: Sync Kultunaut API cache → arrsdata + eventsdata tables.

Fetches cached JSON events, decomposes into arrangement-level (arrsdata)
and event-level (eventsdata) records, enriches with TMDB metadata.
"""

import asyncio
import json
import requests
import hashlib
from datetime import datetime
from kultunaut.lib import lib
from kultunaut.lib.MariaDBInterface import MariaDBInterface
from kultunaut.lib import jsoncache


TMDBKEY = lib.conf['TMDBKEY']
TMDBBASE = lib.conf['TMDBBASE']
AINFOURL = lib.conf['AINFOURL']


def esc(val):
    """Escape a string value for SQL."""
    if val is None:
        return "NULL"
    return "'" + str(val).replace("\\", "\\\\").replace("'", "\\'") + "'"


def parse_time(tidspunkt_str):
    """Parse ArrTidspunkt string like 'kl. 19:45' → '19:45'."""
    if not tidspunkt_str:
        return "19:45"

    # Clean out "kl. " prefix
    parts = tidspunkt_str.split(" ")
    if len(parts) > 1:
        t = parts[1]
    elif len(parts) > 0:
        t = parts[0]
    else:
        t = ""

    if not t:
        return "19:45"

    # Handle ranges like "19-21" → just use start time
    if "-" in t:
        t = t.split("-")[0]

    # Normalize . to : (e.g., "19.45" → "19:45")
    t = t.replace(".", ":")

    # If no colon, assume it's just hours → add :00
    if ":" not in t:
        t = f"{t}:00"

    return t


def calc_kulthash(data_dict):
    """Calculate MD5 hash of dict values for change detection."""
    data_str = "".join(str(v) for v in data_dict.values())
    return hashlib.md5(data_str.encode()).hexdigest()


class EventsData:
    """Sync Kultunaut API cache → arrsdata + eventsdata tables.

    Enriches arrangement data with TMDB metadata.
    """

    def __init__(self):
        self._db = MariaDBInterface()
        self._tmdbkey = TMDBKEY
        self._tmdbbase = TMDBBASE
        self._ainfourl = AINFOURL
        self._kultfilm_cache = {}  # Cache kultfilm to avoid multiple API calls

    async def sync(self, forceUpdate=False):
        """Main entry point: fetch cache → parse → enrich TMDB → insert both tables."""
        print("\n=== EventsData Sync ===\n")

        # 1. Fetch JSON cache
        json_events = await jsoncache.fetch_jsoncache()
        print(f"Loaded {len(json_events)} events from cache")

        if not json_events:
            print("No events in cache, skipping sync")
            return

        # 2. Group by AinfoNr to identify unique arrangements
        ainfos = {}
        for json_event in json_events:
            ainfo = json_event.get("AinfoNr")
            if ainfo and ainfo not in ainfos:
                ainfos[ainfo] = json_event

        print(f"Identified {len(ainfos)} unique arrangements")

        # 3. Sync arrsdata (arrangement-level, one per AinfoNr)
        print("\n--- Syncing arrsdata ---")
        await self._sync_arrangements(ainfos, forceUpdate)

        # 4. Sync eventsdata (event-level, one per ArrNr)
        print("\n--- Syncing eventsdata ---")
        await self._sync_events(json_events, forceUpdate)

        # 5. Verify
        print("\n--- Verification ---")
        r1 = await self._db.fetchall("SELECT COUNT(*) FROM arrsdata")
        r2 = await self._db.fetchall("SELECT COUNT(*) FROM eventsdata")
        r3 = await self._db.fetchall("SELECT COUNT(*) FROM arrevent")
        print(f"arrsdata rows:        {r1[0][0]}")
        print(f"eventsdata rows:      {r2[0][0]}")
        print(f"arrevent (view) rows: {r3[0][0]}")

    async def _sync_arrangements(self, ainfos, forceUpdate=False):
        """Parse arrangement fields + TMDB enrichment → arrsdata INSERT/UPDATE."""
        inserted = 0
        updated = 0
        skipped = 0

        for ainfo, json_event in ainfos.items():
            ainfo = int(ainfo) if isinstance(ainfo, str) else ainfo

            try:
                # Extract arrangement-level fields from JSON
                arr_row = {
                    "AinfoNr": ainfo,
                    "ArrGenre": json_event.get("ArrGenre"),
                    "ArrKunstner": json_event.get("ArrKunstner") or "",
                    "ArrBeskrivelse": json_event.get("ArrBeskrivelse"),
                    "StedNavn": json_event.get("StedNavn"),
                    "ArrLangBeskriv": json_event.get("ArrLangBeskriv"),
                    "ArrUGenre": json_event.get("ArrUGenre"),
                    "BilledeUrl": json_event.get("BilledeUrl"),
                    "Filmvurdering": json_event.get("Filmvurdering"),
                    "Nautanb": json_event.get("Nautanb"),
                    "Nautanmeld": json_event.get("Nautanmeld"),
                    "Playdk": json_event.get("Playdk"),
                }

                # Fetch TMDB data
                tmdb_json = await self._fetch_tmdb_json(ainfo, json_event)

                # Calculate hash
                hash_data = {**arr_row}
                kulthash = calc_kulthash(hash_data)

                # Check existing record
                existing = await self._db.fetchOneDict(
                    f"SELECT * FROM arrsdata WHERE AinfoNr = {ainfo}"
                )

                # Determine action
                if existing is None:
                    # INSERT new
                    stmt = f"""INSERT INTO arrsdata
                        (AinfoNr, ArrGenre, ArrKunstner, ArrBeskrivelse, StedNavn,
                         ArrLangBeskriv, ArrUGenre, BilledeUrl, Filmvurdering,
                         Nautanb, Nautanmeld, Playdk, tmdb)
                        VALUES (
                            {ainfo},
                            {esc(arr_row["ArrGenre"])}, {esc(arr_row["ArrKunstner"])},
                            {esc(arr_row["ArrBeskrivelse"])}, {esc(arr_row["StedNavn"])},
                            {esc(arr_row["ArrLangBeskriv"])}, {esc(arr_row["ArrUGenre"])},
                            {esc(arr_row["BilledeUrl"])}, {esc(arr_row["Filmvurdering"])},
                            {esc(arr_row["Nautanb"])}, {esc(arr_row["Nautanmeld"])},
                            {esc(arr_row["Playdk"])}, {esc(tmdb_json)}
                        )"""
                    try:
                        await self._db.execute(stmt)
                        print(f"  INSERT arrsdata {ainfo}: {arr_row['ArrKunstner']}")
                        inserted += 1
                    except Exception as e:
                        print(f"  FAILED INSERT arrsdata {ainfo}: {e}")
                        skipped += 1

                elif forceUpdate or (kulthash != existing.get("kulthash")):
                    # UPDATE changed
                    stmt = f"""UPDATE arrsdata
                        SET ArrGenre = {esc(arr_row["ArrGenre"])},
                            ArrKunstner = {esc(arr_row["ArrKunstner"])},
                            ArrBeskrivelse = {esc(arr_row["ArrBeskrivelse"])},
                            StedNavn = {esc(arr_row["StedNavn"])},
                            ArrLangBeskriv = {esc(arr_row["ArrLangBeskriv"])},
                            ArrUGenre = {esc(arr_row["ArrUGenre"])},
                            BilledeUrl = {esc(arr_row["BilledeUrl"])},
                            Filmvurdering = {esc(arr_row["Filmvurdering"])},
                            Nautanb = {esc(arr_row["Nautanb"])},
                            Nautanmeld = {esc(arr_row["Nautanmeld"])},
                            Playdk = {esc(arr_row["Playdk"])},
                            tmdb = {esc(tmdb_json)}
                        WHERE AinfoNr = {ainfo}"""
                    try:
                        await self._db.execute(stmt)
                        print(f"  UPDATE arrsdata {ainfo}: {arr_row['ArrKunstner']}")
                        updated += 1
                    except Exception as e:
                        print(f"  FAILED UPDATE arrsdata {ainfo}: {e}")
                        skipped += 1

                else:
                    # No change
                    skipped += 1

            except Exception as e:
                print(f"  ERROR processing arrangement {ainfo}: {e}")
                skipped += 1

        print(f"arrsdata: {inserted} inserted, {updated} updated, {skipped} skipped/failed")

    async def _sync_events(self, json_events, forceUpdate=False):
        """Parse event fields (with combined ArrStart) → eventsdata INSERT/UPDATE."""
        inserted = 0
        updated = 0
        skipped = 0
        fk_errors = 0

        for json_event in json_events:
            arrnr = json_event.get("ArrNr")
            ainfo = json_event.get("AinfoNr")

            if not arrnr:
                print("  SKIP event: missing ArrNr")
                skipped += 1
                continue

            if ainfo is None:
                print(f"  SKIP event {arrnr}: AinfoNr is NULL")
                skipped += 1
                continue

            try:
                # Parse ArrStart = Startdato + ArrTidspunkt
                startdato = json_event.get("Startdato")
                tidspunkt = json_event.get("ArrTidspunkt", "19:45")

                if not startdato:
                    print(f"  SKIP event {arrnr}: missing Startdato")
                    skipped += 1
                    continue

                # Combine date + time
                time_str = parse_time(tidspunkt)
                arr_start_str = f"{startdato} {time_str}"

                try:
                    arr_start = datetime.strptime(arr_start_str, "%Y-%m-%d %H:%M")
                except ValueError as e:
                    print(f"  SKIP event {arrnr}: bad Starter format '{arr_start_str}': {e}")
                    skipped += 1
                    continue

                # Calculate hash
                hash_data = {
                    "ArrNr": arrnr,
                    "AinfoNr": ainfo,
                    "Startdato": startdato,
                    "ArrTidspunkt": tidspunkt,
                }
                kulthash = calc_kulthash(hash_data)

                # Check existing
                existing = await self._db.fetchOneDict(
                    f"SELECT * FROM eventsdata WHERE ArrNr = {arrnr}"
                )

                # Determine action
                if existing is None:
                    # INSERT new
                    stmt = f"""INSERT INTO eventsdata
                        (ArrNr, AinfoNr, ArrStart, kulthash)
                        VALUES (
                            {arrnr}, {ainfo},
                            '{arr_start.strftime('%Y-%m-%d %H:%M:%S')}',
                            {esc(kulthash)}
                        )"""
                    try:
                        await self._db.execute(stmt)
                        inserted += 1
                    except Exception as e:
                        error_str = str(e).lower()
                        if "foreign key" in error_str:
                            print(f"  FK ERROR event {arrnr}: AinfoNr {ainfo} not in arrsdata")
                            fk_errors += 1
                        else:
                            print(f"  FAILED INSERT event {arrnr}: {e}")
                            skipped += 1

                elif forceUpdate or (kulthash != existing.get("kulthash")):
                    # UPDATE changed
                    stmt = f"""UPDATE eventsdata
                        SET ArrStart = '{arr_start.strftime('%Y-%m-%d %H:%M:%S')}',
                            kulthash = {esc(kulthash)}
                        WHERE ArrNr = {arrnr}"""
                    try:
                        await self._db.execute(stmt)
                        updated += 1
                    except Exception as e:
                        print(f"  FAILED UPDATE event {arrnr}: {e}")
                        skipped += 1

                else:
                    # No change
                    skipped += 1

            except Exception as e:
                print(f"  ERROR processing event {arrnr}: {e}")
                skipped += 1

        print(f"eventsdata: {inserted} inserted, {updated} updated, {skipped} skipped, {fk_errors} FK errors")

    async def _fetch_tmdb_json(self, ainfo, json_event):
        """Fetch & enrich with TMDB metadata. Returns JSON string or None."""
        try:
            # Check if AinfoNr != ArrNr (indicates it's a real film, not a singleton event)
            arrnr = json_event.get("ArrNr")
            if ainfo == arrnr:
                # Singleton event, no separate film record in Kultunaut
                return None

            # Fetch kultfilm data from Kultunaut AINFO API
            kultfilm = await self._fetch_kultfilm(ainfo)
            if not kultfilm:
                return None

            # Extract IMDB ID and map to TMDB
            imdb_id = kultfilm.get("Imdb")
            if not imdb_id:
                return None

            tmdb_id = await self._get_tmdb_id(imdb_id)
            if not tmdb_id:
                return None

            # Fetch full TMDB data
            tmdb_data = await self._get_tmdb_info(tmdb_id)
            if not tmdb_data:
                return None

            # Validate and return as JSON string
            tmdb_json_str = json.dumps(tmdb_data, ensure_ascii=False)
            try:
                json.loads(tmdb_json_str)  # Validate JSON
                return tmdb_json_str
            except json.JSONDecodeError:
                print(f"  WARN: invalid TMDB JSON for ainfo {ainfo}, skipping")
                return None

        except Exception as e:
            # Log but don't fail the sync
            print(f"  WARN: could not fetch TMDB for ainfo {ainfo}: {e}")
            return None

    async def _fetch_kultfilm(self, ainfo):
        """Fetch film details from Kultunaut AINFO API."""
        try:
            if ainfo in self._kultfilm_cache:
                return self._kultfilm_cache[ainfo]

            url = f"{self._ainfourl}?AinfoNr={ainfo}"
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                return None

            data = json.loads(response.text)
            if not data.get("film") or data["film"] == {}:
                return None

            film = data["film"].get(str(ainfo))
            if film:
                self._kultfilm_cache[ainfo] = film
            return film

        except Exception as e:
            print(f"  WARN: kultfilm API error for ainfo {ainfo}: {e}")
            return None

    async def _get_tmdb_id(self, imdb_id):
        """Map IMDB ID to TMDB ID via TMDB find endpoint."""
        try:
            url = f"{self._tmdbbase}/find/tt{imdb_id}?api_key={self._tmdbkey}&external_source=imdb_id"
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                return None

            data = json.loads(response.text)
            results = data.get("movie_results", [])
            if results:
                return results[0]["id"]
            return None

        except Exception as e:
            print(f"  WARN: TMDB find error for IMDB {imdb_id}: {e}")
            return None

    async def _get_tmdb_info(self, tmdb_id):
        """Fetch full TMDB movie info (details + videos + cast + crew)."""
        try:
            info = {}

            # 1. Main movie data
            url = f"{self._tmdbbase}/movie/{tmdb_id}?api_key={self._tmdbkey}&language=da"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                info = json.loads(response.text)
            else:
                return None

            # 2. Videos
            url = f"{self._tmdbbase}/movie/{tmdb_id}/videos?api_key={self._tmdbkey}&language=da"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                videos = json.loads(response.text)
                if videos.get("results"):
                    info["videoid"] = videos["results"][0]["key"]

            # 3. Credits (cast + crew)
            url = f"{self._tmdbbase}/movie/{tmdb_id}/credits?api_key={self._tmdbkey}&language=da"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                credits = json.loads(response.text)
                # Limit to top 10
                cast = credits.get("cast", [])
                info["casted"] = [c for c in cast if c.get("order", 999) < 10][:10]

                crew = credits.get("crew", [])
                info["crew"] = crew[:10]

            return info

        except Exception as e:
            print(f"  WARN: TMDB info error for ID {tmdb_id}: {e}")
            return None

    async def fetch_fresh(self):
        """Fetch fresh data from Kultunaut API (delegates to jsoncache)."""
        return await jsoncache.fetch_from_kult()

    async def lock_event(self, arrnr, reason=""):
        """Lock event to prevent accidental overwrites during sync."""
        stmt = f"UPDATE eventsdata SET is_locked = TRUE WHERE ArrNr = {arrnr}"
        await self._db.execute(stmt)
        print(f"LOCKED event {arrnr}" + (f": {reason}" if reason else ""))

    async def unlock_event(self, arrnr):
        """Unlock event to allow sync overwrites."""
        stmt = f"UPDATE eventsdata SET is_locked = FALSE WHERE ArrNr = {arrnr}"
        await self._db.execute(stmt)
        print(f"UNLOCKED event {arrnr}")

    async def get_locked_events(self):
        """Query all locked events."""
        return await self._db.fetchDict("SELECT ArrNr, ArrStart FROM eventsdata WHERE is_locked = TRUE")


async def main():
    """Test sync."""
    ed = EventsData()
    await ed.sync(forceUpdate=False)


if __name__ == "__main__":
    asyncio.run(main())
