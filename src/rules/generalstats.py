# generalstats.py
# Author: Valtyr Farshield

from skeleton import Skeleton


class GeneralStats(Skeleton):

    def __init__(self):
        self.file_name = "general_stats.txt"
        self.total_kills = 0
        self.total_value = 0

    def __str__(self):
        output = ""
        output += "General statistics\n"
        output += "--------------------------------------------\n"
        output += "Total kills: {}\n".format(self.total_kills)
        output += "Total value: {:.2f}b\n".format(float(self.total_value) / 1000000000)
        if self.total_kills > 0:
            output += "Average value/kill: {:.2f}m\n".format(
                float(self.total_value) / 1000000 / self.total_kills
            )
        return output

    def process_km(self, killmail):
        self.total_kills += 1
        self.total_value += killmail['zkb']['totalValue']
