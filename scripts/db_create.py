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
import requests


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
        self.filepath_lh = os.path.join(StatsConfig.DATABASE_PATH, 'answers', 'lastheaders.json')
        self.session = requests.Session()
        self.create_db()

    def create_db(self):
        db_dir = None

        log(self.LOG_LEVEL, 'Database directory?')
        if not os.path.isdir(StatsConfig.DATABASE_PATH):
            os.mkdir(StatsConfig.DATABASE_PATH)
            os.mkdir(os.path.join(StatsConfig.DATABASE_PATH, 'answers'))
            log(self.LOG_LEVEL + 1, 'Database directory created')
        else:
            db_dir = os.listdir(StatsConfig.DATABASE_PATH)
            db_dir.remove('answers')
            log(self.LOG_LEVEL + 1, 'Database directory exists')

        log(self.LOG_LEVEL, 'Last checked timestamp?')
        if db_dir:
            year_last, month_last = sorted(db_dir)[-1].split("-")
            timestamp_last = datetime.strptime(year_last + month_last, '%Y%m')
            log(self.LOG_LEVEL + 1, 'Last checked timestamp: ' + timestamp_last.strftime('%Y-%m-%d'))
        else:
            timestamp_last = self.first()
            log(self.LOG_LEVEL + 1, 'Just fetched first timestamp: ' + timestamp_last.strftime('%Y-%m-%d'))

        log(self.LOG_LEVEL, 'Parsing new data')
        timestamp_today = datetime.now()
        status = self.STATUS_START

        while status != self.STATUS_DONE:
            status, timestamp_last = self.parse(timestamp_last)
            if status != self.STATUS_DONE and timestamp_last >= timestamp_today:
                status = self.STATUS_DONE
        log(self.LOG_LEVEL, 'Done! [zkillboard fetcher]')

    def parse(self, timestamp):
        self.LOG_LEVEL += 1
        log(self.LOG_LEVEL, 'Starting fetch: ' + timestamp.strftime('%Y-%m'))

        db_dir_date = os.path.join(StatsConfig.DATABASE_PATH, timestamp.strftime('%Y-%m'))
        if not os.path.exists(db_dir_date):
            os.mkdir(db_dir_date)
            page = 1
        else:
            try:
                file = sorted(os.listdir(db_dir_date))[-1]
                page = int(file.split('_')[-1].split('.')[0])
                os.remove(os.path.join(db_dir_date, file))
            except IndexError:
                page = 1

        while True:
            mtext, mjson = self.fetch(timestamp, page)

            if len(mjson) != 0:
                filepath = os.path.join(db_dir_date, timestamp.strftime('%Y-%m') + "_{:02d}.json".format(page))
                with open(filepath, 'w') as file:
                    file.write(mtext)
                page += 1
            else:
                if page == 1:
                    os.rmdir(db_dir_date)
                    self.LOG_LEVEL -= 1
                    return self.STATUS_DONE, timestamp
                else:
                    break

        log(self.LOG_LEVEL, 'Fetched ' + str(page) + ' pages')
        self.LOG_LEVEL -= 1

        if timestamp.month == 12:
            timestamp = timestamp.replace(year=timestamp.year + 1, month=1)
        else:
            timestamp = timestamp.replace(month=timestamp.month + 1)
        return self.STATUS_ONGOING, timestamp

    def fetch(self, timestamp, page):
        self.LOG_LEVEL += 1
        log(self.LOG_LEVEL, 'Fetching {}-{}_{}'.format(timestamp.year, timestamp.month, page))

        url = "https://zkillboard.com/api/kills/corporationID/{}/year/{}/month/{}/page/{}/orderDirection/asc/".format(
                self.corporation_ids,
                timestamp.year,
                timestamp.month,
                page,
        )

        r = self.session.get(url, headers=self.headers)
        mtext = r.text
        mjson = r.json()

        if os.path.exists(self.filepath_lh):
            os.remove(self.filepath_lh)
        with open(self.filepath_lh, 'w') as file:
            file.write(str(r.headers))

        self.LOG_LEVEL -= 1
        return mtext, mjson

    def first(self):
        """
        Gets first kill recorded on zkb

        :return datetime
        """
        self.LOG_LEVEL += 1
        log(self.LOG_LEVEL, 'Fetching first kill.')

        filepath = os.path.join(StatsConfig.DATABASE_PATH, 'answers', 'firstkill.json')
        if os.path.exists(filepath):
            with open(filepath) as file:
                mjson = json.load(file)
        else:
            url = "https://zkillboard.com/api/kills/corporationID/{}/limit/1/orderDirection/asc/".format(
                    self.corporation_ids,
            )

            r = self.session.get(url, headers=self.headers)
            mtext = r.text
            mjson = r.json()

            if os.path.exists(self.filepath_lh):
                os.remove(self.filepath_lh)
            with open(self.filepath_lh, 'w') as file:
                file.write(str(r.headers))

            if len(mjson) != 0:
                os.path.join(StatsConfig.DATABASE_PATH, 'answers', 'firstkill.json')
                with open(filepath, 'w') as file:
                    file.write(mtext)

        self.LOG_LEVEL -= 1
        return datetime.strptime(mjson[0]['killTime'], '%Y-%m-%d %H:%M:%S')
