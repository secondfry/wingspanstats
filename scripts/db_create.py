#!/usr/bin/python2
# Author: Rustam Gubaydullin (@second_fry)
# Original author: Valtyr Farshield (github.com/farshield)
# License: MIT (https://opensource.org/licenses/MIT)

import os

from config.statsconfig import StatsConfig
from scripts.alliance import Alliance
from scripts.corporation import Corporation
from scripts.log import log


class DbCreator(object):
  LOG_LEVEL = 1

  @staticmethod
  def factory(type):
    """
    Provides DB creator

    :param type Selects type of DB creator
    """
    if type == "zkillboard-json":
      log(DbCreator.LOG_LEVEL, 'Creating zkillboard fetcher with JSON on our side')
      return DbCreatorZkillboardJSON()

    assert 0, "Source '" + type + "' is not defined"


class DbCreatorZkillboardJSON(DbCreator):
  LOG_LEVEL = 2

  def __init__(self):
    self._init_entities()
    self._init_directories()

  def run(self):
    self._fetch_killmails()

  def _init_entities(self):
    self.entities = {}
    self._init_alliances()
    self._init_corporations()

  def _init_alliances(self):
    for id in StatsConfig.ALLIANCE_IDS:
      self.entities[id] = Alliance(id)

  def _init_corporations(self):
    for id in StatsConfig.CORPORATION_IDS:
      self.entities[id] = Corporation(id)

  def _init_directories(self):
    self.dir = StatsConfig.DATABASE_PATH
    self._check_directory(self.dir)

    for key, entity in self.entities.iteritems():
      self._check_directory(os.path.join(self.dir, str(key)))

  def _check_directory(self, dir):
    if not os.path.isdir(dir):
      os.mkdir(dir)
      log(self.LOG_LEVEL + 1, 'Directory ' + dir + ' created')

  def _fetch_killmails(self):
    for key, entity in self.entities.iteritems():
      log(self.LOG_LEVEL, 'Fetching entity #' + str(key))
      entity.get()
