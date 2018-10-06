# Author: Rustam Gubaydullin (@second_fry)
# License: MIT (https://opensource.org/licenses/MIT)

from pymongo import MongoClient

from config.statsconfig import StatsConfig
from scripts.db_fetch import DBFetcher
from scripts.DBFetcherZkillboardMongo.alliance import Alliance
from scripts.DBFetcherZkillboardMongo.corporation import Corporation
from scripts.log import log


class DBFetcherZkillboardMongo(DBFetcher):
  LOG_LEVEL = 2

  def __init__(self):
    self._init_entities()
    self._init_DB()

  def run(self):
    self._fetch_killmails()

  def _init_entities(self):
    self.entities = {}
    self._init_alliances()
    self._init_corporations()

  def _init_alliances(self):
    for id in StatsConfig.ALLIANCE_IDS:
      self.entities[id] = Alliance(self, id)

  def _init_corporations(self):
    for id in StatsConfig.CORPORATION_IDS:
      self.entities[id] = Corporation(self, id)

  def _init_DB(self):
    self.DBClient = MongoClient('localhost', 27017)
    self.DB = self.DBClient.WDS_statistics_v3

  def _fetch_killmails(self):
    for key, entity in self.entities.items():
      log(self.LOG_LEVEL, 'Fetching entity #' + str(key))
      entity.get()
