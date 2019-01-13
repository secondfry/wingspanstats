# Author: Rustam Gubaydullin (@second_fry)
# License: MIT (https://opensource.org/licenses/MIT)

from multiprocessing import Pool
from pymongo import MongoClient
import requests
import time

from config.statsconfig import StatsConfig
from scripts.db_fetch import DBFetcher
from scripts.log import log


class DBFetcherESIMongo(DBFetcher):
  LOG_LEVEL = 2

  def __init__(self):
    self.endpoint = StatsConfig.ENDPOINT_ESI_KILLMAIL
    self.session = requests.Session()

    self._init_DB()

  def _log(self, message):
    log(self.LOG_LEVEL, message)

  def run(self):
    self._fetch_killmails()

  def _init_DB(self):
    self.DBClient = MongoClient('localhost', 27017)
    self.DB = self.DBClient.WDS_statistics_v3

  def _fetch_killmails(self):
    size = self.DB.killmails.find({'status.zkb': True, 'status.esi': False}).count()
    if size == 0:
      return

    killmails = self.DB.killmails.find({'status.zkb': True, 'status.esi': False})

    with Pool(50) as p:
      p.map(spawn_fetcher_worker, killmails)


def spawn_fetcher_worker(killmail):
  worker = DBFetcherESIMongoWorker(killmail)
  worker.run()
  worker.close()


class DBFetcherESIMongoWorker(object):
  LOG_LEVEL = 3

  def __init__(self, killmail):
    self.endpoint = StatsConfig.ENDPOINT_ESI_KILLMAIL
    self.session = requests.Session()
    self.killmail = killmail

    self._init_DB()

  def _log(self, message):
    log(self.LOG_LEVEL, message)

  def run(self):
    self._fetch_killmail(self.killmail)

  def _init_DB(self):
    self.DBClient = MongoClient('localhost', 27017)
    self.DB = self.DBClient.WDS_statistics_v3

  def _fetch_killmail(self, killmail):
    data = self._fetch(killmail)
    if not data:
      return

    self._process_killmail(killmail, data)

  def _fetch(self, killmail):
    cached = self.DB.esi_killmails.find_one({'_id': killmail['_id']})
    if cached:
      return cached

    url = self.endpoint.format(killmail['_id'], killmail['zkb']['hash'])
    counter = 0
    while counter < 15:
      res = self.session.get(url, headers=StatsConfig.HEADERS)
      if res.status_code == requests.codes.ok:
        return res.json()

      self._log('[RC#{}] ESI experiencing issues'.format(res.status_code))
      counter += 1
      time.sleep(5)

    return None

  def _process_killmail(self, killmail, esi_data):
    line = {
      '_id': esi_data['killmail_id']
    }

    line.update(esi_data)

    try:
      self.DB.esi_killmails.insert_one(line)
    except:
      # self._log('[KM#{}] DB.esi_killmails insert error'.format(line['_id']))
      pass

    line = {}
    line.update(killmail)
    line.update(esi_data)
    line['status']['esi'] = True

    try:
      self.DB.killmails.update_one(
        {'_id': killmail['_id']},
        {'$set': line}
      )
    except:
      self._log('[KM#{}] DB.killmails update error'.format(line['_id']))
      self._log(killmail)
      self._log(esi_data)
      self._log(line)
      raise

  def close(self):
    self.DBClient.close()