#!/usr/bin/env python3
"""
Demo/Test script for manual event editing and locking functionality.

This script demonstrates:
1. Creating and editing events with the new db_interface parameter
2. Manual field editing with audit logging
3. Event locking/unlocking to prevent overwrites
4. Querying locked and edited events
"""
import asyncio
from unittest.mock import MagicMock
from kultunaut.lib.event import Event


class DemoDBInterface:
    """Demo database interface showing method calls"""
    
    def __init__(self):
        self.executed_queries = []
    
    async def execute(self, query):
        """Mock execute that records queries"""
        self.executed_queries.append(query)
        print(f"[DB EXEC] {query[:80]}...")
        return 1
    
    async def fetchOneDict(self, query):
        """Mock fetch returning None"""
        return None
    
    async def fetchDict(self, query):
        """Mock fetch returning empty list"""
        return []


async def demo_basic_event():
    """Demo 1: Basic event creation with db_interface"""
    print("\n" + "="*70)
    print("DEMO 1: Create Event with db_interface (NEW)")
    print("="*70)
    
    event_data = {
        "ArrNr": 18208349,
        "AinfoNr": 7104969,
        "ArrKunstner": "Gladiator II",
        "ArrBeskrivelse": "Ridley Scott action film",
        "ArrLangBeskriv": "Extended description",
        "ArrTidspunkt": "kl. 19:45",
        "Startdato": "2026-04-20",
        "Slutdato": "2026-04-20",
        "Starter": "2026-04-20 19:45",
        "Startformat": "Fri. d. 27/12 19:45",
        "kulthash": "abc123",
        "is_manually_edited": False,
        "is_locked": False,
        "manual_edit_timestamp": None,
        "kjson": "{}"
    }
    
    db = DemoDBInterface()
    event = Event(event_data, db_interface=db)
    
    print(f"✓ Event created: {event}")
    print(f"✓ has_edits property: {event.has_edits}")
    print(f"✓ Event has direct db_interface: {event._db is not None}")


async def demo_edit_field():
    """Demo 2: Manual field editing"""
    print("\n" + "="*70)
    print("DEMO 2: Manual Field Editing (NEW)")
    print("="*70)
    
    event_data = {
        "ArrNr": 18208349,
        "AinfoNr": 7104969,
        "ArrKunstner": "Gladiator II",
        "ArrBeskrivelse": "Old description",
        "ArrLangBeskriv": "Extended description",
        "ArrTidspunkt": "kl. 19:45",
        "Startdato": "2026-04-20",
        "Slutdato": "2026-04-20",
        "Starter": "2026-04-20 19:45",
        "Startformat": "Fri. d. 27/12 19:45",
        "kulthash": "abc123",
        "is_manually_edited": False,
        "is_locked": False,
        "manual_edit_timestamp": None,
        "kjson": "{}"
    }
    
    db = DemoDBInterface()
    event = Event(event_data, db_interface=db)
    
    print(f"\nOriginal: {event._event['ArrBeskrivelse']}")
    
    result = await event.edit_field('ArrBeskrivelse', 'New description - manually corrected')
    
    print(f"✓ Edit successful: {result}")
    print(f"✓ Updated: {event._event['ArrBeskrivelse']}")
    print(f"✓ is_manually_edited flag: {event.has_edits}")
    print(f"✓ Database calls executed: {len(db.executed_queries)}")
    for i, query in enumerate(db.executed_queries, 1):
        print(f"   {i}. {query[:70]}...")


async def demo_lock_unlock():
    """Demo 3: Event locking"""
    print("\n" + "="*70)
    print("DEMO 3: Event Locking (NEW)")
    print("="*70)
    
    event_data = {
        "ArrNr": 18208349,
        "AinfoNr": 7104969,
        "ArrKunstner": "Gladiator II",
        "ArrBeskrivelse": "Description",
        "ArrLangBeskriv": "Extended description",
        "ArrTidspunkt": "kl. 19:45",
        "Startdato": "2026-04-20",
        "Slutdato": "2026-04-20",
        "Starter": "2026-04-20 19:45",
        "Startformat": "Fri. d. 27/12 19:45",
        "kulthash": "abc123",
        "is_manually_edited": False,
        "is_locked": False,
        "manual_edit_timestamp": None,
        "kjson": "{}"
    }
    
    db = DemoDBInterface()
    event = Event(event_data, db_interface=db)
    
    print(f"Initial is_locked: {event._event.get('is_locked', False)}")
    
    await event.lock_event(reason="Waiting for confirmation from organizer")
    print(f"✓ After lock_event(): is_locked = {event._event.get('is_locked')}")
    
    await event.unlock_event()
    print(f"✓ After unlock_event(): is_locked = {event._event.get('is_locked')}")


async def demo_lock_prevents_upsert():
    """Demo 4: Locked events skip updates"""
    print("\n" + "="*70)
    print("DEMO 4: Locked Events Skip Upsert (NEW)")
    print("="*70)
    
    event_data = {
        "ArrNr": 18208349,
        "AinfoNr": 7104969,
        "ArrKunstner": "Gladiator II",
        "ArrBeskrivelse": "Description",
        "ArrLangBeskriv": "Extended description",
        "ArrTidspunkt": "kl. 19:45",
        "Startdato": "2026-04-20",
        "Slutdato": "2026-04-20",
        "Starter": "2026-04-20 19:45",
        "Startformat": "Fri. d. 27/12 19:45",
        "kulthash": "abc123",
        "is_manually_edited": False,
        "is_locked": False,
        "manual_edit_timestamp": None,
        "kjson": "{}"
    }
    
    db = DemoDBInterface()
    event = Event(event_data, db_interface=db)
    
    # Simulate locked event from database
    locked_db_record = {**event_data, 'is_locked': True, 'kulthash': 'old_hash'}
    
    print("Attempting to upsert a locked event...")
    await event.dbUpsert(db_interface=db, eventDbDict=locked_db_record)
    
    print(f"✓ Database execute called: {len(db.executed_queries) > 0}")
    if len(db.executed_queries) > 0:
        print("✗ ERROR: dbUpsert should NOT call execute for locked events!")
    else:
        print("✓ Correctly skipped update - no DB calls made")


async def demo_backward_compat():
    """Demo 5: Backward compatibility with parent parameter"""
    print("\n" + "="*70)
    print("DEMO 5: Backward Compatibility (parent parameter)")
    print("="*70)
    
    event_data = {
        "ArrNr": 18208349,
        "AinfoNr": 7104969,
        "ArrKunstner": "Gladiator II",
        "ArrBeskrivelse": "Description",
        "ArrLangBeskriv": "Extended",
        "ArrTidspunkt": "kl. 19:45",
        "Startdato": "2026-04-20",
        "Slutdato": "2026-04-20",
        "Starter": "2026-04-20 19:45",
        "Startformat": "Fri. d. 27/12 19:45",
        "kulthash": "abc123",
        "is_manually_edited": False,
        "is_locked": False,
        "manual_edit_timestamp": None,
        "kjson": "{}"
    }
    
    # Mock parent with _db
    mock_parent = MagicMock()
    mock_parent._db = DemoDBInterface()
    
    # Old-style creation with parent (still works)
    event = Event(event_data, parent=mock_parent)
    
    print("✓ Event created with parent parameter (backward compatible)")
    print(f"✓ Event.parent: {event.parent is not None}")
    print(f"✓ Can access db via parent: {event.parent._db is not None}")
    print("Note: New code should use db_interface parameter directly")


async def demo_query_helpers():
    """Demo 6: Events class query helpers"""
    print("\n" + "="*70)
    print("DEMO 6: Events Class Query Helpers (NEW)")
    print("="*70)
    
    print("""
Events class now has three new async helper methods:

1. get_locked_events_summary()
   - Returns list of all locked events
   - Shows: ArrNr, ArrKunstner, is_locked, manual_edit_timestamp
   - Example: locked = await events.get_locked_events_summary()

2. get_manually_edited_events()
   - Returns list of all manually edited events
   - Shows: ArrNr, ArrKunstner, is_manually_edited, manual_edit_timestamp
   - Example: edited = await events.get_manually_edited_events()

3. get_edit_history(arrnr=None)
   - Returns edit audit history
   - If arrnr provided: history for specific event
   - If no arrnr: last 100 edits
   - Shows: ArrNr, field_name, old_value, new_value, edited_at, edited_by
   - Example: history = await events.get_edit_history(arrnr=18208349)
    """)


async def main():
    """Run all demos"""
    print("\n" + "█"*70)
    print("MANUAL EVENT EDITING & LOCKING - FEATURE DEMO")
    print("█"*70)
    
    await demo_basic_event()
    await demo_edit_field()
    await demo_lock_unlock()
    await demo_lock_prevents_upsert()
    await demo_backward_compat()
    await demo_query_helpers()
    
    print("\n" + "="*70)
    print("SUMMARY OF CHANGES")
    print("="*70)
    print("""
✓ Event class now accepts db_interface parameter
✓ Event class has new methods:
  - has_edits (property): Check if event was manually edited
  - edit_field(field, value): Manually edit whitelisted fields
  - lock_event(reason): Lock event to prevent overwrites
  - unlock_event(): Unlock event

✓ Event.dbUpsert() now:
  - Accepts db_interface parameter (optional)
  - Skips updates for locked events

✓ Events class has new methods:
  - get_locked_events_summary(): Query all locked events
  - get_manually_edited_events(): Query all edited events
  - get_edit_history(): Query audit trail

✓ Database schema extended with:
  - is_manually_edited BOOLEAN
  - is_locked BOOLEAN
  - manual_edit_timestamp DATETIME
  - kultevents_edit_history table for audit trail

✓ Backward compatible:
  - Event(data, parent=obj) still works
  - Existing code using parent._db continues to work
    """)
    print("="*70)


if __name__ == '__main__':
    asyncio.run(main())
