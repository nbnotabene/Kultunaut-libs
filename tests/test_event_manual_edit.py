"""
Tests for Event manual edit functionality
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
    
    async def fetchDict(self, query):
        return []


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
        "kulthash": "",
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
async def test_event_has_edits_property_false_by_default(event_with_db):
    """Test that has_edits property returns False by default"""
    assert event_with_db.has_edits is False


@pytest.mark.asyncio
async def test_event_has_edits_property_true_when_edited(sample_event_dict):
    """Test that has_edits property returns True after manual edit"""
    sample_event_dict['is_manually_edited'] = True
    mock_db = MockDB()
    event = Event(sample_event_dict, db_interface=mock_db)
    assert event.has_edits is True


@pytest.mark.asyncio
async def test_edit_field_valid_fields(event_with_db):
    """Test editing valid whitelisted fields"""
    valid_fields = ['ArrKunstner', 'ArrBeskrivelse', 'ArrLangBeskriv', 'ArrTidspunkt', 'Startdato', 'Slutdato']
    
    for field in valid_fields:
        # Reset event for each test
        event_with_db._event[field] = f"original_{field}"
        
        with patch.object(event_with_db._db, 'execute', new_callable=AsyncMock) as mock_exec:
            result = await event_with_db.edit_field(field, f"new_{field}")
            assert result is True
            assert mock_exec.called
            # Verify the event was updated
            assert event_with_db._event[field] == f"new_{field}"
            assert event_with_db._event['is_manually_edited'] is True


@pytest.mark.asyncio
async def test_edit_field_invalid_field_raises_error(event_with_db):
    """Test that editing non-whitelisted fields raises ValueError"""
    with pytest.raises(ValueError, match="Field 'ArrNr' not editable"):
        await event_with_db.edit_field('ArrNr', 999)


@pytest.mark.asyncio
async def test_edit_field_update_kulthash(event_with_db):
    """Test that kulthash is recalculated after field edit"""
    with patch.object(event_with_db._db, 'execute', new_callable=AsyncMock):
        old_hash = event_with_db._event['kulthash']
        await event_with_db.edit_field('ArrKunstner', 'New Title')
        
        # New hash should be different
        assert event_with_db._event['kulthash'] != old_hash


@pytest.mark.asyncio
async def test_edit_field_creates_audit_log(event_with_db):
    """Test that edit_field creates an audit history record"""
    with patch.object(event_with_db._db, 'execute', new_callable=AsyncMock) as mock_exec:
        await event_with_db.edit_field('ArrKunstner', 'New Artist')
        
        # Should have called execute twice: once for UPDATE, once for INSERT audit
        assert mock_exec.call_count == 2
        
        # Check that second call includes audit table INSERT
        audit_call = mock_exec.call_args_list[1][0][0]
        assert 'kultevents_edit_history' in audit_call
        assert 'ArrKunstner' in audit_call


@pytest.mark.asyncio
async def test_edit_field_sets_manual_edit_flag_and_timestamp(event_with_db):
    """Test that edit_field sets is_manually_edited and timestamp"""
    with patch.object(event_with_db._db, 'execute', new_callable=AsyncMock):
        await event_with_db.edit_field('ArrBeskrivelse', 'Updated description')
        
        assert event_with_db._event['is_manually_edited'] is True
        # timestamp should be set in database via UPDATE


@pytest.mark.asyncio
async def test_edit_field_escapes_quotes(event_with_db):
    """Test that quotes in field values are properly escaped"""
    with patch.object(event_with_db._db, 'execute', new_callable=AsyncMock) as mock_exec:
        await event_with_db.edit_field('ArrKunstner', "It's a movie")
        
        # Check that quotes were escaped in audit log
        audit_call = mock_exec.call_args_list[1][0][0]
        assert "It´s a movie" in audit_call


@pytest.mark.asyncio
async def test_edit_field_persists_to_database(event_with_db):
    """Test that edit_field persists changes to database"""
    calls = []
    
    async def mock_execute(query):
        calls.append(query)
        return 1
    
    event_with_db._db.execute = mock_execute
    
    await event_with_db.edit_field('ArrTidspunkt', 'kl. 20:00')
    
    # Should have two calls: UPDATE and INSERT
    assert len(calls) == 2
    assert 'UPDATE kultevents' in calls[0]
    assert 'is_manually_edited = TRUE' in calls[0]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
