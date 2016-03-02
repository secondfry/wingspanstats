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


class DbParse(object):
    STATUS_DONE = 0
    STATUS_START = 1
    STATUS_ONGOING = 2
    LOG_LEVEL = 1

    def __init__(self):
        log(self.LOG_LEVEL, 'Starting DB parser')
        self.parse_db()

    def parse_db(self):
        self.LOG_LEVEL += 1
        db_dir = None

        log(self.LOG_LEVEL, 'Checking results directory')
        if not os.path.isdir(StatsConfig.RESULTS_PATH):
            os.mkdir(StatsConfig.RESULTS_PATH)
        else:
            db_dir = os.listdir(StatsConfig.RESULTS_PATH)

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
            log(self.LOG_LEVEL, 'Starting parsing ' + timestamp_check.strftime('%Y-%m'))
            status, timestamp_check = self.parse(timestamp_check)
        log(self.LOG_LEVEL, 'Done! [database parser]')
        self.LOG_LEVEL -= 1

    def parse(self, timestamp_check):
        self.LOG_LEVEL += 1

        db_dir_date = os.path.join(StatsConfig.DATABASE_PATH, timestamp_check.strftime('%Y-%m'))

        page = 1
        while True:
            filepath = os.path.join(db_dir_date, timestamp_check.strftime('%Y-%m') + "_{:02d}.json".format(page))
            if os.path.exists(filepath):
                with open(filepath) as data_file:
                    data = json.load(data_file)

                for killmail in data:
                    self.analyze(killmail)
            else:
                break

        log(self.LOG_LEVEL, 'Fetched ' + str(page) + ' pages')
        self.LOG_LEVEL -= 1

        if timestamp_check.month == 1:
            timestamp_check = timestamp_check.replace(year=timestamp_check.year - 1, month=12)
        else:
            timestamp_check = timestamp_check.replace(month=timestamp_check.month - 1)
        return self.STATUS_ONGOING, timestamp_check

    def analyze(self, killmail):
        self.LOG_LEVEL += 1

        killmail_awox = False
        if killmail['victim']['corporationID'] in StatsConfig.CORPORATION_IDS:
            killmail_awox = True

        attackers_capsuleer, attackers_wingspan = self.count_attackers(killmail['attackers'])

        if attackers_capsuleer < 0: return
        if killmail_awox or not StatsConfig.INCLUDE_AWOX: return
        if float(attackers_wingspan) / float(attackers_capsuleer) < StatsConfig.FLEET_COMP: return


        log(self.LOG_LEVEL, '[Error] Debug error')
        raise SystemExit(0)

        self.LOG_LEVEL -= 1
        return data

    def count_attackers(self, attackers):
        attackers_capsuleer = 0
        attackers_wingspan = 0

        for attacker in attackers:
            # Non-NPC attackers
            if attacker['characterName'] != '':
                attackers_capsuleer += 1

                # Wingspan attackers
                if attacker['corporationID'] in StatsConfig.CORPORATION_IDS:
                    attackers_wingspan += 1

        return attackers_capsuleer, attackers_wingspan
