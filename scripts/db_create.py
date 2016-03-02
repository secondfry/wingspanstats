# !/usr/bin/python2
# Author: Rustam Gubaydullin (@second_fry)
# Original author: Valtyr Farshield (github.com/farshield)
# License: MIT (https://opensource.org/licenses/MIT)

from scripts.log import log
from config.statsconfig import StatsConfig
from datetime import date, datetime
import os
import urllib2
import gzip
import json
from StringIO import StringIO


class DbCreate(object):
    STATUS_DONE = 0
    STATUS_START = 1
    STATUS_ONGOING = 2

    @staticmethod
    def factory(type):
        """
        Provides DB creator

        :param type Selects type of DB creator
        """
        if type == "zkillboard":
            log(1, 'Creating zkillboard fetcher')
            return DbCreateZkillboard()
        assert 0, "Source '" + type + "' is not defined"


class DbCreateZkillboard(DbCreate):
    LOG_LEVEL = 2

    def __init__(self):
        self.headers = StatsConfig.HEADERS
        self.corporation_ids = ",".join([str(corp) for corp in StatsConfig.CORPORATION_IDS])
        self.create_db()

    def create_db(self):
        db_dir = None

        log(self.LOG_LEVEL, 'Checking database directory')
        if not os.path.isdir(StatsConfig.DATABASE_PATH):
            os.mkdir(StatsConfig.DATABASE_PATH)
        else:
            db_dir = os.listdir(StatsConfig.DATABASE_PATH)

        log(self.LOG_LEVEL, 'Finding timestamp to check')
        timestamp_today = date.today()
        if timestamp_today.month == 1:
            timestamp_check = timestamp_today.replace(year=timestamp_today.year - 1, month=12, day=1)
        else:
            timestamp_check = timestamp_today.replace(month=timestamp_today.month - 1, day=1)
        log(self.LOG_LEVEL, 'Will check: ' + timestamp_check.strftime('%Y-%m-%d'))

        log(self.LOG_LEVEL, 'Finding last checked timestamp')
        if db_dir:
            year_last, month_last = sorted(db_dir)[-1].split("-")
            timestamp_last = datetime.strptime(year_last + month_last, '%Y%m').date()
        else:
            timestamp_last = datetime.strptime('2000', '%Y').date()
        log(self.LOG_LEVEL, 'Last checked: ' + timestamp_last.strftime('%Y-%m-%d'))

        log(self.LOG_LEVEL, 'Should we parse new data?')
        if timestamp_last < timestamp_check:
            log(self.LOG_LEVEL + 1, 'Yes')
            status = self.STATUS_START
        else:
            log(self.LOG_LEVEL + 1, 'No')
            status = self.STATUS_DONE

        while status != self.STATUS_DONE:
            log(self.LOG_LEVEL, 'Starting fetch ' + timestamp_check.strftime('%Y-%m'))
            status, timestamp_check = self.parse(timestamp_check)
        log(self.LOG_LEVEL, 'Done! [zkillboard fetcher]')

    def parse(self, timestamp_check):
        self.LOG_LEVEL += 1

        db_dir_date = os.path.join(StatsConfig.DATABASE_PATH, timestamp_check.strftime('%Y-%m'))
        if os.path.exists(db_dir_date):
            log(self.LOG_LEVEL, '[Error] Directory already exists, something went wrong')
            raise EnvironmentError('Directory already exists, something went wrong')
        else:
            os.mkdir(db_dir_date)

        page = 1
        while True:
            data = self.fetch(timestamp_check, page)

            try:
                parsed_json = json.loads(data)
            except ValueError as e:
                log(self.LOG_LEVEL, '[Error] ' + e.message)
                raise SystemExit(0)

            if len(parsed_json) != 0:
                file_name = os.path.join(db_dir_date, timestamp_check.strftime('%Y-%m') + "_{:02d}.json".format(page))
                with open(file_name, 'w') as f_out:
                    f_out.write(data)
                page += 1
            else:
                if page == 1:
                    os.rmdir(db_dir_date)
                    self.LOG_LEVEL -= 1
                    return self.STATUS_DONE, timestamp_check
                else:
                    break

        log(self.LOG_LEVEL, 'Fetched ' + str(page) + ' pages')
        self.LOG_LEVEL -= 1

        if timestamp_check.month == 1:
            timestamp_check = timestamp_check.replace(year=timestamp_check.year - 1, month=12)
        else:
            timestamp_check = timestamp_check.replace(month=timestamp_check.month - 1)
        return self.STATUS_ONGOING, timestamp_check

    def fetch(self, timestamp, page):
        self.LOG_LEVEL += 1
        log(self.LOG_LEVEL, 'Fetching page #' + str(page))

        url = "https://zkillboard.com/api/kills/corporationID/{}/year/{}/month/{}/page/{}/".format(
            self.corporation_ids,
            timestamp.year,
            timestamp.month,
            page,
        )

        try:
            request = urllib2.Request(url, None, self.headers)
            response = urllib2.urlopen(request)
        except urllib2.URLError as e:
            log(self.LOG_LEVEL, '[Error] ' + e.reason)
            raise SystemExit(0)

        if response.info().get("Content-Encoding") == "gzip":
            buf = StringIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
        else:
            data = response.read()

        self.LOG_LEVEL -= 1
        return data
