# capitals.py
# Author: Valtyr Farshield

from skeleton import Skeleton
from statsconfig import StatsConfig


class Capitals(Skeleton):

    def __init__(self):
        self.file_name = "capital_kills.txt"
        self.most_valueable = {}

    def __str__(self):
        output = ""
        output += "Capital kills\n"
        output += "--------------------------------------------\n"
        place = 0
        for w in sorted(
                self.most_valueable,
                key=self.most_valueable.get,
                reverse=True
        )[:StatsConfig.MAX_PLACES]:
            place += 1
            output += "#{:02d} - https://zkillboard.com/kill/{}/ - {:.2f}b\n".format(
                place,
                w,
                self.most_valueable[w] / 1000000000.0,
            )

        return output

    def process_km(self, killmail):
        kill_id = killmail['killID']
        isk_destroyed = killmail['zkb']['totalValue']
        victim_ship = killmail['victim']['shipTypeID']
        if victim_ship in [
            19724, 34339, 19722, 34341, 19726, 34343, 19720, 34345,  # Dreads
            23757, 23915, 24483, 23911,  # Carriers
            37604, 37605, 37606, 37607,  # Force auxiliaries
            23919, 22852, 3628, 23913, 3514, 23917,  # Supers
            11567, 671, 3764, 23773,  # Titans
        ]:
            self.most_valueable[kill_id] = isk_destroyed
