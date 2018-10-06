#!/usr/bin/python2
# Author: Rustam Gubaydullin (@second_fry)
# License: MIT (https://opensource.org/licenses/MIT)

import os
import requests

from config.statsconfig import StatsConfig
from scripts.DBFetcherZkillboardMongo.alliance import Alliance
from scripts.state import State


class Corporation(Alliance):
  def __init__(self, fetcher, id):
    super().__init__(fetcher, id)
    self.endpoint = StatsConfig.ENDPOINT_ZKB_CORPORATION.format(self.id)
