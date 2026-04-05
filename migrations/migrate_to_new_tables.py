"""
Migration: kultevents → eventsdata, kultarrs → arrsdata

Strategy:
- arrsdata (one row per AinfoNr):
    text fields come from kultevents.kjson (first event for that AinfoNr)
    tmdb + kulthash come from kultarrs where available
- eventsdata (one row per ArrNr):
    ArrStart parsed from kjson["Starter"] ("YYYY-MM-DD H:MM")
    kulthash from kultevents.kulthash
    extra = null (available for future use)
"""

import asyncio
import json
from datetime import datetime
from kultunaut.lib.MariaDBInterface import MariaDBInterface


def parse_starter(starter_str):
    """Parse Starter strings like '2026-01-12 9:00' or '2024-12-27 19:45'."""
    return datetime.strptime(starter_str, "%Y-%m-%d %H:%M")


def esc(val):
    """Escape a string value for SQL."""
    if val is None:
        return "NULL"
    return "'" + str(val).replace("\\", "\\\\").replace("'", "\\'") + "'"


async def migrate():
    db = MariaDBInterface()
    if not db.testConn:
        print("DB connection failed")
        return

    # ------------------------------------------------------------------ #
    # 1. Load all data from kultevents
    # ------------------------------------------------------------------ #
    ev_rows = await db.fetchDict("SELECT ArrNr, AinfoNr, kulthash, kjson FROM kultevents ORDER BY ArrNr")
    print(f"kultevents rows: {len(ev_rows)}")

    # Build: AinfoNr → first kultevents row (for arrsdata text fields)
    ainfo_first_event = {}
    for row in ev_rows:
        ainfo = row["AinfoNr"]
        if ainfo is not None and ainfo not in ainfo_first_event:
            ainfo_first_event[ainfo] = row

    # ------------------------------------------------------------------ #
    # 2. Load kultarrs
    # ------------------------------------------------------------------ #
    arr_rows = await db.fetchDict("SELECT AinfoNr, kulthash, tmdb FROM kultarrs")
    print(f"kultarrs rows: {len(arr_rows)}")
    arr_by_ainfo = {r["AinfoNr"]: r for r in arr_rows}

    # ------------------------------------------------------------------ #
    # 3. Collect all unique AinfoNr values
    # ------------------------------------------------------------------ #
    all_ainfos = set(ainfo_first_event.keys()) | set(arr_by_ainfo.keys())
    print(f"Unique AinfoNr to migrate: {len(all_ainfos)}")

    # ------------------------------------------------------------------ #
    # 4. INSERT into arrsdata
    # ------------------------------------------------------------------ #
    print("\n--- Migrating arrsdata ---")
    inserted_arrs = 0
    skipped_arrs = 0

    for ainfo in sorted(all_ainfos):
        ev = ainfo_first_event.get(ainfo)
        arr = arr_by_ainfo.get(ainfo)

        if ev is None:
            print(f"  SKIP arrsdata {ainfo}: no kultevents row found")
            skipped_arrs += 1
            continue

        j = json.loads(ev["kjson"])

        ArrGenre       = j.get("ArrGenre")
        ArrKunstner    = j.get("ArrKunstner") or ""
        ArrBeskrivelse = j.get("ArrBeskrivelse")
        StedNavn       = j.get("StedNavn")
        ArrLangBeskriv = j.get("ArrLangBeskriv")
        ArrUGenre      = j.get("ArrUGenre")
        BilledeUrl     = j.get("BilledeUrl")
        Filmvurdering  = j.get("Filmvurdering")
        Nautanb        = j.get("Nautanb")
        Nautanmeld     = j.get("Nautanmeld")
        Playdk         = j.get("Playdk")

        tmdb = arr["tmdb"] if arr else None

        stmt = f"""INSERT INTO arrsdata
            (AinfoNr, ArrGenre, ArrKunstner, ArrBeskrivelse, StedNavn,
             ArrLangBeskriv, ArrUGenre, BilledeUrl, Filmvurdering,
             Nautanb, Nautanmeld, Playdk, tmdb)
            VALUES (
                {ainfo},
                {esc(ArrGenre)}, {esc(ArrKunstner)}, {esc(ArrBeskrivelse)}, {esc(StedNavn)},
                {esc(ArrLangBeskriv)}, {esc(ArrUGenre)}, {esc(BilledeUrl)}, {esc(Filmvurdering)},
                {esc(Nautanb)}, {esc(Nautanmeld)}, {esc(Playdk)},
                {esc(tmdb)}
            )"""
        result = await db.execute(stmt)
        if result:
            print(f"  INSERT arrsdata {ainfo}: {ArrKunstner}")
            inserted_arrs += 1
        else:
            print(f"  FAILED arrsdata {ainfo}: {ArrKunstner}")
            skipped_arrs += 1

    print(f"arrsdata: {inserted_arrs} inserted, {skipped_arrs} skipped/failed")

    # ------------------------------------------------------------------ #
    # 5. INSERT into eventsdata
    # ------------------------------------------------------------------ #
    print("\n--- Migrating eventsdata ---")
    inserted_evs = 0
    skipped_evs = 0

    for row in ev_rows:
        ArrNr   = row["ArrNr"]
        AinfoNr = row["AinfoNr"]

        if AinfoNr is None:
            print(f"  SKIP event {ArrNr}: AinfoNr is NULL")
            skipped_evs += 1
            continue

        j = json.loads(row["kjson"])
        starter_str = j.get("Starter")
        if not starter_str:
            print(f"  SKIP event {ArrNr}: no Starter in kjson")
            skipped_evs += 1
            continue

        try:
            arr_start = parse_starter(starter_str)
        except ValueError as e:
            print(f"  SKIP event {ArrNr}: cannot parse Starter '{starter_str}': {e}")
            skipped_evs += 1
            continue

        kulthash = row["kulthash"]

        stmt = f"""INSERT INTO eventsdata (ArrNr, AinfoNr, ArrStart, kulthash)
            VALUES ({ArrNr}, {AinfoNr}, '{arr_start.strftime('%Y-%m-%d %H:%M:%S')}', {esc(kulthash)})"""
        result = await db.execute(stmt)
        if result:
            inserted_evs += 1
        else:
            print(f"  FAILED event {ArrNr}")
            skipped_evs += 1

    print(f"eventsdata: {inserted_evs} inserted, {skipped_evs} skipped/failed")

    # ------------------------------------------------------------------ #
    # 6. Verify
    # ------------------------------------------------------------------ #
    print("\n--- Verification ---")
    r1 = await db.fetchall("SELECT COUNT(*) FROM arrsdata")
    r2 = await db.fetchall("SELECT COUNT(*) FROM eventsdata")
    r3 = await db.fetchall("SELECT COUNT(*) FROM arrevent")
    print(f"arrsdata rows:  {r1[0][0]}")
    print(f"eventsdata rows: {r2[0][0]}")
    print(f"arrevent (view) rows: {r3[0][0]}")


if __name__ == "__main__":
    asyncio.run(migrate())
