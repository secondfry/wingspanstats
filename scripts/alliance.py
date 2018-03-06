#!/usr/bin/python2
# Author: Rustam Gubaydullin (@second_fry)
# License: MIT (https://opensource.org/licenses/MIT)

import gzip
import json
import os
import requests

from config.statsconfig import StatsConfig
from scripts.log import log
from scripts.state import State


class Alliance(object):
  DEFAULT_STATE = {'page': 1}
  LOG_LEVEL = 3

  def __init__(self, id):
    self.id = id
    self.endpoint = StatsConfig.ENDPOINT_ALLIANCE.format(self.id)
    self.dir = os.path.join(StatsConfig.DATABASE_PATH, str(self.id))
    self.session = requests.Session()
    self.state = State(os.path.join(self.dir, 'state.json'), self.DEFAULT_STATE)

  def get(self):
    while self._fetch():
      self.state.increment('page')
      self.state.save()

    # Last page is always empty
    # So we need to reset state to previous page
    self.state.decrement('page')
    self.state.save()

    self._log('Done!')

  def _fetch(self):
    self._log('Fetching page #' + str(self.state.get('page')))

    server = self._fetch_page(self.state.get('page'))
    client = self._read_page(self.state.get('page'))

    # We got page from server
    # But it's empty
    # So we stop
    if len(server) == 0:
      self._log('Page #' + str(self.state.get('page')) + ' is empty')
      return False

    # We got page from server
    # But it's same as we have already
    # So we just continue
    if len(client) == len(server):
      return True

    # We got page from server
    # It's legit
    # So we save it to disk
    self._save_page(self.state.get('page'), server)
    return True

  def _fetch_page(self, page):
    url = (self.endpoint + 'page/{}/').format(page)
    res = self.session.get(url, headers=StatsConfig.HEADERS)
    return res.json()

  def _read_page(self, page):
    try:
      path = os.path.join(self.dir, str(page) + '.json.gz')
      with gzip.open(path, 'r') as f:
        return json.load(f)
    except:
      return json.dumps([])

  def _save_page(self, page, jsonData):
    path = os.path.join(self.dir, str(page) + '.json.gz')
    with gzip.open(path, 'w') as f:
      f.write(json.dumps(jsonData))

  def _log(self, message):
    log(self.LOG_LEVEL, '[' + str(self.id) + '] ' + message)
