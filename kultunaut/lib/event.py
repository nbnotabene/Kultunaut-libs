from datetime import datetime
import locale
import re
import hashlib
import json


# from collections.abc import MutableMapping #Interface
# from kultunaut.lib import lib
# from kultunaut.lib.arrangments import Arrangements
class Event:
    """Class for keeping track of one event."""

    def __init__(self, jevent: dict, db_interface=None, parent=None):
        self._event = jevent
        self._db = db_interface  # New: direct DB interface
        self.parent = parent  # Legacy: kept for backward compatibility
        locale.setlocale(locale.LC_ALL, 'da_DK.utf8')        

    def __str__(self):
        return f"Event: {self._event['ArrNr']} / {self._event['AinfoNr']}, {self._event['Starter']} {self._event['ArrKunstner']}"

    async def updateJSONvalues(self):
        # kulthash - before values are changed
        eventStr = "".join(str(v) for v in self._event.values())
        self._event["kulthash"] = hashlib.md5(eventStr.encode()).hexdigest()

        # if 'starter' not in self._event.keys():
        self._event["Starter"] = self._event["Startdato"] + " " + self.getTime()
        self._event["Startformat"] = (
            datetime.strptime(self._event["Starter"], "%Y-%m-%d %H:%M").strftime("%a. d. %-d/%-m")
            + " "
            + self._event["ArrTidspunkt"]
        )

        #AinfoNr
        if self._event["AinfoNr"] is None:
            db = self._db if self._db else (self.parent._db if self.parent else None)
            if db:
                Ainfo = await db.fetchOneDict(f"select AinfoNr from kultevents where vTitle like '{self._event['ArrKunstner']}' order by ArrNr desc") 
                if Ainfo is not None:
                    self._event["AinfoNr"] = Ainfo["AinfoNr"]
                else:
                    self._event["AinfoNr"] = self._event["ArrNr"]
            else:
                self._event["AinfoNr"] = self._event["ArrNr"]

        # Aarhus universitet
        tmpA = self._event["ArrKunstner"].split(
            " (via livestream fra Aarhus Universitet)"
        )
        self._event["ArrKunstner"] = tmpA[0]
        if len(tmpA) > 1:
            self._event["ArrBeskrivelse"] = (
                f"{self._event['ArrBeskrivelse']}</br>(via livestream fra Aarhus Universitet)"
            )

        for largeVal in ["ArrBeskrivelse", "ArrLangBeskriv", "ArrKunstner"]:
            self._event[largeVal] = self._event[largeVal].replace("'", "´")
            self._event[largeVal] = self._event[largeVal].replace('"', '\\"')

    async def dbUpsert(self, db_interface=None, eventDbDict=None, forceUpdate=False):
        """Upsert event to database. Respects locks - skips update if locked."""
        db = db_interface or self._db or (self.parent._db if self.parent else None)
        if not db:
            raise ValueError("No database interface provided to dbUpsert")
        
        await self.updateJSONvalues()
        
        # Check if event is locked - if so, skip update
        if eventDbDict and eventDbDict.get('is_locked'):
            print(f"LOCKED: {str(self)} - skipping upsert")
            return
        
        # INSERT or UPDATE
        if eventDbDict is None or len(eventDbDict) == 0:
            # INSERT
            print(f"INSERT: {str(self)}")
            _eventStr = json.dumps(self._event, ensure_ascii=False)
            myStatement = f"insert into kultevents (ArrNr, kulthash, kjson, AinfoNr) values ({self._event['ArrNr']}, '{self._event['kulthash']}', '{_eventStr}', {self._event['AinfoNr']})"
            await db.execute(myStatement)
        elif forceUpdate or (self._event["kulthash"] != eventDbDict["kulthash"]):
            # UPDATE
            print(f"UPDATE: {str(self)}")
            _eventStr = json.dumps(self._event, ensure_ascii=False)
            myStatement = f"update kultevents set kulthash = '{self._event['kulthash']}', kjson= '{_eventStr}', AinfoNr={self._event['AinfoNr']} where ArrNr = {self._event['ArrNr']}"
            await db.execute(myStatement)
        else:
            print(f"PASS: {str(self)}")

        # print(f"dbrec: {dbrec['ArrNr']}, {dbrec['AinfoNr']}")

    @property
    def has_edits(self):
        """Return whether this event has been manually edited."""
        return self._event.get('is_manually_edited', False)

    async def edit_field(self, field_name, new_value, db_interface=None, edited_by="manual"):
        """
        Manually edit a specific field of an event. Only whitelisted fields allowed.
        Records change in audit history and updates kulthash.
        """
        EDITABLE_FIELDS = ['ArrKunstner', 'ArrBeskrivelse', 'ArrLangBeskriv', 'ArrTidspunkt', 'Startdato', 'Slutdato']
        
        if field_name not in EDITABLE_FIELDS:
            raise ValueError(f"Field '{field_name}' not editable. Allowed: {EDITABLE_FIELDS}")
        
        db = db_interface or self._db or (self.parent._db if self.parent else None)
        if not db:
            raise ValueError("No database interface provided to edit_field")
        
        old_value = self._event.get(field_name)
        self._event[field_name] = new_value
        
        # Recalculate kulthash
        eventStr = "".join(str(v) for v in self._event.values())
        self._event["kulthash"] = hashlib.md5(eventStr.encode()).hexdigest()
        
        # Update database
        _eventStr = json.dumps(self._event, ensure_ascii=False)
        update_stmt = f"""UPDATE kultevents 
            SET is_manually_edited = TRUE, 
                manual_edit_timestamp = NOW(), 
                kulthash = '{self._event['kulthash']}', 
                kjson = '{_eventStr}'
            WHERE ArrNr = {self._event['ArrNr']}"""
        await db.execute(update_stmt)
        
        # Record in audit history
        old_val_str = str(old_value).replace("'", "´")
        new_val_str = str(new_value).replace("'", "´")
        audit_stmt = f"""INSERT INTO kultevents_edit_history 
            (ArrNr, field_name, old_value, new_value, edited_by) 
            VALUES ({self._event['ArrNr']}, '{field_name}', '{old_val_str}', '{new_val_str}', '{edited_by}')"""
        await db.execute(audit_stmt)
        
        print(f"EDIT: {str(self)} - {field_name}: '{old_value}' -> '{new_value}'")
        return True

    async def lock_event(self, db_interface=None, reason=""):
        """Lock event to prevent automatic overwrites during sync."""
        db = db_interface or self._db or (self.parent._db if self.parent else None)
        if not db:
            raise ValueError("No database interface provided to lock_event")
        
        lock_stmt = f"UPDATE kultevents SET is_locked = TRUE WHERE ArrNr = {self._event['ArrNr']}"
        await db.execute(lock_stmt)
        self._event['is_locked'] = True
        
        print(f"LOCKED: {str(self)}" + (f" - Reason: {reason}" if reason else ""))
        return True

    async def unlock_event(self, db_interface=None):
        """Unlock event to allow automatic overwrites during sync."""
        db = db_interface or self._db or (self.parent._db if self.parent else None)
        if not db:
            raise ValueError("No database interface provided to unlock_event")
        
        unlock_stmt = f"UPDATE kultevents SET is_locked = FALSE WHERE ArrNr = {self._event['ArrNr']}"
        await db.execute(unlock_stmt)
        self._event['is_locked'] = False
        
        print(f"UNLOCKED: {str(self)}")
        return True

    # @property
    # def starter(self):
    #    if 'starter' in self._event.keys():
    #        return self._event['starter']

    # @starter.setter
    # def starter(self, value):
    #    pass

    def getTime(self):
        # clean out "Kl. "
        ArrTidspunkt = self._event["ArrTidspunkt"]
        tparts = ArrTidspunkt.split(" ")
        if len(tparts) > 1:
            t = tparts[1]
        elif len(tparts) > 0:
            t = tparts[0]
        else:
            t = "19.45"  # KULTDEFTIME

        # split  "19-21"
        if len(t.split("-")) > 1:
            t = t.split("-")[0]

        # split  "19.45 or 19:45"
        tparts = re.split("[.:]", t)

        if len(tparts) < 2:
            tparts.append(0)
            tparts[1] = "00"
        r = "{}:{}"
        return r.format(tparts[0], tparts[1])


# async def main():
# my_dict = EventsDict()
# {"AinfoNr": "7104969", "ArrBeskrivelse": "Ridley Scott er nu klar med fortsættelsen til Gladiator om den tidligere kejser Marcus Aurelius barnebarn Lucius som tvinges til at kæmpe i Colosseum", "ArrGenre": "Film", "ArrKunstner": "Gladiator II", "ArrLangBeskriv": "", "ArrNr": 18208349, "ArrTidspunkt": "kl. 19:45", "ArrUGenre": "Action/Drama", "BilledeUrl": "http://www.kultunaut.dk/images/film/7104969/plakat.jpg", "Filmvurdering": "t.o.15", "Nautanb": null, "Nautanmeld": null, "Playdk": null, "Slutdato": "2024-12-27", "Startdato": "2024-12-27", "StedNavn": "Svaneke Bio"}
# evs=Events()
# ArrNr=18208349
# aObj = {'ArrNr': 18208349, 'AinfoNr': 7104969, 'tmdbid': '', 'start': '2024-12-27'}
##arrs.__setitem__(ArrNr, aObj)
# evs.__setitem__(18208349,aObj)
##print(arrs.__getitem__(ArrNr))
# print(evs[ArrNr])
##Arrangements.__setitem__(18208349, 7104969, "", "2024-12-27")

# if __name__ == "__main__":
#    asyncio.run(main())
