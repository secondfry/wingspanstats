# !/usr/bin/python2
# Author: Rustam Gubaydullin (@second_fry)
# Original author: Valtyr Farshield (github.com/farshield)
# License: MIT (https://opensource.org/licenses/MIT)

import os


class StatsConfig(object):
    ALLIANCE_ID = 99005770

    ALLIANCE_IDS = [
        99005770,  # The WINGSPAN Logo Alliance <WING>
        99006319   # WiNGSPAN Delivery Network <WDN>
    ]

    CORPORATION_IDS = [
        98330748,  # WiNGSPAN Delivery Services
        98415327   # WiNGSPAN Academy for Enterprising Pilots
    ]

    OTHER_CORPS_IDS = [
        98463483   # Deep Space Travel Agency # I'm still wondering if they were spies all along
    ]

    HEADERS = {
        "User-Agent" : "wingspanstats fork, secondfry@gmail.com",
        "Accept-encoding": "gzip"
    }

    LOG_PATH = os.path.join('logs')
    DATABASE_PATH = os.path.join('database')
    RESULTS_PATH = os.path.join('results')
    SCRIPTS_PATH = os.path.join('scripts')

    FLEET_COMP = 0.25
    INCLUDE_AWOX = False

    MAX_PLACES = 10

    EARLIEST = '2014-07'
