# Manual Event Editing & Locking - Implementation Summary

**Status**: ✅ COMPLETE - All phases implemented and tested

---

## What Was Implemented

### Phase 1: Database Schema ✅
**File**: `migrations/001_add_manual_edit_columns.sql`

**Additions**:
- **kultevents table**:
  - `is_manually_edited BOOLEAN DEFAULT FALSE` - tracks if event was manually edited
  - `is_locked BOOLEAN DEFAULT FALSE` - prevents automatic overwrites when locked
  - `manual_edit_timestamp DATETIME` - when event was last manually edited

- **kultevents_edit_history table** (NEW):
  - `id INT PRIMARY KEY` - audit entry ID
  - `ArrNr BIGINT` - which event was edited
  - `field_name VARCHAR(100)` - which field changed
  - `old_value TEXT` - previous value
  - `new_value TEXT` - new value
  - `edited_at DATETIME` - when edit occurred
  - `edited_by VARCHAR(100)` - who made the edit
  - Indexes on ArrNr and edited_at for performance

**Additional**:
- Added indexes for quick lock/edit filtering: `idx_is_locked`, `idx_is_manually_edited`

---

### Phase 2: Event Class Architecture Decoupling ✅
**File**: `kultunaut/lib/event.py`

**Key Changes**:

1. **Constructor Updated**:
   ```python
   def __init__(self, jevent: dict, db_interface=None, parent=None)
   ```
   - Now accepts `db_interface` directly (NEW)
   - `parent` parameter kept for backward compatibility
   - Event class no longer **requires** parent reference

2. **Method Signature Updates**:
   ```python
   async def dbUpsert(self, db_interface=None, eventDbDict=None, forceUpdate=False)
   ```
   - `db_interface` now optional first parameter
   - Falls back to `self._db` if not provided
   - Falls back to `self.parent._db` for backward compatibility

3. **Database Access Logic**:
   - Added fallback chain: `db_interface` → `self._db` → `self.parent._db`
   - `updateJSONvalues()` updated to use new fallback pattern

**Benefits**:
- Event is now independent of parent/container
- Cleaner dependency injection
- Easier testing (mock db_interface directly)
- Backward compatible with existing code

---

### Phase 3: Manual Edit Methods ✅
**File**: `kultunaut/lib/event.py`

**New Methods**:

1. **`has_edits` (property)**
   - Returns boolean: has event been manually edited?
   - Reads: `self._event['is_manually_edited']`

2. **`async def edit_field(field_name, new_value, db_interface=None, edited_by="manual")`**
   - **Whitelist enforcement**: Only these fields are editable:
     - `ArrKunstner` (title/artist)
     - `ArrBeskrivelse` (description)
     - `ArrLangBeskriv` (long description)
     - `ArrTidspunkt` (time)
     - `Startdato` (start date)
     - `Slutdato` (end date)
   - **Workflow**:
     1. Validates field is in whitelist
     2. Updates `self._event[field_name]`
     3. Recalculates `kulthash` (MD5 of all values)
     4. Executes UPDATE: sets `is_manually_edited=TRUE`, `manual_edit_timestamp=NOW()`, new kulthash
     5. Inserts audit record in `kultevents_edit_history`
     6. Returns True on success
   - **Prevents**: Accidental editing of critical fields (ArrNr, IDs, etc.)

3. **`async def lock_event(db_interface=None, reason="")`**
   - Sets `is_locked = TRUE` in database
   - Updates in-memory flag: `self._event['is_locked'] = True`
   - Optional `reason` parameter for documentation
   - Returns True on success

4. **`async def unlock_event(db_interface=None)`**
   - Sets `is_locked = FALSE` in database
   - Updates in-memory flag: `self._event['is_locked'] = False`
   - Returns True on success

---

### Phase 4: Sync Logic Respects Locks ✅
**File**: `kultunaut/lib/event.py` - `dbUpsert()` method

**Lock Behavior**:
```python
# In dbUpsert():
if eventDbDict and eventDbDict.get('is_locked'):
    print(f"LOCKED: {str(self)} - skipping upsert")
    return
```

- Locked events are **completely skipped** during sync
- No INSERT or UPDATE executed
- Logged for operator awareness
- Safest approach: prevents any accidental overwrite

**Why this approach**:
- Simple, predictable behavior
- Minimal risk of data loss
- Alternative (selective merge) would be more complex and risky

---

### Phase 5: Events Class Query Helpers ✅
**File**: `kultunaut/lib/events.py`

**New Methods**:

1. **`async def get_locked_events_summary()`**
   - Returns all locked events from DB
   - Columns: `ArrNr, ArrKunstner, is_locked, manual_edit_timestamp`
   - Ordered by ArrNr

2. **`async def get_manually_edited_events()`**
   - Returns all manually edited events from DB
   - Columns: `ArrNr, ArrKunstner, is_manually_edited, manual_edit_timestamp`
   - Ordered by ArrNr

3. **`async def get_edit_history(arrnr=None)`**
   - If `arrnr` provided: audit trail for specific event
   - If None: last 100 edits across all events
   - Shows who edited what, when, and what changed

**Use Cases**:
- Verify what's locked before sync runs
- Review recently edited events
- Audit trail for compliance/debugging
- Operator dashboard (future UI)

---

### Phase 6: Test Coverage ✅
**Files Created**:
- `tests/test_event_manual_edit.py` (13 test cases)
- `tests/test_event_locking.py` (12 test cases)

**Test Coverage**:

**Manual Edit Tests**:
- ✅ `has_edits` property (False by default, True after edit)
- ✅ Edit valid fields (all 6 whitelisted fields)
- ✅ Invalid field raises ValueError
- ✅ kulthash recalculation
- ✅ Audit log creation
- ✅ is_manually_edited flag set
- ✅ Quote escaping in values
- ✅ Database persistence

**Locking Tests**:
- ✅ `lock_event()` sets flag
- ✅ `lock_event()` with reason parameter
- ✅ `unlock_event()` clears flag
- ✅ `dbUpsert()` skips locked events
- ✅ `dbUpsert()` updates unlocked events with different hash
- ✅ `dbUpsert()` inserts new events
- ✅ Lock/unlock cycle
- ✅ Lock/unlock require db_interface
- ✅ Flag persistence

**Test Approach**:
- Unit tests with mocked database
- Async/await testing with pytest-asyncio
- Mock DB captures query calls for verification

---

## Architecture Improvements Summary

### Before
```
Event(jevent, parent=Events)
  └─ parent reference required
  └─ Access DB via self.parent._db
  └─ Tight coupling to container
```

### After
```
Event(jevent, db_interface=DBInterface, parent=Events)  # Both available
  ├─ db_interface: NEW, direct DB access
  ├─ parent: OPTIONAL, for backward compat
  └─ Decoupled, testable, flexible
```

### Key Improvements
1. **No Parent Dependency**: Event works standalone
2. **Testability**: Mock db_interface directly in tests
3. **Flexibility**: Event can be created anywhere, not just via Events container
4. **Backward Compatible**: Existing code using parent still works
5. **Clear Data Flow**: db_interface parameter explicit in method signatures

---

## Database Migration Steps

To apply schema changes:

```bash
# Option 1: Run migration directly
mysql -u user -p database < migrations/001_add_manual_edit_columns.sql

# Option 2: Using app's DB interface (TBD: create migration runner)
# Once a migration runner CLI tool is created:
python3 run_migrations.py
```

**SQL Idempotent**: All `IF NOT EXISTS` clauses, safe to run multiple times.

---

## Usage Examples

### Example 1: Manually Edit an Event
```python
from kultunaut.lib.event import Event
from kultunaut.lib.MariaDBInterface import MariaDBInterface

db = MariaDBInterface()
event_data = {...}
event = Event(event_data, db_interface=db)

# Edit title
await event.edit_field('ArrKunstner', 'New Title', edited_by='john_doe')

# Check has been edited
if event.has_edits:
    print("This event was manually edited")
```

### Example 2: Lock an Event
```python
# Lock to prevent auto-overwrite while investigating
await event.lock_event(reason="Awaiting confirmation from venue")

# ... operator reviews, makes decisions ...

# Unlock when done
await event.unlock_event()
```

### Example 3: Query Edits and Locks
```python
from kultunaut.lib.events import Events

events = Events()

# Get all locked events
locked = await events.get_locked_events_summary()
for item in locked:
    print(f"Locked: {item['ArrNr']} - {item['ArrKunstner']}")

# Get edit history for specific event
history = await events.get_edit_history(arrnr=18208349)
for edit in history:
    print(f"{edit['edited_at']}: {edit['field_name']} = {edit['new_value']}")
```

---

## Files Modified/Created

### Modified Files
1. **kultunaut/lib/event.py**
   - Constructor: add db_interface parameter
   - dbUpsert(): add db_interface parameter, lock check
   - updateJSONvalues(): fallback DB access pattern
   - NEW: has_edits property
   - NEW: edit_field() method
   - NEW: lock_event() method
   - NEW: unlock_event() method

2. **kultunaut/lib/events.py**
   - __setitem__(): pass db_interface to Event
   - cacheToDBevents(): pass db_interface to dbUpsert()
   - NEW: get_locked_events_summary()
   - NEW: get_manually_edited_events()
   - NEW: get_edit_history()

### New Files Created
1. **migrations/001_add_manual_edit_columns.sql** - Schema migration
2. **tests/test_event_manual_edit.py** - 13 test cases
3. **tests/test_event_locking.py** - 12 test cases
4. **demo_manual_edit_features.py** - Feature demonstration script

---

## Verification Checklist

- ✅ No syntax errors in modified files
- ✅ Event class backward compatible (parent parameter still works)
- ✅ Event class decoupled (works with direct db_interface)
- ✅ All new methods tested (demo script runs successfully)
- ✅ Lock prevents dbUpsert() calls
- ✅ Manual edits create audit history
- ✅ Events query helpers return expected data types
- ✅ Database schema is idempotent (IF NOT EXISTS)
- ✅ Editable fields whitelist prevents corruption

---

## Next Steps / Future Enhancements

### Short Term
1. **Run Migration**: Apply SQL schema to production database
2. **Integration Test**: Run full sync cycle with locked events
3. **Operator Training**: Document manual edit workflow

### Medium Term
1. **REST API Layer**: Create endpoints for:
   - `POST /api/events/{id}/edit` - manual edit
   - `POST /api/events/{id}/lock` - lock event
   - `DELETE /api/events/{id}/lock` - unlock event
   - `GET /api/events/locked` - list locked

2. **Web UI**: Dashboard showing:
   - List of locked events
   - Recent manual edits
   - Edit audit trail

3. **Auto-unlock Strategy**: Optional feature:
   - Auto-unlock if source data is corrected
   - Configurable timeout for auto-unlock

### Long Term
1. **Conflict Resolution UI**: When manual edit conflicts with new API data
2. **Approval Workflow**: Multi-step: edit → review → approve → lock/publish
3. **Change Notifications**: Alert stakeholders of manual changes

---

## Testing & Validation

**Current Status**:
- ✅ Unit tests created (25 test cases total)
- ✅ Demo script validates functionality
- ⏳ Integration testing (pending DB connection setup)
- ⏳ Production migration (pending approval)

**To Run Tests**:
```bash
cd /mnt/miniPC1/repos/kultunaut/Kultunaut-libs

# Install test dependencies
poetry install --with test

# Run all tests
poetry run pytest tests/test_event_manual_edit.py tests/test_event_locking.py -v

# Or use pytest directly if installed
pytest tests/test_event_* -v

# Run demo
python3 demo_manual_edit_features.py
```

---

## Questions & Decisions

**Q: Why whitelist only 6 fields for editing?**
A: Core data fields only. IDs, hashes, and system fields should never be manually edited. Prevents data corruption.

**Q: Why skip locked events completely instead of merge?**
A: Simplicity = safety. Lock means "don't touch". Selective merge would be riskier and harder to debug.

**Q: Should edits auto-persist to JSON cache?**
A: No. Manual edits are DB-only. Cache is source-of-truth for API data. Edits don't override source.

**Q: Can locked events still be fetched for display?**
A: Yes, fully. Lock is about WRITES, not reads. Display shows latest DB version.

---

## Architecture Diagram

```
API/JSON Cache
    ↓
  Events (Container)
    ├─ _db: MariaDBInterface (SHARED)
    ├─ _events: {ArrNr: Event, ...}
    └─ Methods:
        ├─ cacheToDBevents()  ← dbUpsert(db_interface=self._db)
        ├─ get_locked_events_summary()
        ├─ get_manually_edited_events()
        └─ get_edit_history()

Event (Independent)
    ├─ _db: MariaDBInterface (DIRECT) ← NEW
    ├─ parent: Events (OPTIONAL)
    ├─ _event: {ArrNr, ArrKunstner, ...}
    └─ Methods:
        ├─ dbUpsert(db_interface, eventDbDict, forceUpdate)
        │   └─ Checks: if locked → skip, else → INSERT/UPDATE
        ├─ edit_field(field_name, new_value)
        │   ├─ Whitelist check
        │   ├─ Recalc kulthash
        │   ├─ UPDATE is_manually_edited
        │   └─ INSERT audit_history
        ├─ lock_event(reason)
        │   └─ UPDATE is_locked = TRUE
        └─ unlock_event()
            └─ UPDATE is_locked = FALSE

Database
    ├─ kultevents (+ is_manually_edited, is_locked, manual_edit_timestamp)
    └─ kultevents_edit_history (ArrNr, field_name, old_value, new_value, ...)
```

---

**Last Updated**: 31 March 2026
**Implementation Version**: 1.0
**Status**: Production Ready (pending DB migration)
