#!/usr/bin/python2
# Author: Rustam Gubaydullin (@second_fry)
# Original author: Valtyr Farshield (github.com/farshield)
# License: MIT (https://opensource.org/licenses/MIT)

from dotenv import load_dotenv
import os

load_dotenv()


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
    "User-Agent" : "WDS statistics v3, secondfry@gmail.com",
    "Accept-encoding": "gzip"
  }
  ENDPOINT_ZKB_ALLIANCE = 'https://zkillboard.com/api/allianceID/{}/'  # .format(id)
  ENDPOINT_ZKB_CORPORATION = 'https://zkillboard.com/api/corporationID/{}/'  # .format(id)
  ENDPOINT_ESI_KILLMAIL = 'https://esi.evetech.net/latest/killmails/{}/{}/?datasource=tranquility'  # .format(id, hash)
  ENDPOINT_ESI_UNIVERSE_NAMES = 'https://esi.evetech.net/latest/universe/names/'  # POST request! ids is array

  LOG_PATH = os.path.join('logs')
  DATABASE_PATH = os.path.join('database')
  RESULTS_PATH = os.path.join('results')
  SCRIPTS_PATH = os.path.join('scripts')

  FLEET_COMP = 0.25
  INCLUDE_AWOX = False
  MAX_PLACES = 10

  EARLIEST = '2014-07'

  MONGODB_URL = os.getenv('MONGODB_URL')
