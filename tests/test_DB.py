import asyncio  #mariadb
from kultunaut.lib.MariaDBInterface import MariaDBInterface

def test_DB():
    db=MariaDBInterface()
    fields = asyncio.run(db.get_field_names('kult'))
    assert fields[0] == 'ArrNr'
 
