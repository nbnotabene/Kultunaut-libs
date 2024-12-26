from kultunaut.lib import jsoncache
#import json

def test_fetch_jsoncache():
    data = jsoncache.fetch_jsoncache()
    #data = json.loads(jsondata)
    #assert data[0]["AinfoNr"] == "7104969"
    assert isinstance(data,list)==True
    assert len(data)>0
    assert isinstance(data[0]['ArrNr'],int)
    print(data[0]['ArrNr'])
    
#def test_from_kult():
#  assert 
#  #KULTURL = 'http://www.kultunaut.dk/perl/export/cassiopeia.json'
