#!/usr/bin/python3
# Author: Rustam Gubaydullin (@second_fry)
# License: MIT (https://opensource.org/licenses/MIT)

from pymongo.errors import PyMongoError
import os
import requests
import time

from config.statsconfig import StatsConfig
from scripts.log import log
from scripts.state import State


STATUS_INIT = 0
STATUS_PROGRESS = 1
STATUS_DONE = 2
STATUS_ERROR = 3


class Alliance(object):
  DEFAULT_STATE = {
    'previous_killmail_id_start': 1,
    'previous_killmail_id_finish': 1,
    'current_killmail_id_start': 1,
    'current_killmail_id_finish': 1,
    'page': 1,
  }
  LOG_LEVEL = 3

  def __init__(self, fetcher, id):
    self.fetcher = fetcher
    self.status = STATUS_INIT
    self.id = id
    self.endpoint = StatsConfig.ENDPOINT_ZKB_ALLIANCE.format(self.id)
    self.session = requests.Session()
    self.dir = os.path.join(StatsConfig.DATABASE_PATH, str(self.id))
    self.state = State(os.path.join(self.dir, 'state.json'), self.DEFAULT_STATE)

    self._once_per_fetch = True

    self._init_directories()

  def _log(self, message):
    log(self.LOG_LEVEL, '[A#' + str(self.id) + '] ' + message)

  def _init_directories(self):
    if not os.path.isdir(self.dir):
      os.mkdir(self.dir)
      self._log('Directory {} created'.format(self.dir))

  def get(self):
    while self.status not in [STATUS_DONE, STATUS_ERROR]:
      data = self._fetch()

      if len(data) == 0:
        self.status = STATUS_DONE
        continue

      self._process(data)
      self._check_status()

      if self.status == STATUS_PROGRESS:
        self.state.increment('page')
        self.state.save()

      time.sleep(1)

    self._update_state()
    self._log('Done!')

  def _fetch(self):
    self._log('[P#{}] Fetching'.format(
      self.state.get('page'),
    ))

    url = '{}page/{}/'.format(self.endpoint, self.state.get('page'))
    res = self.session.get(url, headers=StatsConfig.HEADERS)
    return res.json()

  def _process(self, data):
    self._log('[P#{}] Processing'.format(
      self.state.get('page'),
    ))

    for killmail in data:
      self._current_set_ids(killmail['killmail_id'])
      self._process_killmail(killmail)

  def _current_set_ids(self, kmid):
    if self._once_per_fetch:
      self.state.set('current_killmail_id_start', kmid)
      self.state.set('current_killmail_id_finish', kmid)
      self._once_per_fetch = False
      return

    if kmid > self.state.get('current_killmail_id_start'):
      self._log('THIS IS NOT OK, CURRENT PAGE START ID CHANGED DURING THE RUN')
      self.state.set('current_killmail_id_start', kmid)

    if kmid < self.state.get('current_killmail_id_finish'):
      self.state.set('current_killmail_id_finish', kmid)

  def _process_killmail(self, killmail):
    line = {
      '_id': killmail['killmail_id']
    }

    line.update(killmail)

    try:
      self.fetcher.DB.zkillboard.insert_one(line)
    except PyMongoError as e:
      # E11000 duplicate key error...
      if e.code == 11000:
        # It is fine!
        pass
      else:
        self._log('[KM#{}] DB.esi_killmails insert error'.format(line['_id']))
        self._log('Exception: {}'.format(e))

    line.update({
      'status': {
        'zkb': True,
        'esi': False,
        'parser': False
      }
    })

    try:
      self.fetcher.DB.killmails.insert_one(line)
    except PyMongoError as e:
      # E11000 duplicate key error...
      if e.code == 11000:
        # It is fine!
        pass
      else:
        self._log('[KM#{}] DB.esi_killmails insert error'.format(line['_id']))
        self._log('Exception: {}'.format(e))

  def _check_status(self):
    current_finish = self.state.get('current_killmail_id_finish')
    previous_start = self.state.get('previous_killmail_id_start')

    if current_finish < previous_start:
      self.status = STATUS_DONE
      return

    self.status = STATUS_PROGRESS

  def _update_state(self):
    current_start = self.state.get('current_killmail_id_start')
    current_finish = self.state.get('current_killmail_id_finish')
    self.state.set('previous_killmail_id_start', current_start)
    self.state.set('previous_killmail_id_finish', current_finish)
    self.state.set('current_killmail_id_start', 1)
    self.state.set('current_killmail_id_finish', 1)
    self.state.set('page', 1)
    self.state.save()
