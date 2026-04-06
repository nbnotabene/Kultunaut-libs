"""
Tests for EventsData sync functionality
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from kultunaut.lib.eventsdata import EventsData, parse_time, calc_kulthash, esc


class MockDB:
    """Mock database interface for testing"""
    def __init__(self):
        self.arrsdata = {}
        self.eventsdata = {}

    async def execute(self, query):
        """Mock execute - track calls but don't actually run SQL"""
        return 1

    async def fetchall(self, query):
        """Mock fetchall - return empty counts"""
        if "COUNT(*)" in query:
            return [(0,)]
        return []

    async def fetchOneDict(self, query):
        """Mock fetchOneDict - return None (record not found)"""
        return None

    async def fetchDict(self, query):
        """Mock fetchDict - return empty list"""
        return []


@pytest.fixture
def sample_json_event():
    """Sample event JSON from Kultunaut API"""
    return {
        "ArrNr": 19771430,
        "AinfoNr": "7106037",
        "ArrGenre": "Film",
        "ArrKunstner": "Affektionsværdi",
        "ArrBeskrivelse": "",
        "ArrLangBeskriv": "Drama film description",
        "ArrUGenre": "Drama",
        "BilledeUrl": "http://www.kultunaut.dk/images/film/7106037/plakat.jpg",
        "Filmvurdering": "t.o.11",
        "Nautanb": None,
        "Nautanmeld": None,
        "Playdk": None,
        "Startdato": "2026-05-14",
        "ArrTidspunkt": "kl. 19:45",
        "Slutdato": "2026-05-14",
        "StedNavn": "Svaneke Bio",
    }


@pytest.fixture
def eventsdata_with_mock_db(monkeypatch):
    """EventsData instance with mocked database"""
    mock_db = MockDB()
    ed = EventsData()
    ed._db = mock_db
    return ed


class TestParseTime:
    """Tests for parse_time helper function"""

    def test_parse_time_simple(self):
        """Parse simple 'kl. 19:45' format"""
        assert parse_time("kl. 19:45") == "19:45"

    def test_parse_time_with_dots(self):
        """Convert dots to colons"""
        assert parse_time("kl. 19.45") == "19:45"

    def test_parse_time_range(self):
        """Handle time ranges (use start time)"""
        assert parse_time("19-21") == "19:00"

    def test_parse_time_no_minutes(self):
        """Handle hour-only format"""
        assert parse_time("19") == "19:00"

    def test_parse_time_default(self):
        """Use default time for empty/invalid input"""
        assert parse_time("") == "19:45"


class TestCalcKulthash:
    """Tests for calc_kulthash helper function"""

    def test_calc_kulthash_consistent(self):
        """Same input always produces same hash"""
        data = {"ArrNr": 123, "ArrKunstner": "Test"}
        hash1 = calc_kulthash(data)
        hash2 = calc_kulthash(data)
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 is 32 hex chars

    def test_calc_kulthash_different(self):
        """Different input produces different hash"""
        data1 = {"ArrNr": 123, "ArrKunstner": "Test1"}
        data2 = {"ArrNr": 123, "ArrKunstner": "Test2"}
        assert calc_kulthash(data1) != calc_kulthash(data2)


class TestEsc:
    """Tests for SQL escape helper function"""

    def test_esc_none(self):
        """NULL values are returned as NULL"""
        assert esc(None) == "NULL"

    def test_esc_simple_string(self):
        """Simple strings are properly escaped"""
        assert esc("hello") == "'hello'"

    def test_esc_contains_quote(self):
        """Single quotes are escaped"""
        assert esc("it's") == "'it\\'s'"

    def test_esc_contains_backslash(self):
        """Backslashes are escaped"""
        assert esc("path\\to\\file") == "'path\\\\to\\\\file'"


class TestEventsSyncArrangements:
    """Tests for arrangement sync logic"""

    @pytest.mark.asyncio
    async def test_sync_arrangements_insert(self, eventsdata_with_mock_db, sample_json_event):
        """Test INSERT path for new arrangement"""
        ed = eventsdata_with_mock_db

        with patch.object(ed, "_fetch_tmdb_json", new_callable=AsyncMock) as mock_tmdb:
            mock_tmdb.return_value = '{"title": "Test Movie"}'

            ainfos = {7106037: sample_json_event}
            await ed._sync_arrangements(ainfos, forceUpdate=False)

            # Verify TMDB was called
            mock_tmdb.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_arrangements_skip_ainfon_null(self, eventsdata_with_mock_db):
        """Skip events with NULL AinfoNr"""
        ed = eventsdata_with_mock_db

        json_event = {"ArrNr": 123, "AinfoNr": None, "ArrKunstner": "Test"}
        ainfos = {None: json_event}

        # Should skip this
        await ed._sync_arrangements(ainfos, forceUpdate=False)
        # If no exceptions, test passes


class TestEventsSyncEvents:
    """Tests for event sync logic"""

    @pytest.mark.asyncio
    async def test_sync_events_insert(self, eventsdata_with_mock_db, sample_json_event):
        """Test INSERT path for new event"""
        ed = eventsdata_with_mock_db

        json_events = [sample_json_event]
        await ed._sync_events(json_events, forceUpdate=False)

        # Should complete without errors

    @pytest.mark.asyncio
    async def test_sync_events_skip_no_arrnr(self, eventsdata_with_mock_db):
        """Skip events with missing ArrNr"""
        ed = eventsdata_with_mock_db

        json_event = {
            "AinfoNr": 123,
            "ArrKunstner": "Test",
            "Startdato": "2026-05-14",
            "ArrTidspunkt": "kl. 19:45",
        }
        await ed._sync_events([json_event], forceUpdate=False)
        # Should skip (no exception raised)

    @pytest.mark.asyncio
    async def test_sync_events_skip_no_ainfon(self, eventsdata_with_mock_db):
        """Skip events with NULL AinfoNr"""
        ed = eventsdata_with_mock_db

        json_event = {
            "ArrNr": 123,
            "AinfoNr": None,
            "Startdato": "2026-05-14",
            "ArrTidspunkt": "kl. 19:45",
        }
        await ed._sync_events([json_event], forceUpdate=False)
        # Should skip

    @pytest.mark.asyncio
    async def test_sync_events_bad_startdato(self, eventsdata_with_mock_db):
        """Skip events with invalid Startdato format"""
        ed = eventsdata_with_mock_db

        json_event = {
            "ArrNr": 123,
            "AinfoNr": 456,
            "Startdato": "invalid-date",
            "ArrTidspunkt": "kl. 19:45",
        }
        await ed._sync_events([json_event], forceUpdate=False)
        # Should skip


class TestEventsSyncTMDB:
    """Tests for TMDB enrichment logic"""

    @pytest.mark.asyncio
    async def test_fetch_tmdb_json_singleton_event(self, eventsdata_with_mock_db):
        """Return None for singleton events (AinfoNr == ArrNr)"""
        ed = eventsdata_with_mock_db

        json_event = {"ArrNr": 123, "AinfoNr": 123}
        result = await ed._fetch_tmdb_json(123, json_event)
        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_tmdb_json_error_handling(self, eventsdata_with_mock_db):
        """Error in TMDB fetch returns None (doesn't fail sync)"""
        ed = eventsdata_with_mock_db

        with patch.object(ed, "_fetch_kultfilm", new_callable=AsyncMock) as mock_kf:
            mock_kf.side_effect = Exception("API error")
            json_event = {"ArrNr": 123, "AinfoNr": 456}
            result = await ed._fetch_tmdb_json(456, json_event)
            assert result is None


class TestEventsSyncLocking:
    """Tests for event locking functionality"""

    @pytest.mark.asyncio
    async def test_lock_event(self, eventsdata_with_mock_db):
        """Lock an event"""
        ed = eventsdata_with_mock_db

        with patch.object(ed._db, "execute", new_callable=AsyncMock) as mock_exec:
            await ed.lock_event(123, reason="Manual override")
            mock_exec.assert_called_once()
            SQL = mock_exec.call_args[0][0]
            assert "UPDATE eventsdata" in SQL
            assert "is_locked = TRUE" in SQL

    @pytest.mark.asyncio
    async def test_unlock_event(self, eventsdata_with_mock_db):
        """Unlock an event"""
        ed = eventsdata_with_mock_db

        with patch.object(ed._db, "execute", new_callable=AsyncMock) as mock_exec:
            await ed.unlock_event(123)
            mock_exec.assert_called_once()
            SQL = mock_exec.call_args[0][0]
            assert "UPDATE eventsdata" in SQL
            assert "is_locked = FALSE" in SQL


class TestEventsDataIntegration:
    """Integration tests (with mocks)"""

    @pytest.mark.asyncio
    async def test_sync_full_flow(self, eventsdata_with_mock_db, sample_json_event):
        """Test complete sync flow with mock jsoncache"""
        ed = eventsdata_with_mock_db

        with patch("kultunaut.lib.eventsdata.jsoncache.fetch_jsoncache", new_callable=AsyncMock) as mock_cache:
            mock_cache.return_value = [sample_json_event]

            with patch.object(ed, "_fetch_tmdb_json", new_callable=AsyncMock) as mock_tmdb:
                mock_tmdb.return_value = None

                # Run sync - should not raise
                await ed.sync(forceUpdate=False)

                # Verify jsoncache was called
                mock_cache.assert_called_once()
