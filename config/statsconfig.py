#!/usr/bin/python2
# Author: Rustam Gubaydullin (@second_fry)
# Original author: Valtyr Farshield (github.com/farshield)
# License: MIT (https://opensource.org/licenses/MIT)

from datetime import datetime
import os


class StatsConfig(object):
  ALLIANCE_IDS = [
    99005770,  # The WINGSPAN Logo Alliance <WING>
    99006319   # WiNGSPAN Delivery Network <WDN>
  ]

  CORPORATION_IDS = [
    98330748   # WiNGSPAN Delivery Services <WDS>
  ]

  ENTITY_IDS = ALLIANCE_IDS + CORPORATION_IDS

  HEADERS = {
    "User-Agent" : "wingspanstats fork, secondfry@gmail.com",
    "Accept-encoding": "gzip"
  }
  ENDPOINT_ALLIANCE = 'https://zkillboard.com/api/alliance/{}/orderDirection/asc/'
  ENDPOINT_CORPORATION = 'https://zkillboard.com/api/corporation/{}/endTime/201508260400/orderDirection/asc/'

  LOG_PATH = os.path.join('logs')
  DATABASE_PATH = os.path.join('database')
  RESULTS_PATH = os.path.join('results')
  SCRIPTS_PATH = os.path.join('scripts')

  FLEET_COMP = 0.25
  INCLUDE_AWOX = False
  MAX_PLACES = 10

  EARLIEST = '2014-07'
