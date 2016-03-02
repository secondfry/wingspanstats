# generalstats.py
# Author: Valtyr Farshield

import os
from skeleton import Skeleton
from statsconfig import StatsConfig
import csv
import numpy as np
import matplotlib.pyplot as plt


class GeneralStats(Skeleton):
    def __init__(self):
        self.file_name = "general_stats"
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

        self.wh_stats = {}

        with open('security.csv', mode='r') as infile:
            reader = csv.reader(infile)
            self.security = {int(rows[0]): rows[1] for rows in reader}

    def __str__(self):
        output = ""
        output += "General statistics\n"
        output += "--------------------------------------------\n"
        output += "Total kills: {}\n".format(self.total_kills)
        output += "Total value: {:.2f}b\n".format(float(self.total_value) / 1000000000.0)
        if self.total_kills > 0:
            output += "Average value/kill: {:.2f}m\n".format(
                    float(self.total_value) / 1000000 / self.total_kills
            )
        output += "Solo total kills: {}\n".format(self.solo_total_kills)
        output += "Solo total value: {:.2f}b\n".format(float(self.solo_total_value) / 1000000000.0)
        output += "\n\n"
        output += "High-sec total kills: {} ({:.2f}%)\n".format(
                self.total_kills_hs,
                self.total_kills_hs / float(self.total_kills) * 100
        )
        output += "High-sec total value: {:.2f}b ({:.2f}%)\n".format(
                float(self.total_value_hs) / 1000000000.0,
                self.total_value_hs / self.total_value * 100
        )
        output += "\n"
        output += "Low-sec total kills: {} ({:.2f}%)\n".format(
                self.total_kills_ls,
                self.total_kills_ls / float(self.total_kills) * 100
        )
        output += "Low-sec total value: {:.2f}b ({:.2f}%)\n".format(
                float(self.total_value_ls) / 1000000000.0,
                self.total_value_ls / self.total_value * 100
        )
        output += "\n"
        output += "Null-sec total kills: {} ({:.2f}%)\n".format(
                self.total_kills_ns,
                self.total_kills_ns / float(self.total_kills) * 100
        )
        output += "Null-sec total value: {:.2f}b ({:.2f}%)\n".format(
                float(self.total_value_ns) / 1000000000.0,
                self.total_value_ns / self.total_value * 100
        )
        output += "\n"
        output += "W-space total kills: {} ({:.2f}%)\n".format(
                self.total_kills_wh,
                self.total_kills_wh / float(self.total_kills) * 100
        )
        output += "W-space total value: {:.2f}b ({:.2f}%)\n".format(
                float(self.total_value_wh) / 1000000000.0,
                self.total_value_wh / self.total_value * 100
        )

        if self.wh_stats != {}:
            for wh_class in ['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c13', 'c12']:
                if wh_class in self.wh_stats.keys():
                    output += "  [*] {} - total kills: {}, total isk: {:.2f}b\n".format(
                            wh_class.upper() if wh_class != 'c12' else 'Thera',
                            self.wh_stats[wh_class][0],
                            self.wh_stats[wh_class][1] / 1000000000.0,
                    )

            drifter_total = 0
            drifter_isk = 0
            for wh_class in ['c14', 'c15', 'c16', 'c17', 'c18']:
                if wh_class in self.wh_stats.keys():
                    drifter_total += self.wh_stats[wh_class][0]
                    drifter_isk += self.wh_stats[wh_class][1]
            if drifter_total != 0:
                output += "  [*] Drifter wormholes - total kills: {}, total isk: {:.2f}b\n".format(
                        drifter_total,
                        drifter_isk / 1000000000.0,
                )

        return output

    def additional_processing(self, directory):
        # -------------------------------------------------
        sizes = np.array([
            self.total_kills_hs,
            self.total_kills_ls,
            self.total_kills_ns,
            self.total_kills_wh
        ])
        percentage = 100. * sizes / sizes.sum()
        labels = ['High-sec', 'Low-sec', 'Null-sec', 'W-space']
        labels2 = ['{0} - {1:1.2f} %'.format(i, j) for i, j in zip(labels, percentage)]
        colors = ['green', 'yellow', 'red', 'lightskyblue']

        plt.title("Total number of ships killed")
        patches, texts = plt.pie(sizes, colors=colors, shadow=True, startangle=90)
        plt.legend(patches, labels2, loc="best")
        plt.axis('equal')

        plt.plot()
        plt.savefig(os.path.join(directory, 'piechart_all_ships_destroyed'))

        # -------------------------------------------------
        sizes = np.array([
            self.total_value_hs,
            self.total_value_ls,
            self.total_value_ns,
            self.total_value_wh
        ])
        percentage = 100. * sizes / sizes.sum()
        labels = ['High-sec', 'Low-sec', 'Null-sec', 'W-space']
        labels2 = ['{0} - {1:1.2f} %'.format(i, j) for i, j in zip(labels, percentage)]
        colors = ['green', 'yellow', 'red', 'lightskyblue']

        plt.title("Total ISK destroyed")
        patches, texts = plt.pie(sizes, colors=colors, shadow=True, startangle=90)
        plt.legend(patches, labels2, loc="best")
        plt.axis('equal')

        plt.plot()
        plt.savefig(os.path.join(directory, 'piechart_all_isk_destroyed'))

    def process_km(self, killmail):
        self.total_kills += 1
        self.total_value += killmail['zkb']['totalValue']

        [total_non_npc_attackers, wingspan_attackers] = StatsConfig.attacker_types(killmail)
        if total_non_npc_attackers == wingspan_attackers and wingspan_attackers == 1:
            self.solo_total_kills += 1
            self.solo_total_value += killmail['zkb']['totalValue']

        system_id = killmail['solarSystemID']
        if self.security[system_id] == "hs":  # high-sec
            self.total_kills_hs += 1
            self.total_value_hs += killmail['zkb']['totalValue']
        elif self.security[system_id] == "ls":  # low-sec
            self.total_kills_ls += 1
            self.total_value_ls += killmail['zkb']['totalValue']
        elif self.security[system_id] == "ns":  # null-sec
            self.total_kills_ns += 1
            self.total_value_ns += killmail['zkb']['totalValue']
        else:  # w-space
            self.total_kills_wh += 1
            self.total_value_wh += killmail['zkb']['totalValue']

            # stats for each wh class
            if self.security[system_id] in self.wh_stats.keys():
                self.wh_stats[self.security[system_id]][0] += 1
                self.wh_stats[self.security[system_id]][1] += killmail['zkb']['totalValue']
            else:
                self.wh_stats[self.security[system_id]] = [1, killmail['zkb']['totalValue']]
