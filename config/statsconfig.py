#!/usr/bin/python3
# Author: Rustam Gubaydullin (@second_fry)
# Original author: Valtyr Farshield (github.com/farshield)
# License: MIT (https://opensource.org/licenses/MIT)

from dotenv import find_dotenv, load_dotenv, get_key, set_key

import hashlib
import os
import re

dotenvPath = find_dotenv()
if not get_key(dotenvPath, 'MONGODB_URL'):
  raise Exception('You must specify MONGODB_URL in your .env file')
if not re.match('\w+@\w+', os.getenv('MAIL')) and not get_key(dotenvPath, 'MAIL'):
  raise Exception('You must specify your contact MAIL in your .env file')
if not get_key(dotenvPath, 'OS_HASH'):
  osHash = hashlib.sha256(str(os.environ).encode('utf-8')).hexdigest()
  set_key(dotenvPath, 'OS_HASH', osHash)
load_dotenv(dotenvPath)


class StatsConfig(object):
  # # Your main configuration
  ALLIANCE_IDS = [
    99005770, # The WINGSPAN Logo Alliance <WING>
    99006319  # WiNGSPAN Delivery Network <WDN>
  ]

  CORPORATION_IDS = [
    98330748  # WiNGSPAN Delivery Services <WDS>
  ]

  ENTITY_IDS = ALLIANCE_IDS + CORPORATION_IDS

  # Required share of pilots from requested entity for kill to be counted
  FLEET_COMP = 0.25

  # Should awox kills be counted towards full totals? (they have their own category anyway)
  INCLUDE_AWOX = False

  # Earliest month for leaderboard to be created
  EARLIEST = '2014-07'

  # # Network related configuration
  # Amount of threads to create for fetching ESI data
  ESI_WORKERS_POOL = int(os.getenv('ESI_WORKERS_POOL') or 20)
  ESI_WORKER_PAYLOAD_LENGTH = int(os.getenv('ESI_WORKER_PAYLOAD_LENGTH') or 100)

  HEADERS = {
    "User-Agent": 'WDS statistics v3, {} [{}]'.format(os.getenv('MAIL'), os.getenv('OS_HASH')),
    "Accept-encoding": "gzip"
  }
  ENDPOINT_ZKB_ALLIANCE = 'https://zkillboard.com/api/allianceID/{}/'  # .format(id)
  ENDPOINT_ZKB_CORPORATION = 'https://zkillboard.com/api/corporationID/{}/'  # .format(id)
  ENDPOINT_ESI_KILLMAIL = 'https://esi.evetech.net/latest/killmails/{}/{}/?datasource=tranquility'  # .format(id, hash)
  ENDPOINT_ESI_UNIVERSE_NAMES = 'https://esi.evetech.net/latest/universe/names/'  # POST request! ids is array

  # # OS related configuration
  LOG_PATH = os.path.join('logs')
  DATABASE_PATH = os.path.join('database')
  RESULTS_PATH = os.path.join('results')
  SCRIPTS_PATH = os.path.join('scripts')

  # # Deployment related cofiguration
  MONGODB_URL = os.getenv('MONGODB_URL')

  # # etc.
  LOG_LEVEL_CONSOLE = int(os.getenv('LOG_LEVEL_CONSOLE') or 3)
