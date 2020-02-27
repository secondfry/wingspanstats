#!/usr/bin/python3
# Author: Rustam Gubaydullin (@second_fry)
# License: MIT (https://opensource.org/licenses/MIT)

from datetime import datetime
import logging

from config.statsconfig import StatsConfig

logging.basicConfig(filename='wingspanstats.log', level=logging.DEBUG)


def log(level, message):
  logging.info('[' + str(datetime.now()) + '] ' + '-' * level + '> ' + message)
  if level < StatsConfig.LOG_LEVEL_CONSOLE:
    print('[{}] {}> {}'.format(
      datetime.now().strftime('%H:%M:%S'),
      '-' * level,
      message,
    ))
