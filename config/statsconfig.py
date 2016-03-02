# !/usr/bin/python2
# Author: Rustam Gubaydullin (@second_fry)
# Original author: Valtyr Farshield (github.com/farshield)
# License: MIT (https://opensource.org/licenses/MIT)

import os


class StatsConfig(object):
    CORPORATION_IDS = [
        98330748,  # WiNGSPAN Delivery Services
        98415327,  # WiNGSPAN Academy for Enterprising Pilots
    ]

    HEADERS = {
        "User-Agent" : "wingspanstats fork, secondfry@gmail.com",
        "Accept-encoding": "gzip"
    }

    LOG_PATH = os.path.join('logs')
    DATABASE_PATH = os.path.join('database')
    RESULTS_PATH = os.path.join('result')

    FLEET_COMP = 0.25
    INCLUDE_AWOX = False

    MAX_PLACES = 25
