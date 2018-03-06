#!/usr/bin/python2
# Author: Rustam Gubaydullin (@second_fry)
# License: MIT (https://opensource.org/licenses/MIT)

import os
import requests

from config.statsconfig import StatsConfig
from scripts.alliance import Alliance
from scripts.state import State


class Corporation(Alliance):
  def __init__(self, id):
    self.id = id
    self.endpoint = StatsConfig.ENDPOINT_CORPORATION.format(self.id)
    self.dir = os.path.join(StatsConfig.DATABASE_PATH, str(self.id))
    self.session = requests.Session()
    self.state = State(os.path.join(self.dir, 'state.json'), self.DEFAULT_STATE)
