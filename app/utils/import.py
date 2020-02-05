"""This module is hasty implementation that reads cyclist count
from Jyväskylä opendata page and pushes them in mysql db
"""
import codecs
import csv
import datetime
import urllib.request

from app import Data, db

URL = "http://data.jyvaskyla.fi/tiedostot/kevyt_liikenne_laskurit_vrk.csv"
STREAM = urllib.request.urlopen(URL)
CSVFILE = csv.reader(codecs.iterdecode(STREAM, "utf-8"))
next(CSVFILE, None)
LOCATIONS = [
    "Kinakujan silta",
    "JK-1",
    "PP-1",
    "Matkakeskus",
    "Satama",
    "JK-2",
    "PP-2",
    "Tourula",
    "JK-3",
    "PP-3",
    "Vaajakoskentie_Jyska",
]
for line in CSVFILE:
    print("=======")
    d = datetime.datetime.strptime(line[0], "%d/%m/%Y").date().isoformat()
    count = 2
    for location in LOCATIONS:
        print(line[0])
        print(location + " " + line[count])
        r = Data(date=d, qty=line[count], location=location)
        count = count + 1
        db.session.add(r)
        db.session.commit()
