#!/usr/bin/python2
# Author: Rustam Gubaydullin (@second_fry)
# License: MIT (https://opensource.org/licenses/MIT)

from datetime import datetime
from scripts.log import log
from scripts.db_create import DbCreator
from scripts.db_parse import DbParser

if __name__ == "__main__":
  timestamp_start = datetime.now()
  log(0, 'Wingspan Statistics script start')

  creator = DbCreator.factory('zkillboard-json')
  creator.run()

  parser = DbParser.factory('json-mongo')
  parser.run()

  time = datetime.now() - timestamp_start
  log(0, 'Wingspan Statistics script end')
  log(0, 'Elapsed: ' + str(time) + '\n')
