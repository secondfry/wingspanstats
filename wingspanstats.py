#!/usr/bin/python3
# Author: Rustam Gubaydullin (@second_fry)
# Original author: Valtyr Farshield (github.com/farshield)
# License: MIT (https://opensource.org/licenses/MIT)

from datetime import datetime
from scripts.log import log
from scripts.db_fetch import DBFetcher
from scripts.db_parse import DBParser

if __name__ == "__main__":
  timestamp_start = datetime.now()
  log(0, 'Wingspan Statistics script start')

  zkb_fetcher = DBFetcher.factory('zkillboard-mongo')
  zkb_fetcher.run()

  esi_fetcher = DBFetcher.factory('esi-mongo')
  esi_fetcher.run()

  parser = DBParser.factory('mongo')
  parser.run()

  time = datetime.now() - timestamp_start
  log(0, 'Wingspan Statistics script end')
  log(0, 'Elapsed: ' + str(time) + '\n')
