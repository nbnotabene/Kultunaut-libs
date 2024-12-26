from kultunaut.lib import lib

def test_answer():
    assert lib.add_one(2) == 3

def test_env():
    assert lib.conf['KULTURL'] == "http://www.kultunaut.dk/perl/export/cassiopeia.json"
    assert lib.conf['SECRET_KEY'] == "gsabijwjnciiwbjksa"
    assert lib.conf['BRANCH'] == "develop"
    branch = lib.conf['BRANCH']
    con = lib.sqlconn()
    assert con[branch]['mysqlcon']['database']=='bio'
    