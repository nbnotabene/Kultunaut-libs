# Kultunaut libs

crontab -e on nb@nb-miniPC
35 20 * * * /mnt/sda3/nfs/repos/kultunaut/Kultunaut-libs/generateUI.sh >> /var/log/cronjob.log 2>&1
15 16 * * 0 /mnt/sda3/nfs/repos/kultunaut/Kultunaut-libs/generateUI.sh >> /var/log/cronjob.log 2>&1
35 03 * * * /mnt/sda3/nfs/repos/kultunaut/Kultunaut-libs/fetchKult.sh >> /var/log/cronjob.log 2>&1
45 03 * * * /mnt/sda3/nfs/repos/kultunaut/Kultunaut-libs/generateUI.sh >> /var/log/cronjob.log 2>&1

https://builder.statichost.eu/nbnotabene-kultunaut-libs

https://github.com/nbnotabene/Kultunaut-libs

Click on the **Add webhook** button.
Enter https://builder.statichost.eu/YOUR_SITE_NAME in the payload URL field.
Select application/json as the content type.
Select Just the push event.
Press Add webhook.


TEST: python3 -m http.server
LIVE: http://local.svanekebio.dk i MS Edge

kultunaut_libs

Kultunaut Events services for movie theaters

[Kultunaut](https://kultunaut.dk/)

https://packaging.python.org/en/latest/tutorials/packaging-projects/

Use fastAPI? ../bak/kultunaut

python3 -m venv .venv
source .venv/bin/activate
pip install -U pip setuptools
pip install poetry

(poetry shell => activate venv)
poetry run pytest
poetry add request
poetry new --name kultunaut.bio kultunaut-bio

select CONCAT((SELECT REPLACE(GROUP_CONCAT(COLUMN_NAME), 'ainfonr', '') FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'kultevents' AND TABLE_SCHEMA = 'bio'));

create view curEvents as
select e.AinfoNr, min(e.ArrNr) marrnr, min(e.vStarter) mstart, group_concat(e.ArrNr) arrnums, group_concat(e.vStarter) arrstarter from kultevents e
where e.vStarter> now()
group by e.AinfoNr
order by e.vStarter;

create or replace view curArrs as
select c.AinfoNr, c.marrnr, c.mstart,c.arrnums, c.arrstarter,
a.kjson,a.kulthash,a.kultfilm,a.tmdb,a.created,a.updated,a.vStarter,a.vTitle,
e.kjson ekjson, e.vTitle evTitle from curEvents c
left join kultevents e on e.ArrNr=c.marrnr
left join kultarrs a on a.AinfoNr=c.AinfoNr;

Ikoner:
         <!--<i class="material-icons">movie</i>-->
          {% if starter[3] != None %}
          {% from "macro_defs.html" import popup_gen -%}
          {{ popup_gen("Baby-bio!", "Denne visning er specielt tilpasset for forældre, som medtager babyer til filmen")
          }}
              </a><button onclick="document.getElementById('popup').style.display = 'block'">Baby-bio</button>&nbsp;
          {% endif %}

python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip freeze > requirements.txt
pip install -r  requirements.txt
pip install .

(.venv) nb@ubuntu-s-1vcpu-1gb-fra1-01:~/repos/kultunaut/Kultunaut-libs$    pip install .
Processing /home/nb/repos/kultunaut/Kultunaut-libs
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting jinja2<4.0.0,>=3.1.5 (from kultunaut-lib==0.1.0)

Jinja2 3.1.6

35 20 ** * /home/nb/repos/kultunaut/generateUI.sh

// !/bin/bash

// generateUI.sh

cd /home/nb/repos/kultunaut/Kultunaut-libs
source /home/nb/repos/kultunaut/Kultunaut-libs/.venv/bin/activate
.venv/bin/python3 kultunaut/lib/UI.py

timestamp=$(date +"%Y-%m-%d %H:%M:%S")
/usr/bin/git add .
/usr/bin/git commit -m "$timestamp commit"
/usr/bin/git push origin main

DUMP
sudo mariadb-dump bio > ../bioDB.sql
sudo mariadb fromSQL < ../bioDB.sql
sudo mariadb-dump bio | gzip -c > ../bioDB.sql.gz
gunzip bioDB.sql.gz

STATICHOST
https://builder.statichost.eu/login
