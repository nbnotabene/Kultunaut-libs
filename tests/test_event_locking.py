"""
Tests for Event locking functionality
"""
import pytest
from unittest.mock import AsyncMock, patch
from kultunaut.lib.event import Event


class MockDB:
    """Mock database interface for testing"""
    async def execute(self, query):
        return 1
    
    async def fetchOneDict(self, query):
        return None


@pytest.fixture
def sample_event_dict():
    """Sample event data for testing"""
    return {
        "ArrNr": 18208349,
        "AinfoNr": 7104969,
        "ArrKunstner": "Gladiator II",
        "ArrBeskrivelse": "Ridley Scott action film",
        "ArrLangBeskriv": "Extended description",
        "ArrTidspunkt": "kl. 19:45",
        "Startdato": "2024-12-27",
        "Slutdato": "2024-12-27",
        "Starter": "2024-12-27 19:45",
        "Startformat": "Fri. d. 27/12 19:45",
        "kulthash": "abc123",
        "is_manually_edited": False,
        "is_locked": False,
        "manual_edit_timestamp": None,
        "kjson": "{}"
    }


@pytest.fixture
def event_with_db(sample_event_dict):
    """Event instance with mocked database"""
    mock_db = MockDB()
    return Event(sample_event_dict, db_interface=mock_db)


@pytest.mark.asyncio
async def test_lock_event(event_with_db):
    """Test that lock_event sets is_locked flag"""
    with patch.object(event_with_db._db, 'execute', new_callable=AsyncMock) as mock_exec:
        result = await event_with_db.lock_event()
        
        assert result is True
        assert event_with_db._event['is_locked'] is True
        assert mock_exec.called
        
        # Verify SQL contains UPDATE and is_locked = TRUE
        call_args = mock_exec.call_args_list[0][0][0]
        assert 'UPDATE kultevents' in call_args
        assert 'is_locked = TRUE' in call_args


@pytest.mark.asyncio
async def test_lock_event_with_reason(event_with_db):
    """Test that lock_event accepts optional reason parameter"""
    with patch.object(event_with_db._db, 'execute', new_callable=AsyncMock):
        result = await event_with_db.lock_event(reason="Manual correction in progress")
        assert result is True
        assert event_with_db._event['is_locked'] is True


@pytest.mark.asyncio
async def test_unlock_event(event_with_db):
    """Test that unlock_event clears is_locked flag"""
    # First lock it
    event_with_db._event['is_locked'] = True
    
    with patch.object(event_with_db._db, 'execute', new_callable=AsyncMock) as mock_exec:
        result = await event_with_db.unlock_event()
        
        assert result is True
        assert event_with_db._event['is_locked'] is False
        assert mock_exec.called
        
        # Verify SQL contains UPDATE and is_locked = FALSE
        call_args = mock_exec.call_args_list[0][0][0]
        assert 'UPDATE kultevents' in call_args
        assert 'is_locked = FALSE' in call_args


@pytest.mark.asyncio
async def test_dbupsert_skips_locked_event(sample_event_dict):
    """Test that dbUpsert skips update for locked events"""
    mock_db = MockDB()
    event = Event(sample_event_dict, db_interface=mock_db)
    
    # Create a locked event record from database
    locked_db_record = {**sample_event_dict, 'is_locked': True, 'kulthash': 'old_hash'}
    
    with patch.object(mock_db, 'execute', new_callable=AsyncMock) as mock_exec:
        await event.dbUpsert(db_interface=mock_db, eventDbDict=locked_db_record)
        
        # Should NOT call execute for locked events
        assert not mock_exec.called


@pytest.mark.asyncio
async def test_dbupsert_updates_unlocked_event_with_different_hash(sample_event_dict):
    """Test that dbUpsert updates unlocked events with different hash"""
    mock_db = MockDB()
    event = Event(sample_event_dict, db_interface=mock_db)
    
    # Create an unlocked event record with different hash
    db_record = {**sample_event_dict, 'is_locked': False, 'kulthash': 'different_hash'}
    
    with patch.object(mock_db, 'execute', new_callable=AsyncMock) as mock_exec:
        await event.dbUpsert(db_interface=mock_db, eventDbDict=db_record, forceUpdate=False)
        
        # Should call execute for update
        assert mock_exec.called


@pytest.mark.asyncio
async def test_dbupsert_inserts_new_event(sample_event_dict):
    """Test that dbUpsert inserts new events regardless of lock status"""
    mock_db = MockDB()
    event = Event(sample_event_dict, db_interface=mock_db)
    
    with patch.object(mock_db, 'execute', new_callable=AsyncMock) as mock_exec:
        # No record in database (None)
        await event.dbUpsert(db_interface=mock_db, eventDbDict=None, forceUpdate=False)
        
        # Should call execute for insert
        assert mock_exec.called
        call_args = mock_exec.call_args_list[0][0][0]
        assert 'insert' in call_args.lower()


@pytest.mark.asyncio
async def test_lock_unlock_cycle(event_with_db):
    """Test locking and unlocking an event"""
    with patch.object(event_with_db._db, 'execute', new_callable=AsyncMock):
        # Lock
        assert await event_with_db.lock_event() is True
        assert event_with_db._event['is_locked'] is True
        
        # Unlock
        assert await event_with_db.unlock_event() is True
        assert event_with_db._event['is_locked'] is False


@pytest.mark.asyncio
async def test_lock_requires_db_interface(sample_event_dict):
    """Test that lock_event raises error without database interface"""
    event = Event(sample_event_dict)  # No db_interface
    
    with pytest.raises(ValueError, match="No database interface"):
        await event.lock_event()


@pytest.mark.asyncio
async def test_unlock_requires_db_interface(sample_event_dict):
    """Test that unlock_event raises error without database interface"""
    event = Event(sample_event_dict)  # No db_interface
    
    with pytest.raises(ValueError, match="No database interface"):
        await event.unlock_event()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
