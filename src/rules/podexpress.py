# podexpress.py
# Author: Valtyr Farshield

from skeleton import Skeleton
from statsconfig import StatsConfig


class PodExpress(Skeleton):

    def __init__(self):
        self.file_name = "pod_express.txt"
        self.most_valueable = {}

    def __str__(self):
        output = ""
        output += "Most valueable pod kills\n"
        output += "--------------------------------------------\n"
        place = 0
        for w in sorted(
                self.most_valueable,
                key=self.most_valueable.get,
                reverse=True
        )[:StatsConfig.MAX_PLACES]:
            place += 1
            output += "#{:02d} - https://zkillboard.com/kill/{}/ - {:.2f}m\n".format(
                place,
                w,
                self.most_valueable[w] / 1000000.0,
            )

        return output

    def process_km(self, killmail):
        if killmail['victim']['shipTypeID'] in [670, 33328]:
            kill_id = killmail['killID']
            isk_destroyed = killmail['zkb']['totalValue']
            self.most_valueable[kill_id] = isk_destroyed
