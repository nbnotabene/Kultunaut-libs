# Kultunaut libs

TEST: python3 -m http.server

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

