# !/usr/bin/python2
# Author: Rustam Gubaydullin (@second_fry)
# License: MIT (https://opensource.org/licenses/MIT)

from datetime import datetime
import logging

logging.basicConfig(filename='wingspanstats.log', level=logging.DEBUG)


def log(level, message):
    logging.info('[' + str(datetime.now()) + '] ' + '-' * level + '> ' + message)
    if level < 3:
        print '[' + datetime.now().strftime('%H:%M:%S') + '] ' + '-' * level + '> ' + message
