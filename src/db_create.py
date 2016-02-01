# db_create.py
# Author: Valtyr Farshield

import os
import urllib2
import gzip
import json
from StringIO import StringIO
from rules.statsconfig import StatsConfig


def zkill_fetch(year, month, page_nr):
    headers = {
        "User-Agent" : "Wingspan Stats, Mail: valtyr.farshield@gmail.com",
        "Accept-encoding": "gzip"
    }

    # The Wingspan LOGO Alliance
    corporation_ids = ",".join([str(corp) for corp in StatsConfig.CORP_IDS])
    url = "https://zkillboard.com/api/kills/corporationID/{}/year/{}/month/{}/page/{}/".format(
        corporation_ids,
        year,
        month,
        page_nr,
    )

    try:
        request = urllib2.Request(url, None, headers)
        response = urllib2.urlopen(request)
    except urllib2.URLError as e:
        print "[Error]", e.reason
        return None

    if response.info().get("Content-Encoding") == "gzip":
        buf = StringIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
    else:
        data = response.read()

    return data

def extract_data(year, month):
    print "Trying to extract killmails from {}-{}".format(year, month)

    db_dir = os.path.join(StatsConfig.DATABASE_PATH, "{}-{:02d}".format(year, month))
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    page_nr = 1
    while True:
        data =  zkill_fetch(year, month, page_nr)

        # try to parse JSON received from server
        try:
            parsed_json = json.loads(data)
        except ValueError as e:
            print "[Error]", e
            return

        if len(parsed_json) > 0:
            file_name = os.path.join(db_dir, "{}-{:02d}_{:02d}.json".format(year, month, page_nr))
            with open(file_name, 'w') as f_out:
                f_out.write(data)

        if len(parsed_json) < 200:
            break
        else:
            page_nr += 1


def main():
    extract_data(2014, 7)
    extract_data(2014, 8)
    extract_data(2014, 9)
    extract_data(2014, 10)
    extract_data(2014, 11)
    extract_data(2014, 12)

    extract_data(2015, 1)
    extract_data(2015, 2)
    extract_data(2015, 3)
    extract_data(2015, 4)
    extract_data(2015, 5)
    extract_data(2015, 6)
    extract_data(2015, 7)
    extract_data(2015, 8)
    extract_data(2015, 9)
    extract_data(2015, 10)
    extract_data(2015, 11)
    extract_data(2015, 12)
    extract_data(2016, 1)

if __name__ == "__main__":
    main()
