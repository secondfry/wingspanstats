# generalstats.py
# Author: Valtyr Farshield

from skeleton import Skeleton
from statsconfig import StatsConfig
import csv


class GeneralStats(Skeleton):

    def __init__(self):
        self.file_name = "general_stats.txt"
        self.total_kills = 0
        self.total_value = 0
        self.solo_total_kills = 0
        self.solo_total_value = 0

        self.total_kills_hs = 0
        self.total_value_hs = 0
        self.total_kills_ls = 0
        self.total_value_ls = 0
        self.total_kills_ns = 0
        self.total_value_ns = 0
        self.total_kills_wh = 0
        self.total_value_wh = 0

        with open('security.csv', mode='r') as infile:
            reader = csv.reader(infile)
            self.security = {int(rows[0]):int(rows[1]) for rows in reader}

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
        output += "Solo total kills: {}\n".format(self.solo_total_kills)
        output += "Solo total value: {:.2f}b\n".format(float(self.solo_total_value) / 1000000000)
        output += "\n\n"
        output += "High-sec total kills: {} ({:.2f}%)\n".format(
            self.total_kills_hs,
            self.total_kills_hs / float(self.total_kills) * 100
        )
        output += "High-sec total value: {:.2f}b ({:.2f}%)\n".format(
            float(self.total_value_hs) / 1000000000,
            self.total_value_hs / self.total_value * 100
        )
        output += "\n"
        output += "Low-sec total kills: {} ({:.2f}%)\n".format(
            self.total_kills_ls,
            self.total_kills_ls / float(self.total_kills) * 100
        )
        output += "Low-sec total value: {:.2f}b ({:.2f}%)\n".format(
            float(self.total_value_ls) / 1000000000,
            self.total_value_ls / self.total_value * 100
        )
        output += "\n"
        output += "Null-sec total kills: {} ({:.2f}%)\n".format(
            self.total_kills_ns,
            self.total_kills_ns / float(self.total_kills) * 100
        )
        output += "Null-sec total value: {:.2f}b ({:.2f}%)\n".format(
            float(self.total_value_ns) / 1000000000,
            self.total_value_ns / self.total_value * 100
        )
        output += "\n"
        output += "W-space total kills: {} ({:.2f}%)\n".format(
            self.total_kills_wh,
            self.total_kills_wh / float(self.total_kills) * 100
        )
        output += "W-space total value: {:.2f}b ({:.2f}%)\n".format(
            float(self.total_value_wh) / 1000000000,
            self.total_value_wh / self.total_value * 100
        )
        return output

    def process_km(self, killmail):
        self.total_kills += 1
        self.total_value += killmail['zkb']['totalValue']

        [total_non_npc_attackers, wingspan_attackers] = StatsConfig.attacker_types(killmail)
        if total_non_npc_attackers == wingspan_attackers and wingspan_attackers == 1:
            self.solo_total_kills += 1
            self.solo_total_value += killmail['zkb']['totalValue']

        system_id = killmail['solarSystemID']
        if self.security[system_id] == 3:  # high-sec
            self.total_kills_hs += 1
            self.total_value_hs += killmail['zkb']['totalValue']
        elif self.security[system_id] == 2:  # low-sec
            self.total_kills_ls += 1
            self.total_value_ls += killmail['zkb']['totalValue']
        elif self.security[system_id] == 1:  # null-sec
            self.total_kills_ns += 1
            self.total_value_ns += killmail['zkb']['totalValue']
        else:  # w-space
            self.total_kills_wh += 1
            self.total_value_wh += killmail['zkb']['totalValue']
