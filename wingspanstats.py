# !/usr/bin/python2
# Author: Rustam Gubaydullin (@second_fry)
# License: MIT (https://opensource.org/licenses/MIT)

from datetime import datetime
from scripts.log import log
from scripts.db_create import DbCreate
from scripts.db_parse import DbParse

if __name__ == "__main__":
    timestamp_start = datetime.now()
    log(0, 'Wingspan Statistics script start')

    DbCreate.factory('zkillboard-json')
    DbParse.factory('json')
    DbCreate.factory('zkillboard-mongo')
    DbParse.factory('mongo')

    time = datetime.now() - timestamp_start
    log(0, 'Wingspan Statistics script end')
    log(0, 'Elapsed: ' + str(time) + '\n')
