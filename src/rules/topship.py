# topship.py
# Author: Valtyr Farshield

import csv
from skeleton import Skeleton
from statsconfig import StatsConfig


class TopShip(Skeleton):

    def __init__(self):
        self.file_name = "top_ship.txt"
        self.ships_destroyed = {}
        self.isk_destroyed = {}

        with open('typeIDs.csv', mode='r') as infile:
            reader = csv.reader(infile)
            self.items = {int(rows[0]):rows[1] for rows in reader}


    def __str__(self):
        output = ""

        output += "Ships destroyed by a specific hull\n"
        output += "--------------------------------------------\n"
        place = 0
        for w in sorted(
                self.ships_destroyed,
                key=self.ships_destroyed.get,
                reverse=True
        )[:StatsConfig.MAX_PLACES]:
            place += 1
            output += "#{:02d} - {} - {} ships\n".format(
                place,
                self.items[w],
                self.ships_destroyed[w]
            )

        output += "\n"

        output += "ISK destroyed by a specific hull\n"
        output += "--------------------------------------------\n"
        place = 0
        for w in sorted(
                self.isk_destroyed,
                key=self.isk_destroyed.get,
                reverse=True
        )[:StatsConfig.MAX_PLACES]:
            place += 1
            output += "#{:02d} - {} - {:.2f}b\n".format(
                place,
                self.items[w],
                self.isk_destroyed[w] / 1000000000.0
            )

        return output

    def process_km(self, killmail):
        isk_destroyed = killmail['zkb']['totalValue']

        for attacker in killmail['attackers']:
            attacker_name = attacker['characterName']
            attacker_corp = attacker['corporationID']
            attacker_ship = attacker['shipTypeID']

            if attacker_ship != 0 and attacker_ship not in [670, 33328]:  # ignore unknown and capsules
                if attacker_name != "" and attacker_corp in StatsConfig.CORP_IDS:

                    if attacker_ship in self.ships_destroyed.keys():
                        self.ships_destroyed[attacker_ship] += 1
                    else:
                        self.ships_destroyed[attacker_ship] = 1

                    if attacker_ship in self.isk_destroyed.keys():
                        self.isk_destroyed[attacker_ship] += isk_destroyed
                    else:
                        self.isk_destroyed[attacker_ship] = isk_destroyed
